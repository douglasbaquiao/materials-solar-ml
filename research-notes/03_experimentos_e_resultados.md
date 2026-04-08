# 03 — Log de Experimentos e Resultados

**Formato:** cada entrada segue o padrão data / contexto / resultado / decisão.  
**Propósito:** rastreabilidade científica — o que foi testado, o que foi encontrado,
o que foi decidido a partir disso.

---

## Experimento 001 — Extração inicial e comparação das famílias

**Data:** 2026-03  
**Notebook:** `v1_eda_exploratoria.ipynb`

### Configuração
- Double perovskitas: haleto ∈ {F, Cl, Br, I}, nelements=4, band_gap=(0, 4.0), nsites≤40
- Kesteritas: calcogeneto ∈ {S, Se}, nelements=4, band_gap=(0, 3.5), nsites≤50
- Campos: lista v1 (sem efermi, dielétricos, work_function)

### Decisão
- *(preencher com números reais após rodar)*

---

## Experimento 002 — Revisão dos campos da API

**Data:** 2026-03

### Campos adicionados na v2

| Campo | Relevância | Ação |
|---|---|---|
| `efermi` | Alta — tipo n/p | Adicionado à v2 |
| `weighted_work_function` | Alta — Voc em heterojunções | Adicionado à v2 |
| `e_total`, `e_electronic`, `e_ionic` | Média — ~40% cobertura | Adicionado à v2 |
| `n` (índice de refração) | Alta — reflectância da célula | Adicionado à v2 |
| `possible_species` | Alta — valências na estrutura | Adicionado à v2 |
| `theoretical` | Alta — filtra sem síntese | Adicionado à v2 |
| `has_props` | Alta — guia análises futuras | Adicionado à v2 |
| `database_IDs` | Alta — referência experimental | Adicionado à v2 |

### Decisão
- Criar `extraction.py` com lista canônica; manter v1 para rastreabilidade

---

## Experimento 003 — Estruturação do extraction.py

**Data:** 2026-03  
**Arquivo:** `src/extraction.py`

### Funções implementadas
- `conectar_api()`, `docs_para_df()`, `extrair_familia()`, `adicionar_features()`
- `exportar()` / `carregar()` — separação extração × análise
- `pipeline_completo()` — ponto de entrada único para re-extração

### Decisão de design
- Dicionário `FAMILIAS` — novas famílias sem modificar funções
- Constantes físicas no topo — mudança propagada para todos os notebooks

---

## Experimento 004 — Configuração do ambiente GitHub + Colab

**Data:** 2026-03

### Workflow definido
- Edição e execução: Google Colab
- Versionamento: `Arquivo → Salvar cópia no GitHub` (interface gráfica)
- Chave de API: Colab Secrets; módulos .py via `!wget`

---

## Experimento 005 — EDA estatística e gráfica (Fase 1)

**Data:** 2026-03  
**Notebook:** `v2_eda_campos_expandidos.ipynb`

### Subconjuntos após filtros de qualidade
(`usar_em_analise=True`, não-metais, regime DFT conhecido)

| Família | n subconjunto | n dataset total | Redução |
|---|---|---|---|
| Perovskitas Duplas | 2.719 | 6.033 | ~55% excluído |
| Kesteritas | 234 | 4.367 | ~95% excluído |

### Candidatos (após filtros + e_hull < 0.05 eV/átomo)

| Critério | Perovskitas Duplas | Kesteritas |
|---|---|---|
| PV ampliado (0.7–2.0 eV) | 355 | 31 |
| IBSC ampliado (1.4–3.2 eV) | 506 | 25 |
| PV — estrutura confirmada | 227 | 24 |
| IBSC — estrutura confirmada | 346 | 16 |

### Achados principais
- PD: distribuição de gap aproximadamente plana 0–4 eV — positivo para triagem
- K: mediana zero por subestimação GGA severa; triagem por gap inviável sem HSE06
- GGA e GGA+U têm médias similares nas PD por viés composicional, não física igual
- Ausência de correlação gap × formação em ambas as famílias — positivo para triagem
- nsites × volume nas K: r=0.91 — redundantes como features ML

### Figuras geradas para o artigo

| Figura | Status |
|---|---|
| Band gap por categoria estrutural (boxplot horizontal) | Pronto |
| Distribuição gap não-metais (comparação famílias) | Pronto |
| Estabilidade termodinâmica (log + barra hull=0) | Pronto |
| Energia formação vs. gap (cores discretas) | Pronto |
| Sistema cristalino (barras empilhadas) | Código gerado, aguarda execução |
| Nível de Fermi por regime | Código gerado, aguarda execução |
| Mapa de correlação Pearson | Pronto |

---

## Experimento 006 — Descritores composicionais Magpie (Fase 2)

**Data:** 2026-03  
**Notebook:** `v3_descritores_magpie.ipynb`  
**Biblioteca:** matminer 0.10.0 (132 features — versões anteriores: 114)

### Subconjuntos de trabalho

