from fastapi.exceptions import ValidationException  # Basically this file!


class SocketIORequestValidationError(ValidationException):
    pass
