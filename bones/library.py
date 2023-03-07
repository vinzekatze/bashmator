import os
import json
import os.path
import sys

from bones.yamlscript import YamlScript

def check_library_folder(path: str, msg):
    yamls_path = os.path.join(path, 'modules')
    files_path = os.path.join(path, 'files')
    if not os.path.isdir(yamls_path) or not os.path.isdir(files_path):
        msg.error('Library path error',f'Can\'t find folders \'modules\' and \'files\' at library directory \'{path}\'.')
        msg.text_message('Create these folders in the root of your library, or make sure the library path is correct.')
        return False
    else:
        return True

class Library:
    def __read_json__(self):
        try:
            # Возможно, лучше было бы использовать TinyDB.
            # Внедрю, если возникнут проблемы с текущим решением.
            with open(self.jsonpath, mode='r', encoding='utf-8') as json_file:
                self.data = json.load(json_file)
        except OSError:
            self.data = {}
    
    def __init__(self, path: str, msg, folder_status: bool, known_shells: dict, verbose=False):
        self.msg = msg
        self.path = path
        self.yamls_path = os.path.join(path, 'modules')
        self.files_path = os.path.join(path, 'files')
        self.jsonpath = os.path.join(path, 'library.json')
        self.files = {}
        self.lib_changes = []
        self.lib_new = []
        self.lib_losts = []
        self.__read_json__()
        self.verbose = verbose
        self.known_shells = known_shells
        if not folder_status:
            sys.exit(1)
    
    def file_search(self):
        for root, _, files in os.walk(self.yamls_path):
            for file_name in files:
                if file_name.endswith(".yaml"):
                    fullpath = os.path.join(root, file_name)
                    name = os.path.splitext(os.path.relpath(fullpath, self.yamls_path))[0]
                    self.files.update({name:{'path':fullpath,'mtime':os.path.getmtime(fullpath)}})

    # Наверное тоже не самое лучшее решение, но пусть пока будет так
    def check_changes(self):
        for key in self.files.keys():
            try:
                if self.files[key]['mtime'] != self.data[key]['mtime']: 
                    self.lib_changes.append(key)
            except KeyError:
                self.lib_new.append(key)
        for key in self.data.keys():
            try: 
                _ = self.files[key]
            except KeyError:
                self.lib_losts.append(key)

    def update_lib(self):
        if len(self.lib_changes) + len(self.lib_losts) + len(self.lib_new) != 0:
            self.msg.message('Library changes detected. Scanning ...')
            if self.verbose:
                if self.lib_new: 
                    self.msg.message('New scripts:')
                    for script in self.lib_new: self.msg.text_message(script)
                if self.lib_changes: 
                    self.msg.message('Changed scripts:')
                    for script in self.lib_changes: self.msg.text_message(script)
                if self.lib_losts:
                    self.msg.message('Deleted scripts:')
                    for script in self.lib_losts: self.msg.text_message(script)
            for key in self.lib_losts: del self.data[key] 
            for key in self.lib_changes + self.lib_new:
                self.data.update({key:{}})
                script = YamlScript(path=self.files[key]['path'], 
                                    name=key, 
                                    library_files_path=self.files_path, 
                                    bshm_version='' ,
                                    known_shells=self.known_shells,
                                    msg=self.msg,
                                    status_from_lib='',
                                    verbose_validation=False)
                self.data[key]['path'] = self.files[key]['path']
                self.data[key]['description'] = script.description
                self.data[key]['author'] = script.author
                self.data[key]['tags'] = script.tags
                self.data[key]['shell'] = script.main_shell
                self.data[key]['mtime'] = os.path.getmtime(self.files[key]['path'])
                self.data[key]['status'] = script.status
            with open(self.jsonpath, mode='w', encoding='utf-8') as f:
                json.dump(self.data, f, sort_keys=True)
            self.__read_json__()
            self.msg.message('Scan completed')
        elif self.verbose:
            self.msg.message('No changes found in the library')

    def search(self, keys: list, words: list, outkeys: list, ignoge_case: bool):
        result = []
        out = []
        for line in self.data.items():
            string = line[0]
            for value in keys:
                if value == 'tags': string += ' ' + ' '.join(line[1].get(value, ''))
                else: string += ' ' + line[1].get(value, '')
            entrycount=0
            for word in words:
                if ignoge_case: 
                    if word.lower() in string.lower(): entrycount+=1
                else:
                    if word in string: entrycount+=1
            if entrycount == len(words): 
                result_line = [line[0]]+[line[1].get(outkey, '-') for outkey in outkeys] + [', '.join(line[1].get('tags', ''))]
                result.append(result_line)

        if len(result):
            out = [['script name'] + outkeys + ['tags']] + result
        return out