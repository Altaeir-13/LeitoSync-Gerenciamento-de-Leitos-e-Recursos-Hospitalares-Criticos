from fastapi import HTTPException, status

class ConcurrencyConflictException(HTTPException):
    def __init__(self, detail: str = "Resource is no longer available for this operation."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class ResourceNotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class InvalidStateTransitionException(HTTPException):
    def __init__(self, detail: str = "Invalid state transition for this resource."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
