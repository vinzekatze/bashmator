# Bashmator - script/one-liner manager
> One Tool to rule them all, One Tool to find them,  
> One Tool to log them all, and in the CLI bind them ...

Основная задача программы - предоставить единую легко дополняемую среду для запуска, систематизации, поиска и логирования большого количества однострочников и небольших скриптов.

Каждый отдельный скрипт или набор скриптов записываются в YAML-файл, из которого bashmator генерирует аргументы командной строки, подставляет их значения в указанные точки и запускает скрипт в указанной оболочке.

В папке со скриптами (библиотеке) bashmator создает файл `__library.json` и поддерживает его актуальность. В данном файле записывается информация о доступных скриптах, что избавляет от необходимости парсить все YAML-файлы при каждом запуске программы.
## Install
```
git clone https://github.com/VinzeKatze/bashmator
cd ./bashmator
pip install -r requirements.txt
```
Рекомендуется добавить bashmator в PATH, иначе программой будет не удобно пользоваться:
```
sudo ln -s $(pwd)/bashmator.py /usr/local/bin/bashmator
```
## Update
Буду стараться делать так, чтобы для обновления было достаточно использовать только `git pull`, но иногда может потребоваться пересобрать библиотеку скриптов:
```
git pull
bashmator update -f
```
## Usage
### Program
```
$ bashmator -h 
usage: bashmator [-h] [-v] {search,update,use,set} ...

-----------------------------------------------------------------
--- bashmator 0.3.3 (https://github.com/VinzeKatze/bashmator) ---
-----------------------------------------------------------------

Library path:
/...YOUR PATH.../bashmator/library

positional arguments:
  {search,update,use,set}
    search              search script at library by keywords
    update              library update options
    use                 use script
    set                 settings

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```
Поиск доступен в `use` и `search`, однако в первом случае осуществляется только по названию, а во втором - названию и тегам (расширяемо флагами):
```
$ bashmator use hello world             
Script "hello" not found. Search results:

 script name            | shell     | status   | tags
------------------------+-----------+----------+---------------
 examples/hello_world_1 | /bin/bash | OK       | help, example
 examples/hello_world_2 | python3   | OK       | help, example
 examples/hello_world_3 | /bin/bash | OK       | example, help
 
$ bashmator search -S python
Search results:

 script name            | status   | shell   | tags
------------------------+----------+---------+---------------
 examples/hello_world_2 | OK       | python3 | help, example
```
`use` help:
```
$ bashmator use -h
usage: bashmator use [-h] [-i] [--shell path] [-o file] [-l] [-c] [-d *] script

positional arguments:
  script               script name and it's options

options:
  -h, --help           show this help message and exit
  -i, --install        show script's installation information
  --shell path         specify shell for script execution

logging options:
  -o file, --out file  log execution process to file (append mod)
  -l, --log-headers    print log headers when executing script

code printing options:
  -c, --code           print script without execution
  -d *, --delimiter *  concatenate used item scripts using the specified delimiter (default: \n)
```
Пример запуска скрипта из библиотеки с опцией логирования результатов:
```
$ bashmator use -o ./hello_world.log examples/hello_world_1 2
Hello World!
...Hello, vinzekatze

Hello World!
...Hello, vinzekatze
```
Лог:
```
$ cat ./hello_world.log 
+------------------------------------------------------------
+ Generated by bashmator 0.3.3
+------------------------------------------------------------
+ Script name:               examples/hello_world_1 (0)
+ Start time:                2022-10-09 20:33:06 (UTC)
+ Shell:                     /bin/bash
+------------------------------------------------------------
+ Running code
+------------------------------------------------------------

phrase='Hello World'
ans=$(echo $phrase | cut -d ' ' -f 1)
for i in $(seq 1 2); do
  echo 'Hello World!'
  echo -e "...$ans, $(whoami)\n"
done

+------------------------------------------------------------
+ Log
+------------------------------------------------------------

Hello World!
...Hello, vinzekatze

Hello World!
...Hello, vinzekatze


+------------------------------------------------------------
+ End time:                  2022-10-09 20:33:06 (UTC)
+------------------------------------------------------------
```
### Library
По умолчанию для хранения скриптов bashmator использует внутреннюю папку `library`. Внутри этой папки можно создавать произвольные каталоги и подкаталоги. Чтобы добавить новый скрипт в программу необходимо поместить YAML-файл внутри данной папки и обновить библиотеку (по умолчанию включено автообновление при каждом запуске). 
Название скрипта генерируется следующим образом `{folder_name}/{subfolder_name}/.../{basename_of_yaml}`

