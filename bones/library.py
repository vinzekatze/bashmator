import os
import json
from bones.funcs import warning, message
from bones.yamlscript import YamlScript

class Library:
    def __init__(self, path: str):
        self.path = path
        self.jsonpath = os.path.join(path, '__library.json')
        self.files = {}
        self.lib_changes = []
        self.lib_new = []
        self.lib_losts = []
        try:
            # Возможно, лучше было бы использовать TinyDB.
            # Внедрю, если возникнут проблемы с текущим решением.
            with open(self.jsonpath, mode='r', encoding='utf-8') as json_file:
                self.data = json.load(json_file)
        except Exception as errormsg:
            warning('Can\'t load script library', errormsg)
            self.data = {}
    
    def FileSearch(self):
        for root, _, files in os.walk(self.path):
            for file_name in files:
                if file_name.endswith(".yaml"):
                    fullpath = os.path.join(root, file_name)
                    name = os.path.splitext(os.path.relpath(fullpath, self.path))[0]
                    self.files.update({name:{'path':fullpath,'mtime':os.path.getmtime(fullpath)}})

    def CheckChanges(self):
        for key in self.files.keys():
            try:
                if self.files[key]['mtime'] != self.data[key]['mtime']: 
                    self.lib_changes.append(key)
            except:
                self.lib_new.append(key)
        for key in self.data.keys():
            try: 
                self.files[key]
            except:
                self.lib_losts.append(key)

    def Update(self):
        if len(self.lib_changes) + len(self.lib_losts) + len(self.lib_new) != 0:
            for key in self.lib_losts: del self.data[key] 
            message('Updating local library ...')
            for key in self.lib_changes + self.lib_new:
                self.data.update({key:{}})
                script = YamlScript(self.files[key]['path'],key)
                self.data[key]['path'] = self.files[key]['path']
                self.data[key]['info'] = script.info
                self.data[key]['author'] = script.author
                self.data[key]['tags'] = script.tags
                self.data[key]['shell'] = script.shell
                self.data[key]['mtime'] = os.path.getmtime(self.files[key]['path'])
                self.data[key]['status'] = script.status
            with open(self.jsonpath, mode='w', encoding='utf-8') as f:
                json.dump(self.data, f, sort_keys=True)
            message('Update completed')

    def Search(self, keys: list, words: list, outkeys: list, ignoge_case: bool):
        result = []
        out = []
        for line in self.data.items():
            string = line[0]
            for value in keys:
                if value == 'tags': string += ' ' +' '.join(line[1].get(value, ''))
                else: string += ' ' + line[1].get(value, '')
            entrycount=0
            for word in words:
                if ignoge_case: 
                    if word.lower() in string.lower(): entrycount+=1
                else:
                    if word in string: entrycount+=1
            if entrycount == len(words): 
                result.append(
                    [line[0]]+[line[1].get(outkey, '-') for outkey in outkeys]+ [', '.join(line[1].get('tags', ''))]
                    )
        if len(result):
            # Сортировка не требуется тк библиотека скриптов уже отсортирована
            out = [['script name'] + outkeys + ['tags']] + result
        return out