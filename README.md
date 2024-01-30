<h1 align="center">
  <img src="https://raw.githubusercontent.com/vinzekatze/bashmator/main/static/bashmator.png" alt="bshm" width="500px">
  <br>
  <a href="https://github.com/vinzekatze/bashmator"><img src="https://img.shields.io/github/release/vinzekatze/bashmator?style=flat-square"></a>
  <a href="http://www.python.org/download/"><img src="https://img.shields.io/badge/python-3.7+-blue.svg?style=flat-square&logo=python"></a>
  <a href="https://github.com/vinzekatze/bashmator"><img src="https://img.shields.io/badge/linux-✔️-green.svg?style=flat-square&logo=linux&logoColor=white"></a>
  <a href="https://github.com/vinzekatze/bashmator"><img src="https://img.shields.io/badge/macos-✔️-green.svg?style=flat-square&logo=macos&logoColor=white"></a>
  <a href="https://github.com/vinzekatze/bashmator"><img src="https://img.shields.io/badge/win-✔️%20%5Bnot%20tested%20enough%5D-orange.svg?style=flat-square&logo=windows"></a>
  </br>
</h1>

__Bashmator__ - консольный менеджер скриптов, основанный на формате YAML.

Основная задача программы - предоставить простую и универсальную систему для хранения, поиска, запуска и логирования большого количества небольших скриптов и однострочников.

# Как это работает

<div align="center">
  <img src="https://raw.githubusercontent.com/vinzekatze/bashmator/main/static/how_it_works.png" alt="bshm" width="1000px">
</div>

Каждый скрипт вносится в YAML файл. В этом файле с помощью ключей задаются аргументы командной строки, параметры подстановки их значений в код скрипта, используемая оболочка, а также информация, по которой этот скрипт можно будет найти.

YAML файлы хранятся в папке (библиотеке). Для каждой библиотеки bashmator собирает необходимую информацию о доступных скриптах и поддерживает её актуальность, чтобы обеспечить возможность быстрого поиска.

# Установка

```
pip install bashmator
```
В комадной строке станет доступен под короткими названиям `bashmator` и `bshm`.

Далее рекомендуется добавить оболочку и пересканить библиотеку:
```
bashmator shell add /usr/bin/bash
bashmator library scan -f
```

# Использование

<table>
<tr>
<td>

<details>
  <summary><code>bashmator --help</code></summary>

```
usage: bashmator [-h] [-v] {use,search,set,shell,library} ...

                                        __     _  
    _           _             _         \ \   | | 
   | |_ ___ ___| |_ _____ ___| |_ ___ ___\ \ / __)
   | . | .'|_ -|   |     | .'|  _| . |  _|> >\__ \
   |___|__,|___|_|_|_|_|_|__,|_| |___|_| / / (   /
    by vinzekatze                       /_/   |_| 
    version 1.0.0
    
.................................................................

used library: default

commands:
  {use,search,set,shell,library}
    use                 use script
    search              search script at library by keywords
    set                 settings
    shell               shells management
    library             libraries management

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

</details>

<details>
  <summary><code>bashmator use --help</code></summary>
  
```
usage: bashmator use [-l] [-o FILE] [-i] [-c] [-h] script ...

Runs a script from the library by it's name.

.................................................................

positional arguments:
  script               script name and it's options

script launch options:
  -l, --log-headers    print log headers when executing script
  -o FILE, --out FILE  log execution process to file (append
                       mod)

code printing options:
  -i, --install        show script's installation information
  -c, --code           print script without execution

other options:
  -h, --help           show this help message and exit
```
  
</details>

<details>
  <summary><code>bashmator search --help</code></summary>
  
```
usage: bashmator search [-i] [-A] [-D] [-S] [-h] [keyword ...]

Search for a script in the used library. By default, the search
is performed by tags and script names.

.................................................................

positional arguments:
  keyword            keywords for search

search options:
  -i, --ignore-case  ignore case distinctions
  -A, --author       add search by author
  -D, --description  add search by script description
  -S, --shell        add search by shell

other options:
  -h, --help         show this help message and exit
