# ==============================================================================
# 2.1 Coleta de Dados IBGE (IPCA)
# Substitua TODO o código desta célula por este (usaremos requests direto, sem sidrapy para não travar):
# ==============================================================================
import requests
import pandas as pd

print("Coletando dados do SIDRA via requests...")
# Montando período 201601 a 201812
periodos = "|".join([f"{y}{m:02d}" for y in range(2016, 2019) for m in range(1, 13)])
url = f"https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/{periodos}/variaveis/63?localidades=N1[all]"

response = requests.get(url)
data = response.json()

resultados = data[0]['resultados'][0]['series'][0]['serie']
ipca = pd.DataFrame(list(resultados.items()), columns=['Mês (Código)', 'Valor'])
ipca['Mês (Código)'] = pd.to_numeric(ipca['Mês (Código)'])
ipca['Valor'] = pd.to_numeric(ipca['Valor'])

print("IPCA Carregado com Sucesso!")
display(ipca.head())


# ==============================================================================
# 2.2 Coleta de Dados Olist
# Substitua TODO o código desta célula por este (que faz o merge e cálculos que faltavam):
# ==============================================================================
print("Carregando datasets da Olist (isso pode levar alguns segundos)...")
orders = pd.read_csv('../data/raw/olist_orders_dataset.csv')
order_items = pd.read_csv('../data/raw/olist_order_items_dataset.csv')
reviews = pd.read_csv('../data/raw/olist_order_reviews_dataset.csv')
customers = pd.read_csv('../data/raw/olist_customers_dataset.csv')

print("Tratando dados logísticos (Tempo de Entrega e Ruptura)...")
# Apenas pedidos entregues
orders = orders[orders['order_status'] == 'delivered'].copy()

# Conversão de datas
time_cols = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
for col in time_cols:
    orders[col] = pd.to_datetime(orders[col])

