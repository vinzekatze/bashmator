#!/usr/bin/env python3
# vinzekatze was here

import os.path
import argparse
import sys
#from sys import version_info
from appdirs import user_config_dir
from colorama import deinit as colorama_deinit
from colorama import just_fix_windows_console

from bshm.bones.yamlscript import YamlScript
from bshm.bones.library import Library
from bshm.bones.config import Configuration

def main():
    __version__ = "1.1.7"
    __programm_location__ = os.path.dirname(os.path.realpath(__file__))
    __default_lib_path__ = os.path.join(__programm_location__,'library')
    __config_location__ = user_config_dir('bashmator')

    settings_json = Configuration(__config_location__, __default_lib_path__)
    
    msg = settings_json.msg

    if settings_json.color:
        just_fix_windows_console()

    logoart = msg.get_logo_art(__version__)
    style_line2 = msg.gen_color_style_line(65)
    used_library_with_status = settings_json.used_library if settings_json.used_library_status else f'{settings_json.used_library} {msg.c("[ERROR]","R")}'
    __main_description__ = f'''
{logoart}
{style_line2}

{msg.c('used library:','_B')} {used_library_with_status}
'''

    # Тупо чтобы help показывать, когда нет аргументов
    def bshm_root(allargs):
        if not allargs.main_subparsers:
            mainparser.print_help()
    
    # Команда use
    def command_use(allargs):
        mainlib = Library(path=settings_json.used_library_path, 
                        msg=settings_json.msg, 
                        folder_status=settings_json.used_library_status,
                        known_shells=settings_json.shell_dict,
                        json_path=settings_json.used_lib_db_path) # Загрузка 'library.json'
        if settings_json.auto_scan:
            mainlib.file_search()
            mainlib.check_changes()
            mainlib.update_lib()
        
        if allargs.script_name in mainlib.data.keys():
            used_script = YamlScript(path=mainlib.data[allargs.script_name]['path'], 
                                    name=allargs.script_name, 
                                    library_files_path=mainlib.files_path, 
                                    bshm_version=__version__,
                                    known_shells=settings_json.shell_dict,
                                    msg=settings_json.msg,
                                    auto_scan=settings_json.auto_scan,
                                    status_from_lib=mainlib.data.get(allargs.script_name,{}).get('status', ''),
                                    library_name=settings_json.used_library)
            # Флаг install
            if allargs.install:
                print(used_script.install)
            # исполнение / печать кода
            else:
                used_script.script_launch(logging=allargs.logging,
                                        show_log=allargs.show_log,
                                        script_name=allargs.script_name,
                                        script_args=allargs.options,
                                        code_print=allargs.print)
        # Поиск, если запрашиваемый скрипт не найден
        elif allargs.script_name:
            founds = mainlib.search([], [allargs.script_name], ['status'], True)
            if len(founds):
                print(f'Script "{allargs.script_name}" not found. Search results:\n')
                print(msg.make_table(founds))
            else:
                print(f'Script "{allargs.script_name}" not found.')
        
        # Если ничего не вбито
        else:
            use_parcer.print_usage()
            founds = mainlib.search([], [], ['status'], True)
            print()
            print(f'Use \'bashmator search\' for advanced search.\nList of all available scripts:\n')
            print(msg.make_table(founds))

    # Команда search
    def command_search(allargs):
        mainlib = Library(path=settings_json.used_library_path, 
                        msg=settings_json.msg, 
                        folder_status=settings_json.used_library_status,
                        known_shells=settings_json.shell_dict,
                        json_path=settings_json.used_lib_db_path) # Загрузка 'library.json'
        
        if settings_json.auto_scan:
            mainlib.file_search()
            mainlib.check_changes()
            mainlib.update_lib()
        add_search=[]
        if allargs.author: add_search.append('author')
        if allargs.shell: add_search.append('shell')
        if allargs.description: add_search.append('description')
        founds = mainlib.search(['tags'] + add_search, allargs.keyword, ['status'] + add_search, allargs.ignore_case)
        if len(founds):
            if not allargs.keyword:
                search_parcer.print_usage()
                print()
                print('List of all available scripts:\n')
            else:
                print('Search results:\n')
            print(msg.make_table(founds))
        else:
            print('Nothing found ...')

    # Команда config
    def command_config(allargs):
        if not allargs.lib_autoupdate and not allargs.bshm_color:# and allargs.reset_settings:
            bshm_config_parcer.print_usage()
            print()
            print(current_bshm_sets_text)
        else:
            #if allargs.reset_settings:
            if allargs.lib_autoupdate: settings_json.set_settings_bool('auto-scan', allargs.lib_autoupdate)
            if allargs.bshm_color: settings_json.set_settings_bool('color', allargs.bshm_color)

    # LIBRARY
    def library_root(allargs):
        if not allargs.library_subparsers:
            library_config_parser.print_usage()
            print()
            print(libraries_table_text)

    def library_add(allargs):
        settings_json.set_library(allargs.library_path, allargs.library_name)

    def library_del(allargs):
        settings_json.del_library(allargs.libraries_names)

    def library_use(allargs):
        settings_json.select_library(allargs.library_name)
        _ = Library(path=settings_json.used_library_path,
                    msg=settings_json.msg,
                    folder_status=settings_json.used_library_status,
                    known_shells=settings_json.shell_dict,
                    json_path=settings_json.used_lib_db_path,
                    verbose=True) # Загрузка 'library.json'

    def library_scan(allargs):
        mainlib = Library(path=settings_json.used_library_path,
                        msg=settings_json.msg,
                        folder_status=settings_json.used_library_status,
                        known_shells=settings_json.shell_dict,
                        json_path=settings_json.used_lib_db_path,
                        verbose=True) # Загрузка 'library.json'
        if allargs.rebuild_lib: mainlib.data = {}
        mainlib.file_search()
        mainlib.check_changes()
        mainlib.update_lib()

    # SHELL
    def shell_root(allargs):
        if not allargs.shell_subparcers:
            shell_config_parcer.print_usage()
            print()
            print(shells_table_text)

    def shell_add(allargs):
        shell_name = allargs.shell_name if allargs.shell_name else os.path.basename(allargs.shell_path)
        settings_json.shell_set(shell_name, allargs.shell_path, allargs.shell_popen_args, allargs.shell_encoding, False)

    def shell_del(allargs):
        settings_json.del_shells(allargs.shells_names)


    #if settings_json.color: print(Style.RESET_ALL, end='') # Lol просто фикс тупой консоли кали на маке, которая красит все в серый :/ 
    try:
        #if version_info < (3, 10, 6):
        #    warning('Outdated Python','Please upgrade your Python version to 3.10.6 or higher', settings_json.color)
        
        # Определение парсера аргументов
        mainparser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
                                             description=__main_description__, 
                                             add_help=False)
        mainparser.set_defaults(func=bshm_root)

        main_subparsers = mainparser.add_subparsers(title=msg.c('commands','_B'),
                                                    dest='main_subparsers', 
                                                    required=False)

        mainoptions = mainparser.add_argument_group(msg.c('options','_B'))
        mainoptions.add_argument('-h', '--help', action='help', help="show this help message and exit")
        mainoptions.add_argument('-v', '--version', action='version', version=__version__)
        
        #####################################
        # Субпарсер для use
        #####################################
        use_parcer = main_subparsers.add_parser('use',
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                help='use script',
                                                description=msg.frame_text(f'Runs a script from the library by it\'s name.'),
                                                add_help=False,
                                                usage='%(prog)s [-l] [-o FILE] [-i] [-c] [-h] script ...')
        # Группа позиционных аргументов
        use_positional_group = use_parcer.add_argument_group(msg.c('positional arguments','_B'))
        use_positional_group.add_argument('script_name', nargs='?', metavar='script', help='script name and it\'s options')
        use_positional_group.add_argument('options', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
        # Группа запуска скриптов
        use_launch_group = use_parcer.add_argument_group(msg.c('script launch options','_B'))
        use_launch_group.add_argument('-l','--log-headers', dest='show_log', action="store_true", help="print log headers when executing script")
        use_launch_group.add_argument("-o","--out", dest="logging", metavar="FILE", help="log execution process to file (append mod)")
        #use_launch_group.add_argument('-s','--shell', default='' ,dest='run_shell', metavar='PATH', help='specify shell for script execution')
        # Группа печати
        coder_group = use_parcer.add_argument_group(msg.c('code printing options','_B'))
        coder_group.add_argument("-i","--install", action="store_true", help="show script\'s installation information")
        coder_group.add_argument("-c","--code", dest="print", action="store_true", help="print script without execution")
        # Группа других аргументов
        use_other_group = use_parcer.add_argument_group(msg.c('other options','_B'))
        use_other_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
        use_parcer.set_defaults(func=command_use)
        
        #####################################
        # Субпарсер для search
        #####################################
        search_parcer = main_subparsers.add_parser('search', 
                                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                                   help='search script at library by keywords', 
                                                   description=msg.frame_text(f'Search for a script in the used library. By default, the search is performed by tags and script names.'), 
                                                   add_help=False)
        # Группа позиционных аргументов
        search_positional_group = search_parcer.add_argument_group(msg.c('positional arguments','_B'))
        search_positional_group.add_argument('keyword', nargs='*', help='keywords for search', default=[])
        # Группа опций
        search_options_group = search_parcer.add_argument_group(msg.c('search options','_B'))
        search_options_group.add_argument("-i","--ignore-case",dest="ignore_case", action="store_true", help="ignore case distinctions")
        search_options_group.add_argument("-A","--author", action="store_true", help="add search by author")
        search_options_group.add_argument("-D","--description", action="store_true", help="add search by script description")
        search_options_group.add_argument("-S","--shell", action="store_true", help="add search by shell")
        # Группа других опций
        search_other_group = search_parcer.add_argument_group(msg.c('other options','_B'))
        search_other_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
        search_parcer.set_defaults(func=command_search)
        
        #####################################
        # Субпарсер для set
        #####################################
        current_bshm_sets_text = f'{msg.c("Current settings","_B")}:\n  auto-scan {settings_json.auto_scan}\n  color {settings_json.color}'
        bshm_config_parcer = main_subparsers.add_parser('set',
                                                        formatter_class=argparse.RawDescriptionHelpFormatter, 
                                                        help='settings', 
                                                        description=msg.frame_text(current_bshm_sets_text),
                                                        add_help=False)
        bshm_config_settings_group = bshm_config_parcer.add_argument_group(msg.c('settings','_B'))
        bshm_config_settings_group.add_argument('--auto-scan', dest='lib_autoupdate', choices=['true','false'], help='automatically detect changes in the used library')
        bshm_config_settings_group.add_argument('--color', dest='bshm_color', choices=['true','false'], help='use color on the command line')
        #bshm_config_settings_group.add_argument('--reset', dest='reset_settings', action='store_true', help='reset settings to default')
        bshm_config_other_group = bshm_config_parcer.add_argument_group(msg.c('other options','_B'))
        bshm_config_other_group.add_argument('-h', '--help', action='help', help='show this help message and exit')
        bshm_config_parcer.set_defaults(func=command_config)

        #####################################
        # Cубпарсер для shell
        #####################################
        if not settings_json.user_shell_list:
            shells_table = '  empty'
        else:
            shells_table = msg.make_table([['name', 'path', 'popen arguments', 'encoding']] + settings_json.get_shells_table())
        shells_table_text = f'{msg.c("known shells","_B")}:\n{shells_table}'

        shell_config_parcer = main_subparsers.add_parser('shell',
                                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                                         help='shells management',
                                                         epilog=f'{msg.gen_color_style_line()}\n{shells_table_text}',
                                                         description='',
                                                         add_help=False)
        shell_config_parcer.set_defaults(func=shell_root)
        shell_subparcers = shell_config_parcer.add_subparsers(title=msg.c('commands','_B'),
                                                              dest='shell_subparcers', 
                                                              required=False)
        ## Субпарсер для shell add
        shell_subparcers_add = shell_subparcers.add_parser('add',
                                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                                           help='add a new shell to the known list',
                                                           description=msg.frame_text('Add a new shell to the known list.'),
                                                           add_help=False)
        shell_subparcers_add.set_defaults(func=shell_add)
        shell_subparcers_add_positional_group = shell_subparcers_add.add_argument_group(msg.c('positional arguments','_B'))
        shell_subparcers_add_positional_group.add_argument('shell_path', metavar='path', help='full path to the shell (for example: /usr/bin/bash)')
        shell_subparcers_add_options_group = shell_subparcers_add.add_argument_group(msg.c('options','_B'))
        shell_subparcers_add_options_group.add_argument('--name', metavar='NAME', dest='shell_name', default='', help="specify shell name (default: base name)")
        shell_subparcers_add_options_group.add_argument('--encoding', metavar='CODE', dest='shell_encoding', default='utf-8', help='shell encoding (used when logging; default: \'utf-8\')')
        shell_subparcers_add_options_group.add_argument('--popen-args', metavar='LIST', dest='shell_popen_args', default='["-c"]', help='shell arguments for the subprocess.Popen function (default: \'["-c"]\')')
        shell_subparcers_add_options_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
        
        ## Субпарсер для shell delete
        shell_subparcers_delete = shell_subparcers.add_parser('delete',
                                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                                           help='remove a shell from the known list', 
                                                           description=msg.frame_text('Remove a shell from the known list. Use \'delete ALL\' to clear.'),
                                                           add_help=False)
        shell_subparcers_delete.set_defaults(func=shell_del)
        shell_subparcers_delete_positional_group = shell_subparcers_delete.add_argument_group(msg.c('positional arguments','_B'))
        shell_subparcers_delete_positional_group.add_argument('shells_names', metavar='name', nargs='+' ,help='shell name (can be multiple)')
        shell_subparcers_delete_options_group = shell_subparcers_delete.add_argument_group(msg.c('options','_B'))
        shell_subparcers_delete_options_group.add_argument('-h', '--help', action='help', help="show this help message and exit")

        # Группа для опций shell
        shell_subparcers_group = shell_config_parcer.add_argument_group(msg.c('options','_B'))
        shell_subparcers_group.add_argument('-h', '--help', action='help', help="show this help message and exit")

        #####################################
        # Cубпарсер для library
        #####################################
        libraries_table = msg.make_table([['name', 'status', 'path']] + settings_json.get_libraries_table())
        libraries_table_text = f'{msg.c("known libraries","_B")}:\n{libraries_table}'
        library_config_parser = main_subparsers.add_parser('library',
                                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                                           help='libraries management', 
                                                           epilog=f'{msg.gen_color_style_line()}\n{libraries_table_text}',
                                                           add_help=False)
        library_config_parser.set_defaults(func=library_root)
        library_config_subparsers = library_config_parser.add_subparsers(title=msg.c('commands','_B'),
                                                                         dest='library_subparsers',
                                                                         required=False)
        ## Субпарсер для library add
        library_config_add = library_config_subparsers.add_parser('add',
                                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                                           help='add a new library to the known list', 
                                                           description=msg.frame_text('Add a new library to the known list.'),
                                                           add_help=False)
        library_config_add.set_defaults(func=library_add)
        library_config_add_positional_group = library_config_add.add_argument_group(msg.c('positional arguments','_B'))
        library_config_add_positional_group.add_argument('library_path', metavar='path', help="path to main library directory")
        library_config_add_options_group = library_config_add.add_argument_group(msg.c('options','_B'))
        library_config_add_options_group.add_argument('--name', metavar='NAME', dest='library_name', default='', help="specify library name (default: folder name)")
        library_config_add_options_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
        ## Субпарсер для library delele
        library_config_del = library_config_subparsers.add_parser('delete',
                                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                                           help='remove library from the known list', 
                                                           description=msg.frame_text('Remove a library from the known list. Type \'delete ALL\' to clear.'),
                                                           add_help=False)
        library_config_del.set_defaults(func=library_del)
        library_config_del_positional_group = library_config_del.add_argument_group(msg.c('positional arguments','_B'))
        library_config_del_positional_group.add_argument('libraries_names', metavar='name', nargs='+' ,help='library name (can be multiple)')
        library_config_del_options_group = library_config_del.add_argument_group(msg.c('options','_B'))
        library_config_del_options_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
        ## Субпарсер для library scan
        library_config_scan = library_config_subparsers.add_parser('scan',
                                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                                           help='detect changes in the used library',
                                                           description=msg.frame_text('Scans the directory of the used library for changes in it\'s contents.'),
                                                           add_help=False)
        library_config_scan.set_defaults(func=library_scan)
        library_config_scan_options_group = library_config_scan.add_argument_group(msg.c('options','_B'))
        library_config_scan_options_group.add_argument('-f','--forced', dest='rebuild_lib', action='store_true', help='reset the saved information and rescan the library')
        library_config_scan_options_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
        ## Субпарсер для library use
        library_config_use = library_config_subparsers.add_parser('use',
                                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                                           help='select library for use',
                                                           description=msg.frame_text('Select the library to use from the known list.'),
                                                           add_help=False)
        library_config_use.set_defaults(func=library_use)
        library_config_use_positional_group = library_config_use.add_argument_group(msg.c('positional arguments','_B'))
        library_config_use_positional_group.add_argument('library_name', metavar='name', help='library name')
        library_config_use_options_group = library_config_use.add_argument_group(msg.c('options','_B'))
        library_config_use_options_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
        # Группа для опций library
        library_config_group = library_config_parser.add_argument_group(msg.c('options','_B'))
        library_config_group.add_argument('-h', '--help', action='help', help="show this help message and exit")
        
        #####################################
        allargs = mainparser.parse_args()
        allargs.func(allargs)

    except KeyboardInterrupt: 
        sys.exit(msg.exit_code)
    finally:
        settings_json.save_changes()   
        colorama_deinit()
        sys.exit(msg.exit_code)

if __name__ == "__main__":
    main()