from tabulate import tabulate
from textwrap import wrap
from math import floor
from shutil import get_terminal_size

from colorama import Fore, Style

#######################################################
terminal_size, _ = get_terminal_size()
messages_size = 14
standard_text_size = 80
style_line = '+' + '-' * (standard_text_size - 1) + '\n'
style_line2 = '#' + '-' * (standard_text_size - 1) + '\n'
#######################################################

def wrap_text(text: str, delimiter='\n', max_symbols=standard_text_size, min_symbols=terminal_size):
    symbols = max([1, min([max_symbols, min_symbols - len(delimiter)])])
    out = ''
    if text:
        text_list = text.split('\n')
        for line in text_list:
            out += delimiter.join(wrap(line,symbols))
    return out


def color(text: str, color_sym, min_length=0, bshm_color=False):
    if len(str(text)) < min_length:
        formated_text = text + ' ' * (min_length - len(text))
    else:
        formated_text = text

    if bshm_color:
        if color_sym == 'R':
            out = f'{Fore.RED}{formated_text}{Fore.RESET}'
        elif color_sym == 'RB':
            out = f'{Style.BRIGHT}{Fore.RED}{formated_text}{Style.RESET_ALL}'
        elif color_sym == 'G':
            out = f'{Fore.GREEN}{formated_text}{Fore.RESET}'
        elif color_sym == 'GB':
            out = f'{Style.BRIGHT}{Fore.GREEN}{formated_text}{Style.RESET_ALL}'
        elif color_sym == 'Y':
            out = f'{Fore.YELLOW}{formated_text}{Fore.RESET}'
        elif color_sym == 'YB':
            out = f'{Style.BRIGHT}{Fore.YELLOW}{formated_text}{Style.RESET_ALL}'
        elif color_sym == '_B':
            out = f'{Style.BRIGHT}{formated_text}{Style.RESET_ALL}'
        elif color_sym == '_D':
            out = f'{Style.DIM}{formated_text}{Style.RESET_ALL}'
        elif color_sym == '_':
            out = formated_text
        else:
            out = f'{color_sym}{formated_text}{Style.RESET_ALL}'
    else:
        out = formated_text
    return out

