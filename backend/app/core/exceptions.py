from fastapi import HTTPException, status

class ConcurrencyConflictException(HTTPException):
    def __init__(self, detail: str = "O recurso não está mais disponível para esta operação."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class ResourceNotFoundException(HTTPException):
    def __init__(self, detail: str = "Recurso não encontrado."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class InvalidStateTransitionException(HTTPException):
    def __init__(self, detail: str = "Transição de estado inválida para este recurso."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
