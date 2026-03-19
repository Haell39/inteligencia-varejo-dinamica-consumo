# Inteligência de Varejo: Dados, Logística e Estratégia 📊

[![Website](https://img.shields.io/badge/Project-Website-blue?style=for-the-badge&logo=netlify)](https://inteligenciavarejodeploy.netlify.app/)

Uma exploração analítica sobre o ecossistema de e-commerce brasileiro, integrando dados reais da **Olist** com indicadores macroeconômicos do **IBGE**.

## 🎯 Objetivo

Entender o impacto de inflação, logística e comportamento do cliente no desempenho de vendas (sell-out) e experiência do consumidor.

---

## 📊 Principais Insights

- 🚚 **Logística > Inflação**  
  Lead Time impacta mais a satisfação (-0.33) do que o IPCA  
  → Inflação não explica vendas no curto prazo :contentReference[oaicite:0]{index=0}

- 📍 **Custo Nordeste**  
  PE: +116% Lead Time | +107% frete vs SP :contentReference[oaicite:1]{index=1}

- ⭐ **Atraso reduz satisfação pela metade**  
  4.29★ → 2.27★ (-47%) :contentReference[oaicite:2]{index=2}

- 👥 **Baixa retenção**  
  ~0–1% após 1 mês | ~50% da base em risco :contentReference[oaicite:3]{index=3}

---

## 🤖 Modelos

- **Classificação (atraso)**  
  Acurácia: 96.7% | Recall: 64%  
  → Alerta precoce de ruptura

- **Regressão (satisfação)**  
  MAE: 0.878 | R²: 0.22 (+13% vs baseline)  
  → Útil para identificar risco, mas limitado

---

## 🎯 Direcionamento

1. Priorizar **redução de Lead Time**
2. Implementar **alerta de atrasos (ML)**
3. Atuar em **retenção (clientes em risco)**

---

## 📌 Conclusão

A eficiência logística é o principal driver de performance no e-commerce analisado, mais relevante que fatores macroeconômicos como inflação.
