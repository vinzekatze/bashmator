#!/usr/bin/env python3
# vinzekatze was here

from genericpath import isdir
import os.path
import argparse
from sys import version_info

from bones.yamlscript import YamlScript
from bones.library import Library
from bones.funcs import error, make_table, warning, make_lines #, tobase64
from bones.config import ConfigFile

__version__ = "bashmator 0.3.3"
__mainlocation__ = os.path.dirname(os.path.realpath(__file__))
ConfigFile = ConfigFile(__mainlocation__)

version_text = make_lines(f'--- {__version__} (https://github.com/VinzeKatze/bashmator) ---')
__main_description__ = f'''
{version_text}

Library path:
{ConfigFile.CONF_Library_Path}
'''

# Команда use
def command_use(allargs):
    if ConfigFile.CONF_Library_autoupdate:
        mainlib.FileSearch()
        mainlib.CheckChanges()
        mainlib.Update()
    
    if allargs.script in mainlib.data.keys():
        run_script = YamlScript(mainlib.data[allargs.script]['path'], allargs.script)
        # Флаг install
        if allargs.install:
            print(run_script.install)
        # Печать кода без исполнения
        elif allargs.print:
            run_script.ParseArgs(allargs.options, allargs.script)
            builded_script_list = []
            for script in run_script.items_launch_set:  
                builded_script_list.append(run_script.BuildScript(run_script.scripts_dict[script]['script']))
            # обратная замена некоторых escape последовательностей
            delimite = str(allargs.merge_symbol).replace('\\n','\n')
            delimite = delimite.replace('\\r','\r')
            delimite = delimite.replace('\\a','\a')
            delimite = delimite.replace('\\b','\b')
            delimite = delimite.replace('\\f','\f')
            delimite = delimite.replace('\\t','\t')
            delimite = delimite.replace('\\v','\v')
            
            codetoprint = delimite.join(builded_script_list)
            print(codetoprint)
            #if allargs.base64:
            #    print(tobase64(codetoprint))
            #else:
            #    print(codetoprint)
        # Исполнение кода
        else:
            if allargs.run_shell:
                run_shell = allargs.run_shell
            else:
                run_shell = run_script.shell
            
            run_script.ParseArgs(allargs.options, allargs.script)
            for script in run_script.items_launch_set:
                builded_script = run_script.BuildScript(run_script.scripts_dict.get(script, {}).get('script', ''))
                if allargs.log:
                    run_script.Execute_log(run_shell, builded_script, __version__, allargs, script)
                else:
                    run_script.Execute(run_shell, builded_script, __version__, allargs, script)
    # Поиск, если запрашиваемый скрипт не найден
    else:
        founds = mainlib.Search([], [allargs.script], ['shell','status'], True)
        if len(founds):
            print(f'Script "{allargs.script}" not found. Search results:\n')
            print(make_table(founds))
        else:
            print(f'Script "{allargs.script}" not found.')

# Команда search
def command_search(allargs):
    if ConfigFile.CONF_Library_autoupdate:
        mainlib.FileSearch()
        mainlib.CheckChanges()
        mainlib.Update()
    add_search=[]
    if allargs.author: add_search.append('author')
    if allargs.shell: add_search.append('shell')
    if allargs.description: add_search.append('description')
    founds = mainlib.Search(['tags'] + add_search, allargs.keyword, ['status'] + add_search, allargs.ignore_case)
    if len(founds):
        print('Search results:\n')
        print(make_table(founds))
    else:
        print('Nothing found ...')
    
