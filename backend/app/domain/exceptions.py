class VectorVaultError(Exception):
    pass


class NotFoundError(VectorVaultError):
    pass


class UnsupportedFileTypeError(VectorVaultError):
    pass


class DocumentProcessingError(VectorVaultError):
    pass


class ExternalServiceError(VectorVaultError):
    pass