| Subconjunto | Critério | PD (n) | K (n) |
|---|---|---|---|
| Filtrado | usar_em_analise + não-metal + hull<0.05 | 924 | 97 |
| Geral | usar_em_analise + não-metal (sem hull) | 1.850 | 117 |

Categoria "outra" excluída de ambos. Dois subconjuntos revelam física complementar:
filtrado → features eletrônicas dominam; geral → features de tamanho/período dominam.

### Seleção de features (dois passos: variância < 0.01 → colinearidade > 0.95)

| Subconjunto | Inicial | Final |
|---|---|---|
| PD filtrado | 132 | 88 |
| K filtrado | 132 | 81 |
| PD geral | 132 | 88 |
| K geral | 132 | 86 |
| Comuns PD/K gerais | — | 78 |

### Correlações com band_gap — subconjunto filtrado (top 6 por |corr_PD|)

| Feature | corr_PD | corr_K | Sinal igual |
|---|---|---|---|
| mean NdValence | -0.238 | -0.606 | Sim |
| mean NValence | -0.218 | -0.473 | Sim |
| avg_dev Column | +0.186 | +0.349 | Sim |
| avg_dev NdValence | -0.171 | +0.291 | **Não** |
| avg_dev CovalentRadius | +0.170 | +0.407 | Sim |
| mode MeltingT | -0.170 | -0.513 | Sim |

### Correlações por regime — PD filtrado

| Feature | corr_GGA | corr_GGA+U | Padrão |
|---|---|---|---|
| avg_dev CovalentRadius | +0.170 | +0.166 | **Estável** |
| avg_dev NdValence | -0.157 | -0.178 | **Estável** |
| mean NValence | -0.250 | +0.155 | Inversão |
| mean Number | -0.191 | +0.173 | Inversão |

Features de tamanho/dispersão estáveis entre regimes; features de elétrons de
valência e número atômico invertem sinal — causado por diferença composicional
entre grupos GGA e GGA+U, não por mudança de física.

### Discriminação candidatos PV vs IBSC — PD

Candidatos PV vs outros: diferenças interpretáveis (mean NValence +23%,
avg_dev CovalentRadius -14%, avg_dev Column -20%).

Candidatos IBSC vs outros: diferenças < 5% em quatro condições independentes.
**Ausência de discriminação composicional para IBSC é achado robusto.**

### Datasets exportados

| Arquivo | n | Features |
|---|---|---|
| `data/fase2/perovskita_ml_ready.csv` | 924 | 88 Magpie + fase1 + dummies regime |
| `data/fase2/kesterita_ml_ready.csv` | 97 | 81 Magpie + fase1 + dummies regime |

---

## Experimento 007 — Modelos de Machine Learning (Fase 3)

**Data:** 2026-03  
**Notebooks:** `v4_modelos_ml.ipynb` + `v4_secao8_otimizacao.ipynb` (pendente execução)

### Configuração
- Base: `perovskita_ml_ready.csv` (n=924) e `kesterita_ml_ready.csv` (n=97)
- CV: RepeatedStratifiedKFold (5×5 para PD; 5×10 para K)
- `class_weight="balanced"` em todos os classificadores

### Resultados — Classificação PV

**Perovskitas Duplas (n=924, pos=203, ~22%):**

| Modelo | AUC | F1 (thr=0.50) |
|---|---|---|
| Logística (baseline) | 0.794 ± 0.035 | 0.545 ± 0.044 |
| Random Forest | 0.869 ± 0.020 | 0.626 ± 0.056 |

Desempenho por regime (RF, predições OOF):

| Regime | n | AUC | F1 |
|---|---|---|---|
| GGA | 737 | 0.884 | 0.654 |
| GGA+U | 172 | 0.723 | 0.263 |
| HSE06 | 15 | 0.909 | 0.900 |

**Kesteritas (n=97, pos=15, ~15%):**

| Modelo | AUC | F1 |
|---|---|---|
| Logística | 0.845 ± 0.118 | 0.438 ± 0.224 |
| Random Forest | 0.802 ± 0.130 | 0.448 ± 0.265 |

Logística supera RF — modelo mais simples generaliza melhor com n=97.
Resultados indicativos apenas dado n pequeno e subestimação GGA.

### Resultados — Classificação IBSC

RF AUC=0.813 ± 0.036 — resultado inesperado (esperado ~0.50 dado achados Fase 2).
Interpretação: RF captura combinações não-lineares de features. Pode estar capturando
posição no espaço de gap (região 1.8–2.6 eV) mais do que física IBSC específica.
Verificação com XGBoost pendente (v4_secao8_otimizacao.ipynb).

### Resultados — SHAP (classificação PV, PD, RF treinado no conjunto completo)

Top 5 features por |SHAP| médio:
1. mean NValence (0.0196)
2. avg_dev Column (0.0187)
3. mean Column (0.0173)
4. avg_dev SpaceGroupNumber (0.0167) — propriedade do elemento puro, não do material
5. avg_dev NUnfilled (0.0162)

