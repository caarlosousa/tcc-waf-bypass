import requests
import time
import csv

# --- CONFIGURAÇÃO ---
# Alterne o alvo para rodar duas vezes (uma para AWS, uma para Local)
ALVO = "http://localhost/sqli-login.php" # Mude para o DNS da AWS depois
NOME_TESTE = "ModSecurity_Local" # Mude para "AWS_WAF" depois
NUM_REQUISICOES = 30 # 30 já é uma amostra estatística excelente

# A matriz exata de testes que você definiu + pontos de quebra
TAMANHOS_KB = [1, 4, 8, 16, 32, 64, 96, 120, 128, 130]

resultados = []

print(f"=== INICIANDO COLETA DE DADOS PARA O TCC ===")
print(f"Alvo: {ALVO}\n")

for tamanho in TAMANHOS_KB:
    print(f"[*] Testando Payload de {tamanho} KB...")
    lixo = "A" * (tamanho * 1024)
    payload = {"usuario": "admin", "senha": "123", "dados_extras": lixo}
    
    tempos = []
    status_codes = set() # Para registrar se deu 200 ou 413
    
    for i in range(NUM_REQUISICOES):
        inicio = time.perf_counter()
        try:
            resposta = requests.post(ALVO, data=payload, timeout=15)
            fim = time.perf_counter()
            tempos.append((fim - inicio) * 1000)
            status_codes.add(resposta.status_code)
        except requests.exceptions.RequestException:
            status_codes.add("TIMEOUT/ERRO")
            
    if tempos:
        media = sum(tempos) / len(tempos)
        status_final = list(status_codes)[0] if len(status_codes) == 1 else str(list(status_codes))
        print(f"    -> Média: {media:.2f} ms | Status: {status_final}")
        
        resultados.append({
            "Tamanho (KB)": tamanho,
            "Latência Média (ms)": round(media, 2),
            "Status HTTP": status_final
        })
    time.sleep(1) # Respiro para não derrubar o servidor

# Exportando para CSV
nome_arquivo = f"dados_tcc_{NOME_TESTE}.csv"
with open(nome_arquivo, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["Tamanho (KB)", "Latência Média (ms)", "Status HTTP"])
    writer.writeheader()
    writer.writerows(resultados)

print(f"\n[SUCESSO] Dados exportados para {nome_arquivo}! Pode gerar os gráficos.")