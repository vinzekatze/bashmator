from jsonschema import validate
import argparse
import subprocess
from yaml import safe_load
import sys

from bones.funcs import *
from bones.schemas import main_schema, help_yaml_structure

class YamlScript:
    def __init__(self, path: str, name):
        self.yaml_schema = safe_load(main_schema)
        self.name = name
        self.path = path
        # Информация из yaml
        self.author = ''
        self.description = ''
        self.tags = []
        self.install = ''
        self.shell = ''
        self.arguments = {}
        self.scripts_dict = {}
        # Индикаторы
        self.status = 'OK'
        self.items = False
        self.script = False
        # Параметры аргументов
        self.items_launch_set = [0]

        # Загрузка yaml файла
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                try: content = safe_load(f)
                except Exception as errormsg:
                    self.status = 'ERROR'
                    error('YAML syntax error', errormsg)
        except Exception as errormsg:
            error('Can\'t load yaml file.', errormsg)
            self.status = 'ERROR'
        
        # Валидация структуры yaml
        if self.status == 'OK':
            try:
                validate(content, self.yaml_schema)
            except Exception as errormsg:
                error('YAML validation error', str(errormsg).partition('\n')[0])
                warning_file(self.path)
                self.status = 'ERROR'
            else:
                # Считывание данных
                self.author =  content.get('author', '')
                self.description = content.get('description','')
                self.install = content.get('install','')
                self.shell = content.get('shell','') 
                if content.get('tags',[]):
                    self.tags = [str(tag) for tag in content.get('tags',[])]
                if content.get('arguments',[]):
                    self.arguments = content.get('arguments',{})
                
                # Формирование словаря доступных скриптов
                if content.get('script',''):
                    self.scripts_dict.update({0: {'script': content['script'],'description':'main script (default)'}})
                    self.script = True
                for key in content.keys():
                    if key.startswith("item_"):
                        self.scripts_dict.update({int(key[5:]): content.get(key,{})})
                        self.items = True
                
    def ParseArgs(self, args: list, scriptname: str):
        if self.status == 'OK':
            try:
                # Формирование эпилога
                epilog_s2 = 'Shell:  {shell}\nAuthor: {author}\nTags:   {tags}'.format(
                        author=self.author,
                        tags=', '.join(self.tags),
                        shell=self.shell)
                if self.items:
                    items_table = [['#', 'description']]
                    for key in sorted(self.scripts_dict.keys()):
                        items_table.append([key, self.scripts_dict[key].get('description','')])
                    items_table_parced = 'items list:\n'+ make_table(items_table)
                    epilog = items_table_parced + '\n\n' + epilog_s2
                else:
                    epilog = epilog_s2

                # Создание парсера аргументов для скрипта
                self.parser = argparse.ArgumentParser(
                    formatter_class = argparse.RawDescriptionHelpFormatter,
                    description = self.description, 
                    prog = scriptname, 
                    epilog=epilog
                    )
                if self.status == 'OK':
                    # Добавление аргументов для items
                    if self.items:
                        items_g = self.parser.add_argument_group('items options')
                        items_g.add_argument('--item', 
                            default='0', 
                            metavar='NUM',
                            dest='items_launch_set', 
                            help='item index to execute (can be a sequence, ex: \'1,2,4-6\')',
                            required=not self.script)
                    
                    #  Добавление общих аргументов
                    if self.arguments:
                        for arg in self.arguments.keys():
                            arg_name = f'--{str(arg)}' if len(str(arg))>1 else f'-{str(arg)}'
                            if type(self.arguments[arg]['default']) is list:
                                self.parser.add_argument(
                                    str(arg),
                                    choices = [str(variant) for variant in self.arguments[arg]['default']],
                                    help = self.arguments[arg]['description']
                                    )
                            else:
                                self.parser.add_argument(
                                    str(arg) if self.arguments[arg]['default'] is None else arg_name,
                                    default = str(self.arguments[arg]['default']), 
                                    help = self.arguments[arg]['description'],
                                    metavar =  str(arg) if self.arguments[arg]['default'] is None else 'value'
                                    )   
                    self.args = self.parser.parse_args(args) 
                    
            except Exception as errormsg:
                error('Can\'t build CLI from YAML', errormsg)
                warning_file(self.path)
                sys.exit(1)

            # Создание порядка запуска скриптов и обработка исключений
            if vars(self.args).get('items_launch_set',''):
                # Парс диапазона
                try:
                    self.items_launch_set = make_range(self.args.items_launch_set)
                except:
                    self.parser.print_usage()
                    print(f'Failed to resolve execution sequence "{self.args.items_launch_set}"')
                    print(items_table_parced)
                    sys.exit(1)
                # Проверка наличия скриптов в диапазоне
                else:
                    for item in self.items_launch_set:
                        if item not in self.scripts_dict:
                            self.parser.print_usage()
                            print(f'Execution sequence "{self.args.items_launch_set}" out of range\n')
                            print(items_table_parced)
                            sys.exit(1)
        else:
            print('\nPlease, check your YAML structure. Required structure:')
            print(help_yaml_structure)

    def BuildScript(self, script):
        if self.status == 'OK' and self.arguments != None:
            out = script
            for key in self.arguments.keys():
                out = out.replace(self.arguments[key]['replacer'], str(vars(self.args)[key]))
            return out
    
    def Execute(self, shell, script, __version__, args):
        if self.status == 'OK':
            if args.show_log:
                # создание заголовков логгера
                headerstr = get_main_header(__version__,self.name,get_local_time(),shell)
                headerstr += get_code_log(script)
                headerstr += get_log_header()
                print(headerstr, end='')
            try:
                subprocess.run(script, shell=True, executable=shell)
            except Exception as errormsg:
                error('Can\'t run script', errormsg)
                warning_file(shell)
                sys.exit(1)
            finally:
                if args.show_log:
                    endstr = get_log_end(get_local_time())
                    print(endstr, end='')
    
    def Execute_log(self, shell, script, __version__, args):
        if self.status == 'OK':
            used_encoding=sys.stdout.encoding
            # создание заголовков логгера
            headerstr = get_main_header(__version__,self.name,get_local_time(),shell)
            headerstr += get_code_log(script)
            headerstr += get_log_header()
            try:
                with open(args.log, 'ab') as logfile:
                    logfile.write(headerstr.encode(used_encoding))
                    # Показать заголовок логгера, если выключена опция
                    if args.show_log: 
                        print(headerstr, end='')
                    try:
                        # Запуск выполнения скрипта
                        proc = subprocess.Popen(
                            script, shell=True, executable=shell, 
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                            )
                    except Exception as errormsg:
                        error('Can\'t run script', errormsg)
                        warning_file(shell)
                        sys.exit(1)
                    else:
                        # Чтение stdout и логирование
                        while True:
                            char=proc.stdout.read(1)
                            sys.stdout.buffer.write(char)
                            logfile.write(char)
                            sys.stdout.flush()
                            if proc.poll() is not None and not char:
                                break
                    finally:
                        endstr = get_log_end(get_local_time())
                        # Показать заголовок логгера, если выключена опция
                        if args.show_log: 
                            print(endstr, end='')
                        logfile.write(endstr.encode(used_encoding))
                        try:
                            proc.terminate()
                        except UnboundLocalError:
                            pass
            
            except Exception as errormsg:
                error('Can\'t write to log file', errormsg)
                sys.exit(1)