```
  
</details>

<details>
  <summary><code>bashmator set --help</code></summary>
  
```
usage: bashmator set [--auto-scan {true,false}]
                     [--color {true,false}] [-h]

Current setings:
  auto-scan True
  color True

.................................................................

settings:
  --auto-scan {true,false}
                        automatically detect changes in the
                        used library
  --color {true,false}  use color on the command line

other options:
  -h, --help            show this help message and exit
```

</details>

<details>
  <summary><code>bashmator shell --help</code></summary>
  
```
usage: bashmator shell [-h] {add,delete} ...

commands:
  {add,delete}
    add         add a new shell to the known list
    delete      remove a shell from the known list

options:
  -h, --help    show this help message and exit

.................................................................

known shells:
 name    | path             | popen arguments   | encoding
---------+------------------+-------------------+------------
 bash    | /usr/bin/bash    | ['-c']            | utf-8
```

</details>

<details>
  <summary><code>bashmator shell add --help</code></summary>

```
usage: bashmator shell add [--name NAME] [--encoding CODE]
                           [--popen-args LIST] [-h]
                           path

Add a new shell to the known list.

.................................................................

positional arguments:
  path               full path to the shell (for example:
                     /usr/bin/bash)

options:
  --name NAME        specify shell name (default: base name)
  --encoding CODE    shell encoding (used when logging;
                     default: 'utf-8')
  --popen-args LIST  shell arguments for the subprocess.Popen
                     function (default: '["-c"]')
  -h, --help         show this help message and exit
```

</details>

<details>
  <summary><code>bashmator shell delete --help</code></summary>

```
usage: bashmator shell delete [-h] name [name ...]

Remove a shell from the known list. Use 'delete ALL' to clear.

.................................................................

positional arguments:
  name        shell name (can be multiple)

options:
  -h, --help  show this help message and exit
```

</details>

<details>
  <summary><code>bashmator library --help</code></summary>

```
usage: bashmator library [-h] {add,delete,scan,use} ...

commands:
  {add,delete,scan,use}
    add                 add a new library to the known list
    delete              remove library from the known list
    scan                detect changes in the used library
    use                 select library for use

options:
  -h, --help            show this help message and exit

.................................................................

known libraries:
 name    | status   | path
---------+----------+----------------------------------
 default | IN USE   | /home/vinzekatze/workspace/apps/
         |          | bashmator/library
```

</details>

<details>
  <summary><code>bashmator library add --help</code></summary>

```
usage: bashmator library add [--name NAME] [-h] path

Add a new library to the known list.

.................................................................

positional arguments:
  path         path to main library directory

options:
  --name NAME  specify library name (default: folder name)
  -h, --help   show this help message and exit
```

</details>

<details>
  <summary><code>bashmator library delete --help</code></summary>

```
usage: bashmator library delete [-h] name [name ...]

Remove a library from the known list. Type 'delete ALL' to clear.

.................................................................

positional arguments:
  name        library name (can be multiple)

options:
  -h, --help  show this help message and exit
```

</details>

<details>
  <summary><code>bashmator library scan --help</code></summary>

```
usage: bashmator library scan [-f] [-h]

Scans the directory of the used library for changes in it's
contents.

.................................................................

options:
  -f, --forced  reset the saved information and rescan the
                library
  -h, --help    show this help message and exit
```

</details>

<details>
  <summary><code>bashmator library use --help</code></summary>

```
usage: bashmator library use [-h] name

Select the library to use from the known list.

.................................................................

positional arguments:
  name        library name

options:
  -h, --help  show this help message and exit
