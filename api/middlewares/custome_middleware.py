class CustomException(Exception):
    def __init__(self, error_code, message=None, label=None):
        self.error_code = error_code
        self.message = message
        self.label = label