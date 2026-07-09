import threading
import time
import random
from datetime import datetime

recursos_hospitalares = {
    "UTI-01": {
        "hospital": "Hospital Regional Norte",
        "tipo": "Leito de UTI",
        "status": "disponivel",
        "paciente": None
    },
    "UTI-02": {
        "hospital": "Hospital Central",
        "tipo": "Leito de UTI",
        "status": "disponivel",
        "paciente": None
    },
    "CLINICO-01": {
        "hospital": "Hospital Universitário",
        "tipo": "Leito Clínico",
        "status": "ocupado",
        "paciente": "PAC-100"
    }
}

logs_auditoria = []

leitores_ativos = 0
mutex_leitores = threading.Semaphore(1)
trava_recursos = threading.Semaphore(1)

def consultar_disponibilidade(id_leitor, filtro_tipo=None):
    """
    Representa um LEITOR.
    Pode consultar recursos sem impedir que outros leitores façam o mesmo simultaneamente.
    """
    global leitores_ativos

    print(f"[LEITOR {id_leitor}] Tentando consultar disponibilidade...")

    mutex_leitores.acquire()
    leitores_ativos += 1
    if leitores_ativos == 1:
        trava_recursos.acquire()
    mutex_leitores.release()

    print(f"[LEITOR {id_leitor}] Consultando disponibilidade de leitos...")
    
    time.sleep(random.uniform(0.1, 0.5))
    
    for codigo, dados in recursos_hospitalares.items():
        if dados["status"] == "disponivel":
            if filtro_tipo is None or dados["tipo"] == filtro_tipo:
                print(f"  -> [LEITURA {id_leitor}] {codigo} | {dados['hospital']} | {dados['tipo']} | {dados['status']}")
    
    mutex_leitores.acquire()
    leitores_ativos -= 1
    if leitores_ativos == 0:
        trava_recursos.release()
    mutex_leitores.release()

    print(f"[LEITOR {id_leitor}] Consulta finalizada.")

def registrar_auditoria(acao, recurso, status_anterior, novo_status, responsavel):
    """Função auxiliar para registrar log."""
    log = {
        "acao": acao,
        "recurso": recurso,
        "status_anterior": status_anterior,
        "novo_status": novo_status,
        "responsavel": responsavel,
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    logs_auditoria.append(log)

def reservar_recurso(id_escritor, codigo_recurso, paciente, responsavel):
    """
    Representa um ESCRITOR.
    Precisa de exclusividade total para evitar reserva duplicada.
    """
    print(f"[ESCRITOR {id_escritor}] Aguardando acesso exclusivo para reservar {codigo_recurso}...")
    
    trava_recursos.acquire()

    time.sleep(random.uniform(0.1, 0.3))
    
    if codigo_recurso in recursos_hospitalares:
        recurso = recursos_hospitalares[codigo_recurso]
        
        if recurso["status"] == "disponivel":
            status_antigo = recurso["status"]
            
            recurso["status"] = "reservado"
            recurso["paciente"] = paciente
            
            registrar_auditoria("reserva", codigo_recurso, status_antigo, "reservado", responsavel)
            print(f"[SUCESSO] Escritor {id_escritor} ({responsavel}) reservou com sucesso o recurso {codigo_recurso}.")
        else:
            print(f"[CONFLITO] Escritor {id_escritor} tentou reservar {codigo_recurso}, mas o recurso já está {recurso['status']}.")
    
    trava_recursos.release()

def liberar_recurso(id_escritor, codigo_recurso, responsavel):
    """Outro tipo de ESCRITOR, altera status para disponivel."""
    print(f"[ESCRITOR {id_escritor}] Aguardando acesso exclusivo para liberar {codigo_recurso}...")
    trava_recursos.acquire()
    
    if codigo_recurso in recursos_hospitalares:
        recurso = recursos_hospitalares[codigo_recurso]
        status_antigo = recurso["status"]
        recurso["status"] = "disponivel"
        recurso["paciente"] = None
        
        registrar_auditoria("liberacao", codigo_recurso, status_antigo, "disponivel", responsavel)
        print(f"[SUCESSO] Escritor {id_escritor} ({responsavel}) liberou o recurso {codigo_recurso}.")
        
    trava_recursos.release()

def bloquear_recurso(id_escritor, codigo_recurso, responsavel, motivo):
    """Outro tipo de ESCRITOR, altera status para bloqueado."""
    print(f"[ESCRITOR {id_escritor}] Aguardando acesso exclusivo para bloquear {codigo_recurso}...")
    trava_recursos.acquire()
    
    if codigo_recurso in recursos_hospitalares:
        recurso = recursos_hospitalares[codigo_recurso]
        status_antigo = recurso["status"]
        recurso["status"] = "bloqueado"
        recurso["paciente"] = None
        
        registrar_auditoria("bloqueio", codigo_recurso, status_antigo, "bloqueado", f"{responsavel} ({motivo})")
        print(f"[SUCESSO] Escritor {id_escritor} ({responsavel}) bloqueou o recurso {codigo_recurso}.")
        
    trava_recursos.release()

def exibir_status_final():
    print("\n" + "="*50)
    print("ESTADO FINAL DOS RECURSOS HOSPITALARES")
    print("="*50)
    for codigo, dados in recursos_hospitalares.items():
        paciente = dados["paciente"] if dados["paciente"] else "Vazio"
        print(f"[{codigo}] Status: {dados['status']} | Paciente: {paciente}")
    
    print("\n" + "="*50)
    print(f"LOGS DE AUDITORIA ({len(logs_auditoria)} alterações realizadas)")
    print("="*50)
    for log in logs_auditoria:
        print(f"[{log['data_hora']}] {log['responsavel']} executou '{log['acao']}' em {log['recurso']} ({log['status_anterior']} -> {log['novo_status']})")
    print("="*50 + "\n")

if __name__ == "__main__":
    print("\nINICIANDO SIMULAÇÃO DO LEITOSYNC (Problema Leitores-Escritores)\n")
    
    threads = []
    
    for i in range(1, 4):
        t = threading.Thread(target=consultar_disponibilidade, args=(i,))
        threads.append(t)
        t.start()
        
    time.sleep(0.1)
        
    for i in range(1, 6):
        t = threading.Thread(target=reservar_recurso, args=(i, "UTI-01", f"PAC-{i}00", f"Central {i}"))
        threads.append(t)
        t.start()
        
    for i in range(4, 7):
        t = threading.Thread(target=consultar_disponibilidade, args=(i,))
        threads.append(t)
        t.start()
        
    time.sleep(1)
    
    t_liberar = threading.Thread(target=liberar_recurso, args=(6, "CLINICO-01", "Central 1"))
    threads.append(t_liberar)
    t_liberar.start()
    
    t_bloquear = threading.Thread(target=bloquear_recurso, args=(7, "UTI-02", "Equipe Manutenção", "Limpeza pesada"))
    threads.append(t_bloquear)
    t_bloquear.start()

    for t in threads:
        t.join()
        
    exibir_status_final()
