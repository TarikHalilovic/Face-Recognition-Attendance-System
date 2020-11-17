class ActionResponse:
    def __init__(self, serverError, isSuccessful, statusCode, message, fullName, messageCode):
        self.serverError = serverError
        self.isSuccessful = isSuccessful
        self.statusCode = statusCode
        self.message = message
        self.fullName = fullName
        self.messageCode = messageCode