```

</details>

</td>
</tr>
</table>

# Оболочки
Не смотря на название, bashmator способен работать не только с bash. Ниже представлены примеры команд добавления некоторых других оболочек, интерпритаторов и программ:

<details>
  <summary><b>Linux</b></summary>

```
bashmator shell add /usr/bin/zsh
bashmator shell add /usr/bin/python3
bashmator shell add /usr/bin/node --popen-args '["-e"]'
bashmator shell add /usr/bin/msfconsole --popen-args '["-q", "-x"]'
```

</details>

<details>
  <summary><b>Windows</b></summary>

>⚠️ _Для powershell и cmd важно указать кодировку, что бы логирование с помощью `use -o <file> ...` работало корректно_

```
bashmator shell add C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe --popen-args "['-Command']" --encoding 'cp866' --name powershell
bashmator shell add C:\Windows\System32\cmd.exe --popen-args "['/C']" --encoding 'cp866' --name cmd
bashmator shell add C:\...path\to\python\...\python.exe --name python3
```

</details>

Потенциально bashmator может работать с любыми интерпритаторами, способными принимать последовательность команд из аргументов командной строки. Флаг, отвечающий за прием последовательности команд, должен всегда располагаться в конце списка, передаваемого в аргументе `--popen-args`.

# Создание библиотек
> _Рекомендуется создавать собственные библиотеки, а не добавлять свои скрипты в библиотеку по умолчанию._

Библиотекой будет считаться любой каталог, содержащий следующие подкаталоги:

- `files` - каталог для файлов, используемых в скриптами. Полезен для повышения совместимости.

- `modules` - каталог для YAML файлов.

Данные подкаталоги могут иметь собственные подкаталоги - bashmator будет их учитывать в работе.

Добавить библиотеку в bashmator и выбрать её для использования:

```
bashmator library add <path to library>
bashmator library use <library name>
```

# Создание YAML модулей
Минимальная структура, необходимая для работы:

```yaml
shell: <SHELL NAME>
script: |-
  <YOUR CODE>
```
<details>
  <summary>Общая структура</summary>

```yaml
author: <NAME>
description: <TEXT>
tags:
  - <TAG1>
  - <TAG2>
  - ...
install: <INSTALLATION INFORMATION>

arguments:
  <ARG NAME>:
    default: <EMPTY, STRING OR LIST>
    description: <TEXT>
    metavar: <STRING>
    multiple: <TRUE | FALSE>
    replacer: <VALUE REPLACER>
    regex: <REGEX STRING>
  <OTHER ARG NAME>:
    ...
  ...

mode:
  readfile:
    - <ARG NAME>
    ...
  replace:
    <ARG NAME>:
      <VALUE TO REPLACE>: <REPLACEMENT>
  loop: <ARG NAME>
  format:
    <ARG NAME>: <.format() TEMPLATE>
    <OTHER ARG>: ...
    ...
  join:
    <ARG NAME>: <DELIMITER>
    <OTHER ARG>: ...
    ...
  pformat:
    <ARG NAME>: <.format() TEMPLATE>
    <OTHER ARG>: ...
    ...

shell: <MAIN SHELL SHORT NAME OR PATH>
script: |- 
  <YOUR MAIN CODE>

file_<NUMBER>:
  path: <SHORT PATH TO FILE AT LIBRARY/FILES DIRECTORY>
  replacer: <FULL PATH REPLACER>
  description: <TEXT>
file_<OTHER NUMBER>:
  ...
...

item_<NUMBER>:
  shell: <OTHER SHELL SHORT NAME OR PATH>
  description: <TEXT>
  mode: 
    <SAME STRUCTURE AS AT MAIN>
  script: |-
    <YOUR OTHER CODE>
item_<OTHER NUMBER>:
  ...
...
```

</details>

## Описание ключей:

<details>
  <summary><b>author</b></summary>

Содержит имя автора модуля, используется для поиска и удовлетворения чувства собственной значимости😅. Пример:

```yaml
author: vinzekatze
```

</details>

<details>
  <summary><b>description</b></summary>

Содержит общую информацию о работе скрипта, которая будет выведена при вызове помощи `use <script name> -h` или `use <script name> --help`.

Для большего удобства рекомендуется использовать `|-`. Пример:

```yaml
description: |-
  Набор однострочников для получение базовой DNS информации
```

</details>

<details>
  <summary><b>tags</b></summary>

Содержит список тегов, по которым можно будет найти скрипт с помощью команды `search`. Пример:

```yaml
tags:
  - 53
  - dns
  - recon
