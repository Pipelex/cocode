class CocodeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class PythonProcessingError(CocodeError):
    pass


class RepoxException(CocodeError):
    pass


class NoDifferencesFound(CocodeError):
    pass
