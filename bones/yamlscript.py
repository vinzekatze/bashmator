import argparse
import subprocess
import sys
import os.path
import copy

from io import TextIOWrapper
from yaml import safe_load
from time import time

from bones.msg import wrap_text
from bones.funcs import none_controll, make_range
from bones.funcs import get_main_header, get_local_time, get_code_log, get_alt_code_cog, get_log_header, get_log_end, get_code_print_header
from bones.validate import YamlValidator, re_compile

breaker_time = 1

class YamlScript:
    def __shell_collector__(self, item: int, shell: str):
        if shell in self.all_shells:
            self.all_shells[shell]['items'].append(item)
        else:
            if shell in self.known_shells.keys():
                shell_status = ''         
            else:
                shell_status = '[UNKNOWN]'
                self.status = 'WARNING'
            self.all_shells.update({shell: {'items': [item], 'status': shell_status}})


    def __mode_collector__(self, mode):
        out = copy.deepcopy(self.main_mode)
        out.update({'loop': mode.get('loop', self.main_mode['loop'])})
        out.update({'readfile': mode.get('readfile', self.main_mode['readfile'])})
        for arg in self.arguments.keys():
            join_val = mode.get('join',{}).get(arg, None)
            format_val = mode.get('format',{}).get(arg, None)
            replace_val = mode.get('replace',{}).get(arg, {})
            pformat_val = mode.get('pformat',{}).get(arg, None)
            out['join'][arg] = join_val if join_val else self.main_mode['join'][arg]
            out['format'][arg] = format_val if format_val else self.main_mode['format'][arg]
            out['replace'][arg] = replace_val if replace_val else self.main_mode['replace'][arg]
            out['pformat'][arg] = pformat_val if pformat_val else self.main_mode['pformat'][arg]
        return out
    
    def __content_parse__(self, content):
        # Включение only_fags_mode
        if self.arguments:
            multiple = 0
            for argument in self.arguments.keys():
                default_val = self.arguments[argument].get('default', None)
                if self.arguments[argument].get('multiple', False):
                    if type(default_val) is list and len(default_val) == 2:
                        pass
                    else:
                        multiple += 1 

            if multiple > 1:
                self.only_fags_mode = True

        # Main mode сборка
        mode = content.get('mode', {})
        self.main_mode.update({'loop': mode.get('loop', None),
                               'readfile': mode.get('readfile', []),
                               'join': {},
                               'format': {},
                               'replace': {},
                               'pformat': {}})
        for arg in self.arguments.keys():
            join_val = mode.get('join',{}).get(arg, None)
            format_val = mode.get('format',{}).get(arg, None)
            replace_val = mode.get('replace',{}).get(arg, {})
            pformat_val = mode.get('pformat',{}).get(arg, None)
            self.main_mode['join'][arg] = join_val if join_val is not None else ' '
            self.main_mode['format'][arg] = format_val if format_val else ''
            self.main_mode['replace'][arg] = replace_val if replace_val else {}
            self.main_mode['format'][arg] = format_val if format_val else ''
            self.main_mode['pformat'][arg] = pformat_val if pformat_val else ''

        # Формирование словаря доступных скриптов
        if content.get('script',''):
            self.scripts_dict.update({0: {'script': content['script'],
                                          'description':'main script (default)',
                                          'shell': self.main_shell,
                                          'mode': self.main_mode 
                                          }})
            self.__shell_collector__(0, self.main_shell)
            self.has_main_script = True
        for key in content.keys():
            if key.startswith("item_"):
                item_content = content.get(key,{})
                self.scripts_dict.update({int(key[5:]): {'script': item_content.get('script', ''),
                                                         'description': item_content.get('description', ''),
                                                         'shell': item_content.get('shell', self.main_shell),
                                                         'mode': self.__mode_collector__(item_content.get('mode', {}))
                                                         }})
                self.__shell_collector__(int(key[5:]), item_content.get('shell', self.main_shell))
                self.has_items = True

        # Формирования словаря доступных файлов
        for key in content.keys():
            if key.startswith("file_"):
                file_content = content.get(key,{})
                self.files_dict.update({int(key[5:]): {'path': file_content.get('path', ''),
                                                       'replacer': file_content.get('replacer', f'{self.default_replacer}{key}{self.default_replacer}'),
                                                       'description': file_content.get('description', '')}})
                self.has_files = True
        
        # Проверка файлов
        for key in self.files_dict.keys():
            full_path = os.path.join(self.library_files_path, os.path.normcase(self.files_dict[key].get('path')))
            if os.path.exists(full_path): 
                status = 'FOUND'
            else:
                status = 'NOT FOUND'
                self.status = 'WARNING'
            self.files_dict[key].update({'full_path': full_path, 'status': status})

    
    def __init__(self, path: str, 
                 name: str, 
                 library_files_path: str, 
                 bshm_version: str, 
                 known_shells: dict, 
                 msg, 
                 verbose_validation=True, 
                 auto_scan=False, 
                 status_from_lib='',
                 library_name=''):
        self.msg = msg
        self.bshm_version = f'bashmator {bshm_version}'
        self.verbose_validation = verbose_validation
        self.name = name
        self.path = path
        self.library_files_path = library_files_path
        self.library_name = library_name
        self.known_shells = known_shells
        # Информация из yaml
        self.author = ''
        self.description = ''
        self.tags = []
        self.install = ''
        self.main_shell = ''
        self.main_mode = {}
        self.arguments = {}
        self.scripts_dict = {}
        self.files_dict = {}
        self.all_shells = {}
        self.default_replacer = '#'
        self.args_regex = {}
        # Индикаторы
        self.status = '' if status_from_lib == 'ERROR' else status_from_lib
        self.flow_status = True
        self.has_items = False
        self.has_main_script = False
        self.has_files = False
        self.only_fags_mode = False
        self.interrupt_time = time()
        self.interrupt_count = 0
        # Параметры аргументов
        self.items_launch_set = [0]
 

        # Загрузка yaml файла
        try:
            with open(path, mode='r', encoding='utf-8') as f:
                try: content = safe_load(f)
                except Exception as errormsg:
                    self.status = 'ERROR'
                    self.msg.error('Yaml read error', errormsg)
        except Exception as errormsg:
            self.msg.error('Can\'t load yaml file', errormsg)
            self.status = 'ERROR'
        else:
        # Валидация структуры yaml
            if not auto_scan:
                validation_trigger = self.status != 'ERROR'
            else:
                validation_trigger = (self.status == 'WARNING' or not self.status) and self.status != 'ERROR'

            if validation_trigger: 
                validation = YamlValidator(content=content, 
                                           msg=self.msg, 
                                           verbose=self.verbose_validation, 
                                           default_replacer=self.default_replacer)
                if not validation.status:
                    self.status = 'ERROR'
                    if not self.verbose_validation: 
                        self.msg.yaml_error(f'Script \'{self.name}\' is broken', f'{self.path}')
                elif not validation.no_warnings:
                    self.status = 'WARNING'
                    if not self.verbose_validation: 
                        self.msg.yaml_warning(f'Non-critical errors in the \'{self.name}\' script', f'{self.path}')
                else:
                    self.status = 'OK'
            # Считывание данных
            if self.status != 'ERROR':
                self.author =  none_controll(content.get('author', '')) 
                self.description = none_controll(content.get('description',''))
                self.install = none_controll(content.get('install',''))
                self.main_shell = none_controll(content.get('shell',''))
                if content.get('tags',[]):
                    self.tags = [str(tag) for tag in content.get('tags',[])]
                if type(content.get('arguments', None)) is dict:
                    self.arguments = content.get('arguments', {})
                    # добавление дефолтных реплейсеры
                    for i in self.arguments.keys():
                        if not self.arguments[i].get('replacer', None):
                            self.arguments[i]['replacer'] = f'{self.default_replacer}{i}{self.default_replacer}'
                self.__content_parse__(content)
                
                
    def __epilog_build__(self):
        epilog = ''
        size = 9
        delimiter = '\n'+' '*size
        script_info = []
        yellow_words = ['[UNKNOWN]']
        shellname_len = 0

        if self.has_items or self.has_files:
            epilog += self.msg.gen_color_style_line() + '\n'

        # Создание таблицы с items
        if self.has_items:
            items_table = [['#', 'description']]
            for key in sorted(self.scripts_dict.keys()):
                items_table.append([key, self.scripts_dict[key].get('description','')])
            self.items_table_parced = f'{self.msg.c("items list", "_B")}:\n{self.msg.make_table(items_table)}'
            epilog += self.items_table_parced + '\n\n'
    
        # Создание таблицы с файлами
        if self.has_files:
            files_table = [['path', 'status', 'description']]
            for key in sorted(self.files_dict.keys()):
                files_table.append([self.files_dict[key].get('path',''),
                self.files_dict[key].get('status',''),
                self.files_dict[key].get('description','')])
            self.files_table_parced = f'{self.msg.c("used files", "_B")}:\n{self.msg.make_table(files_table)}'
            epilog += self.files_table_parced + '\n\n'

        # Создание строки эпилога с доп инфой
        if len(self.all_shells.keys()) == 1:
            script_info.append(['Shell:', self.main_shell, self.all_shells[self.main_shell]['status']])
        else:
            for i, shell_name in enumerate(self.all_shells.keys()):
                if i == 0: header = 'Shells:'
                else: header = ''
                script_info.append([header, 
                                    '{}:{}'.format(shell_name, ','.join(map(str, self.all_shells[shell_name]['items']))),
                                    self.all_shells[shell_name]['status']])       
            shellname_len = max([len(i[1]) for i in script_info])
        
        if self.author: script_info.append(['Author:', self.author, ''])
        if self.tags: script_info.append(['Tags:', ', '.join(self.tags), ''])


        # Создание строки эпилога с доп инфой
        for line in script_info:
            text_line = ''
            if line[2] in yellow_words:
                text_line += self.msg.c(self.msg.c(line[0],'_', size), '_D')
                text_line += self.msg.c('{} {}'.format(self.msg.c(line[1],'_',shellname_len), line[2]),'Y')
            else:
                text_line += self.msg.c('{}{} {}'.format(self.msg.c(line[0],'_', size),
                                        line[1] if not line[2] else self.msg.c(line[1],'_',shellname_len),
                                        line[2]),'_D')
            epilog += wrap_text(text_line, delimiter) + '\n'
        return epilog
    
    def __parse_items__(self):
        if vars(self.parsed_args).get('items_launch_set',''):
            # Парс диапазона
            try:
                self.items_launch_set = make_range(self.parsed_args.items_launch_set)
            except ValueError:             
                self.parser.print_usage()
                self.msg.myprint(f'{self.name}: error: argument --item: failed to resolve execution sequence \'{self.parsed_args.items_launch_set}\'')
                self.msg.myprint(self.items_table_parced)
                self.msg.exit_code = 2
                sys.exit(self.msg.exit_code)
            # Проверка наличия скриптов в диапазоне
            else:
                for item in self.items_launch_set:
                    if item not in self.scripts_dict:
                        self.parser.print_usage()
                        self.msg.myprint(f'{self.name}: error: argument --item: execution sequence \'{self.parsed_args.items_launch_set}\' out of range\n')
                        self.msg.myprint(self.items_table_parced)
                        self.msg.exit_code = 2
                        sys.exit(self.msg.exit_code)

    def __gen_args_regular_mode__(self, arg, options: argparse.ArgumentParser, required: argparse.ArgumentParser):
        arg_option_name = f'--{str(arg)}' if len(str(arg))>1 else f'-{str(arg)}'
        arg_full_name = arg_option_name if self.only_fags_mode else str(arg)
        arg_defaults = self.arguments[arg].get('default', None)
        help_text = self.arguments[arg].get('description', '') if self.arguments[arg].get('description', '') else ''
        multiple = self.arguments[arg].get('multiple', False)
        arg_metavar = self.arguments[arg].get('metavar', 'VAL')

        if type(arg_defaults) is list and arg_defaults:
            choice_list = [variant for variant in self.arguments[arg]['default']]
            def_val = '' if not choice_list[0] else str(choice_list[0])
            if len(arg_defaults) == 1:
                options.add_argument(arg_option_name,
                                     dest=str(arg),
                                     help=help_text + f' (default: \'{def_val}\')' if def_val else help_text,
                                     metavar=arg_metavar,
                                     required=False,
                                     default=[def_val],
                                     nargs='+' if multiple else 1
                                     )
            elif len(arg_defaults) == 2 and not multiple:
                options.add_argument(arg_option_name,
                                     dest=str(arg),
                                     help=help_text,
                                     required=False,
                                     default=[def_val],
                                     action='store_const',
                                     const=[] if not choice_list[1] else [str(choice_list[1])],
                                     )
            elif len(arg_defaults) == 2 and multiple:
                options.add_argument(arg_option_name,
                                     dest=str(arg),
                                     help=help_text + ' (multiple)',
                                     required=False,
                                     default=[] if not choice_list[0] else [str(choice_list[0])],
                                     action='append_const',
                                     const=None if not choice_list[1] else str(choice_list[1]),
                                     )
            elif choice_list[0]:
                options.add_argument(arg_option_name,
                                     dest=str(arg),
                                     help=help_text + f' (default: \'{def_val}\')',
                                     metavar=None if arg_metavar == 'VAL' else arg_metavar,
                                     required=False,
                                     default=[def_val],
                                     choices=[str(x) for x in choice_list],
                                     nargs='+' if multiple else 1
                                     )
            elif not choice_list[0]:
                required.add_argument(arg_full_name,
                                     help=help_text,
                                     metavar=None if arg_metavar == 'VAL' else arg_metavar,
                                     choices=[str(x) for x in choice_list[1:]],
                                     nargs='+' if multiple else 1
                                     )
        elif not arg_defaults:
            required.add_argument(arg_full_name,
                                 help=help_text,
                                 nargs='+' if multiple else 1
                                 )
        else:
            options.add_argument(arg_option_name,
                                 dest=str(arg),
                                 help=help_text  + f' (default: \'{str(arg_defaults)}\')',
                                 required=False,
                                 default=[str(arg_defaults)],
                                 metavar=arg_metavar,
                                 nargs='+' if multiple else 1
                                 )
            

    
    def __gen_args_multiple_mode__(self, arg, options: argparse.ArgumentParser, required: argparse.ArgumentParser):
        arg_option_name = f'--{str(arg)}' if len(str(arg))>1 else f'-{str(arg)}'
        arg_defaults = self.arguments[arg].get('default', None)
        help_text = self.arguments[arg].get('description', '') if self.arguments[arg].get('description', '') else ''
        multiple = self.arguments[arg].get('multiple', False)
        arg_metavar = self.arguments[arg].get('metavar', 'VAL')

        if type(arg_defaults) is list and arg_defaults:
            choice_list = [variant for variant in self.arguments[arg]['default']]
            def_val = '' if not choice_list[0] else str(choice_list[0])
            if len(arg_defaults) == 1:
                options.add_argument(arg_option_name,
                                     dest=str(arg),
                                     help=help_text + f' (default: \'{def_val}\')' if def_val else help_text,
                                     metavar=arg_metavar,
                                     required=False,
                                     default=[def_val],
                                     nargs='+' if multiple else 1
                                     )
            elif len(arg_defaults) == 2 and not multiple:
                options.add_argument(arg_option_name,
                                     dest=str(arg),
                                     help=help_text,
                                     required=False,
                                     default=[def_val],
                                     action='store_const',
                                     const=[] if not choice_list[1] else [str(choice_list[1])],
                                     )
            elif len(arg_defaults) == 2 and multiple:
                options.add_argument(arg_option_name,
                                     dest=str(arg),
                                     help=help_text  + ' (multiple)',
                                     required=False,
                                     default=[] if not choice_list[0] else [str(choice_list[0])],
                                     action='append_const',
                                     const=None if not choice_list[1] else str(choice_list[1]),
                                     )
            elif choice_list[0]:
                options.add_argument(arg_option_name,
                                     dest=str(arg),
                                     help=help_text + f' (default: \'{def_val}\')',
                                     metavar=None if arg_metavar == 'VAL' else arg_metavar,
                                     required=False,
                                     default=[def_val],
                                     choices=[str(x) for x in choice_list],
                                     nargs='+' if multiple else 1
                                     )
            elif not choice_list[0]:
                required.add_argument(arg_option_name,
                                      dest=str(arg),
                                      help=help_text,
                                      metavar=None if arg_metavar == 'VAL' else arg_metavar,
                                      required=True,
                                      choices=[str(x) for x in choice_list[1:]],
                                      nargs='+' if multiple else 1
                                      )
        elif not arg_defaults:
            required.add_argument(arg_option_name,
                                  dest=str(arg),
                                  help=help_text,
                                  required=True,
                                  metavar=arg_metavar,
                                  nargs='+' if multiple else 1
                                  )
        else:
            options.add_argument(arg_option_name,
                                 dest=str(arg),
                                 help=help_text  + f' (default: \'{str(arg_defaults)}\')',
                                 required=False,
                                 default=[str(arg_defaults)],
                                 metavar=arg_metavar,
                                 nargs='+' if multiple else 1
                                 )

    
    def parse_args(self, script_args: list, scriptname: str):
        if self.status != 'ERROR':
            try:
                # Создание парсера аргументов для скрипта
                self.parser = argparse.ArgumentParser(
                    formatter_class = argparse.RawDescriptionHelpFormatter,
                    description = self.msg.frame_text(self.description), 
                    prog = scriptname,
                    epilog = self.__epilog_build__(), # построение эпилога
                    add_help=False)

                group_names = ["required", "optional"] if self.only_fags_mode else ["positional arguments", "options"] 
                script_arguments_group = self.parser.add_argument_group(f'{self.msg.c(group_names[0],"_B")}')
                script_options_group = self.parser.add_argument_group(f'{self.msg.c(group_names[1],"_B")}')
                
                item_location = script_arguments_group if self.only_fags_mode and not self.has_main_script else script_options_group

                # Добавление аргумента item
                if self.has_items:
                    itemhelp_req_marker = f'{self.msg.c("[REQUIRED] ","R")}' if not self.has_main_script and not self.only_fags_mode else ''
                    item_location.add_argument('--item', 
                        default = '0', 
                        metavar = 'NUM',
                        dest = 'items_launch_set', 
                        help = f'{itemhelp_req_marker}item index to execute (can be a sequence, ex: \'1,2,4-6\')',
                        required = not self.has_main_script)

                #  Добавление аргументов скрипта
                if self.arguments:
                    for arg in self.arguments.keys():
                        if self.only_fags_mode:
                            self.__gen_args_multiple_mode__(arg, script_options_group, script_arguments_group)
                        else:
                            self.__gen_args_regular_mode__(arg, script_options_group, script_arguments_group)

                script_options_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
                self.parsed_args = self.parser.parse_args(script_args) 
                self.__parse_items__()

            except Exception as errormsg:
                self.msg.error('Can\'t build CLI from YAML', errormsg)
                self.msg.warning_file(self.path)
                sys.exit(1)
        else:
            self.msg.warning_file(self.path)

    def __build_script__(self, script: str, arg_values: dict):
        if self.status != 'ERROR' and self.arguments != None:
            out = script
            for key in self.arguments.keys():
                out = out.replace(self.arguments[key]['replacer'], arg_values[key])
            for key in self.files_dict.keys():
                out = out.replace(self.files_dict[key]['replacer'], self.files_dict[key]['full_path'])
            return out
    
    def __build_log_header__(self, script: str, shell: str, item: int, new_log):
        if new_log:
            headerstr = get_main_header(self.bshm_version, self.name, get_local_time(), shell, item)
            headerstr += get_code_log(script)
        else:
            headerstr = get_alt_code_cog(script, get_local_time())
        headerstr += get_log_header()
        return headerstr

    def execute(self, show_log: bool, popen_cmd: list,  item: int, new_log=True, last_log=True):
        if show_log:
            headerstr = self.__build_log_header__(script=popen_cmd[-1], shell=' '.join(popen_cmd[:-1]), item=item, new_log=new_log)
            print(headerstr, end='')
        try:
            subprocess.run(popen_cmd)
        except Exception as errormsg:
            self.msg.error('Can\'t run script', errormsg)
            self.msg.warning_file(' '.join(popen_cmd[:-1]))
            sys.exit(1)
        except KeyboardInterrupt:
            if time() - self.interrupt_time < breaker_time:
                self.interrupt_count += 1
            else:
                self.interrupt_count = 0
                self.interrupt_time = time()
            if self.interrupt_count > 2:
                raise
        finally: 
            if show_log:
                endstr = get_log_end(get_local_time()) if last_log or self.interrupt_count > 2 else '\n'
                print(endstr, end='')
    
    def execute_and_log(self, logging: str, show_log: bool, popen_cmd: list, shell_encoding: str,  item: int, new_log=True, last_log=True):
        headerstr = self.__build_log_header__(script=popen_cmd[-1], shell=' '.join(popen_cmd[:-1]), item=item, new_log=new_log)
        try:
            with open(logging, 'a', encoding='utf-8', buffering=1) as logfile:
                # Запись и отображение первого заголовка логера
                logfile.write(headerstr)
                if show_log: print(headerstr, end='')
                try:
                    # Старт субпроцесса
                    with subprocess.Popen(popen_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
                        reader = TextIOWrapper(proc.stdout, encoding=shell_encoding, newline='', line_buffering=False)
                        while True:
                            char=reader.read(1)
                            if char:
                                #encoded_char = str(char, shell_encoding)
                                _ = sys.stdout.write(char)    #(encoded_char)
                                _ = logfile.write(char)       #(encoded_char)
                                sys.stdout.flush()
                            if proc.poll() is not None and not char: break
                except Exception as errormsg:
                    self.msg.error('Can\'t run script', errormsg)
                    self.msg.warning_file(' '.join(popen_cmd[:-1]))
                    sys.exit(1)
                except KeyboardInterrupt:
                    if time() - self.interrupt_time < breaker_time:
                        self.interrupt_count += 1
                    else:
                        self.interrupt_count = 0
                        self.interrupt_time = time()
                    if self.interrupt_count > 2:
                        raise
                finally:
                    # Запись и отображение последнего заголовка логера
                    endstr = get_log_end(get_local_time()) if last_log or self.interrupt_count > 2 else '\n'
                    logfile.write(endstr)
                    if show_log: print(endstr, end='')
        except Exception as errormsg:
            self.msg.error('Can\'t write to log file', errormsg)
            sys.exit(1)

    # форматирует множественные аргументы
    def __format_multiargs__(self, values: list, format_string: str, join_delimiter: str, pformat_string: str):
        preout = []
        # обработка каждого значения
        if format_string:
            preout = [format_string.format(str(value)) if value else '' for value in values]
        else:
            preout = [str(value) if value else '' for value in values]
        preout2 = join_delimiter.join(preout)
        # обработка финальной строки
        if pformat_string:
            out = pformat_string.format(preout2) if preout2 else ''
        else:
            out = preout2
        return out

    # Возвращает значения аргументов
    def __get_arg_values__(self, arg: str, script_number: int):
        out = []
        preout = []
        # если идет чтение из файла
        if arg in self.scripts_dict[script_number]['mode']['readfile']:
            for file in vars(self.parsed_args)[arg]:
                if file:
                    try:
                        with open(file, 'r') as file:
                            lines_from_file = file.read().splitlines()
                        preout.extend(lines_from_file)
                    except Exception as errormsg:
                        self.msg.myprint('{}: error: argument {}: {}'.format(self.name, f'\'{arg}\'', errormsg))
                        self.msg.exit_code = 1
                        self.flow_status = False
        else:
            preout = vars(self.parsed_args)[arg]

        # если есть мод replace
        if arg in self.scripts_dict[script_number]['mode']['replace'].keys():
            for arg_value in preout:
                replaced = self.scripts_dict[script_number]['mode']['replace'][arg].get(arg_value, arg_value)
                out.extend(replaced) if type(replaced) is list else out.append(replaced)
        else:
            out = preout
        # валидация значений с помощью regex
        if self.args_regex.get(arg, None):
            for val in out:
                if val and not self.args_regex[arg].fullmatch(val):
                    self.msg.myprint('{}: error: argument {}: {}'.format(self.name, f'\'{arg}\'', f'invalid value \'{val}\''))
                    self.msg.exit_code = 1
                    self.flow_status = False   
        return out


    def script_launch(self, logging: str, show_log: bool, script_name: str, script_args: list, code_print=False):
        self.parse_args(script_args, script_name)
        if self.status != 'ERROR':
            # компил regex для аргументов
            for arg in self.arguments.keys():
                regex_str = self.arguments[arg].get('regex', None)
                self.args_regex[arg] = re_compile(regex_str) if regex_str else None   
            # Запуск скриптов
            for script_number in self.items_launch_set:    
                if self.scripts_dict[script_number]['shell'] == 'default' or not self.scripts_dict[script_number]['shell']:
                    self.msg.error(f'Can\'t run script ({script_number})', 'Shell is not defined.')
                    self.flow_status = False
                elif self.scripts_dict[script_number]['shell'] in self.known_shells.keys(): 
                    path = self.known_shells[self.scripts_dict[script_number]['shell']]['path']
                    popen_args = self.known_shells[self.scripts_dict[script_number]['shell']]['popen_args']
                    encoding = self.known_shells[self.scripts_dict[script_number]['shell']]['encoding']
                else:
                    path = self.scripts_dict[script_number]['shell']
                    popen_args = self.known_shells['default']['popen_args']
                    encoding = self.known_shells['default']['encoding']
                if code_print:
                    print(get_code_print_header(path, script_number)) 

                # loop режим
                if self.scripts_dict[script_number]['mode']['loop']:
                    loop_arg = self.scripts_dict[script_number]['mode']['loop']
                    arg_prevalues = self.__get_arg_values__(loop_arg, script_number)
                    loop_vars_count = len(arg_prevalues) - 1
                    
                    for i, loop_val in enumerate(arg_prevalues):
                        arg_values = {}
                        for key in self.arguments.keys():
                            arg_values[key] = self.__format_multiargs__([loop_val] if key == loop_arg else self.__get_arg_values__(key, script_number),
                                                                        self.scripts_dict[script_number]['mode']['format'][key],
                                                                        self.scripts_dict[script_number]['mode']['join'][key],
                                                                        self.scripts_dict[script_number]['mode']['pformat'][key])
                        
                        builded_script = self.__build_script__(self.scripts_dict[script_number]['script'], arg_values)
                        popen_cmd = [path] + popen_args + [builded_script]
                        #print(popen_cmd)
                        if code_print and self.flow_status:
                            print(builded_script)
                        elif logging and self.flow_status:
                            self.execute_and_log(logging=logging,
                                                show_log=show_log,
                                                popen_cmd=popen_cmd,
                                                shell_encoding=encoding,
                                                item=script_number,
                                                new_log=True if i == 0 else False,
                                                last_log=True if i == loop_vars_count else False)
                        elif self.flow_status:
                            self.execute(show_log=show_log,
                                        popen_cmd=popen_cmd,
                                        item=script_number,
                                        new_log=True if i == 0 else False,
                                        last_log=True if i == loop_vars_count else False)

                # обычный режим 
                else:
                    arg_values = {}
                    for key in self.arguments.keys():
                        arg_values[key] = self.__format_multiargs__(self.__get_arg_values__(key, script_number),
                                                                    self.scripts_dict[script_number]['mode']['format'][key],
                                                                    self.scripts_dict[script_number]['mode']['join'][key],
                                                                    self.scripts_dict[script_number]['mode']['pformat'][key])
                    
                    builded_script = self.__build_script__(self.scripts_dict[script_number]['script'], arg_values)
                    popen_cmd = [path] + popen_args + [builded_script]
                    if code_print and self.flow_status:
                        print(builded_script)
                    elif logging and self.flow_status:
                        self.execute_and_log(logging=logging,
                                            show_log=show_log,
                                            popen_cmd=popen_cmd,
                                            shell_encoding=encoding,
                                            item=script_number)
                    elif self.flow_status:
                        self.execute(show_log=show_log,
                                    popen_cmd=popen_cmd,
                                    item=script_number)
                
                # да тут все верно, просто нужен перенос строки, не пугайся пжлст
                if code_print:
                    print()