class Msg:
    def __init__(self, bshm_color=False):
        self.bshm_color = bshm_color
    
    def change_color_set(self, bshm_color):
        self.bshm_color = bshm_color
    
    def c(self, text: str, color_sym, min_length=0):
        out = color(text, color_sym, min_length, self.bshm_color)
        return out

    def gen_color_style_line(self, max_symbols=standard_text_size, min_symbols=terminal_size):
        symbols = max([1, min([max_symbols, min_symbols])])
        out = color('.' * symbols, '_D', 0, self.bshm_color) + '\n'
        return(out)
    
    def color_multiline(self, string: str, asci_sym):
        preout = []
        for line in string.split('\n'):
            preout.append(self.c(line, asci_sym))
        out = '\n'.join(preout)
        return out

    def frame_text(self, text: str, max_symbols=standard_text_size, min_symbols=terminal_size):
        symbols = max([1, min([max_symbols, min_symbols])])
        if text:
            text_list = text.split('\n')
            if self.bshm_color: out = Style.RESET_ALL
            else: out = ''
            for line in text_list:
                out += '\n'.join(wrap(line,symbols)) + '\n'
            out += '\n\n' + self.gen_color_style_line(max_symbols=max_symbols)
        else:
            out = ''
        return out

    def make_table(self, data: list):
        formated_data = []
        max_lengths = []
        wrapsizes = []
        columns_count = len(data[0])
        table_size_fix = 4 * columns_count
        wrap_up_limit=25
        
        for column in range(columns_count):    
            max_lengths.append(min([wrap_up_limit, max([1,len(max([str(word[column]) for word in data], key=len))])]))
        for column in range(columns_count):
            wrapsizes.append(floor((terminal_size) * max_lengths[column]/(sum(max_lengths) + table_size_fix)))

        correction = terminal_size - sum(wrapsizes) - table_size_fix
        if correction < 0:
            for _ in range(correction):
                max_index = wrapsizes.index(max(wrapsizes))
                wrapsizes[max_index] -= 1
        elif correction > 0:
            for _ in range(correction):
                min_index = wrapsizes.index(min(wrapsizes))
                wrapsizes[min_index] += 1

        for line in data:
            formated_data.append(['\n'.join(wrap(str(text), max([1, wrapsizes[i]]))) for i, text in enumerate(line)])
        # Раскраска
        if self.bshm_color:
            table_len = len(data)
            for i, header in enumerate(data[0]):
                if header == 'status':
                    for j in range(table_len):
                        if data[j][i] in ['NOT FOUND', 'ERROR']:
                            formated_data[j][i] = self.color_multiline(formated_data[j][i], 'R')
                        if data[j][i] in ['IN USE']:
                            formated_data[j][i] = self.color_multiline(formated_data[j][i], 'G')
                        if data[j][i] in ['WARNING']:
                            formated_data[j][i] = self.color_multiline(formated_data[j][i], 'Y')
                        
                        
        out = tabulate(formated_data, headers="firstrow", tablefmt="presto")
        return out

    def message(self, text):
        print(self.c('[MESSAGE]','_B',messages_size), 
            text,
            sep='')
        
    def text_message(self, text):
        print(self.c('','_B',messages_size), 
            text,
            sep='')
    
    def error(self, name, info):
        print(self.c('[ERROR]','RB',messages_size), 
            self.c(f'[{name}]: ','R',0),
            info,
            sep='')
    
    def warning(self, name, info):
        print(self.c('[WARNING]','YB',messages_size), 
            self.c(f'[{name}]: ','Y',0),
            info,
            sep='')

    def yaml_error(self, name, info):
        print(self.c('[YAML ERROR]','RB',messages_size), 
            self.c(f'[{name}]: ','R',0),
            info,
            sep='')

    def yaml_warning(self, name, info):
        print(self.c('[YAML WARNING]','YB',messages_size), 
            self.c(f'[{name}]: ','Y',0),
            info,
            sep='')

    def warning_file(self, path):
        print(self.c('','_',messages_size,),
            self.c('[FILE]: ','_B',0),
            path,
            sep='')

    def get_logo_art(self, version):
        if self.bshm_color: 
            c = [Fore.GREEN, Style.BRIGHT, Style.RESET_ALL]
        else: 
            c = ['', '', '']
        
        if terminal_size > 55:
            logoart=f'''
                                        {c[1]}{c[0]}__     _{c[2]}  
    {c[1]}_           {c[0]}_{c[2]}             _         {c[1]}{c[0]}\ \   | |{c[2]} 
   {c[1]}| |_ ___ {c[0]}___| |_{c[2]} _____ ___| |_ ___ ___{c[1]}{c[0]}\ \ / __){c[2]}
   {c[1]}| . | .'{c[0]}|_ -|   {c[2]}|     | .'|  _| . |  _|{c[1]}{c[0]}> >\__ \{c[2]}
   {c[1]}|___|__,{c[0]}|___|_|_{c[2]}|_|_|_|__,|_| |___|_| {c[1]}{c[0]}/ / (   /{c[2]}
    by vinze{c[1]}katze{c[2]}                       {c[1]}{c[0]}/_/   |_|{c[2]} 
    version {version}
    '''
        else:
            logoart=f'''
                    {c[1]}{c[0]}__     _{c[2]}  
    {c[1]}_       {c[0]}_{c[2]}       {c[1]}{c[0]}\ \   | |{c[2]} 
   {c[1]}| |_{c[0]} ___| |_{c[2]} _____{c[1]}{c[0]}\ \ / __){c[2]}
   {c[1]}| . {c[0]}|_ -|   {c[2]}|     |{c[1]}{c[0]}> >\__ \{c[2]}
   {c[1]}|___{c[0]}|___|_|_{c[2]}|_|_|_|{c[1]}{c[0]} / (   /{c[2]}
    by vinze{c[1]}katze{c[2]}   {c[1]}{c[0]}/_/   |_|{c[2]} 
    version {version}
        '''

        return logoart