Чтобы использовать другую папку в качестве библиотеки выполните команду:
```
bashmator set -Lp <path to directory>
```
### YAML
Ниже представлена общая требуемая структура YAML-файлов:
```
description:      <string or null>      # описание скрипты
author:           <string or null>      # автор скрипта
tags:             <list or null>        # теги для поиска
  - [tag]         <string or number>     
  - [...]
install:          <string or null>      # информация о установке необходимых для работы скрипта программ
arguments:        <dictionary or null>  # аргументы командной строки
  [argument name]:                      # произвольное имя аргумента
    default:      <string, number, list or null>  # значение по умолчанию
    replacer:     <string>              # cтрока, которая будет заменена в коде на значение аргумента
    description:  <string or null>      # описание аргумента
  [...]                                 # количество аргументов не ограничено
shell:            <string>              # путь до оболочки, в которой скрипт будет запущен
script:           <string or null>      # код
item_[NUM]:       (not required)        # блок с дополнительным скриптом
  script:         <string or null>      # код
  description:    <string or null>      # описание скрипта
item_[...]                              # количество дополнительных скриптов не ограниченно
```
Чтобы лучше понять структуру, рекомендуется ознакомиться с примерами в `library/examples`.
Также не забывайте использовать возможности YAML для работы со строками, например `|-` даст возможность вводить многострочные тексты и скрипты:
```
description: |-
  Многострочное
  описание
  работы 
  скрипта
script: |-
  for i in {1..5}; do
    echo $i
  done
```
#### Arguments
В зависимости от значения ключа `default` bashmator будет генерировать аргументы с разными свойствами:
- если `default` пуст, будет сгенерирован обязательный позиционный аргумент;
- если `default` имеет одно значение, будет сгенерирована опция со значением по умолчанию;
- если `default` - список значений, будет сгеренирован обязательный позиционный аргумент с ограниченным выбором значений.

##### Пример 1
Фрагмент YAML:
```
arguments:
  count:
    default:
    replacer: __COUNT__
    description: number of repetitions. must be int.
  t:
    default: 'Hello World'
    replacer: --TEXT--
    description: phrase to repeat. default is 'Hello World'
```
Результат:
```
$ bashmator use examples/hello_world_1 -h
usage: examples/hello_world_1 [-h] [-t value] count

positional arguments:
  count       number of repetitions. must be int.

options:
  -h, --help  show this help message and exit
  -t value    phrase to repeat. default is 'Hello World'
```
##### Пример 2
Фрагмент YAML:
```
arguments:
  x:
    default:
    replacer: _X_
    description: argument number 1 (int)
  operation:
    default:
      - '+'
      - '-'
      - '*'
      - '/'
    replacer: _OPER_
    description: arithmetic operator 
  y:
    default:
    replacer: _Y_
    description: argument number 2 (int)
```
Результат:
```
$ bashmator use examples/hello_world_2 -h
usage: examples/hello_world_2 [-h] x {+,-,*,/} y

positional arguments:
  x           argument number 1 (int)
  {+,-,*,/}   arithmetic operator
  y           argument number 2 (int)

options:
  -h, --help  show this help message and exit
```
#### Script
В ключе `script` содержется сам код, который будет исполняться при запуске. Чтобы подставить значение аргументов в код, необходимо вставить строку из `replacer` в соответствующих местах. Следите, чтобы значения ключа `replacer` разных аргументов не пересекались, иначе возникнут ошибки подстановки.
##### Пример
Фрагмент YAML:
```
arguments:
  count:
    default:
    replacer: __COUNT__
    description: number of repetitions. must be int.
  t:
    default: 'Hello World'
    replacer: --TEXT--
    description: phrase to repeat. default is 'Hello World'
shell: /bin/bash
script: |- 
  phrase='--TEXT--'
  ans=$(echo $phrase | cut -d ' ' -f 1)
  for i in $(seq 1 __COUNT__); do
    echo '--TEXT--!'
    echo -e "...$ans, $(whoami)\n"
  done
```
Результат запуска в режиме вывода кода без запуска:
```
$ bashmator use -c examples/hello_world_1 10 -t 'NO_WAR'
phrase='NO_WAR'
ans=$(echo $phrase | cut -d ' ' -f 1)
for i in $(seq 1 10); do
  echo 'NO_WAR!'
  echo -e "...$ans, $(whoami)\n"
done
```
#### Items
Если у Вас есть множество скриптов, которые объеденены общими аргументами и предназначением, Вы можете использовать ключи `item_{NUMBER}` чтобы внести их в один YAML-файл.
В таком случае будет сгенерирована опция `--item`, которая позволит вызывать скрипты по номеру. `--item` также поддерживает последовательности и диапазоны, например `--item 1,2,3-6`.
##### Пример
Фрагмент YAML:
```
arguments:
  file:
    default:
    replacer: __PATH__
    description: path to file
shell: /bin/bash
script: # if there is a script here, it will become the default item.
item_1:
  description: get file stat
  script: |-
    echo '-------------'
    echo '- FILE STAT:'
    echo '-------------'
    stat __PATH__
item_2:
  description: get md5 hash
  script: |-
    echo '-------------'
    echo '- MD5 HASH:'
    echo '-------------'
    md5sum __PATH__
item_3:
  description: read file
  script: |-
    echo '-------------'
    echo '- FILE CAT:'
    echo '-------------'
    cat __PATH__
item_4:
  description: encode file to base64
  script: |-
    echo '-------------'
    echo '- BASE64:'
    echo '-------------'
    base64 __PATH__
```
Результат:
```
$ bashmator use examples/hello_world_3 -h            
usage: examples/hello_world_3 [-h] --item NUM file

positional arguments:
  file        path to file

options:
  -h, --help  show this help message and exit

items options:
  --item NUM  item index to execute (can be a sequence, ex: '1,2,4-6')

items list:
   # | description
-----+-----------------------
   1 | get file stat
   2 | get md5 hash
   3 | read file
   4 | encode file to base64
```
