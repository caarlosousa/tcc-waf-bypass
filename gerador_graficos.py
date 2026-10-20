import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ==========================================
# CONFIGURAÇÕES DE ESTILO ACADÊMICO (Padrão TCC)
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 300,  # Alta resolução para o PDF do LaTeX
})

COR_SEM_WAF = '#5cb85c'
COR_MODSEC = '#5bc0de'
COR_AWS = '#d9534f'

# ==========================================
# 1. CARREGAMENTO E PREPARAÇÃO DOS DADOS
# ==========================================
try:
    df_aws = pd.read_csv('dados_tcc_AWS_WAF.csv')
    df_modsec = pd.read_csv('dados_tcc_ModSecurity_Local.csv')
    df_sem_waf = pd.read_csv('dados_tcc_Sem_WAF.csv')
except FileNotFoundError as e:
    print(f"Erro: Arquivo não encontrado. {e}")
    exit()

df_aws['Ambiente'] = 'AWS WAF (Edge)'
df_modsec['Ambiente'] = 'ModSecurity (Embedded)'
df_sem_waf['Ambiente'] = 'Sem WAF (Controle)'

# Limpeza numérica (payloads em bypass, ex. 'bypass', viram NaN e são descartados nos gráficos)
for df in (df_aws, df_modsec, df_sem_waf):
    df['Tamanho (KB)'] = pd.to_numeric(df['Tamanho (KB)'], errors='coerce')
    df['Latência Média (ms)'] = pd.to_numeric(df['Latência Média (ms)'], errors='coerce')

# Base LOCAL (comparável): Sem WAF + ModSecurity, mesmo host, mesma rede.
# O AWS WAF fica de fora dessas duas figuras por envolver rede pública e
# hardware distinto (instância t3.micro) — ver Seção 5.4.4 do TCC.
df_local = pd.concat([df_sem_waf, df_modsec], ignore_index=True).dropna(
    subset=['Tamanho (KB)', 'Latência Média (ms)']
)

LIMITE_MODSEC_KB = 128  # limite nativo do ModSecurity (SecRequestBodyLimit)

# ==========================================
# GRÁFICO 1: grafico1_comparativo_principal
# Linha completa, Sem WAF vs ModSecurity, 1 KB a 130 KB
# ==========================================
plt.figure(figsize=(10, 6))

sns.lineplot(
    data=df_local,
    x='Tamanho (KB)',
    y='Latência Média (ms)',
    hue='Ambiente',
    style='Ambiente',
    markers=True,
    dashes=False,
    palette={'Sem WAF (Controle)': COR_SEM_WAF, 'ModSecurity (Embedded)': COR_MODSEC},
    linewidth=2,
    markersize=7,
)

plt.axvline(
    x=LIMITE_MODSEC_KB,
    color='black',
    linestyle='--',
    linewidth=1.2,
    label=f'Limite nativo ModSecurity ({LIMITE_MODSEC_KB} KB)',
)

plt.title('Latência Local: Sem WAF vs. ModSecurity (1 KB a 130 KB)')
plt.xlabel('Tamanho do Payload (KB)')
plt.ylabel('Latência Média (ms)')
plt.legend(title=None, loc='upper left')
plt.tight_layout()
plt.savefig('grafico1_comparativo_principal.pdf')
print("[+] grafico1_comparativo_principal.pdf gerado.")
plt.close()

# ==========================================
# GRÁFICO 2: grafico2_zoom_modsec_vs_semwaf
# Zoom 0-50 ms, com área sombreada representando o overhead
# ==========================================
pivot = (
    df_local.pivot_table(index='Tamanho (KB)', columns='Ambiente', values='Latência Média (ms)')
    .sort_index()
    .dropna()
)

plt.figure(figsize=(9, 6))

plt.plot(pivot.index, pivot['Sem WAF (Controle)'], color=COR_SEM_WAF, marker='o',
         linewidth=2, label='Sem WAF (Controle)')
plt.plot(pivot.index, pivot['ModSecurity (Embedded)'], color=COR_MODSEC, marker='o',
         linewidth=2, label='ModSecurity (Embedded)')

plt.fill_between(
    pivot.index,
    pivot['Sem WAF (Controle)'],
    pivot['ModSecurity (Embedded)'],
    color=COR_MODSEC,
    alpha=0.2,
    label='Overhead de inspeção',
)

plt.ylim(0, 50)
plt.title('Overhead de Inspeção do ModSecurity (Zoom 0–50 ms)')
plt.xlabel('Tamanho do Payload (KB)')
plt.ylabel('Latência Média (ms)')
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig('grafico2_zoom_modsec_vs_semwaf.pdf')
print("[+] grafico2_zoom_modsec_vs_semwaf.pdf gerado.")
plt.close()

# ==========================================
# GRÁFICO 3: grafico3_overhead_modsecurity
# Overhead absoluto (ModSecurity - Sem WAF), colorido por faixa de impacto
# ==========================================
pivot['Overhead (ms)'] = pivot['ModSecurity (Embedded)'] - pivot['Sem WAF (Controle)']


def faixa_cor(overhead_ms):
    if overhead_ms < 10:
        return '#5bc0de'   # baixo
    elif overhead_ms <= 25:
        return '#f0ad4e'   # médio
    else:
        return '#d9534f'   # alto


cores_barras = [faixa_cor(v) for v in pivot['Overhead (ms)']]

plt.figure(figsize=(9, 6))
ax = plt.gca()
bars = ax.bar(
    pivot.index.astype(str),
    pivot['Overhead (ms)'],
    color=cores_barras,
    edgecolor='black',
)

for bar in bars:
    height = bar.get_height()
    ax.annotate(
        f"{height:.1f} ms",
        (bar.get_x() + bar.get_width() / 2, height),
        ha='center', va='bottom',
        xytext=(0, 3), textcoords='offset points',
        fontweight='bold', fontsize=9,
    )

# Legenda manual das faixas
from matplotlib.patches import Patch
legenda_faixas = [
    Patch(facecolor='#5bc0de', edgecolor='black', label='Overhead baixo (< 10 ms)'),
    Patch(facecolor='#f0ad4e', edgecolor='black', label='Overhead médio (10–25 ms)'),
    Patch(facecolor='#d9534f', edgecolor='black', label='Overhead alto (> 25 ms)'),
]
ax.legend(handles=legenda_faixas, loc='upper left')

plt.title('Overhead de Inspeção do ModSecurity em Relação ao Ambiente Sem WAF')
plt.xlabel('Tamanho do Payload (KB)')
plt.ylabel('Overhead (ms)')
plt.tight_layout()
plt.savefig('grafico3_overhead_modsecurity.pdf')
print("[+] grafico3_overhead_modsecurity.pdf gerado.")
plt.close()

# ==========================================
# REFERÊNCIA: dados do AWS WAF para a Tabela 5.4 (não plotados)
# ==========================================
df_aws_validos = df_aws.dropna(subset=['Tamanho (KB)', 'Latência Média (ms)'])
print("\n[i] Valores do AWS WAF (uso na Tabela de latência via Internet pública, não na figura):")
print(df_aws_validos[['Tamanho (KB)', 'Latência Média (ms)']].to_string(index=False))