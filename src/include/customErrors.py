class APIError(Exception):
    """No API found"""
    def __init__(self, specific="") -> None:
        self.message = "No " + specific + "API found"
        super().__init__(self.message)

class RecognizerAPIError(APIError):
    """No Recognizer API found"""
    def __init__(self) -> None:
        self.message = "speech recognition "
        super().__init__(specific=self.message)