```

</details>

<details>
  <summary><b>install</b></summary>

Содержит информацию о ПО, которое необходимо установить для правильной работы скрипта. Данная информация будет отображена при вызове скрипта с помощью команды `use -i <script name>`.

Если есть возможность, рекомендуется писать сразу последовательность команд для установки, либо явно указывать, что установка чего-либо не требуется. Пример:

```yaml
install: |-
  sudo apt update -y && sudo apt install dnsrecon -y
```

</details>

<details>
  <summary><b>arguments</b></summary>

Содержит имена аргументов и их параметры. На основе заданных тут данных bashmator создает CLI для скрипта.

Рекомендуется использовать полные названия для позиционных аргументов, и однобуквенные для опций.

`replacer` по умолчанию: `#[ARGUMENT NAME]#`

Общий вид:

```yaml
arguments:
  n:
    default: 42
    metavar: NUM
    regex: \d+
  arg:
    replacer: __B__
    multiple: true
    description: bla bla bla
    
```

Ключи аргументов:

<table>
<tr>
<td>

<details>
  <summary><b>default</b></summary>

Определяет значение аргумента по умолчанию, либо список возможных значений.

Если `default` пуст, либо отсутствует, аргумент будет обязательным.

Если `default` содержит строковое или числовое значение, то аргумент будет опцией, которая по умолчанию будет подставлять указанное значение. Пример:

```yaml
  a:
    default: 53
```

Если `default` - список из одного пустого значения, то аргумент будет опцией с пустым значением по умолчанию. Пример:

```yaml
  a:
    default:
      -
```

Если `default` содержит список из двух элементов, то аргумент будет флагом, подставляющим первое значение когда отсутствует в команде, а второе - когда присутствует. Пример:

```yaml
  a:
    default:
      - https://
      - http://
```

Если `default` содержит список из более чем трех элементов, аргумент сможет принимать только значения из списка. Если при этом первый элемент пуст, то аргумент будет обязательным, если же нет - первое значение из списка будет использоваться по умолчанию. Пример:

```yaml
  arg:
    default:
      -
      - one
      - two
```

</details>

<details>
  <summary><b>description</b></summary>

Содержит описание назначения аргумента, которое будет выведено при вызове помощи `use <script name> -h` или `use <script name> --help`. Пример:

```yaml
  arg:
    description: очень важный аргумент
```

</details>

<details>
  <summary><b>metavar</b></summary>

Косметический ключ, позволяющий задать свое метазначение для опций. На позиционные аргументы не влияет.

Пример:
```yaml
arg:
  default: 42
  metavar: MY_METAVAR
```

Отображение:
```
usage: test [--arg MY_METAVAR] [-h]

options:
  --arg MY_METAVAR  (default: '42')
  -h, --help        show this help message and exit

```

</details>

<details>
  <summary><b>multiple</b></summary>

Определяет, может ли аргумент принимать множественные значения, или нет. По умолчанию `false`. Пример:

```yaml
  arg:
    multiple: true
```

</details>

<details>
  <summary><b>replacer</b></summary>

Содержит строку, котороя будет заменятья в коде скрипта (ключ `script`) на значение аргумента. Не самое элегантное решение, но позволяет творить интересные трюки в комбинации с `mode: format`.

Реплейсеры в коде скрипта заменяются в том порядке, в каком описаны ключи в `arguments`. После аргументов в код подставляются значения `file_[NUMBER]`, если они есть.

Если ключ отсутвует либо пуст, то реплейсер принимает значение `#[ARGUMENT NAME]#`

Пример реплейсеров и скрипта:

```yaml
arguments:
  arg:
    replacer: -+PLACEHOLDER+-
script: >-
  cat -+PLACEHOLDER+- | ncat 127.0.0.1 9090
```

</details>

<details>
  <summary><b>regex</b></summary>

Позволяет задать регулярное выражение, с помощью которого будут проверяться значения аргумента. Не прошедие проверку значения будут вызывать ошибку и не позволять запустить скрипт. Для проверки используется функция `re.fullmatch`

Пример:

```yaml
arguments:
  ip:
    regex: >-
      ((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3,3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])

script: 'echo #ip# is ok'
```

