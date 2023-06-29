import os.path
import json
from ast import literal_eval
from pathlib import Path

from bones.library import check_library_folder
from bones.msg import Msg

default_config={
    "settings": {
        "auto-scan": True,
        "color": True,
        "used_library": "default"
    },
    "libraries": {
        "default": {
            "path": ""
        }
    },
    "shells": {
        "default":{
            "path": "",
            "popen_args": ['-c'],
            "encoding": "utf-8"
        }
    }
}

class Configuration:
    def __write_json__(self):
        try:
            with open(self.config_path, mode='w', encoding='utf-8') as json_file:
                json.dump(self.config, json_file, sort_keys=True)
        except OSError as errormsg:
            self.msg.error(f'Error writing \'{self.config_path}\'', errormsg)
            exit(1)
    
    def __read_json__(self):
        try:
            with open(self.config_path, mode='r', encoding='utf-8') as json_file:
                self.config = json.load(json_file)
        except json.JSONDecodeError:
            self.config = default_config
            self.__changed__ = True
            self.msg.warning(f'Error reading \'{self.config_name}\'', 'The default settings have been restored.')
        except OSError as errormsg:
            self.msg.error(f'Error reading \'{self.config_path}\'', errormsg)
            exit(1)
    
    # добавление недостающих ключей
    def __fix_dict_add__(self, target_dict:dict, default_dict:dict):
        for key in list(default_dict.keys()):
            if key not in target_dict: 
                target_dict[key] = default_dict[key]
                self.__changed__ = True
    
    # удаление лишних ключей
    def __fix_dict_del__(self, target_dict:dict, default_dict:dict):    
        for key in list(target_dict.keys()):
            if key not in default_dict:
                del target_dict[key]
                self.__changed__ = True
    
    # проверка типов значений ключей
    def __fix_dict_values__(self, target_dict:dict, default_dict:dict, default_key=None):
        for key in list(target_dict.keys()):
            sample = default_dict[key] if not default_key else default_dict[default_key]
            if type(target_dict[key]) is not type(sample):
                target_dict[key] = sample
                self.__changed__ = True

    def fix_config(self):
        # Фикс общей структуры и settings
        if type(self.config) is not type(default_config): 
            self.config = default_config
            self.__changed__ = True
        else:
            self.__fix_dict_add__(self.config, default_config)
            self.__fix_dict_del__(self.config, default_config)
            self.__fix_dict_values__(self.config, default_config)
            self.__fix_dict_add__(self.config['settings'], default_config['settings'])
            self.__fix_dict_del__(self.config['settings'], default_config['settings'])
            self.__fix_dict_values__(self.config['settings'], default_config['settings'])
            # Фикс libraries
            self.__fix_dict_add__(self.config['libraries'], default_config['libraries'])
            self.__fix_dict_values__(self.config['libraries'], default_config['libraries'],'default')
            for key in list(self.config['libraries']):
                self.__fix_dict_add__(self.config['libraries'][key], default_config['libraries']['default'])
                self.__fix_dict_del__(self.config['libraries'][key], default_config['libraries']['default'])
                self.__fix_dict_values__(self.config['libraries'][key], default_config['libraries']['default'])
            # Фикс shells
            self.__fix_dict_add__(self.config['shells'], default_config['shells'])
            self.__fix_dict_values__(self.config['shells'], default_config['shells'],'default')
            for key in list(self.config['shells']):
                self.__fix_dict_add__(self.config['shells'][key], default_config['shells']['default'])
                self.__fix_dict_del__(self.config['shells'][key], default_config['shells']['default'])
                self.__fix_dict_values__(self.config['shells'][key], default_config['shells']['default'])
        # Запись исправлений, если были
        if self.__changed__:
            self.msg.warning(f'Invalid config file', f'The structure of the {self.config_name} has been restored.')

    def __check_value__(self, target_dict: dict, default_dict: dict, key: str):
        if type(target_dict[key]) is not type(default_dict[key]):
            raise TypeError
        else:
            return target_dict[key]

    def __select_default_library__(self):
        self.config['settings']['used_library'] = default_config['settings']['used_library']
        self.used_library = 'default'

    def __get_full_library_path__(self, library_name: str):
        library_path_data = self.config['libraries'][library_name]['path']
        library_path = self.default_library_path if library_name == 'default' and not library_path_data else library_path_data
        return library_path

    def __check_libraries_paths__(self):
        self.libraries_status = {}
        for library_name in self.library_list:
            self.libraries_status[library_name] = check_library_folder(self.__get_full_library_path__(library_name), self.msg)
        self.used_library_status = self.libraries_status[self.used_library]

    def __get_config__(self):
        # Получение основных настроек
        self.color = self.__check_value__(self.config['settings'], default_config['settings'], 'color')
        self.msg.change_color_set(self.color)
        self.auto_scan = self.__check_value__(self.config['settings'], default_config['settings'], 'auto-scan')
        # Получение информации об известных библиотеках
        self.library_list = list(self.__check_value__(self.config, default_config, 'libraries').keys())
        self.user_library_list = list(self.library_list) # список библиотек без дефолтной
        self.user_library_list.remove('default')
        # Проверка, известна ли библиотека
        used_library = self.__check_value__(self.config['settings'], default_config['settings'], 'used_library')
        if used_library not in self.library_list:
            self.__select_default_library__()
            self.__changed__ = True
            self.msg.error(f'Unknown library \'{used_library}\'', 'Default library has been selected.')
        else:
            self.used_library = used_library
        # Проверка наличия пути до библиотеки
        library_path = self.__check_value__(self.config['libraries'][self.used_library], default_config['libraries']['default'], 'path')
        if self.used_library == 'default':
            self.used_library_path = self.default_library_path
        elif not library_path:
            self.__select_default_library__()
            self.__changed__ = True
            self.used_library_path = self.default_library_path
            self.msg.error(f'Path not set for library \'{used_library}\'', 'Default library has been selected.')
        else:
            self.used_library_path = library_path
        self.__check_libraries_paths__()
        # Получение информации об известных оболочках
        self.shell_dict = self.__check_value__(self.config, default_config, 'shells')
        self.shell_list = list(self.shell_dict.keys())
        # Проверка содержимого настроек оболочек
        for shell in self.shell_list:
            for option in default_config['shells']['default'].keys():
                _ = self.__check_value__(self.config['shells'][shell], default_config['shells']['default'], option)
        self.user_shell_list = list(self.shell_list) # список оболочек без дефолтной
        self.user_shell_list.remove('default')


    def get_config(self):
        try:
            self.__get_config__()    
        except (AttributeError, TypeError, LookupError):
            self.fix_config()
            self.__get_config__()

    def __get_lib_db_path__(self, lib_name):
        path = os.path.join(self.lib_db_path, f'{lib_name}.json')
        return path

    def __init__(self, config_dir:str, default_library_path:str, config_name='settings.json', lib_db_path='libraries', color=False):
        self.msg = Msg(color)
        self.color = color
        self.config_dir = config_dir
        self.config_name = config_name
        self.config_path = os.path.join(self.config_dir, self.config_name)
        self.lib_db_path = os.path.join(self.config_dir, lib_db_path)
        self.default_library_path = default_library_path
        self.__changed__ = False
        self.config = {}
        
        # Создает папку .config/bashmator и дефолтный конфиг, если их нет
        if not os.path.exists(self.config_path):
            try:
                Path(self.config_dir).mkdir(parents=True, exist_ok=True)
                self.config = default_config
                self.__write_json__()
                self.msg.message(f'Configuration file \'{self.config_name}\' was created.')
            except Exception as errormsg:
                self.msg.error(f'Can\'t create \'{self.config_dir}\'', errormsg)
                exit(1)
        elif self.__changed__:
            self.__write_json__()
        # чтение конфига
        self.__read_json__()
        self.get_config()
        self.used_lib_db_path = self.__get_lib_db_path__(self.used_library)

        # Создает папку .config/bashmator/libraries, если ее нет
        if not os.path.exists(self.lib_db_path):
            try:
                Path(self.lib_db_path).mkdir(parents=True, exist_ok=True)
            except Exception as errormsg:
                self.msg.error(f'Can\'t create \'{self.lib_db_path}\'', errormsg)
                exit(1)


    def set_settings_bool(self, option:str, value:str):
        bools = {"true": True, "false": False}
        self.config['settings'][option] = bools[value]
        self.msg.message(f'The \'{option}\' is set to \'{bools[value]}\'')
        self.__changed__ = True
    

    def __presence_in_list_checks__(self, must_be_in_list: bool, name_in_message: str, name: str, names_list: list):
        out = True
        forbiden_names = ['default', 'ALL']
        if must_be_in_list:
            if name not in names_list:
                self.msg.error(f'{name_in_message} name error', f'A {name_in_message.lower()} named \'{name}\' not found.')
                out = False
            if name == 'default':
                self.msg.error(f'{name_in_message} name error', f'The default {name_in_message.lower()} cannot be modified.')
                out = False
        else:
            if name in forbiden_names:
                self.msg.error(f'{name_in_message} name error', f'Sorry, but you can\'t use \'{name}\' as {name_in_message.lower()} name.')
                out = False
            elif name in names_list:
                self.msg.error(f'{name_in_message} name error', f'A {name_in_message.lower()} named \'{name}\' has already been added.')
                out = False 
            if not name:
                self.msg.error(f'{name_in_message} name error', f'{name_in_message} name cannot be empty.')
                out = False
            
        return out

    # удаление файла
    def __delete_file__(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as errormsg:
            self.msg.error(f'Error deleting \'{path}\'', errormsg)


    def __delete_from_dicts__(self, names:list, names_list:list, root_dict:dict, name_in_message: str, plural_name_in_message: str):
        deleted_names = []
        if 'ALL' in names:
            for name in names_list:
                del root_dict[name]
                self.__delete_file__(self.__get_lib_db_path__(name))
            deleted_names = names_list
        else:
            for name in names:
                if name in names_list:
                    del root_dict[name]
                    self.__delete_file__(self.__get_lib_db_path__(name))
                    deleted_names.append(name)
                else:
                    self.msg.error(f'{name_in_message} name error', f'A {name_in_message.lower()} named \'{name}\' not found.')
        if deleted_names:
            self.__changed__ = True
            self.msg.message(f'List of removed {plural_name_in_message.lower()}:')
            for name in deleted_names:
                self.msg.text_message(name)

    ############# LIBRARIES #############

    def set_library(self, path: str, name: str, name_in_list=False):
        library_path = os.path.realpath(path)
        library_name = name if name else os.path.basename(library_path)
        set_is_ok = self.__presence_in_list_checks__(name_in_list, 'Library', library_name, self.library_list)
        # Проверки
        if os.path.isdir(library_path):
            if not check_library_folder(library_path, self.msg): 
                set_is_ok = False              
        else:
            self.msg.error('Library path error', f'\'{library_path}\' is not a directory.')
            set_is_ok = False
        # Запись настроек, если проверки пройдены
        if set_is_ok:
            self.config['libraries'][library_name] = {'path' : library_path}
            self.__changed__ = True
            self.msg.message(f'Library \'{library_name}\' was added to known list.')


    def del_library(self, library_names:list):
        self.__delete_from_dicts__(library_names, self.user_library_list, self.config['libraries'], 'Library', 'Libraries')
        


    def get_libraries_table(self):
        out = []
        for library_name in self.library_list:
            library_path = self.__get_full_library_path__(library_name)
            if not self.libraries_status[library_name]:
                library_status = 'ERROR'
            elif library_name == self.used_library:
                library_status = 'IN USE'
            else:
                library_status = 'OK'
            out.extend([[library_name, library_status, library_path]])
        return out


    def select_library(self, library_name: str):
        if library_name in self.library_list:
            if self.libraries_status[library_name]:  
                self.config['settings']['used_library'] = library_name
                self.__changed__ = True
                self.msg.message(f'\'{library_name}\' library is selected for use.')
        else:
            self.msg.error('Library name error', f'A library named \'{library_name}\' not found.')

    ############# SHELLS #############

    def shell_set(self, shell_name: str, shell_path: str, shell_popen_args: str, shell_encoding: str, shell_in_list: bool):
        set_is_ok = self.__presence_in_list_checks__(shell_in_list, 'Shell', shell_name, self.shell_list)
        # Проверка пути до оболочки (не знаю какие еще проверки можно запихать)
        if not os.path.exists(shell_path):
            self.msg.error('Shell path error', f'File \'{shell_path}\' not found.')
            set_is_ok = False
        # Проверка аргументов для Popen
        try:
            parsed_popen_args = literal_eval(shell_popen_args)
            for arg in parsed_popen_args:
                if type(arg) is not str or not arg:
                    self.msg.error('Popen arguments list read error', f'Argument value \'{arg}\' is not a string.')
                    set_is_ok = False
        except Exception as errormsg:
            self.msg.error('Popen arguments list read error', errormsg)
            set_is_ok = False
        # Проверка кодировки
        if not shell_encoding:
            self.msg.error('Shell encoding error', 'Encoding not specified.')
            set_is_ok = False
        try:
            ''.encode(shell_encoding)
        except LookupError as errormsg:
            self.msg.error('Shell encoding error', errormsg)
            set_is_ok = False
        # Запись настроек, если проверки пройдены
        if set_is_ok:
            self.config['shells'][shell_name] = {'path': shell_path,
                                                 'popen_args': parsed_popen_args,
                                                 'encoding': shell_encoding}
            self.__changed__ = True
            self.msg.message(f'Shell \'{shell_name}\' was added to known list.')

    def del_shells(self, shells_names:list):
        self.__delete_from_dicts__(shells_names, self.user_shell_list, self.config['shells'], 'Shell', 'Shells')

    def get_shells_table(self):
        out = []
        for shell_name in self.user_shell_list:
            out.extend([[shell_name, self.shell_dict[shell_name]['path'], self.shell_dict[shell_name]['popen_args'], self.shell_dict[shell_name]['encoding']]])
        return out

    ################
    

    def save_changes(self):
        if self.__changed__:
            self.get_config()
            self.__write_json__()  