from genericpath import exists
from types import NoneType
from jsonschema import validate
import argparse
import subprocess
from yaml import safe_load
import sys

from bones.funcs import warning_file, error, get_local_time, get_code_log, get_log_end, get_log_header, get_main_header
from bones.schemas import main_schema, variables_schema

class YamlScript:
    def __init__(self, path: str, name):
        self.yaml_schema = safe_load(main_schema)
        self.variable_schema = safe_load(variables_schema)
        self.name = name
        self.path = path
        self.author = ''
        self.info = ''
        self.tags = []
        self.install = ''
        self.shell = ''
        self.variables = {}
        self.script = '' 
        self.status = 'OK'
        
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
        
        # Валидация yaml
        if self.status == 'OK':
            try:
                validate(content, self.yaml_schema)
            except Exception as errormsg:
                error('YAML validation error', str(errormsg).partition('\n')[0])
                warning_file(self.path)
                self.status = 'ERROR'
            
            # Считывание данных
            self.author =  content.get('author', '')
            self.info = content.get('info','')
            if content['tags'] is not None:
                self.tags = [str(tag) for tag in content.get('tags',[])]
            self.install = content.get('install','')
            self.shell = content.get('shell','')
            self.script = content.get('script','')
            
            # Валидация переменных 
            if content['variables'] is not None:
                for key in content['variables'].keys():
                    try: 
                        validate(content['variables'][key], self.variable_schema)
                    except Exception as errormsg:
                        self.status = 'ERROR'
                        error('YAML \'variables\' block validation error', str(errormsg).partition('\n')[0])
                        warning_file(self.path)
                    else: 
                        self.variables = content.get('variables',{})
        
    def ParseArgs(self, args: list, scriptname: str):
        try:
            self.parser = argparse.ArgumentParser(
                formatter_class = argparse.RawDescriptionHelpFormatter,
                description = self.info, 
                prog = scriptname, 
                epilog='Shell:  {shell}\nAuthor: {author}\nTags:   {tags}'.format(
                    author=self.author,
                    tags=', '.join(self.tags),
                    shell=self.shell)
                )
            if self.status == 'OK':
                if self.variables != None:
                    for arg in self.variables.keys():
                        arg_name = f'--{str(arg)}' if len(str(arg))>1 else f'-{str(arg)}'
                        if type(self.variables[arg]['default']) is list:
                            self.parser.add_argument(
                                arg_name,
                                choices = [str(variant) for variant in self.variables[arg]['default']],
                                help = self.variables[arg]['info'],
                                required=True
                                )
                        else:
                            self.parser.add_argument(
                                str(arg) if self.variables[arg]['default'] is None else arg_name,
                                default = str(self.variables[arg]['default']), 
                                help = self.variables[arg]['info'],
                                metavar =  str(arg) if self.variables[arg]['default'] is None else 'value'
                                )
                self.args = self.parser.parse_args(args)
        except Exception as errormsg:
            error('Can\'t build CLI from YAML', errormsg)
            warning_file(self.path)
            sys.exit(1)

    def BuildScript(self):
        if self.status == 'OK' and self.variables != None:
            for key in self.variables.keys():
                self.script = self.script.replace(self.variables[key]['replacer'], str(vars(self.args)[key]))
    
    def Execute(self, shell, script, __version__, args):
        if self.status == 'OK':
            
            # создание заголовков логгера
            headerstr = get_main_header(__version__,self.name,get_local_time(),shell)
            headerstr += get_code_log(script)
            headerstr += get_log_header()

            if args.log is not None:
                used_encoding=sys.stdout.encoding
                try:
                    logfile = open(args.log, 'ab')
                except Exception as errormsg:
                    error('Can\'t write to log file', errormsg)
                    sys.exit(1)
                else:
                    logfile.write(headerstr.encode(used_encoding))
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
                        # Считывание stdout
                        # Без обработки ошибок, по крайней мере пока
                        # 
                        # tee = subprocess.Popen(["tee", "log.txt"], stdin=subprocess.PIPE)
                        # os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
                        # os.dup2(tee.stdin.fileno(), sys.stderr.fileno())
                        while True:
                            char=proc.stdout.read(1)
                            sys.stdout.buffer.write(char)
                            logfile.write(char)
                            sys.stdout.flush()
                            if proc.poll() is not None and not char:
                                break
                    finally:
                        endstr = get_log_end(get_local_time())
                        if args.show_log: 
                            print(endstr, end='')
                        logfile.write(endstr.encode(used_encoding))
                        logfile.close()
                        try:
                            proc.terminate()
                        except:
                            pass             
            else:
                if args.show_log:
                    print(headerstr, end='')
                try:
                    proc = subprocess.run(script, shell=True, executable=shell)
                except Exception as errormsg:
                    error('Can\'t run script', errormsg)
                    warning_file(shell)
                    sys.exit(1)
                finally:
                    if args.show_log:
                        endstr = get_log_end(get_local_time())
                        print(endstr, end='')