Реакция скрипта на ввод:

```
$ bashmator use ip 77.88.55.60
77.88.55.60 is ok

$ bashmator use ip 77.88.55.601
ip: error: argument 'ip': invalid value '77.88.55.601'
```

</details>

</td>
</tr>
</table>

</details>

<details>
  <summary><b>mode</b></summary>

Используется для модификации значений аргументов. Общий вид:

```yaml
mode:
  readfile:
    - arg2
  replace:
    arg3:
      v1: value1
      v2: value2
  loop: arg1
  format: 
    arg2: '{0!r}'
  join:
    arg2: ','
    arg3: ';'
  pformat:
    arg2: ' [ {} ] '
```

Ключи mode:

<table>
<tr>
<td>

<details>
  <summary><b>readfile</b></summary>

Содержит список имен аргументов, которые будут интерпритированы как имена файлов.

Данные файлы будут читаться построчно, а считанные строки будут подставляться в скрипт на место реплейсера.

Пример:

```yaml
shell: bash
arguments:
  arg1:
    description: test
mode:
  readfile:
    - arg1
script: >-
  echo #arg1#
```

Содержимое файла `some_file.txt`:

```
one
two
three
```

Если запустить скрипт с аргументом `./some_file.txt`, то для исполнения будет сформирован следующий код:

```bash
echo one two three
```

</details>

<details>
  <summary><b>replace</b></summary>

Подзволяет заменять значения аргументов. Содержит в себе имена аргументов в качестве ключей, которые в свою очередь содержат замены в виде `ключ:значение`.

Пример:

```yaml
shell: bash
arguments:
  arg1:
    default:
      - A
      - B
      - C
mode:
  replace:
    arg1:
      A: One
      B: Two
script: >-
  echo #arg1#
```

В данном примере, когда на вход скрпта в аргумент `--arg1` будет подаваться значение `A`, в скрипт будет подставлено значение `One`, а когда `B` - `Two`. Значение `C` заменено не будет и попадет в скрипт напрямую.

</details>

<details>
  <summary><b>loop</b></summary>

Если содержит имя множественного аргумента (`multiply: true`), то скрипт будет запускаться отдельно для каждого его значения. По умолчанию этого не происходит.

Пример:

```yaml
shell: bash
arguments:
  arg1:
    multiple: true
mode:
  loop: arg1
script: >-
  echo -n #arg1#; echo ' end'
```

Результат выполнения скрипта c аргументами `1 2 3 4 5`:

```
1 end
2 end
3 end
4 end
5 end
```

</details>

<details>
  <summary><b>format</b></summary>

Содержит имена аргументов в качестве ключей и шаблоны python функции `.format()` в качестве значений. Если значение аргумента пусто, то форматирование не происходит и соответсвующий реплейсер удаляется из скрипта.

Для множественных аргументов форматирование производится для каждого из значений отдельно. Операция `join` всегда происходит после.

Обычно этот ключ применяется для правильной подстановки неоднозначных значений с использованием шаблона `{0!r}`, однако в комбинации с пустыми по умолчанию аргументами может позволить опционально вставлять в скрипт дополнительные куски.

Пример:

```yaml
shell: bash
arguments:
  arg1:
    default:
      -
  arg2:
    multiple: true
mode:
  format:
    arg1: >-
      | tee {0!r}
    arg2: >-
      {0!r}
script: >-
  echo #arg1# #arg2#
```

Если запустить скрипт с аргументами `a d c r t`, для исполнения будет сформирован следующий код:

```bash
echo 'a' 'd' 'c' 'r' 't' 
```

Если с аргументами `--arg1 ./file.txt a d c r t`:

```bash
echo 'a' 'd' 'c' 'r' 't' | tee './test.txt'
```

</details>

<details>
  <summary><b>join</b></summary>

Содержит имена множественных аргументов (`multiply: true`) в качестве ключей и строки-разделители для объединения в качестве значений. По умолчанию объединение значений множественных аргументов происходит через пробел.

Пример:

```yaml
  join:
    arg1: ','
```

