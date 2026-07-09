export interface RPCRequest {
  jsonrpc: "2.0";
  method: string;
  params?: any;
  id: string | number;
}

export interface RPCResponse<T = any> {
  jsonrpc: "2.0";
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
  id: string | number;
}

let callId = 1;

export async function rpcCall<T>(method: string, params?: unknown): Promise<T> {
  const currentId = callId++;
  const payload: RPCRequest = {
    jsonrpc: "2.0",
    method,
    params,
    id: currentId,
  };

  const response = await fetch("http://localhost:8000/rpc", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data: RPCResponse<T> = await response.json();

  if (data.error) {
    throw {
      response: {
        data: {
          detail: data.error.message,
        },
      },
    };
  }

  return data.result as T;
}