avg_dev CovalentRadius: rank 12 | avg_dev NdValence: rank 26.
Diferença de ranking entre correlação linear (Fase 2) e SHAP (Fase 3) é esperada.

Nota sobre avg_dev SpaceGroupNumber: é estatística do grupo espacial do **elemento
puro** (estado fundamental do elemento isolado), não do material de interesse.
Propriedade composicional legítima com interpretação indireta — não é contaminante.

### Resultados — PCA dos candidatos (n=648, janelas ampliadas PD)

PC1=19.2%, PC2=18.0%, acumulado=37.2%. Necessárias 10 componentes para 74%.

Loadings: PC1 = tamanho/período (GSvolume_pa, CovalentRadius, MeltingT).
PC2 = elétrons de valência (NValence, Electronegativity, Column).

Separação visual clara por **regime** e **estrutura** no PCA e UMAP.
Separação por **janela de gap** (PV vs IBSC) **não aparece** em nenhuma projeção.
Confirma visualmente a ausência de discriminação composicional para IBSC.

Confundimento documentado: estrutura esperada e regime_calc estão correlacionados
(GGA+U mais prevalente em relacionadas — ratio 2:1 vs 6:1 nas confirmadas).

### Resultados — Top candidatos identificados

**PV (PD confirmadas, hull=0): n=72 candidatos**

Dominados pela série REB₂XO₄ (RE = terra rara, Bi, haleto, O) — óxidos-halogenetos
em camadas (tipo Aurivillius/Sillén), não double perovskitas clássicas A₂B'B''X₆.
is_gap_direct=False para todos, gap 1.2–1.45 eV, probabilidades 0.97–0.998.

Nota para o artigo: reportar como "compostos quaternários halogenados com gap na
janela PV identificados pela triagem", não como "double perovskitas".

Exemplos: DyBi₂BrO₄ (proba=0.998), HoBi₂BrO₄ (0.997), TbBi₂IO₄ (0.996),
HoBi₂IO₄ (0.995, HSE06), TbBi₂BrO₄ (0.995).

**IBSC (PD confirmadas, hull=0): n=60 candidatos**

Mais diversa composicionalmente: fluoretos simples (Sr₂BN₂F, Ba₂SnS₃F₂),
fluoretos com metais de transição (Rh, Ir, Mo, Mn, V, Fe), haletos mistos.
Maioria com is_gap_direct=True — positivo para aplicações IBSC.
GGA+U (CsZnFeF₆, CsMnVF₆, CsVFeF₆, Na₂VNiF₇) requerem cautela adicional.

### Resultados — Regressão de gap

| Modelo | R² teste | MAE (eV) | Gap overfitting |
|---|---|---|---|
| Ridge completo | 0.323 ± 0.084 | 0.690 ± 0.047 | 0.139 |
| RF completo | 0.583 ± 0.051 | 0.492 ± 0.036 | 0.265 |
| RF GGA | 0.646 ± 0.037 | 0.454 ± 0.014 | 0.222 |
| RF GGA+U | 0.273 ± 0.050 | 0.639 ± 0.043 | 0.449 |
| Ridge kesteritas | 0.527 ± 0.219 | 0.404 ± 0.101 | 0.432 |

R²=0.646 para GGA consistente com literatura (features composicionais apenas).
GGA+U com R²=0.273 — parâmetro U não captado pelo Magpie é causa identificada.
Kesteritas: overfitting severo — resultado não utilizável no artigo.

### Resultados — Validação HSE06

13/15 concordâncias (87%) entre classificador PV e gaps HSE06.
Erros em compostos atípicos: Cs₂ScAuI₆ (Au no sítio B'' — raro no treino)
e Cs₂KMnF₆ (GGA+U — regime de menor desempenho documentado).
Probabilidades calibradas são mais informativas que threshold fixo para priorização.

### Pendências — Seção 8 (otimização, notebook criado, execução pendente)

| Item | Notebook | Status |
|---|---|---|
| Threshold ótimo via curva PR | v4_secao8_otimizacao.ipynb | Pendente |
| XGBoost com Optuna (50 trials) | v4_secao8_otimizacao.ipynb | Pendente |
| Voting Classifier (RF+XGB+LR) | v4_secao8_otimizacao.ipynb | Pendente |
| Stacking (RF+XGB+GB → LR) | v4_secao8_otimizacao.ipynb | Pendente |
| ElasticNet / Lasso para regressão | v4_secao8_otimizacao.ipynb | Pendente |
| XGBoost regressor otimizado | v4_secao8_otimizacao.ipynb | Pendente |
| GGA+U com features robustas apenas | v4_secao8_otimizacao.ipynb | Pendente |
| Calibração Platt + lista final | v4_secao8_otimizacao.ipynb | Pendente |

---

## Template para novos experimentos

```
## Experimento XXX — [título]

**Data:** AAAA-MM  
**Notebook/Arquivo:**
**Commit:**

### Configuração
-

### Resultados
| Métrica | Valor |
|---|---|
| | |

### Observações
-

### Decisão
-
```
