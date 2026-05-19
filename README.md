# 🛡️ TCC: Avaliação Prática de WAFs via Exaustão de Limite de Inspeção

Repositório destinado a armazenar os artefatos práticos (aplicações vulneráveis e *scripts* de automação) desenvolvidos para o Trabalho de Conclusão de Curso. O projeto foca na análise comparativa entre **AWS WAF** e **ModSecurity**, explorando os limites de inspeção de corpo (*Body Inspection Limit*).

⚠️ **Aviso:** Todos os *scripts* e técnicas documentados neste repositório têm fins estritamente acadêmicos e educacionais. Os testes foram realizados em ambientes de laboratório controlados de propriedade do autor.

---

## 📂 Estrutura do Projeto

O repositório está dividido logicamente entre a aplicação alvo e os vetores de ataque automatizados:

```text
TCC-WAF-BYPASS/
├── app-vulneravel/
│   ├── index.php                    # Página principal da aplicação
│   └── sqli-login.php               # Aplicação PHP intencionalmente vulnerável a SQLi
└── scripts-ataque/
    ├── alteracao_logica/            # Testes de linha de base (Baseline)
    │   ├── ataque 1-1.py            # Bypass de autenticação clássico (OR '1'='1)
    │   ├── ataque 1-2.py            # Ofuscação com comentários SQL (/*...*/)
    │   └── ataque 1-3.py            # Uso de operadores alternativos (XOR)
    ├── blind_SQL/
    │   └── ataque_time_based.py     # Injeção baseada em tempo (SLEEP)
    └── OWASP/                       # Ataques avançados utilizando Bypass Volumétrico (8KB)
        ├── ataque_boolean_blind.py  # Inferência booleana (SUBSTRING)
        ├── ataque_error_based.py    # Exfiltração via erro XML (ExtractValue)
        └── ataque_union.py          # Fabricação de registros (UNION SELECT)
```

---

## ⚙️ A Técnica Central: *Body Inspection Limit Bypass*

A premissa base dos ataques contidos na pasta `OWASP` é a exploração de uma característica de arquitetura de WAFs em nuvem (*Fail Open*). Serviços de borda, como o Application Load Balancer (ALB) da AWS, possuem um limite rígido de inspeção dos primeiros **8.192 bytes (8 KB)** do corpo da requisição POST.

Para contornar as regras de detecção, os *scripts* em Python implementam a técnica de **Payload Padding**:
1. Geram um parâmetro contendo 8.192 caracteres inofensivos (ex: `lixo = "A" * 8192`).
2. Posicionam o *payload* malicioso imediatamente após este bloco.
3. O WAF inspeciona apenas os 8 KB iniciais, não encontra ameaças, e libera a requisição.
4. O interpretador PHP processa a carga inteira e o MariaDB executa a injeção.

---

## 🔬 Decomposição Lógica dos Ataques (PoC)

Abaixo encontra-se a mecânica de como cada *payload* interage com o banco de dados MariaDB/MySQL.

### 📁 Módulo: `OWASP` (Ataques com Evasão Volumétrica)

#### 1. UNION Based SQLi (`ataque_union.py`)
* **Payload:** `' UNION SELECT 1, 2, 3 -- `
* **Lógica:** A aplicação alvo executa a verificação lógica `if ($result->num_rows > 0)`. Como não há usuário vazio, a consulta original retorna um conjunto vazio. O operador `UNION` anexa o resultado da nossa segunda consulta (`SELECT 1, 2, 3`). O banco retorna essa linha fabricada, satisfazendo a condição do PHP e autorizando o acesso.

#### 2. Error Based SQLi (`ataque_error_based.py`)
* **Payload:** `' AND ExtractValue(1, concat(0x3a, @@version)) -- `
* **Lógica:** Utiliza-se a função de manipulação XML `ExtractValue()`. A função `concat()` junta o caractere `0x3a` (que representa ":" em hexadecimal) com a variável global `@@version`. Como a sintaxe XPath não permite que uma expressão comece com ":", o MariaDB gera um erro fatal que reflete a versão do sistema: `XPATH syntax error: ':10.11.13-MariaDB'`. A mensagem é vazada nos *logs* do servidor.

#### 3. Boolean-Based Blind SQLi (`ataque_boolean_blind.py`)
* **Payload:** `' OR (SUBSTRING(@@version, 1, 1) = '1') -- `
* **Lógica:** O atacante faz uma pergunta condicional ao banco. A função `SUBSTRING` extrai o primeiro caractere da versão do banco e verifica se é igual a '1'. A consulta torna-se `FALSO OR VERDADEIRO`, forçando o *login*. Iterando esse processo, é possível extrair todo o banco de dados de forma inferencial através do comportamento da página (Sucesso/Falha).

### 📁 Módulo: `blind_SQL`

#### Time-Based Blind SQLi (`ataque_time_based.py`)
* **Payload:** `' OR SLEEP(5) -- `
* **Lógica:** Caso a primeira condição da consulta falhe (usuário inexistente), o banco é forçado a avaliar a segunda expressão devido ao operador `OR`. A função `SLEEP(5)` pausa a *thread* de execução do SGBD por exatamente 5 segundos. O sucesso do ataque é mensurado pelo *Round-Trip Time* (RTT) da requisição HTTP.