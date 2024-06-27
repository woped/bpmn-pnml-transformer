"""Utility module for exception handling."""


class KnownException(Exception):
    """Base class for all known transformer exceptions."""

    def __init__(self, id: int, message: str) -> None:
        """Init user facing named exceptions with id's."""
        self._message = message
        self._id = id
        super().__init__(message)

    def __str__(self):
        """Return a string representation of the error."""
        if self._id:
            return f"[{self._id}] Internal error: {self._message}"
        else:
            return f"Internal error: {self._message}"


class PrivateInternalException(Exception):
    """Exception for internal errors."""


class InternalTransformationException(PrivateInternalException):
    """Internal exceptions while transforming."""


class UnexpectedError(KnownException):
    """Exception class for ."""

    def __init__(self) -> None:
        """Init exception."""
        super().__init__(0, "")


class NotSupportedBPMNElement(KnownException):
    """Exception class for not supported BPMN elements."""

    def __init__(self, element_names: str) -> None:
        """Init exception."""
        super().__init__(1, f"BPMN element {element_names} not supported.")


class MissingEnvironmentVariable(KnownException):
    """Exception class for ."""

    def __init__(self, var_name: str) -> None:
        """Init exception."""
        super().__init__(1, f"Env variable {var_name} not set!")


class TokenCheckUnsuccessful(KnownException):
    """Exception class for ."""

    def __init__(self) -> None:
        """Init exception."""
        super().__init__(1, "Token check not successful")


class UnexpectedQueryParameter(KnownException):
    """Exception class for ."""

    def __init__(self, query_param: str) -> None:
        """Init exception."""
        super().__init__(1, f"Query parameter {query_param} wrong.")


class UnnamedLane(KnownException):
    """Exception class for ."""

    def __init__(self) -> None:
        """Init exception."""
        super().__init__(1, "Please name all of your lanes.")


class UnkownIntermediateCatchEvent(KnownException):
    """Exception class for ."""

    def __init__(self) -> None:
        """Init exception."""
        super().__init__(1, "Wrong intermediate event type used!")


class WrongSubprocessDegree(KnownException):
    """Exception class for ."""

    def __init__(self) -> None:
        """Init exception."""
        super().__init__(1, "Subprocess must have exactly one in and outgoing flow!")


class ORGatewayDetectionIssue(KnownException):
    """Exception class for ."""

    def __init__(self) -> None:
        """Init exception."""
        super().__init__(1, "Could not find matching splits and joins for OR-Gateways")


class SubprocessWrongInnerSourceSinkDegree(KnownException):
    """Exception class for ."""

    def __init__(self) -> None:
        """Init exception."""
        super().__init__(
            1,
            "currently source/sink in subprocess must have no incoming/outgoing arcs"
            " to convert to BPMN Start and Endevents.",
        )


class UnkownResourceOrganizationMapping(KnownException):
    """Exception class for ."""

    def __init__(self) -> None:
        """Init exception."""
        super().__init__(1, "Resources must belong to the same organization.")


# class (KnownException):
#     """Exception class for ."""

#     def __init__(self) -> None:
#         """Init exception."""
#         super().__init__(1, "")
