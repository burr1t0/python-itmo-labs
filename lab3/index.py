import os
from typing import cast

# для работы с файлами
import pickle

from lab3.constants import PYGIT_DIR, INDEX_FILE, DEFAULT_FILE_MODE
from lab3.objects import hash_object, Blob, BLOB_TYPE

# запись в индексе (путь, sha, режим)
IndexEntry = tuple[str, str, str]


def read_index() -> list[tuple[str, str, str]]:
    """
    Читает файл

    returns:
        список записи инд-са в формате: path, sha, mode
    """
    index_path = os.path.join(PYGIT_DIR, INDEX_FILE)

    # если файл индекса не сущ-т, то пустой список
    if not os.path.exists(index_path):
        return []

    with open(index_path, "rb") as f:
        # 'rb' - чтение в бин-м режиме
        index_data = pickle.load(f)
        # pickle.load() - для чтения байтов и преобр-я в объекты
        # проверка данных на правильный тип
        if not isinstance(index_data, list):
            return []
        return cast(list[IndexEntry], index_data)


def write_index(entries: list[IndexEntry]) -> None:
    """
    Записывает инд-кс в файл

    args:
        entries: список записей для сохр-я в индекс
    """
    index_path = os.path.join(PYGIT_DIR, INDEX_FILE)

    # созд-е дир-ии в .pygit если ее нет
    os.makedirs(PYGIT_DIR, exist_ok=True)

    with open(index_path, "wb") as f:
        # 'wb' - запись в бин-м виде
        pickle.dump(entries, f)
        # ickle.dump() - преобразование объекта в байты и запись


def add_to_index(file_path: str) -> str:
    """
    Добавление файла в индекс

    args:
        file_path: путь к файлу для добавления

    returns:
        SHA-1 хеш созданного blob объекта

    raises:
        FileNotFoundError: если файл не сущ-т
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"файл не найден: {file_path}")

    with open(file_path, "rb") as f:
        file_data = f.read()

    # созд-е blob объекта и получ-е его хеша
    blob = Blob(file_data)
    sha_hash = hash_object(blob.serialize(), BLOB_TYPE)

    # чтение текущего индекса
    index_entries = read_index()

    # удаление старой записи, если она была
    index_entries = [entry for entry in index_entries if entry[0] != file_path]

    # добавление новой записи
    index_entries.append((file_path, sha_hash, DEFAULT_FILE_MODE))

    # сохр-е обновленного инд-са
    write_index(index_entries)

    return sha_hash


def get_index_dict() -> dict[str, tuple[str, str]]:
    """
    Возвращает инд-кс в виде словаря (для удобства)

    returns:
        словарь, с ключом в виде пути к файлу, значение - sha, mode
    """
    index_entries = read_index()
    return {path: (sha, mode) for path, sha, mode in index_entries}
