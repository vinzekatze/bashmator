#!/usr/bin/env python3
# vinzekatze was here

import os
import argparse
import sys
from bones.yamlscript import YamlScript
from bones.library import Library
from bones.funcs import make_table, tobase64, warning, make_lines

__version__ = "bashmator 0.2.1"
__mainlocation__ = os.path.dirname(os.path.realpath(__file__))
__librarypath__ = os.path.join(__mainlocation__,'library')

version_text = make_lines(f'{__version__} (https://github.com/VinzeKatze/bashmator)')
__main_description__ = f'''
{version_text}

Library path:
{__librarypath__}
'''
# Команда use
def command_use(allargs):
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
                    run_script.Execute_log(run_shell, builded_script, __version__, allargs)
                else:
                    run_script.Execute(run_shell, builded_script, __version__, allargs)
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
    add_search=[]
    if allargs.author: add_search.append('author')
    if allargs.shell: add_search.append('shell')
    if allargs.description: add_search.append('description')
    founds = mainlib.Search(['tags']+add_search, allargs.keyword, ['status']+add_search, allargs.ignore_case)
    if len(founds):
        print('Search results:\n')
        print(make_table(founds))
    else:
        print('Nothing found ...')
    
# Команда update
def command_update(_):
    mainlib.data = {}
    mainlib.FileSearch()
    mainlib.CheckChanges()
    mainlib.Update() 

if __name__ == "__main__":
    try: 
        if sys.version_info < (3, 10, 6):
            warning('Outdated Python','Please upgrade your Python version to 3.10.6 or higher')
        
        # Загрузка и автоапдейт '__library.json'.
        mainlib = Library(__librarypath__)
        mainlib.FileSearch()
        mainlib.CheckChanges()
        mainlib.Update()

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

        # Субпарсер для use
        use_parcer = subparsers.add_parser('use', help='use script')
        use_parcer.add_argument('script', help='script name')
        use_parcer.add_argument('options', nargs=argparse.REMAINDER, help='script options')
        use_parcer.add_argument("-i","--install", action="store_true", help="show installation information")
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


        # Субпарсер для update
        update_parcer = subparsers.add_parser('update', help='force update library', description='Not required under normal conditions. Use it if something goes wrong with \'__library.json\'.')
        update_parcer.set_defaults(func=command_update)

        allargs = mainparser.parse_args()
        allargs.func(allargs)

    except KeyboardInterrupt: 
        quit(0)