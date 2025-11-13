from pipelex.base_exceptions import RootException


class PythonProcessingError(RootException):
    pass


class RepoxException(RootException):
    pass


class NoDifferencesFound(RootException):
    pass
