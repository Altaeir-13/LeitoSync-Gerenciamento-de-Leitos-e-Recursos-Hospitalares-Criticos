class RPCException(Exception):
    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        err = {"code": self.code, "message": self.message}
        if self.data is not None:
            err["data"] = self.data
        return err

class ParseError(RPCException):
    def __init__(self):
        super().__init__(-32700, "Parse error")

class InvalidRequestError(RPCException):
    def __init__(self):
        super().__init__(-32600, "Invalid Request")

class MethodNotFoundError(RPCException):
    def __init__(self):
        super().__init__(-32601, "Method not found")

class InvalidParamsError(RPCException):
    def __init__(self, data=None):
        super().__init__(-32602, "Invalid params", data)

class InternalError(RPCException):
    def __init__(self, data=None):
        super().__init__(-32603, "Internal error", data)

class ResourceNotFoundError(RPCException):
    def __init__(self, data=None):
        super().__init__(404, "Recurso não encontrado", data)

class ConcurrencyConflictError(RPCException):
    def __init__(self, data=None):
        super().__init__(409, "O recurso não está mais disponível para reserva.", data)

class InvalidStateTransitionError(RPCException):
    def __init__(self, data=None):
        super().__init__(400, "Transição inválida", data)