# Команда config
def command_config(allargs):
    if allargs.lib_path:
        if os.path.isdir(allargs.lib_path) or allargs.lib_path == 'default':
            ConfigFile.config.set('Library', 'path', allargs.lib_path)   
        else:
            error('Directory does not exist', allargs.lib_path)
            exit(1)
    if allargs.lib_autoupdate:
        ConfigFile.config.set('Library', 'autoupdate', allargs.lib_autoupdate)
    
    ConfigFile.Write()
    print('Current settings:')
    print()
    print(ConfigFile.ReadFile())

    if ConfigFile.CONF_Library_autoupdate:
        ConfigFile.Read()
        newlib = Library(ConfigFile.CONF_Library_Path)
        newlib.FileSearch()
        newlib.CheckChanges()
        newlib.Update()

# Команда update
def command_update(allargs):
    if allargs.rebuild_lib: mainlib.data = {}
    mainlib.FileSearch()
    mainlib.CheckChanges()
    mainlib.Update()

if __name__ == "__main__":
    try: 
        if version_info < (3, 10, 6):
            warning('Outdated Python','Please upgrade your Python version to 3.10.6 or higher')
        
        # Определение парсера аргументов
        mainparser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__main_description__)
        mainparser.add_argument('-v', '--version', action='version', version=__version__)
        subparsers = mainparser.add_subparsers(required=True)

        # Субпарсер для search
        search_parcer = subparsers.add_parser('search', help='search script at library by keywords', description='By default, the search is performed by tags and script names.')
        search_parcer.add_argument('keyword', nargs='+', help='search keywords')
        search_parcer.add_argument("-i","--ignore-case",dest="ignore_case", action="store_true", help="ignore case distinctions")
        search_parcer.add_argument("-A","--author", action="store_true", help="add search by author")
        search_parcer.add_argument("-S","--shell", action="store_true", help="add search by shell")
        search_parcer.add_argument("-D","--description", action="store_true", help="add search by script description")
        search_parcer.set_defaults(func=command_search)

        # Субпарсер для update
        update_parser = subparsers.add_parser('update', help='library update options', description='Run without flags to update script library (not required if auto-update is enabled).')
        update_parser.add_argument('-f','--forced', dest='rebuild_lib', action="store_true", help="rebuild script library")
        update_parser.set_defaults(func=command_update)

        # Субпарсер для use
        use_parcer = subparsers.add_parser('use', help='use script')
        use_parcer.add_argument('script', help='script name and it\'s options')
        use_parcer.add_argument('options', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
        use_parcer.add_argument("-i","--install", action="store_true", help="show script\'s installation information")
        use_parcer.add_argument("--shell", default='' ,dest="run_shell", metavar="path", help="specify shell for script execution")
        
        # Группа логирования
        logger_group = use_parcer.add_argument_group('logging options')
        logger_group.add_argument("-o","--out", dest="log", metavar="file", help="log execution process to file (append mod)")
        logger_group.add_argument("-l","--log-headers", dest="show_log", action="store_true", help="print log headers when executing script")
        use_parcer.set_defaults(func=command_use)
        
        # Группа печати
        coder_group = use_parcer.add_argument_group('code printing options')
        coder_group.add_argument("-c","--code", dest="print", action="store_true", help="print script without execution")
        coder_group.add_argument("-d","--delimiter", metavar='*', dest="merge_symbol", default='\n', help="concatenate used item scripts using the specified delimiter (default: {})".format('\\n'))
        #coder_group.add_argument("-b","--base64", dest="base64", action="store_true", help="print encoded in base64 script without execution")

        # Субпарсер для set
        config_parcer = subparsers.add_parser('set', help='settings', description='')
        config_group = config_parcer.add_argument_group('library settings')
        config_group.add_argument("-Lp", dest="lib_path", metavar="directory", help="set path to library (set \'default\' to use bashmator\'s local library)")
        config_group.add_argument("-La", dest="lib_autoupdate", choices=['true','false'], help="enable/disable library auto-update")
        config_parcer.set_defaults(func=command_config)

        allargs = mainparser.parse_args()
        mainlib = Library(ConfigFile.CONF_Library_Path) # Загрузка '__library.json'
        allargs.func(allargs)

    except KeyboardInterrupt: 
        quit(0)