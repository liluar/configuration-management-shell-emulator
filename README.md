# shell emulator
эмулятор командной оболочки UNIX-подобной операционной системы

# вариант
вариант №11

# этап 1
на первом этапе реализованы:
1) консольный интерфейс
2) REPL
3) приглашение к вводу с именем VFS
4) простой разбор команд по пробелам
5) команда-заглушка 'ls'
6) команда-заглушка 'cd'
7) команда 'exit'
8) обработка неизвестных команд

# запуск
первый способ:
```bash
./run.sh
```
второй способ:
```bash
python3 src/main.py
```
# пример работы
```text
my_vfs> ls
ls []

my_vfs> ls home
ls ['home']

my_vfs> cd
cd []
my_vfs> cd home
cd ['home']

my_vfs> hello
Unknown command: hello

my_vfs> exit
```