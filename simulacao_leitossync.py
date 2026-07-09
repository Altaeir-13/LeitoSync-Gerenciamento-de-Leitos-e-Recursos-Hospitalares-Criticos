"""
Simulação simplificada do LeitoSync com RPC.

Este arquivo demonstra, em uma única execução Python, a lógica principal do projeto completo:
clientes fazem chamadas remotas de procedimento para consultar ou reservar leitos.

Leitores: chamadas RPC de consulta.
Escritores: chamadas RPC de reserva.
Recurso compartilhado: dicionário de leitos mantido no servidor RPC.
Solução: múltiplas leituras podem ocorrer, mas a escrita exige exclusividade para evitar reserva duplicada.
"""

from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import xmlrpc.client
import threading
import time
import random

leitos = {
    "UTI-01": "disponivel",
    "UTI-02": "disponivel",
    "CLINICO-01": "ocupado"
}

leitores_ativos = 0
mutex_leitores = threading.Semaphore(1)
trava_leitos = threading.Semaphore(1)

class ServidorRPCConcorrente(ThreadingMixIn, SimpleXMLRPCServer):
    pass

def consultar_leitos(nome_cliente):
    global leitores_ativos
    
    # Protocolo de entrada dos leitores
    mutex_leitores.acquire()
    leitores_ativos += 1
    if leitores_ativos == 1:
        trava_leitos.acquire()
    mutex_leitores.release()
    
    print(f"[{nome_cliente}] (Leitor) Consultando estado dos leitos...")
    time.sleep(random.uniform(0.1, 0.5))
    estado = leitos.copy()
    print(f"[{nome_cliente}] (Leitor) Consulta concluída. Leitos encontrados: {len(estado)}")
    
    # Protocolo de saída dos leitores
    mutex_leitores.acquire()
    leitores_ativos -= 1
    if leitores_ativos == 0:
        trava_leitos.release()
    mutex_leitores.release()
    
    return estado

def reservar_leito(codigo_leito, nome_cliente):
    print(f"[{nome_cliente}] (Escritor) Tentando reservar o leito {codigo_leito}...")
    
    # Protocolo de entrada dos escritores
    trava_leitos.acquire()
    
    print(f"[{nome_cliente}] (Escritor) Lock obtido no servidor. Verificando {codigo_leito}...")
    time.sleep(random.uniform(0.1, 0.5))
    
    if codigo_leito not in leitos:
        resultado = {"sucesso": False, "mensagem": "Leito não encontrado."}
    elif leitos[codigo_leito] == "disponivel":
        leitos[codigo_leito] = "reservado"
        resultado = {"sucesso": True, "mensagem": f"Leito {codigo_leito} reservado com sucesso!"}
        print(f"[{nome_cliente}] (Escritor) SUCESSO: Reserva confirmada no banco (dicionário).")
    else:
        resultado = {"sucesso": False, "mensagem": "Conflito: O leito não está mais disponível para reserva."}
        print(f"[{nome_cliente}] (Escritor) REJEITADO: Conflito de concorrência detectado.")
        
    trava_leitos.release()
    return resultado

def estado_final():
    return leitos

def iniciar_servidor():
    server = ServidorRPCConcorrente(("localhost", 8001), logRequests=False)
    server.register_function(consultar_leitos, "consultar_leitos")
    server.register_function(reservar_leito, "reservar_leito")
    server.register_function(estado_final, "estado_final")
    print("Servidor RPC iniciado em localhost:8001")
    server.serve_forever()

def cliente_leitor(id_leitor):
    nome = f"Leitor {id_leitor}"
    proxy = xmlrpc.client.ServerProxy("http://localhost:8001/")
    try:
        proxy.consultar_leitos(nome)
    except Exception as e:
        print(f"[{nome}] Erro de comunicação RPC: {e}")

def cliente_escritor(id_escritor):
    nome = f"Escritor {id_escritor}"
    proxy = xmlrpc.client.ServerProxy("http://localhost:8001/")
    try:
        resultado = proxy.reservar_leito("UTI-01", nome)
        if resultado["sucesso"]:
            print(f"--- [{nome}] FINALIZADO COM SUCESSO ---")
        else:
            print(f"--- [{nome}] FINALIZADO COM ERRO: {resultado['mensagem']} ---")
    except Exception as e:
        print(f"[{nome}] Erro de comunicação RPC: {e}")

if __name__ == "__main__":
    t_server = threading.Thread(target=iniciar_servidor, daemon=True)
    t_server.start()
    
    time.sleep(1)
    
    threads = []
    
    for i in range(1, 4):
        t = threading.Thread(target=cliente_leitor, args=(i,))
        threads.append(t)
        
    for i in range(1, 6):
        t = threading.Thread(target=cliente_escritor, args=(i,))
        threads.append(t)
        
    random.shuffle(threads)
    
    print("\nIniciando clientes (Leitores e Escritores em concorrência)...\n")
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
        
    proxy = xmlrpc.client.ServerProxy("http://localhost:8001/")
    estado = proxy.estado_final()
    print(f"\nEstado final dos leitos no servidor RPC: {estado}")
