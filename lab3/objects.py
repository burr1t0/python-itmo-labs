import abc

# для созд-я абстрактных классов
import hashlib
import time

# для работы с хешем
import zlib

# сжатие и распаковка данных
import os

# для работы с файлами
from typing import Optional, Generator, Iterator

# для неопределенных типов данных

from lab3.constants import (
    BLOB_TYPE,
    TREE_TYPE,
    COMMIT_TYPE,
    ENCODING,
    PYGIT_DIR,
    OBJECTS_DIR,
    DIRECTORY_MODE,
    DEFAULT_AUTHOR,
)


class GitObject(abc.ABC):
    """Класс для всех объектов гита"""
    parent_sha: Optional[str] = None

    @abc.abstractmethod
    # Делает метод абстрактным
    def serialize(self) -> bytes:
        """
        Сериализует (преобразует) объекты в байты для хранения

        Returns:
            Сериализованные объектные данные в виде байтов
        """
        pass

    @abc.abstractmethod
    def deserialize(self, data: bytes) -> None:
        """
        Десериализуем (восстанавливает) объект из байтов

        Args:
            Байты для десериализации в объекты
        """
        pass


class Blob(GitObject):
    """Двоичный объект с содержимым файла"""

    def __init__(self, data: bytes = b"") -> None:
        """
        Инициализация двоичного объекта данными

        args:
            Содержимое файла в байтах, по умолчанию пустые байты

        """
        self.data: bytes = data

    def serialize(self) -> bytes:
        """
        Возвращает данные большого двоичного объекта

        Returns:
            Данные большого двоичного объекта в виде байтов
        """
        return self.data

    def deserialize(self, data: bytes) -> None:
        """
        Задает данные двоичного объекта из байтов

        Args:
            Данные для десериализации
        """
        self.data = data


class TreeEntry:
    """Запись в виде дерева"""

    def __init__(self, mode: str, path: str, sha: str) -> None:
        """
        Инициализация записи в дереве

        args:
            режим: Режим файла/разрешения (например файл с прав-ми 644)
            путь: путь к файлу/каталогу
            sha: SHA-1 хэш объекта (связывает запись с реальным содержимым)
        """
        self.mode: str = mode
        self.path: str = path
        self.sha: str = sha


class Tree(GitObject):
    """Дерево представляющее структуру каталогов"""

    def __init__(self) -> None:
        """Инициализация пустого дерева"""
        self.entries: list[TreeEntry] = []

    def add_entry(self, mode: str, path: str, sha: str) -> None:
        """
        Добавление в дерево

        args:
            режим: Режим файла
            путь: Путь к файлу/каталогу
            sha: SHA-1 хэш объекта
        """
        self.entries.append(TreeEntry(mode, path, sha))

    def serialize(self) -> bytes:
        """
        Преобразование дерево в байты в формате Git

        Returns:
            Сериализованные данные (в виде дерева) в виде байтов
        """
        serialized_entries: list[bytes] = []

        # Сортировка по пути для обеспечения согласованного порядка
        sorted_entries = sorted(self.entries, key=lambda x: x.path)

        for entry in sorted_entries:
            # Формат: путь к режиму
            entry_bytes = f"{entry.mode} {entry.path}\0".encode(ENCODING)

            # Преобразует hex строку в бинарную
            sha_bytes = bytes.fromhex(entry.sha)
            serialized_entries.append(entry_bytes + sha_bytes)

        return b"".join(serialized_entries)
        # Преобразование сериализованных отсортированных данных в одну строку

    def deserialize(self, data: bytes) -> None:
        """
        Десериализует дерево из байтов

        args:
            байты для десериализации
        """
        self.entries = []
        pos = 0

        while pos < len(data):
            null_pos = data.find(b"\0", pos)
            # поиск нулевого байта
            if null_pos == -1:
                break

            mode_path = data[pos:null_pos].decode(ENCODING)
            mode, path = mode_path.split(" ", 1)
            # разрешения и путь к файлу

            sha_start = null_pos + 1
            # Позиция после первого байта
            sha_end = sha_start + 20
            # 20, т.к SHA всегда 20 байт
            sha_bytes = data[sha_start:sha_end]
            sha = sha_bytes.hex()
            # преобразование в hex строку

            self.entries.append(TreeEntry(mode, path, sha))
            # Переход к след-й записи
            pos = sha_end


