class LocalActionResponse:
    def __init__(self, isSuccessful=None, message=None, messageCode=None):
        self.isSuccessful = isSuccessful
        self.message = message
        self.messageCode = messageCode
