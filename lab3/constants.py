from typing import Final

# для типизации данных переменных

PYGIT_DIR: Final[str] = ".pygit"
OBJECTS_DIR: Final[str] = "objects"
REFS_DIR: Final[str] = "refs"
HEADS_DIR: Final[str] = "heads"
HEAD_FILE: Final[str] = "HEAD"
INDEX_FILE: Final[str] = "index"


# значения по умолчанию
DEFAULT_BRANCH: Final[str] = "main"
DEFAULT_HEAD_REF: Final[str] = f"ref: refs/{HEADS_DIR}/{DEFAULT_BRANCH}"

# режимы файлов
DEFAULT_FILE_MODE: Final[str] = "100644"
DIRECTORY_MODE: Final[str] = "40000"

# типы объектов
BLOB_TYPE: Final[str] = "blob"
TREE_TYPE: Final[str] = "tree"
COMMIT_TYPE: Final[str] = "commit"

# Кодировка
ENCODING: Final[str] = "utf-8"

# для коммитов
DEFAULT_AUTHOR: Final[str] = "pygit user <pygit@itmo.ru>"