В этом случае значения множественного аргумента `arg1` будут подставлены в скрипт в виде следующей строки:

```
val1,val2,val3,val4
```

</details>

<details>
  <summary><b>pformat</b></summary>

Тоже что и `format`, но отрабатывает после всех других модов. Полезен при обработке множественных аргументов без режима `loop`, позволяя дополнительно форматировать собранную с помощью `format` и `join` строку перед вставкой в код скрипта.

</details>

</td>
</tr>
</table>

</details>

<details>
  <summary><b>shell</b></summary>

В данном ключе указывается короткое имя оболочки, используемой для запуска скрипта, либо путь до неё.

В целях улучшения совместимости рекомендуется добавлять оболочки в bashmator с помощью `bashmator shell add`, а в ключе `shell` указывать их короткие имена.

Данный ключ обязателен, если отсутствуют ключи `item_[NUMBER]`, либо для каждого из них не заданы `shell` отдельно.

Пример:

```yaml
shell: bash
```

Это тоже сработает, но так делать не рекомендуется:

```yaml
shell: /usr/bin/bash
```

</details>

<details>
  <summary><b>script</b></summary>

Содержит непосредственно код скрипта, который будет исполняться. _Не забудьте вставить реплейсеры аргументов!_

Чтобы записывать многострочные скрипты используйте `|-`. Чтобы записать однострочник, но в коде использовать перенос строки, используйте `>-`

Пример 1:

```yaml
script: |-
  ls -la
  rm -r ./
```

Пример 2:

```yaml
script: >-
  ls -la;
  rm -r ./
```

</details>

<details>
  <summary><b>file_[NUMBER]</b></summary>

Используется для подстановки полных путей файлов из директории `files` библиотеки.

`replacer` по умолчанию: `#file_[NUMBER]#`

Общий вид:

```yaml
file_1:
  description: My Wordlist
  path: dicts/my_wordlist.txt
file_2:
  description: My Big Script
  path: scripts/big_script.sh
  replacer: __BIG_SCRIPT__
```

Ключи file_\[NUMBER\]:

<table>
<tr>
<td>

<details>
  <summary><b>path</b></summary>

>⚠️ __Обязательный ключ__

Содержит путь до файла в библиотеке относительно директории `files`. Используйте `/` для перехода в директорию независимо от системы (windows, linux). Пример:

```yaml
file_1:
  path: lorem/lorem.txt
```
Так же можно обращаться к файлам по полному пути и использовать возвраты в родительскую директорию, но этого делать не рекомендуется. Скорее всего я закрою эту возможность спустя какое-то время, так как это больше баг, чем фитча 🥲.

</details>

<details>
  <summary><b>replacer</b></summary>

Работает аналогично ключу `replacer` для `arguments`, но не подвергается форматированию.

</details>

<details>
  <summary><b>description</b></summary>

Содержит краткое описание файла, которое будет выведено при вызове помощи `use <script name> -h` или `use <script name> --help`. Пример:

</details>

</td>
</tr>
</table>

</details>

<details>
  <summary><b>item_[NUMBER]</b></summary>

Используется для добавления дополнительных скриптов в один модуль. Это удобно, когда разные скрипты принимают на вход одни и те же аргументы и объеденены общим смыслом.

Если существуют `item`, то в CLI добавляется опция `--item`, которая позволяет вызывать подскрипты по номеру. Для массового запуска можно использовать последовательности: `--item 1,2,4-6`.

Если вместе с `item` существует основной `script`, то ему будет присвоен номер `0`. Запускаться по умолчанию будет только он.

Общий вид:

```yaml
item_1:
  description: script 1
  shell: python3
  script: |-
    print(1+2)
item_2:
  description: script 2
  mode:
    loop: arg1
  script: echo _ARG1_
```

Ключи item_\[NUMBER\]:

<table>
<tr>
<td>

<details>
  <summary><b>shell</b></summary>

Работает аналогично ключу `shell` в корне. Если ключ отсутствует, item будет использовать значение главного `shell`.

</details>

<details>
  <summary><b>mode</b></summary>

