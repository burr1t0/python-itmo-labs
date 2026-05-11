# Лаб 3. PyGit — собственная реализация Git

Упрощённый аналог системы контроля версий Git, написанный на Python с нуля.

## Файлы

- `pygit_commands.py` — CLI-команды (init, add, commit, log и др.)
- `objects.py` — объекты репозитория (blob, tree, commit)
- `index.py` — индекс (staging area)
- `constants.py` — константы

## Использование

```bash
python pygit_commands.py init
python pygit_commands.py add <file>
python pygit_commands.py commit -m "message"
python pygit_commands.py log
```

## Технологии

Python 3
