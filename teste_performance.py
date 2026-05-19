import requests
import time

# --- CONFIGURAÇÃO ---
# Alterne aqui entre 'localhost' e o DNS da AWS para testar ambos
ALVO = "http://localhost/sqli-login.php"
NUM_REQUISICOES = 50

def medir_latencia(tamanho_kb, descricao):
    print(f"\n[+] Iniciando Teste: {descricao} ({tamanho_kb} KB)")
    
    # Gera o tamanho exato de lixo em KB
    lixo = "A" * (tamanho_kb * 1024)
    payload = {"usuario": "admin", "senha": "123", "dados_extras": lixo}
    
    tempos = []
    
    for i in range(1, NUM_REQUISICOES + 1):
        inicio = time.perf_counter()
        
        try:
            # Enviando a requisição POST
            resposta = requests.post(ALVO, data=payload, timeout=10)
            fim = time.perf_counter()
            
            tempo_ms = (fim - inicio) * 1000
            tempos.append(tempo_ms)
            
            # Print de progresso no terminal
            print(f"  Req {i}/{NUM_REQUISICOES} | Status: {resposta.status_code} | Tempo: {tempo_ms:.2f} ms")
            
        except requests.exceptions.RequestException as e:
            print(f"  Req {i} | ERRO DE CONEXÃO")
            
    # Calculando a média
    if tempos:
        media = sum(tempos) / len(tempos)
        print(f"\n[RESULTADO] {descricao}: Média de {media:.2f} ms por requisição.")
    else:
        print("\n[RESULTADO] Nenhuma requisição teve sucesso.")

# Executando os dois cenários
print(f"=== TESTE DE LATÊNCIA E PERFORMANCE ===")
print(f"Alvo: {ALVO}\n")

# Cenário 1: Payload pequeno (1 KB)
medir_latencia(1, "Cenário Leve (Baseline)")

# Pausa para não encavalar os logs
time.sleep(2)

# Cenário 2: Payload gigante (130 KB)
medir_latencia(120, "Cenário Pesado (Estresse de Inspeção)")