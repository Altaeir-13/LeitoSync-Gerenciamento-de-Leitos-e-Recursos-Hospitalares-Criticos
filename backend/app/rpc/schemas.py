from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, Union

class JSONRPCRequest(BaseModel):
    jsonrpc: str = Field(..., pattern="^2\.0$")
    method: str
    params: Optional[Union[Dict[str, Any], list]] = None
    id: Optional[Union[str, int]] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None
