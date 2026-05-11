import os
import sys
from typing import Callable, Any, Optional
from lab3.constants import PYGIT_DIR
from lab3.index import add_to_index
from lab3.objects import (
    write_tree,
    create_commit,
    get_current_branch_head,
    update_branch_head,
    get_commit_history,
    read_object,
)

# реестр команд
_COMMANDS: dict[str, Callable[..., Any]] = {}
# Callable[..., Any] - вызов объектов как ф-й,
# принимает люб-е арг-ты и возвращает любые арг-ты


def command(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Декоратор для рег-ии ф-ий команд

    args:
        name: назв-е команды

    returns:
        декорированная ф-я
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        _COMMANDS[name] = func
        return func

    return decorator


def _ensure_pygit_initialized() -> None:
    """
    проверка сущ-ия репозитория pygit

    raises:
        SystemExit: если реп-и не инициализирован
    """
    if not os.path.exists(PYGIT_DIR):
        sys.exit(1)
        # реп-ий не инициализирован


@command("init")
def init() -> None:
    """
    инициализирует новый реп-ий pegit
    создает необх-ую структуру директорий для нового реп-ия
    """
    from lab3.constants import (
        OBJECTS_DIR,
        REFS_DIR,
        HEADS_DIR,
        HEAD_FILE,
        DEFAULT_HEAD_REF,
    )

    directories = [
        os.path.join(PYGIT_DIR, OBJECTS_DIR),
        os.path.join(PYGIT_DIR, REFS_DIR, HEADS_DIR),
    ]

    files = [(os.path.join(PYGIT_DIR, HEAD_FILE), DEFAULT_HEAD_REF)]

    # созд-е дир-ии
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # exist_ok=True - чтобы избежать ошибки, в случае сущ-ия дир-и
        print(f"создана дир-я: {directory}")

    # созд-е файла
    for file_path, content in files:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"создан файл {file_path}")


@command("add")
def add(files: Optional[list[str]] = None) -> None:
    """
    добавляет файл в индекс

    usage:
        pygit add file
    """
    _ensure_pygit_initialized()

    # если аргументы переданы напрямую
    if files is not None:
        # обработка как списка файлов, так и одиночного файла
        files_to_add = files if isinstance(files, list) else [files]
    # если вызвано из командной строки
    elif len(sys.argv) < 3:
        # не хватает аргументов
        sys.exit(1)
    else:
        files_to_add = sys.argv[2:]

    for file_path in files_to_add:
        try:
            sha_hash = add_to_index(file_path)
            print(f"добавлен файл {file_path} {sha_hash}")
            # добавили файл
        except FileNotFoundError:
            sys.exit(1)
            # если файл не найден
        except Exception:
            # не удалось добавить файл
            sys.exit(1)


@command("write-tree")
def write_tree_command() -> None:
    """
    создает tree объект из текущего индекса и выводит его sha

    usage:
        pygit write-tree
    """
    _ensure_pygit_initialized()

    try:
        write_tree()
    except ValueError:
        # обработка ошибок
        sys.exit(1)
    except Exception:
        sys.exit(1)


@command("commit")
def commit_command() -> None:
    """
    создает коммит из текущего индекса

    usage:
        pygit commit -m "сообщение коммита"
    """
    _ensure_pygit_initialized()

    # проверка аргументов
    if len(sys.argv) < 4 or sys.argv[2] != "-m":
        sys.exit(1)

    message = sys.argv[3]
    if not message:
        sys.exit(1)

    try:
        # создание tree из индекса
        tree_sha = write_tree()
        print(f"создан tree: {tree_sha}")

        # получаем родительский комммит
        parent_sha = get_current_branch_head()

        if parent_sha and len(parent_sha) == 40:
            # т.к sha коммита всегда 40
            try:
                obj_type, git_obj = read_object(parent_sha)
                if obj_type != "commit":
                    parent_sha = None
            except Exception:
                parent_sha = None

        if parent_sha:
            print(f"родит-ий коммит: {parent_sha}")
        else:
            print("первый коммит")

        # созд-е коммита
        commit_sha = create_commit(tree_sha, message, parent_sha)
        print(f"создан commit: {commit_sha}")

        # обновление указателя ветка
        update_branch_head(commit_sha)

    # если ошибки
    except ValueError:
        sys.exit(1)
    except Exception:
        sys.exit(1)


@command("log")
def log_command() -> None:
    """
    показывает историю коммитов
    usage:
        pygit log
    """
    _ensure_pygit_initialized()

    #
    current_commit_sha = get_current_branch_head()

    if not current_commit_sha:
        print("нет коммитов")
        return

    try:
        #
        history_iterator = get_commit_history(current_commit_sha)

        # вывод истории
        for commit_sha, commit in history_iterator:
            print(f"коммит {commit_sha}")
            print(f"автор {commit.author}")
            print(f"сообщение {commit.message}")
            print(f"tree {commit.tree_sha}")
            if commit.parent_sha:
                print(f"родитель {commit.parent_sha}")

    except Exception:
        sys.exit(1)


@command("status")
def status() -> None:
    """Показывает статус рабочей дир-ии"""
    _ensure_pygit_initialized()

    from lab3.index import read_index

    index_entries = read_index()

    if not index_entries:
        # индекс пуст
        return

    print("файл готов к коммиту")


def main() -> None:
    """главная точка входа для команды pygit"""
    if len(sys.argv) < 2:
        # недостаточно команд
        sys.exit(1)

    command_name = sys.argv[1]
    if command_name not in _COMMANDS:
        # неизвестная команда
        sys.exit(1)

    # вызов ф-ии команды
    cmd_func = _COMMANDS[command_name]
    cmd_func()


if __name__ == "__main__":
    main()
