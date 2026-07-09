import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from app.rpc.errors import (
    RPCException, ParseError, InvalidRequestError, MethodNotFoundError,
    InvalidParamsError, InternalError, ResourceNotFoundError, ConcurrencyConflictError, InvalidStateTransitionError
)
from app.core.exceptions import ResourceNotFoundException, ConcurrencyConflictException, InvalidStateTransitionException
from pydantic import ValidationError
from app.rpc.methods import (
    sistema_health, hospitais_listar, tipos_recursos_listar, recursos_listar,
    recursos_obter, recursos_disponibilidade, dashboard_resumo, auditoria_listar,
    recursos_reservar, recursos_liberar, recursos_ocupar, recursos_bloquear, recursos_manutencao,
    simulacao_leitores, simulacao_escritores, simulacao_leitores_escritores
)

METHODS = {
    "sistema.health": sistema_health,
    "hospitais.listar": hospitais_listar,
    "tipos_recursos.listar": tipos_recursos_listar,
    "recursos.listar": recursos_listar,
    "recursos.obter": recursos_obter,
    "recursos.disponibilidade": recursos_disponibilidade,
    "dashboard.resumo": dashboard_resumo,
    "auditoria.listar": auditoria_listar,
    "recursos.reservar": recursos_reservar,
    "recursos.liberar": recursos_liberar,
    "recursos.ocupar": recursos_ocupar,
    "recursos.bloquear": recursos_bloquear,
    "recursos.manutencao": recursos_manutencao,
    "simulacao.leitores": simulacao_leitores,
    "simulacao.escritores": simulacao_escritores,
    "simulacao.leitores_escritores": simulacao_leitores_escritores
}

async def dispatch_rpc(payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    req_id = payload.get("id")
    try:
        if payload.get("jsonrpc") != "2.0":
            raise InvalidRequestError()
        
        method_name = payload.get("method")
        if not method_name:
            raise InvalidRequestError()
            
        if method_name not in METHODS:
            raise MethodNotFoundError()
            
        params = payload.get("params", {})
        if isinstance(params, list):
            # Positional params not supported in this simple dispatcher
            raise InvalidParamsError("Only named parameters are supported")
            
        handler = METHODS[method_name]
        try:
            result = await handler(db, params)
            return {"jsonrpc": "2.0", "result": result, "id": req_id}
        except ResourceNotFoundException as e:
            raise ResourceNotFoundError(str(e.detail) if hasattr(e, 'detail') else None)
        except ConcurrencyConflictException as e:
            raise ConcurrencyConflictError(str(e.detail) if hasattr(e, 'detail') else None)
        except InvalidStateTransitionException as e:
            raise InvalidStateTransitionError(str(e.detail) if hasattr(e, 'detail') else None)
        except ValidationError as e:
            raise InvalidParamsError(e.errors())
        except RPCException as e:
            raise e
        except Exception as e:
            logging.exception("Internal error in RPC")
            raise InternalError(str(e))
            
    except RPCException as e:
        return {"jsonrpc": "2.0", "error": e.to_dict(), "id": req_id}
    except Exception as e:
        return {"jsonrpc": "2.0", "error": InternalError(str(e)).to_dict(), "id": req_id}
