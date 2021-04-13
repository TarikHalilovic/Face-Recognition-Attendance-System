class LocalActionResponse:
    def __init__(self, isSuccessful=False, message=None, messageCode=None):
        self.isSuccessful = isSuccessful
        self.message = message
        self.messageCode = messageCode
