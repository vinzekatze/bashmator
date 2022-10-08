from tabulate import tabulate
from textwrap import wrap
import datetime
import base64

style_line = "+" + "-" * 60 + '\n'

def NoneControll(value):
    out = '' if value is None else value
    return out

def tobase64(text):
    code = text
    code_bytes = code.encode('utf-8')
    base64_bytes = base64.b64encode(code_bytes)
    base64_msg = base64_bytes.decode('utf-8')
    return(base64_msg)

def warning(name, info):
    print(f'[WARNING] [{name}]: {info}')

def warning_file(path):
    print(f'          [FILE]: {path}')

def error(name, info):
    print(f'[ERROR]   [{name}]: {info}')

def message(text):
    print(f'[MESSAGE] {text}')

def make_table(data: list):
    formated_data=[]
    for line in data:
        formated_data.append(['\n'.join(wrap(str(i),50)) for i in line])
    out = tabulate(formated_data, headers="firstrow", tablefmt="presto")
    return out

def make_lines(text):
    s1 = '-' * len(text) + '\n'
    s2 = text + '\n'
    s3 = s1
    return (s1+s2+s3)

def get_local_time():
    now = datetime.datetime.now(datetime.timezone.utc)
    form_now = now.strftime("%Y-%m-%d %H:%M:%S")
    local_tz = datetime.timezone.utc
    out=f'{form_now} ({local_tz})'
    return(out)

def get_main_header(version,script_name,time,shell,item):
    s1 = style_line
    s2 = f'+ Generated by {version}\n'
    s3 = style_line
    s4 = f'+ Script name:               {script_name} ({item})\n'
    s5 = f'+ Start time:                {time}\n'
    s6 = f'+ Shell:                     {shell}\n'
    return (s1+s2+s3+s4+s5+s6)

def get_code_log(code):
    s1 = style_line
    s2 = "+ Running code\n"
    s3 = style_line
    s4 = f'\n{code}\n\n'
    return(s1+s2+s3+s4)

def get_log_header():
    s1 = style_line
    s2 = "+ Log\n"
    s3 = style_line
    return (s1+s2+s3+"\n")

def get_log_end(time):
    s1 = style_line
    s2 = f'+ End time:                  {time}\n'
    s3 = style_line
    return("\n"+s1+s2+s3+"\n")

def make_range(input):
    result = []
    for part in input.split(','):
        if '-' in part:
            a, b = part.split('-')
            a, b = int(a), int(b)
            if a < b:
                result.extend(range(a, b + 1))
            if a > b:
                result.extend(reversed(range(b, a + 1)))
            if a == b:
                result.extend([a])
        else:
            a = int(part)
            result.append(a)
    return result