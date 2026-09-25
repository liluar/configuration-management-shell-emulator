# Shell Emulator

эмулятор командной оболочки UNIX-подобной операционной системы

# Вариант

вариант №11

# Этап 1 - REPL

на первом этапе реализованы:

1. консольный интерфейс
2. REPL
3. приглашение к вводу с именем VFS
4. простой разбор команд по пробелам
5. команда-заглушка 'ls'
6. команда-заглушка 'cd'
7. команда 'exit'
8. обработка неизвестных команд

## Этап 2 — Конфигурация

На втором этапе добавлены:

1. параметр `--vfs` для передачи пути к VFS;
2. параметр `--script` для передачи пути к стартовому скрипту;
3. отладочный вывод параметров при запуске;
4. выполнение команд из стартового скрипта;
5. поддержка комментариев в стартовом скрипте;
6. отображение команд стартового скрипта как пользовательского ввода;
7. Bash-скрипты для проверки параметров командной строки.

## Структура проекта

````text
src/
    main.py

tests/
    test_emulator.py

scripts/
    startup.txt

test_scripts/
    test_vfs.sh
    test_script.sh
    test_all.sh

README.md
.gitignore
run.sh
```


# Запуск
Обычный запуск:

```bash
./run.sh
````

или:

```bash
python3 src/main.py
```

Запуск с путем к VFS:

```bash
./run.sh --vfs example_vfs.xml
```

Запуск со стартовым скриптом:

```bash
./run.sh --script scripts/startup.txt
```

Запуск с обоими параметрами:

```bash
./run.sh --vfs example_vfs.xml --script scripts/startup.txt
```

## Параметры командной строки

### `--vfs`

Передает путь к физическому расположению VFS.

Пример:

```bash
python3 src/main.py --vfs example_vfs.xml
```

### `--script`

Передает путь к стартовому скрипту.

Пример:

```bash
python3 src/main.py --script scripts/startup.txt
```

## Стартовый скрипт

Пример файла `scripts/startup.txt`:

```text
# Стартовый скрипт

ls
cd home

# Проверка неизвестной команды
hello
```

Строки, начинающиеся с `#`, считаются комментариями и не выполняются.

## Тестирование

Запуск автоматических тестов:

```bash
python3 -m unittest discover -s tests
```

Запуск системных тестовых скриптов:

```bash
./test_scripts/test_vfs.sh
```

```bash
./test_scripts/test_script.sh
```

```bash
./test_scripts/test_all.sh
```

## Пример работы

```text
VFS: example_vfs.xml
Script: scripts/startup.txt
my_vfs> ls
ls []
my_vfs> cd home
cd ['home']
my_vfs> hello
Unknown command: hello
my_vfs>
```