class Commit(GitObject):
    """Фиксирует объект (делает снимок текущего сост-я),
    сохраняя историю изменений"""

    def __init__(
        self,
        tree_sha: str = "",
        parent_sha: Optional[str] = None,
        author: str = "",
        message: str = "",
    ) -> None:
        """
        Инициализация объекта для фиксации

        args:
            three_sha: SHA-1 хэш объекта дерева
            parent_sha: SHA-1 хэш родит-го коммита
            (отсутствует при нач-й фикс-ии)
            author: информация об авторе данной фикс-ии
            message: сообщение о фик-ии
        """
        self.tree_sha: str = tree_sha
        self.parent_sha: Optional[str] = parent_sha
        self.author: str = author
        self.message: str = message

    def serialize(self) -> bytes:
        """
        Преобразует фикс-ю в байты в формате Git

        Returns:
            Сериализованные данные в виде байтов
        """
        lines = []
        lines.append(f"tree {self.tree_sha}")

        if self.parent_sha:
            lines.append(f"parent {self.parent_sha}")

        lines.append(f"author {self.author}")
        lines.append("")
        lines.append(self.message)

        # удаляю пустые строки, оставляя только непустые
        return "\n".join([line for line in lines if line]).encode(ENCODING)

    def deserialize(self, data: bytes) -> None:
        """
        Десериализует коммит из байтов

        args:
            data: байты для десериализации
        """
        content = data.decode(ENCODING)
        lines = content.split("\n")

        self.tree_sha = ""
        self.parent_sha = None
        self.author = ""
        self.message = ""

        for i, line in enumerate(lines):
            # startswith - сравнивает начало строки с введенной строкой
            if line.startswith("tree "):
                self.tree_sha = line[5:]
            elif line.startswith("parent "):
                self.parent_sha = line[7:]
            elif line.startswith("author "):
                self.author = line[7:]
            elif line == "":
                if i + 1 < len(lines):
                    # добавление сообщения о фикс-ии и выходит
                    self.message = "\n".join(lines[i + 1:])
                break
        # если не нашлась пустая строка
        if not self.message and self.author:
            # поиск конца "author"
            for i, line in enumerate(lines):
                if line.startswith("author "):
                    if i + 1 < len(lines):
                        self.message = "\n".join(lines[i + 1:])
                    break


def hash_object(data: bytes, obj_type: str) -> str:
    """
    Хеширует и сохраняет Git объект

    args:
        data: данные объекты для хеширования
        obj_type: тип объекта (blob, tree, commit)

    returns:
        SHA-1 хеш объекта

    raises:
        valueError: в случае, если тип объекта неверный
    """
    if obj_type not in (BLOB_TYPE, TREE_TYPE, COMMIT_TYPE):
        raise ValueError(f"неверный тип объекта: {obj_type}")

    # создает заголовок: "тип размер\0"
    header = f"{obj_type} {len(data)}\0".encode(ENCODING)
    full_data = header + data

    # вычисление SHA-1 хеш
    sha_hash = hashlib.sha1(full_data).hexdigest()

    # создание пути к дир-ии объектов
    objects_dir = os.path.join(PYGIT_DIR, OBJECTS_DIR)
    obj_dir = os.path.join(objects_dir, sha_hash[:2])
    # по первым 2-м сим-ам находит нужную папку
    obj_path = os.path.join(obj_dir, sha_hash[2:])

    # создание дир-ии в случае ее отсутствия
    os.makedirs(obj_dir, exist_ok=True)

    # сжатие с помощью zlib и сохр-е
    compressed_data = zlib.compress(full_data)
    with open(obj_path, "wb") as f:
        f.write(compressed_data)

    return sha_hash


