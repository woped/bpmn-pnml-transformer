"""Utility module for exception handling."""


class InternalErrorException(Exception):
    """Internal errors for which a GitHub Issue should be opened."""

    def __init__(self, message=""):
        """Initialize the exception with an message and ID."""
        self.message = message
        self.id = 0

    def __str__(self):
        """Return a string representation of the error."""
        if self.id:
            return f"[{self.id}] Internal error: {self.message}"
        else:
            return "Internal error: {self.message}"


class MissingValueException(Exception):
    """Exception for cases in which an element is missing a required attribute."""

    def __init__(self, message=""):
        """Initialize the exception with the missing value and ID."""
        self.message = message
        self.id = 1

    def __str__(self):
        """Return a string representation of the missing value."""
        if self.id:
            return f"[{self.id}] Missing value: {self.message}"
        else:
            return f"Missing value: {self.message}"


class NotSupportedException(Exception):
    """Exception for cases when input element is not supported by the transformer."""

    def __init__(self, message=""):
        """Initialize the exception with an message and ID."""
        self.message = message
        self.id = 2

    def __str__(self):
        """Return a string representation of the unsupported element."""
        if self.id:
            return f"[{self.id}] Not supported: {self.message}"
        else:
            return f"Not supported: {self.message}"


class AlreadyExistingException(Exception):
    """Exception for cases in which an element already exists."""

    def __init__(self, message=""):
        """Initialize the exception with the already existing value and ID."""
        self.message = message
        self.id = 3

    def __str__(self):
        """Return a string representation of the already existing value."""
        if self.id:
            return f"[{self.id}] Already existing: {self.message}"
        else:
            return f"Already existing: {self.message}"


class InputSyntaxException(Exception):
    """Exception for cases when the input syntax contains errors."""

    def __init__(self, message=""):
        """Initialize the exception with an ID and message."""
        self.message = message
        self.id = 4

    def __str__(self):
        """Return a string representation of the input syntax error."""
        if self.id:
            return f"[{self.id}] Other input syntax error: {self.message}"
        else:
            return f"Not supported: {self.message}"


class NotSupportedBPMNElement(Exception):
    """Exception class for not supported BPMN elements."""

    ...
