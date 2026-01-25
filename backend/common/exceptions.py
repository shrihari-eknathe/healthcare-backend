class AppException(Exception):
    status_code = 400

    def __init__(self, message):
        self.message = message

class UnauthorizedError(AppException):
    status_code = 401

class ForbiddenError(AppException):
    status_code = 403