# Criação das variáveis de Ruptura (Atraso) e Lead Time    
orders['delivery_delay_days'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days
orders['lead_time_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days

# Meses para cruzamento com IPCA (ano + mês)
orders['Mes_Codigo'] = orders['order_purchase_timestamp'].dt.year * 100 + orders['order_purchase_timestamp'].dt.month

# Merges para trazer Estado, Nota (Review) e Frete para a tabela orders
orders = orders.merge(customers[['customer_id', 'customer_state']], on='customer_id', how='inner')

reviews_clean = reviews.sort_values('review_creation_date').drop_duplicates('order_id', keep='last')
orders = orders.merge(reviews_clean[['order_id', 'review_score']], on='order_id', how='left')

order_totals = order_items.groupby('order_id').agg({'price':'sum', 'freight_value':'sum'}).reset_index()
orders = orders.merge(order_totals, on='order_id', how='inner')

print("Dados da Olist Tratados e Prontos para Análise!")
display(orders.head(3))


# ==============================================================================
# 3.1 Custo Pernambuco vs São Paulo
# Substitua TODA a célula 3.1 por este código:
# ==============================================================================
import matplotlib.pyplot as plt
import seaborn as sns

# Filtro destinos PE e SP
pe_sp_orders = orders[orders['customer_state'].isin(['PE', 'SP'])].copy()

# Agrupamento
custo_pe = pe_sp_orders.groupby('customer_state').agg(
    Media_Frete=('freight_value', 'mean'),
    Media_Lead_Time_Dias=('lead_time_days', 'mean')
).reset_index()

# Cores CX Trade
cx_colors = ["#003366", "#0066cc", "#4da6ff", "#cccccc"]

# Gráficos
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

sns.barplot(data=custo_pe, x='customer_state', y='Media_Frete', ax=ax[0], palette=[cx_colors[2], cx_colors[0]])
ax[0].set_title('Frete Médio: PE vs SP', fontsize=14, fontweight='bold')
ax[0].set_ylabel('Valor do Frete (R$)', fontsize=12)
ax[0].set_xlabel('Estado do Cliente')

sns.barplot(data=custo_pe, x='customer_state', y='Media_Lead_Time_Dias', ax=ax[1], palette=[cx_colors[2], cx_colors[0]])
ax[1].set_title('Lead Time Médio (Dias): PE vs SP', fontsize=14, fontweight='bold')
ax[1].set_ylabel('Tempo de Espera (Dias)', fontsize=12)
ax[1].set_xlabel('Estado do Cliente')

plt.tight_layout()
plt.show()


# ==============================================================================
# 3.2 Impacto da Ruptura no Review Score
# Substitua TODA a célula 3.2 (Se tiver apenas comentários) por este bloco abaixo:
# ==============================================================================
import numpy as np

# Classificar entrega com atraso (ruptura) vs no prazo
orders['Status_Entrega'] = np.where(orders['delivery_delay_days'] > 0, 'Atrasado (Ruptura)', 'No Prazo')
ruptura_score = orders.dropna(subset=['review_score']).groupby('Status_Entrega')['review_score'].mean().reset_index()

plt.figure(figsize=(8, 5))
sns.barplot(data=ruptura_score, x='Status_Entrega', y='review_score', palette=[cx_colors[1], cx_colors[3]])
plt.title('Impacto da Ruptura Logística na Satisfação do Cliente (Sell-out)', fontsize=14, fontweight='bold')
plt.ylabel('Nota Média (1 a 5)', fontsize=12)
plt.xlabel('')
plt.ylim(0, 5)

for i, v in enumerate(ruptura_score['review_score']):
    plt.text(i, v + 0.1, f'{v:.2f}', ha='center', fontweight='bold', fontsize=12)
    
plt.show()


# ==============================================================================
# 3.3 Sensibilidade de Vendas ao IPCA
# Substitua TODA a célula vazia da 3.3 por este bloquinho:
# ==============================================================================
# Agrupamento Vendas Olist por Mês
vendas_mes = orders.groupby('Mes_Codigo').size().reset_index(name='Volume_Vendas')

# Cruzamento com IPCA (que baixamos no passo 2.1)
df_ipca_vendas = vendas_mes.merge(ipca[['Mês (Código)', 'Valor']], left_on='Mes_Codigo', right_on='Mês (Código)', how='inner')

# Formatando coluna de Mês para exibição (Ex: 201701 -> 2017-01)
df_ipca_vendas['Mês_Formatado'] = df_ipca_vendas['Mes_Codigo'].astype(str).str[:4] + '-' + df_ipca_vendas['Mes_Codigo'].astype(str).str[4:]

# Gráfico de eixo duplo
fig, ax1 = plt.subplots(figsize=(14, 6))

color1 = cx_colors[0]
ax1.set_xlabel('Mês-Ano', fontsize=12)
ax1.set_ylabel('Volume de Vendas E-commerce', color=color1, fontsize=12, fontweight='bold')
sns.lineplot(data=df_ipca_vendas, x='Mês_Formatado', y='Volume_Vendas', color=color1, marker='o', ax=ax1, linewidth=2)
ax1.tick_params(axis='y', labelcolor=color1)
ax1.tick_params(axis='x', rotation=45)

# Segundo eixo (IPCA)
ax2 = ax1.twinx()
color2 = '#ff4da6' # Rosa/Vermelho para alertar a Inflação
ax2.set_ylabel('IPCA Variação Mensal (%)', color=color2, fontsize=12, fontweight='bold')
sns.lineplot(data=df_ipca_vendas, x='Mês_Formatado', y='Valor', color=color2, marker='X', ax=ax2, linestyle='--', linewidth=2)
ax2.tick_params(axis='y', labelcolor=color2)

plt.title('Elasticidade: Vendas E-commerce vs Inflação IPCA (2017-2018)', fontsize=15, fontweight='bold')
fig.tight_layout()
plt.show()


# ==============================================================================
# CÓDIGO UNIFICADO PARA A CÉLULA:
# "3. A Grande Revelação: O impacto da Ruptura na satisfação do cliente em Pernambuco"
# (Esse é o código que faltava e substitui exatamente aquela célula com os comentários soltos)
# ==============================================================================
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Cores CX Trade
cx_colors = ["#003366", "#0066cc", "#4da6ff", "#cccccc"]

print("--- IMPACTO DA RUPTURA E CUSTO PERNAMBUCO ---")
# Filtro destinos PE e SP para comparar logística
pe_sp_orders = orders[orders['customer_state'].isin(['PE', 'SP'])].copy()

# Agrupamento 
custo_pe = pe_sp_orders.groupby('customer_state').agg(
    Media_Frete=('freight_value', 'mean'),
    Media_Lead_Time_Dias=('lead_time_days', 'mean')
).reset_index()

display(custo_pe)

# Classificar entrega com atraso (ruptura) vs no prazo
orders['Status_Entrega'] = np.where(orders['delivery_delay_days'] > 0, 'Atrasado (Ruptura)', 'No Prazo')
ruptura_score = orders.dropna(subset=['review_score']).groupby('Status_Entrega')['review_score'].mean().reset_index()

# Gráfico Duplo (Lead Time Regional e Impacto da Ruptura)
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

sns.barplot(data=custo_pe, x='customer_state', y='Media_Lead_Time_Dias', ax=ax[0], palette=[cx_colors[2], cx_colors[0]])
ax[0].set_title('Lead Time Físico (Dias): PE vs SP', fontsize=14, fontweight='bold')
ax[0].set_ylabel('Tempo de Espera (Dias)', fontsize=12)
ax[0].set_xlabel('Estado do Cliente')

sns.barplot(data=ruptura_score, x='Status_Entrega', y='review_score', ax=ax[1], palette=[cx_colors[1], cx_colors[3]])
ax[1].set_title('Impacto da Ruptura Logística na Satisfação (Sell-out)', fontsize=14, fontweight='bold')
ax[1].set_ylabel('Nota Média (1 a 5)', fontsize=12)
ax[1].set_xlabel('')
ax[1].set_ylim(0, 5)

for i, v in enumerate(ruptura_score['review_score']):
    ax[1].text(i, v + 0.1, f'{v:.2f}', ha='center', fontweight='bold', fontsize=12)
    
plt.tight_layout()
plt.show()

print("\n--- CORRELAÇÃO DE VENDAS COM IPCA (CATEGORIAS CHAVE) ---")
# Trazer o nome das categorias para os pedidos (traduzido para o ingles oficial e dps cruzado)
products_df = pd.read_csv('../data/raw/olist_products_dataset.csv')
translation_df = pd.read_csv('../data/raw/product_category_name_translation.csv')

# Mergiando produtos para pegar a categoria original
orders_with_cat = orders.merge(products_df[['product_id', 'product_category_name']], on='product_id', how='left')

# Focar em categorias sensíveis (Alimentação e Utilidades de Residência)
# Exemplos no dataset da Olist: "utilidades_domesticas", "alimentos_bebidas", "cama_mesa_banho", "moveis_decoracao"
categorias_foco = ['utilidades_domesticas', 'alimentos_bebidas', 'cama_mesa_banho']
orders_foco = orders_with_cat[orders_with_cat['product_category_name'].isin(categorias_foco)]

# Agrupando Vendas Olist por Mês dessas categorias
vendas_cat_mes = orders_foco.groupby('Mes_Codigo').size().reset_index(name='Volume_Vendas')

# Cruzamento com IPCA 
df_ipca_cat = vendas_cat_mes.merge(ipca[['Mês (Código)', 'Valor']], left_on='Mes_Codigo', right_on='Mês (Código)', how='inner')
df_ipca_cat['Mês_Formatado'] = df_ipca_cat['Mes_Codigo'].astype(str).str[:4] + '-' + df_ipca_cat['Mes_Codigo'].astype(str).str[4:]

# Gráfico de eixo duplo sensibilidade Categoria Foco vs IPCA
fig, ax1 = plt.subplots(figsize=(14, 6))
color1 = cx_colors[0]
ax1.set_xlabel('Mês-Ano', fontsize=12)
ax1.set_ylabel('Volume Vendas (Residência & Alimentos)', color=color1, fontsize=12, fontweight='bold')
sns.lineplot(data=df_ipca_cat, x='Mês_Formatado', y='Volume_Vendas', color=color1, marker='o', ax=ax1, linewidth=2)
ax1.tick_params(axis='y', labelcolor=color1)
ax1.tick_params(axis='x', rotation=45)

ax2 = ax1.twinx()
color2 = '#ff4da6' 
ax2.set_ylabel('IPCA Variação Mensal (%)', color=color2, fontsize=12, fontweight='bold')
sns.lineplot(data=df_ipca_cat, x='Mês_Formatado', y='Valor', color=color2, marker='X', ax=ax2, linestyle='--', linewidth=2)
ax2.tick_params(axis='y', labelcolor=color2)

plt.title('Sensibilidade da Demanda em Categoria Base (Alimentos/Residência) ao IPCA', fontsize=15, fontweight='bold')
fig.tight_layout()
plt.show()
