class VectorVaultError(Exception):
    pass


class NotFoundError(VectorVaultError):
    pass


class UnsupportedFileTypeError(VectorVaultError):
    pass

class ExternalServiceError(VectorVaultError):
    pass

class FileAlreadyExistsError(VectorVaultError):
    pass