def read_object(sha: str) -> tuple[str, GitObject]:
    """
    Чтение и распаковка Git объекта

    args:
        sha: SHA-1 хеш объекта для чтения

    returns:
        кортеж (десериализованный объект, тип объекта)

    raises:
        fileNotFoundError: если объект не сущ-т
        valueError: если тип объекта неизвестен
    """
    # формирование пути к файлу объекта
    obj_path = os.path.join(PYGIT_DIR, OBJECTS_DIR, sha[:2], sha[2:])

    with open(obj_path, "rb") as f:
        compressed_data = f.read()

    # распаковка данных
    full_data = zlib.decompress(compressed_data)

    # извлечение заголовка, чтобы получить тип и размер
    null_pos = full_data.find(b"\0")
    if null_pos == -1:
        raise ValueError("неверный формат объекта")

    header = full_data[:null_pos].decode(ENCODING)
    obj_type, size_str = header.split(" ", 1)

    # извлечение данных объекта
    obj_data = full_data[null_pos + 1:]

    # создание соотв-го типа объекта
    git_obj: GitObject
    if obj_type == BLOB_TYPE:
        git_obj = Blob()
    elif obj_type == TREE_TYPE:
        git_obj = Tree()
    elif obj_type == COMMIT_TYPE:
        git_obj = Commit()
    else:
        raise ValueError(f"неизвестный тип объекта: {obj_type}")

    # десериализация данных в объект
    git_obj.deserialize(obj_data)
    return obj_type, git_obj


def _build_tree_generator(
    index_dict: dict[str, tuple[str, str]],
) -> Generator[tuple[str, Tree], None, None]:
    """
    генератор для рекурсивного построения дерева

    args:
        index_dict: словарь индекса {path: (sha, mode)}

    yields:
        кортежи (path, tree_object) для каждой дир-ии
    """
    # группировка файлов по дир-ям
    dir_structure: dict[str, dict[str, tuple[str, str]]] = {}

    for file_path, file_info in index_dict.items():
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)

        if dir_name not in dir_structure:
            dir_structure[dir_name] = {}
        dir_structure[dir_name][base_name] = file_info

    processed_dirs = set()

    # начинаем с корневой директории
    stack = [""]
    trees: dict[str, str] = {}

    while stack:
        dir_path = stack.pop()
        if dir_path in processed_dirs:
            continue

        tree = Tree()

        # обработка файлов в текущей директории
        if dir_path in dir_structure:
            for file_name, (file_sha, file_mode) in dir_structure[
                dir_path
            ].items():
                tree.add_entry(file_mode, file_name, file_sha)

        # сборка поддир-ии под обработку
        subdirs = set()
        for other_dir in dir_structure:
            if (
                other_dir.startswith(dir_path + os.sep)
                and other_dir != dir_path
            ):
                rel_path = (
                    other_dir[len(dir_path) + 1:] if (dir_path) else other_dir
                )
                first_sep = rel_path.find(os.sep)
                if first_sep == -1:
                    subdirs.add(other_dir)

        # добавление непроцессированных поддиректорий в стек
        for subdir in subdirs:
            if subdir not in processed_dirs:
                stack.append(subdir)

        # если есть поддиректории, которые еще не обработаны,
        # откладываем эту директорию
        pending_subdirs = [subdir for subdir in subdirs if subdir not in trees]
        if pending_subdirs:
            # откладываем обработку
            stack.append(dir_path)
            continue

        # добавление поддир-ий в tree
        for subdir in subdirs:
            rel_path = subdir[len(dir_path) + 1:] if (dir_path) else subdir
            tree.add_entry(DIRECTORY_MODE, rel_path, trees[subdir])

        # сохранение tree объект если есть записи
        if tree.entries:
            tree_sha = hash_object(tree.serialize(), TREE_TYPE)
            trees[dir_path] = tree_sha
            yield (dir_path, tree)
            processed_dirs.add(dir_path)


def write_tree() -> str:
    """
    созд-е tree объектов на основе индекса и
    возвращает sha корневого treee

    returns:
        sha-1 хеш корневого tree объекта
    """
    from lab3.index import get_index_dict

    index_dict = get_index_dict()

    if not index_dict:
        # пустой индекс
        raise ValueError("индекс пуст")

    # с помощью генератора строит tree объект
    tree_generator = _build_tree_generator(index_dict)

    root_tree_sha = ""

    # обработка всех объектов из генератора
    for tree_path, tree_obj in tree_generator:
        tree_sha = hash_object(tree_obj.serialize(), TREE_TYPE)
        if tree_path == "":
            root_tree_sha = tree_sha

    if not root_tree_sha:
        # не удалось создать корневой tree объект
        raise ValueError("не удалось создать")

    return root_tree_sha


def get_current_author() -> str:
    """
    возвращает информацию об авторе коммита

    returns:
        строка с информацией об авторе "имя <email> время коммита
    """
    timestamp = int(time.time())
    return f"{DEFAULT_AUTHOR} {timestamp}"


