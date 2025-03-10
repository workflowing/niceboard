class SearchError(Exception):
    """
    Exception raised when a NiceBoard search operation fails.
    Attributes:
    message -- explanation of the error
    cause -- the original exception that caused this error (optional)
    """

    def __init__(self, message: str, cause: Exception | None = None):
        self.message = message
        self.cause = cause
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (Caused by: {str(self.cause)})"
        return self.message
