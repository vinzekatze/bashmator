from re import compile as re_compile

class YamlValidator:
    def mark_unknowns(self, known_list: list, all: list, source_name: str):
        for element in all:
            if element not in known_list:
                if self.verbose:
                    self.msg.yaml_warning(f'Unknown key at {source_name}', 
                                 f'The \'{self.msg.c(element, "_B")}\' key is unknown. It\'s contents will not affect anything.')
                self.no_warnings = False
    

    def call_yaml_error(self, error_name='', error_info=''):
        if error_name and error_info:
            self.status = False
        if self.verbose and error_name and error_info:
            self.msg.yaml_error(error_name, error_info)


    def check_value(self, value, types: list, can_be_empty: bool, error_name='', error_info='', last_check=True):
        out = last_check
        if can_be_empty and last_check:
            if value and type(value) not in types:
                out = False
                self.call_yaml_error(error_name, error_info)       
        elif last_check:
            if type(value) not in types:
                out = False
                self.call_yaml_error(error_name, error_info)
        return out

    def check_regex(self, last_check, value: str, regex, error_name='', error_info=''):
        out = last_check
        if last_check:
            if not regex.match(str(value)):
                out = False
                self.call_yaml_error(error_name, error_info)
        return out
    
    def validate_tags(self, last_check: bool):
        out = last_check
        content = self.content.get('tags', [])
        if last_check and content:
            for tag in content:
                if not self.check_value(tag, 
                                        [str, int], 
                                        False, 
                                        'Invalid \'tags\' values', 
                                        f'Tag \'{self.msg.c(tag, "_B")}\' is not a string or an integer.', 
                                        last_check):
                    out = False
        return out


    def __validate_argument_default__(self, last_check, argument: str, value, can_be_empty=True):
        out = last_check
        if last_check:
            out = self.check_value(value,
                                        [str, int],
                                        can_be_empty,
                                        f'Invalid \'default\' values of the \'{argument}\' argument',
                                        f'Value \'{self.msg.c(value, "_B")}\' is not a string or an integer.',
                                        last_check) and out
        return out


    def validate_argument_content(self, last_check, argument: str):
        out = last_check
        if last_check:
            content = self.content['arguments'][argument]
            default_status = self.check_value(content.get('default', None), 
                                              [str, int, list], 
                                              True, 
                                              f'Invalid argument \'{argument}\' key value', 
                                              f'Value of the \'{self.msg.c("default", "_B")}\' key must be a string, an integer or list.', 
                                              last_check)
            if type(content.get('default', None)) is list:
                for i, value in enumerate(content.get('default', [])):
                    can_be_empty = True if i == 0 else False
                    out = self.__validate_argument_default__(default_status, argument, value, can_be_empty) and out
            else:
                out = self.__validate_argument_default__(default_status, argument, content.get('default', None)) and out
                    
            out = self.check_value(content.get('replacer', None), 
                                               [str], 
                                               False, 
                                               f'Invalid argument \'{argument}\' key value', 
                                               f'The key \'{self.msg.c("replacer", "_B")}\' is required and must contain a string value.', 
                                               last_check) and out
            out = self.check_value(content.get('description', None),
                                                  [str],
                                                  True,
                                                  f'Invalid argument \'{argument}\' key value',
                                                  f'Value of the \'{self.msg.c("description", "_B")}\' key must be a string.', 
                                                  last_check) and out
            out = self.check_value(content.get('multiple', None),
                                               [bool],
                                               True,
                                               f'Invalid argument \'{argument}\' key value',
                                               f'Value of the \'{self.msg.c("multiple", "_B")}\' key can be \'true\' or \'false\'.',
                                               last_check) and out
            self.mark_unknowns(['default', 'replacer', 'description', 'multiple'], content.keys(), f'\'arguments\':\'{argument}\'')
        return out

    def validate_arguments(self, last_check: bool):
        out = last_check
        content = self.content.get('arguments', None)
        if last_check and content:
            regex = re_compile('^[A-Za-z][A-Za-z0-9_-]*$')
            for key in content.keys():
                out = self.check_regex(last_check, 
                                              key, 
                                              regex, 
                                              'Invalid argument name', 
                                              f'The argument name \'{self.msg.c(key, "_B")}\' contains invalid characters.')  and out
                type_check = self.check_value(self.content['arguments'].get(key, None),
                                              [dict],
                                              False,
                                              f'Invalid argument \'{key}\' structure',
                                              f'Arguments are described as dictionaries containing the keys \'replacer\', \'default\', \'description\' and other.',
                                              last_check)
                out = self.validate_argument_content(type_check, key) and out
        return out

    def validate_file_key(self, last_check: bool, key):
        out = last_check
        content = self.content.get(key, None)
        if last_check and content:
            out = self.check_value(content.get('path', None),
                                           [str],
                                           False,
                                           f'Invalid key value at \'{key}\'',
                                           f'The key \'{self.msg.c("path", "_B")}\' is required and must contain a string value.',
                                           last_check) and out
            out = self.check_value(content.get('replacer', None),
                                           [str],
                                           False,
                                           f'Invalid key value at \'{key}\'',
                                           f'The key \'{self.msg.c("replacer", "_B")}\' is required and must contain a string value.',
                                           last_check) and out
            out = self.check_value(content.get('description', None),
                                           [str],
                                           True,
                                           f'Invalid key value at \'{key}\'',
                                           f'Value of the \'{self.msg.c("description", "_B")}\' key must be a string.',
                                           last_check) and out
            self.mark_unknowns(['path', 'replacer', 'description'], content, f'\'{key}\'')
        return out


    def check_argument_multiple(self, last_check: bool, argument, source, mode_key):
        out = last_check
        if last_check and self.arguments_status:
            if not self.content['arguments'][argument].get('multiple', False):
                out = False
                self.call_yaml_error(f'Invalid \'mode\':\'{mode_key}\' key value at {source}', 
                                     f'The argument \'{argument}\' is not multiple.')
        return out


    def check_argument_exist(self, last_check: bool, argument, source: str, mode_key: str):
        out = last_check
        if last_check and self.arguments_status:
            arguments = self.content['arguments'].keys()
            if argument not in arguments and argument:
                out = False
                self.call_yaml_error(f'Invalid \'mode\':\'{mode_key}\' key value at {source}',
                                     f'The \'{argument}\' argument is not defined in the \'arguments\' key.')
        return out

    def validate_mode_key(self, last_check: bool, content, source: str):
        out = last_check
        if last_check and content and self.arguments_status:
            check_loop = self.check_value(content.get('loop', None),
                                          [str],
                                          True,
                                          f'Invalid \'mode\' key value at {source}',
                                          f'Value of the \'{self.msg.c("loop", "_B")}\' key must be a string.',
                                          last_check)
            check_loop_exist = self.check_argument_exist(check_loop, content.get('loop', None), source, 'loop')
            if content.get('loop', None):
                out = self.check_argument_multiple(check_loop_exist, content.get('loop', None), source, 'loop')
            else:
                out = check_loop_exist
            
            check_join = self.check_value(content.get('join', {}),
                                          [dict],
                                          False,
                                          f'Invalid \'mode\' key value at {source}',
                                          f'The \'{self.msg.c("join", "_B")}\' key must contain the names of the arguments as keys.',
                                          last_check)
            if check_join and type(content.get('join', {})) is dict:
                for argument in content.get('join', {}).keys():
                    exist_status = self.check_argument_exist(check_join, argument, source, 'join')
                    multiple_status = self.check_argument_multiple(exist_status, argument, source, 'join')
                    out = self.check_value(content['join'][argument],
                                           [str],
                                           True,
                                           f'Invalid \'mode\':\'join\':\'{argument}\' key value at {source}',
                                           'The value must be a string.',
                                           multiple_status) and out
            else:
                out = check_join and out

            check_format = self.check_value(content.get('format', {}),
                                           [dict],
                                           False,
                                           f'Invalid \'mode\' key value at {source}',
                                           f'The \'{self.msg.c("format", "_B")}\' key must contain the names of the arguments as keys.',
                                           last_check)
            if check_format and type(content.get('format', {})) is dict:
                for argument in content.get('format', {}).keys():
                    exist_status = self.check_argument_exist(check_format, argument, source, 'format')
                    type_status = self.check_value(content['format'][argument],
                                                   [str],
                                                   True,
                                                   f'Invalid \'mode\':\'format\':\'{argument}\' key value at {source}',
                                                   'The value must be a string.',
                                                   exist_status)
                    if type_status:
                        try:
                            formated_string = content['format'][argument]
                            _ = formated_string.format('TEST')
                        except Exception:
                            out = self.call_yaml_error(f'Invalid \'mode\':\'format\':\'{argument}\' key value at {source}',
                                                       f'Applying the \'.format()\' function to the \'{formated_string}\' line ended with an error. It is recommended to use placeholder ' + '\'{0}\'.') and out
            
            self.mark_unknowns(['loop', 'format', 'join'], content.keys(), f'\'mode\' at {source}')
        return out


    def validate_item_key(self, last_check: bool, key):
        out = last_check
        content = self.content.get(key, None)
        if last_check and content:
            out = self.check_value(content.get('script', None),
                                   [str],
                                   False,
                                   f'Invalid key value at \'{key}\'',
                                   f'The key \'{self.msg.c("script", "_B")}\' is required and must contain a string value.',
                                   last_check) and out
            out = self.check_value(content.get('description', None),
                                   [str],
                                   True,
                                   f'Invalid key value at \'{key}\'',
                                   f'Value of the \'{self.msg.c("description", "_B")}\' key must be a string.',
                                   last_check) and out
            out = self.check_value(content.get('shell', None),
                                   [str],
                                   self.main_shell,
                                   f'Invalid key value at \'{key}\'',
                                   f'The \'{self.msg.c("shell", "_B")}\' key must contain a string value and be present in each item if the main shell is not specified.',
                                   last_check) and out
            
            if content.get('mode', None) and not self.arguments_status:
                out = False
                self.call_yaml_error(f'Invalid key at \'{key}\'', f'It is not possible to use \'{self.msg.c("mode", "_B")}\' functions without arguments.')
            
            mode_check = self.check_value(content.get('mode', {}),
                                        [dict],
                                        False,
                                        f'Invalid \'mode\' structure at \'{key}\'',
                                        'The mode is specified as a dictionary containing \'loop\', \'join\' and \'format\' keys.',
                                        last_check)
            out = self.validate_mode_key(mode_check, content.get('mode', None), f'\'{key}\'') and out
            
            self.mark_unknowns(['script', 'description', 'shell', 'mode'], content.keys(), f'\'{key}\'')
        return out

    def validate(self):
        known_keys = ['author', 'description', 'install', 'shell', 'script', 'tags', 'arguments', 'mode']
        files_keys = []
        # Проверка ямла из файла
        file_status = self.check_value(self.content, 
                                       [dict], 
                                       False, 
                                       'Invalid Yaml structure', 
                                       'The file does not contain any keys.')
        if not file_status:
            all_keys = []
        else:
            all_keys = [key for key in self.content.keys()]
            
            # Проверка наличия главного script
            if self.content.get('script', None):
                self.main_script = True

            # Проверка наличия главного shell:
            if self.content.get('shell', None):
                self.main_shell = True

            # Проверка простых ключей
            for key in ['author', 'description', 'install']:
                _ = self.check_value(self.content.get(key, None), 
                                    [str], 
                                    True, 
                                    'Invalid general structure', 
                                    f'The value of the key \'{self.msg.c(key, "_B")}\' must be a string.', 
                                    file_status)
            
            # Проверка тегов
            tags_status = self.check_value(self.content.get('tags', []), 
                                        [list], 
                                        False, 
                                        'Invalid general structure', 
                                        f'{self.msg.c("Tags", "_B")} must be specified as a list.', 
                                        file_status)
            _ = self.validate_tags(tags_status)

            # Проверка аргументов
            arguments_status = self.check_value(self.content.get('arguments', {}), 
                                                [dict], 
                                                False, 
                                                'Invalid general structure', 
                                                f'The \'{self.msg.c("arguments", "_B")}\' key must contain the names of the arguments as keys.', 
                                                file_status)
            arguments_content_status = self.validate_arguments(arguments_status)
            if self.content.get('arguments', None) and arguments_content_status:
                self.arguments_status = True

            # Проверка итемов и файлов
            regex_item = re_compile('^item_[1-9][0-9]*$')
            regex_file = re_compile('^file_[1-9][0-9]*$')
            for key in all_keys:
                if self.check_regex(file_status, key, regex_file):
                    known_keys.append(key)
                    # Проверка файлов
                    file_key_status = self.check_value(self.content.get(key), 
                                                    [dict], 
                                                    False, 
                                                    f'Invalid \'{key}\' structure', 
                                                    f'The files are specified as a dictionary containing \'path\' and \'replacer\' keys.', 
                                                    file_status)
                    _ = self.validate_file_key(file_key_status, key)
                    files_keys.append(key)
                
                if self.check_regex(file_status, key, regex_item):
                    known_keys.append(key)
                    # Проверка итемов
                    item_key_status = self.check_value(self.content.get(key), 
                                                    [dict], 
                                                    False, 
                                                    f'Invalid \'{key}\' structure', 
                                                    f'Items are specified as a dictionary containing \'script\', \'shell\' and \'mode\' keys.',
                                                    file_status)
                    _ = self.validate_item_key(item_key_status, key)
                    self.items_status = True
            
            # Проверка главного mode
            if self.content.get('mode', None) and not self.arguments_status:
                self.call_yaml_error(f'Invalid key at general structure', f'It is not possible to use \'{self.msg.c("mode", "_B")}\' functions without arguments.')
            
            mode_check = self.check_value(self.content.get('mode', {}),
                                        [dict],
                                        False,
                                        'Invalid \'mode\' structure at general structure',
                                        'The mode is specified as a dictionary containing \'loop\', \'join\' and \'format\' keys.',
                                        file_status)
            _ = self.validate_mode_key(mode_check, self.content.get('mode', None), f'general structure')

            # Проверка script
            _ = self.check_value(self.content.get('script', None), 
                                [str], 
                                self.items_status, 
                                'Invalid general structure', 
                                f'The \'{self.msg.c("script", "_B")}\' key is required if there are no items and must contain a string value.', 
                                file_status)
            # Проверка shell
            _ = self.check_value(self.content.get('shell', None), 
                                [str], 
                                not self.main_script, 
                                'Invalid general structure', 
                                f'The \'{self.msg.c("shell", "_B")}\' key is required if the main script is set and must contain a string value.', 
                                file_status)

            # Проверка реплейсеров
            if self.status:
                # Сбор всех реплейсеров
                all_replacers = {}
                
                count = 0
                for key in self.content.get('arguments', {}).keys():
                    all_replacers.update({count: {'replacer': self.content['arguments'][key].get('replacer', ''),
                                              'name': f'argument \'{key}\''
                                              }})
                    count += 1
                for key in files_keys:
                    all_replacers.update({count: {'replacer': self.content[key].get('replacer', ''),
                                              'name': f'\'{key}\''
                                              }})
                    count += 1
                # Проверка реплейсеров на повторения
                for check in all_replacers.keys():
                    for check_in in all_replacers.keys():
                        if all_replacers[check]['replacer'] in all_replacers[check_in]['replacer'] and check != check_in:
                            self.call_yaml_error('Replacers are in conflict',
                                                 f'The replacer of {all_replacers[check]["name"]} is contained in the replacer of {all_replacers[check_in]["name"]}.')
                

            # Проверка наличия лишних аргументов
            if file_status:
                self.mark_unknowns(known_keys, self.content.keys(), 'general structure')

        
    def __init__(self, content, msg, verbose=True):
        self.msg = msg
        self.content = content
        self.verbose = verbose
        self.status = True
        self.no_warnings = True
        # маркеры
        self.main_shell = False
        self.main_script = False
        self.items_status = False
        self.arguments_status = False

        self.validate()