def get_current_branch_head() -> Optional[str]:
    """
    читает текущую ветку из HEAD и возвращает SHA последнего коммита

    returns:
        SHA-1 хеш последнего коммита в текущей ветке (если сущ-т)
    """
    head_path = os.path.join(PYGIT_DIR, "HEAD")

    if not os.path.exists(head_path):
        return None

    with open(head_path, "r", encoding=ENCODING) as f:
        head_content = f.read().strip()

    # если HEAD указывает на ветку
    if head_content.startswith("ref: "):
        ref_path = head_content[5:]
        branch_path = os.path.join(PYGIT_DIR, ref_path)

        if os.path.exists(branch_path):
            try:
                with open(branch_path, "r", encoding=ENCODING) as f:
                    branch_content = f.read().strip()
                return branch_content
            except Exception:
                return None
        return None

    # если HEAD указывает напрямую на коммит
    return head_content if head_content else None


def update_branch_head(commit_sha: str) -> None:
    """
    обновляет указатель на новый коммит

    args:
        commit_sha; SHA-1 хеш нового коммита
    """
    head_path = os.path.join(PYGIT_DIR, "HEAD")

    with open(head_path, "r", encoding=ENCODING) as f:
        head_content = f.read().strip()

    # если HEAD указывает на ветку
    if head_content.startswith("ref: "):
        ref_path = head_content[5:]
        branch_path = os.path.join(PYGIT_DIR, ref_path)

        # созд-е дир-ии при необходимости
        os.makedirs(os.path.dirname(branch_path), exist_ok=True)

        with open(branch_path, "w", encoding=ENCODING) as f:
            f.write(commit_sha)

    # если "отсоединенный HEAD", то обновление HEAD
    else:
        with open(head_path, "w", encoding=ENCODING) as f:
            f.write(commit_sha)


def create_commit(
    tree_sha: str, message: str, parent_sha: Optional[str] = None
) -> str:
    """
    создает и сохраняет объект коммита

    args:
        tree_sha: SHA-1 хеш корневого tree объекта
        message: сообщение коммита
        parent_sha: SHA-1 хеш род-го коммита

    returns:
        SHA-1 хеш созданного коммита
    """
    author = get_current_author()
    commit = Commit(tree_sha, parent_sha, author, message)

    commit_data = commit.serialize()
    commit_sha = hash_object(commit_data, COMMIT_TYPE)

    return commit_sha


class CommitHistoryIterator(Iterator[tuple[str, Commit]]):
    """
    итератор для обхода истории коммитов
    проходит по всем коммитам от текущего до начального
    """

    def __init__(self, start_commit_sha: str) -> None:
        """
        инициализирует итератор с начального коммита

        args:
            start_commit_sha: SHA-1 хеш коммита, с которого начинается обход
        """
        self.current_commit_sha: Optional[str] = start_commit_sha

    def __iter__(self) -> "CommitHistoryIterator":
        """возврат самого итератора"""
        return self

    def __next__(self) -> tuple[str, Commit]:
        """
        возврат след-го коммита в истории

        returns:
            кортеж (sha_commit, commit_objects)

        raises:
            StopIteration: если закончились коммиты
        """
        if self.current_commit_sha is None:
            raise StopIteration

        try:
            # загрузка текущего коммита
            obj_type, git_obj = read_object(self.current_commit_sha)

            if obj_type != COMMIT_TYPE:
                raise ValueError
            if not isinstance(git_obj, Commit):
                raise ValueError

            commit = git_obj

            # сохр-е sha текущего коммита перед переходом
            current_sha = self.current_commit_sha

            # переход к род-му коммиту
            self.current_commit_sha = commit.parent_sha

            return current_sha, commit

        except (FileNotFoundError, ValueError) as e:
            raise StopIteration from e


def get_commit_history(start_commit_sha: str) -> "CommitHistoryIterator":
    """
    создает итератор для обхода коммитов

    args:
        start_commit_sha: SHA-1 хеш коммита, с которого начинается обход

    returns:
        итератор истории коммитов
    """
    return CommitHistoryIterator(start_commit_sha)


__all__ = [
    "GitObject",
    "Blob",
    "Tree",
    "Commit",
    "CommitHistoryIterator",
    "BLOB_TYPE",
    "TREE_TYPE",
    "COMMIT_TYPE",
    "hash_object",
    "read_object",
    "write_tree",
    "create_commit",
    "get_current_branch_head",
    "update_branch_head",
    "get_commit_history",
]
