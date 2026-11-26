class AppError(Exception):
    def __init__(self, message, status=400, code="invalid_request"):
        self.message, self.status, self.code = message, status, code
        super().__init__(message)


def conflict(message):
    return AppError(message, 409, "state_conflict")