Работает аналогично ключу `mode` в корне. Используется для изменения главных параметров форматирования для `item`. 

Чтобы отметить действие `loop` главного `mode`, оставьте ключ пустым. Например:

```yaml
item_2:
  script: echo _A_
  mode:
    loop:
```

</details>

<details>
  <summary><b>description</b></summary>

Содержит краткое описание назначения `item`, которое будет выведено при вызове помощи `use <script name> -h` или `use <script name> --help`.

</details>

<details>
  <summary><b>script</b></summary>

>⚠️ __Обязательный ключ__

Работает аналогично главному `script`.

</details>

</td>
</tr>
</table>

</details>


Примеры YAML модулей представлены во [встроенной библиотеке](https://github.com/vinzekatze/bashmator/tree/main/bshm/library/modules/examples):

```
$ bashmator search examples
Search results:

 script name                  | status   | tags
------------------------------+----------+-----------------------------
 examples/args/choice         | OK       | help, manual, arguments
 examples/args/choice_default | OK       | help, manual, arguments
 examples/args/default        | OK       | help, manual, arguments
 examples/args/default_empty  | OK       | help, manual, arguments
 examples/args/flag           | OK       | help, manual, arguments
 examples/args/metavar        | OK       | help, manual, arguments
 examples/args/multiple       | OK       | help, manual, arguments
 examples/args/regex          | OK       | help, manual, arguments
 examples/args/replacer       | OK       | help, manual, arguments
 examples/args/simple         | OK       | help, manual, arguments
 examples/files/replacer      | OK       | help, manual, files
 examples/files/simple        | OK       | help, manual, files
 examples/items/default       | OK       | help, manual, items
 examples/items/mode          | OK       | help, manual, items
 examples/items/shell         | OK       | help, manual, items
 examples/items/simple        | OK       | help, manual, items
 examples/minimal             | OK       |
 examples/mode/format         | OK       | help, manual, mode
 examples/mode/format_empty   | OK       | help, manual, mode
 examples/mode/join           | OK       | help, manual, mode
 examples/mode/loop           | OK       | help, manual, mode
 examples/mode/pformat        | OK       | help, manual, mode
 examples/mode/readfile       | OK       | help, manual, mode
 examples/mode/replace        | OK       | help, manual, mode
 examples/simple              | OK       | help, manual, informational
```

# Пример работы
Ниже представлен пример запуска скрипта [examples/args/simple](https://github.com/vinzekatze/bashmator/blob/main/bshm/library/modules/examples/simple.yaml):

<details>
  <summary>Аргументы командной строки, сгенерированные из YAML</summary>
  
```console
$ bashmator use examples/args/simple -h
usage: examples/args/simple [-h] arg

Example of a simple required argument

.................................................................

positional arguments:
  arg         random string

options:
  -h, --help  show this help message and exit

Shell:   bash 
Author:  demo 
Tags:    help, manual, arguments      
```
  
</details>

<details>
  <summary>Запуск скрипта с включенной опцией логирования</summary>
  
```console
$ bashmator use -o example.log examples/args/simple blablabla
Input: blablabla
```

</details>

<details>
  <summary>Содержимое записанного файла <code>example.log</code></summary>

```console
$ cat example.log 
+-------------------------------------------------------------------------------
+ Generated by bashmator 1.1.1
+-------------------------------------------------------------------------------
+ Script name:               examples/args/simple (0)
+ Start time:                2023-06-29 16:11:25 (UTC)
+ Shell:                     /usr/bin/bash -c
+-------------------------------------------------------------------------------
+ Running code
+-------------------------------------------------------------------------------

echo 'Input: blablabla'

+-------------------------------------------------------------------------------
+ Log
+-------------------------------------------------------------------------------

Input: blablabla

+-------------------------------------------------------------------------------
+ End time:                  2023-06-29 16:11:25 (UTC)
+-------------------------------------------------------------------------------

```

</details>

# Доступные библиотеки

Потихоньку веду коллекцию сомнительных скриптов для Kali-Linux [ktz-autokali](https://github.com/vinzekatze/ktz-autokali)