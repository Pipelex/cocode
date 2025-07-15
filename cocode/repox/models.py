from pipelex.types import StrEnum


class NotableFileType(StrEnum):
    PYTHON = "python"


class OutputStyle(StrEnum):
    REPO_MAP = "repo_map"
    FLAT = "flat"
    IMPORT_LIST = "import_list"
    TREE = "tree"
