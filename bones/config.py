import configparser
import os.path

from sys import exit
from pathlib import Path
from appdirs import user_config_dir

from bones.funcs import error, message, warning


class ConfigFile:    
    def Write(self):
        # Проверка конфига секции Library
        if not self.config.has_section('Library'): self.config.add_section('Library')
        if not self.config.has_option('Library','path'): self.config.set('Library','path','default')
        
        if not self.config.has_option('Library','autoupdate'): self.config.set('Library','autoupdate','true')
        try: self.config.getboolean('Library','autoupdate')
        except: self.config.set('Library','autoupdate','true')
        
        # Проверка конфига секции Tool
        #if not self.config.has_section('Tool'): self.config.add_section('Tool')
        #if not self.config.has_option('Tool','color'): self.config.set('Tool','color','true')
        #try: self.config.getboolean('Tool','color')
        #except: self.config.set('Tool','color','true')
        
        # Запись файла
        try:
            with open(self.configpath, mode='w', encoding='utf-8') as config_file:
                self.config.write(config_file)
        except Exception as errormsg:
            error('Can\'t write settings.ini', errormsg)
            exit(1)
    
    def __GetOptions__(self):
        librarypath = self.config.get("Library", "path")
        if librarypath == 'default': 
            self.CONF_Library_Path = os.path.join(self.prog_path,'library')
        else:
            self.CONF_Library_Path = librarypath
        self.CONF_Library_autoupdate = self.config.getboolean("Library", "autoupdate")
        #self.CONG_Tool_color = self.config.getboolean("Tool", "color")
        
    def Read(self):
        try:
            self.config.read(self.configpath, encoding='utf-8')
            self.__GetOptions__()
        except:
            warning('Error reading \'settings.ini\'','trying to fix...')
            try:
                self.Write()
                self.config.read(self.configpath, encoding='utf-8')
                self.__GetOptions__()
                message('\'settings.ini\' successfully fixed')
            except Exception as errormsg:
                error('Failed to fix', errormsg)
                exit(1)

    def __init__(self, prog_path):
        self.configdir = user_config_dir('bashmator')
        self.configpath = os.path.join(self.configdir, 'settings.ini')
        self.config = configparser.ConfigParser()
        self.prog_path = prog_path
        if not Path(self.configpath).exists():
            try:
                Path(self.configdir).mkdir(parents=True, exist_ok=True)
                self.Write()
                message(f'Configuration file \'{self.configpath}\' was created')
            except Exception as errormsg:
                error('Can\'t create settings.ini', errormsg)
                exit(1)
        self.Read()

    def ReadFile(self):
        with open(self.configpath, mode='r', encoding='utf-8') as config_file:
            out = config_file.read()
        return(out)
        