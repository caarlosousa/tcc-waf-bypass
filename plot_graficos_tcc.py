import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações de estilo acadêmico (Padrão Artigo/TCC)
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 300, # Alta resolução para o PDF do LaTeX
})

# ==========================================
# 1. CARREGAMENTO E PREPARAÇÃO DOS DADOS
# ==========================================
try:
    # Ajuste o separador se o seu arquivo usar ponto e vírgula sep=';'
    df_aws = pd.read_csv('dados_tcc_AWS_WAF.csv')
    df_modsec = pd.read_csv('dados_tcc_ModSecurity_Local.csv')
    df_sem_waf = pd.read_csv('dados_tcc_Sem_WAF.csv')
except FileNotFoundError as e:
    print(f"Erro: Arquivo não encontrado. {e}")
    exit()

# Adicionando a coluna de Ambiente para diferenciar no gráfico
df_aws['Ambiente'] = 'AWS WAF (Edge)'
df_modsec['Ambiente'] = 'ModSec (Embedded)'
df_sem_waf['Ambiente'] = 'Sem WAF (Controle)'

# Juntando tudo em um único DataFrame
df_completo = pd.concat([df_aws, df_modsec, df_sem_waf], ignore_index=True)

# Limpeza: garantindo que as colunas numéricas sejam tratadas como números
# Caso o CSV tenha gerado '140' como string, isso resolve:
df_completo['Tamanho (KB)'] = pd.to_numeric(df_completo['Tamanho (KB)'], errors='coerce')
df_completo['Latência Média (ms)'] = pd.to_numeric(df_completo['Latência Média (ms)'], errors='coerce')

# ==========================================
# GRÁFICO: O Trade-off Arquitetural (Carga Pesada)
# ==========================================
# Filtrando apenas as requisições grandes (assumindo que 140 ou 143 representa os 140KB)
# ==========================================
# GRÁFICO: O Trade-off Arquitetural (Carga Volumétrica)
# ==========================================
# Pegando automaticamente o maior tamanho de payload testado (ex: 10 KB)
tamanho_maximo = df_completo['Tamanho (KB)'].max()
df_pesado = df_completo[df_completo['Tamanho (KB)'] == tamanho_maximo].copy()

if not df_pesado.empty:
    plt.figure(figsize=(9, 6))
    
    # Criando um gráfico de barras comparativo
    sns.barplot(
        data=df_pesado, 
        x='Ambiente', 
        y='Latência Média (ms)',
        palette=['#d9534f', '#5bc0de', '#5cb85c'],
        edgecolor='black',
        capsize=0.1
    )
    
    plt.title(f'Impacto Computacional da Inspeção (Payload de {tamanho_maximo} KB)')
    plt.ylabel('Tempo de Processamento (ms)')
    plt.xlabel('Cenário Arquitetural')
    
    # Adicionando os valores em cima das barras
    ax = plt.gca()
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.1f} ms", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 9), 
                    textcoords='offset points',
                    fontweight='bold')

    plt.tight_layout()
    plt.savefig('grafico_tradeoff_volumetrico.pdf')
    print("[+] SUCESSO! Gráfico gerado: grafico_tradeoff_volumetrico.pdf")
else:
    print("Aviso: Dados não encontrados.")