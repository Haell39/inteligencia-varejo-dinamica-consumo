# Plano de Ação: Inteligência de Varejo e Dinâmica de Consumo

## 1. Escopo Técnico
O projeto visa analisar a correlação entre indicadores macroeconômicos (IPCA) e a performance operacional/comercial de um ecossistema de e-commerce (Olist). O objetivo é identificar padrões de sensibilidade de consumo e gargalos logísticos regionais.

## 2. Processamento e Ingestão
- **Dados Externos:** Coleta automatizada de séries históricas do IPCA via API SIDRA (IBGE) para o período 2016-2018.
- **Tratamento de Dados:** Limpeza, normalização e integração de múltiplos datasets (Orders, Items, Customers, Reviews, Products).
- **Enriquecimento:** Criação de features de performance (`delivery_performance`, `lead_time`) e agregação temporal (`Sell-out` mensal).

## 3. Trilhas de Análise
- **Logística e Satisfação:** Análise do impacto da Ruptura (atrasos) no NPS (calculado via `review_score`).
- **Geointeligência:** Estudo comparativo de eficiência logística (Lead Time e Frete) entre regiões Nordeste (PE) e Sudeste (SP).
- **Dinâmica de Preços:** Cruzamento de volume de vendas com índices inflacionários para medição de elasticidade por categorias.

## 4. Modelagem e Validação
- Implementação de modelos estatísticos ou de Machine Learning (Scikit-Learn) para segmentação de comportamento e predição de tendências de consumo sob variações econômicas.