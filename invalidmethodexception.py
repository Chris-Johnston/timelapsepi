"""
Invalid Method Exception

Thrown when an invalid capture method is supplied.
"""

class InvalidMethodException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
