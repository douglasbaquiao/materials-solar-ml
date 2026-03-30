# 03 — Log de Experimentos e Resultados

**Formato:** cada entrada segue o padrão data / contexto / resultado / decisão.  
**Propósito:** rastreabilidade científica — o que foi testado, o que foi encontrado,
o que foi decidido a partir disso.

---

## Experimento 001 — Extração inicial e comparação das famílias

**Data:** 2026-03  
**Notebook:** `v1_eda_exploratoria.ipynb`  
**Commit:** *(adicionar hash após push)*

### Configuração
- Double perovskitas: haleto ∈ {F, Cl, Br, I}, nelements=4, band_gap=(0, 4.0), nsites≤40
- Kesteritas: calcogeneto ∈ {S, Se}, nelements=4, band_gap=(0, 3.5), nsites≤50
- Campos: lista v1 (sem efermi, dielétricos, work_function)

### Resultados
*(preencher com números reais após rodar)*

| Métrica | Double Perovskitas | Kesteritas |
|---|---|---|
| Total extraído | — | — |
| Candidatos PV (1.0–1.8 eV) | — | — |
| Candidatos IBSC (1.8–2.6 eV) | — | — |
| Termodinâmicamente estáveis (hull=0) | — | — |
| Quasi-estáveis (<50 meV) | — | — |
| Gap direto (% dos não-metais) | — | — |
| Sistema cristalino dominante | — | — |

### Observações
- *(registrar aqui qualquer resultado inesperado durante a execução)*
- *(anotar materiais específicos que chamaram atenção)*

### Decisão
- *(o que foi decidido a partir desta rodada)*

---

## Experimento 002 — Revisão dos campos da API

**Data:** 2026-03  
**Contexto:** revisão sistemática de todos os campos disponíveis no SummaryDoc  
**Referência:** documentação oficial `materialsproject.github.io/api/`

### Campos identificados como ausentes na v1

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
- Criar `extraction.py` com lista canônica de campos
- Manter notebook v1 no repositório para rastreabilidade
- Criar notebook v2 com campos expandidos e usando extraction.py

---

## Experimento 003 — Estruturação do extraction.py

**Data:** 2026-03  
**Arquivo:** `src/extraction.py`  
**Commit:** *(adicionar hash após push)*

### Funções implementadas
- `conectar_api()` — autenticação com prioridade .env > env var > argumento
- `docs_para_df()` — conversão SummaryDoc → DataFrame com campos v2
- `extrair_familia()` — query parametrizada pelo dicionário FAMILIAS
- `adicionar_features()` — features derivadas centralizadas
- `exportar()` / `carregar()` — separação extração × análise
- `pipeline_completo()` — ponto de entrada único para re-extração

### Decisão de design
- Dicionário `FAMILIAS` permite adicionar novas famílias sem modificar funções
- Constantes físicas no topo do arquivo — mudança propagada para todos os notebooks
- `carregar()` permite notebooks de análise sem chamar a API

---

## Experimento 004 — Configuração do ambiente GitHub + Colab

**Data:** 2026-03  
**Contexto:** definição de workflow multi-instituição

### Problema encontrado
- `git push` falhou com erro `src refspec main does not match any`
- Causa: nenhum commit local existia, branch main não criado
- Solução: `git add . → git commit → git push`

### Problema de autenticação
- GitHub descontinuou autenticação por senha em 2021
- Alternativas: SSH key ou Personal Access Token (PAT)
- **Decisão:** usar interface gráfica do GitHub + Google Colab para evitar
  configuração de SSH em múltiplas máquinas

### Workflow definido
- Edição e execução: Google Colab
- Versionamento: `Arquivo → Salvar cópia no GitHub` (interface gráfica)
- Chave de API: Colab Secrets (ver nota 05)
- Notebooks `.py` auxiliares: importados via `!wget` do repositório

---

## Experimento 005 — EDA estatística e gráfica (Fase 1)

**Data:** 2026-03  
**Notebook:** `v2_eda_campos_expandidos.ipynb`  
**Commit:** *(adicionar hash após push)*

### Subconjuntos após filtros de qualidade
(`usar_em_analise=True`, não-metais, regime DFT conhecido)

| Família | n subconjunto | n dataset total | Redução |
|---|---|---|---|
| Perovskitas Duplas | 2.719 | 6.033 | ~55% excluído |
| Kesteritas | 234 | 4.367 | ~95% excluído |

### Candidatos identificados (após filtros + e_hull < 0.05 eV/átomo)

| Critério | Perovskitas Duplas | Kesteritas |
|---|---|---|
| PV restrito (1.0–1.8 eV) | 218 | — |
| PV ampliado (0.7–2.0 eV) | 355 | 31 |
| IBSC restrito (1.8–2.6 eV) | 228 | — |
| IBSC ampliado (1.4–3.2 eV) | 506 | 25 |
| Candidatos PV por estrutura: confirmada | 227 | 24 |
| Candidatos PV por estrutura: relacionada | 104 | — |
| Candidatos IBSC por estrutura: confirmada | 346 | 16 |
| Candidatos IBSC por estrutura: relacionada | 144 | — |

### Achados principais

**Gap:**
- PD: distribuição aproximadamente plana 0–4 eV — incomum, positivo para triagem
- K: mediana zero por subestimação GGA severa (CZTS DFT 0.09 eV → HSE06 1.18 eV)
- GGA e GGA+U têm médias similares nas PD por viés composicional, não física igual

**Estabilidade:**
- K mais estável em média (hull mediano 0.024 eV/át.) que PD (0.065 eV/át.)
- PD: hull máximo 6.659 eV/át. — materiais muito instáveis sobrevivendo ao filtro estrutural
- Ausência de correlação gap × formação em ambas as famílias: resultado positivo para triagem

**Estrutura cristalina:**
- PD: dominância cúbica ~60% (grupo Fm-3m) — valida uso desse grupo como canônico
- PD: triclínico inesperadamente alto (383) — provável artefato de convergência
- K: tetragonal e trigonal dominam, consistente com grupos I-4 e R3m

**Correlações (mapa de Pearson):**
- nsites × volume nas K: r=0.91 — redundantes como features ML
- densidade é feature mais informativa para K que para PD
- efermi tem correlações moderadas nas K mas não nas PD

### Decisões tomadas
- Estratificação por regime (GGA vs GGA+U) obrigatória em todas as fases
- Flag `usar_em_analise` eficaz — exclui sem impactar os candidatos relevantes
- Janelas ampliadas justificadas: adicionam ~66–109% de candidatos que DFT escondia
- Filtro adicional hull < 0.5 eV descartado (sem respaldo sistemático na faixa 0.05–0.5)
- Subconjunto ML usa mesmo limiar HULL_THRESH = 0.05 eV/átomo

### Figuras geradas para o artigo

| Figura | Versão | Status |
|---|---|---|
| Band gap por categoria estrutural (boxplot horizontal) | v2 | Pronto (ajuste menor na legenda) |
| Distribuição gap não-metais (comparação famílias) | — | Pronto |
| Estabilidade termodinâmica (log + barra hull=0) | v3 | Pronto |
| Energia formação vs. gap (cores discretas) | v3 | Pronto |
| Sistema cristalino (barras empilhadas) | v2 | Código gerado, aguarda execução |
| Nível de Fermi por regime | v2 | Código gerado, aguarda execução |
| Mapa de correlação Pearson | — | Pronto |

---

## Experimento 006 — Descritores composicionais Magpie (Fase 2)

**Data:** 2026-03  
**Notebook:** `v3_descritores_magpie.ipynb`  
**Biblioteca:** matminer 0.10.0 (132 features — versão anterior: 114)  
**Commit:** *(adicionar hash após push)*

### Subconjuntos de trabalho

| Subconjunto | Critério | PD (n) | K (n) |
|---|---|---|---|
| Filtrado | usar_em_analise + não-metal + hull<0.05 | 924 | 97 |
| Geral | usar_em_analise + não-metal (sem hull) | 1.850 | 117 |

Ambos restritos a estruturas confirmadas/relacionadas (usar_em_analise=True).
Categoria "outra" excluída para garantir comparabilidade estrutural.

### Seleção de features

| Subconjunto | Inicial | Pós-variância | Pós-colinearidade |
|---|---|---|---|
| PD filtrado | 132 | 124 | 88 |
| K filtrado | 132 | 120 | 81 |
| PD geral | 132 | 124 | 88 |
| K geral | 132 | 121 | 86 |
| Comuns PD/K gerais | — | — | 78 |

### Correlações com band_gap — conjunto filtrado

Top 6 por |corr_PD| (subconjunto filtrado):

| Feature | corr_PD | corr_K | Sinal igual |
|---|---|---|---|
| mean NdValence | -0.238 | -0.606 | Sim |
| mean NValence | -0.218 | -0.473 | Sim |
| avg_dev Column | +0.186 | +0.349 | Sim |
| avg_dev NdValence | -0.171 | +0.291 | **Não** |
| avg_dev CovalentRadius | +0.170 | +0.407 | Sim |
| mode MeltingT | -0.170 | -0.513 | Sim |

Correlações geralmente fracas nas PD (máx |r|=0.24), mais altas nas K (máx |r|=0.61).
Atenuação esperada: subestimação DFT não-uniforme comprime o sinal.

### Correlações por regime — PD filtrado

Separação GGA vs GGA+U revelou padrão sistemático:

| Feature | corr_misto | corr_GGA | corr_GGA+U |
|---|---|---|---|
| mean NdValence | -0.238 | -0.245 | -0.162 |
| mean NValence | -0.218 | -0.250 | +0.155 ← inversão |
| avg_dev Column | +0.186 | +0.210 | -0.010 |
| avg_dev NdValence | -0.171 | -0.157 | -0.178 ← estável |
| avg_dev CovalentRadius | +0.170 | +0.170 | +0.166 ← estável |
| mode MeltingT | -0.170 | -0.181 | -0.044 |
| minimum Number | -0.168 | -0.186 | +0.092 ← inversão |
| mean Number | -0.160 | -0.191 | +0.173 ← inversão |

**Padrão:** features de número atômico e elétrons de valência invertem sinal
entre regimes. Features de dispersão de raio covalente e elétrons d mantêm
sinal — são os descritores composicionais mais robustos.

### Discriminação candidatos PV vs IBSC

**PD — candidatos PV vs outros (subconjunto filtrado):**

| Feature | Média cand. PV | Média outros | Diferença |
|---|---|---|---|
| mean NValence | 10.12 ± 3.90 | 8.24 ± 2.76 | +23% |
| avg_dev CovalentRadius | 36.47 ± 12.93 | 42.43 ± 13.10 | -14% |
| avg_dev Column | 4.44 ± 2.03 | 5.53 ± 1.60 | -20% |

Discriminação existe e tem interpretação física: mais elétrons de valência
médios e menor dispersão de raio covalente caracterizam candidatos PV.

**PD — candidatos IBSC vs outros (subconjunto filtrado):**
Diferenças < 5% em todas as features, desvios padrão completamente sobrepostos.
Sem discriminação composicional em nenhum subconjunto ou regime testado.

**K — candidatos PV vs outros:**
`range Electronegativity` maior nos candidatos (1.32 vs 1.10) — maior caráter
iônico associado a gaps maiores, coerente com física do CZTS.

### Achado principal da Fase 2

Features composicionais Magpie discriminam candidatos PV com sinal físico
interpretável nas PD. Candidatos IBSC não mostram discriminação composicional
em quatro condições testadas (PD filtrado, PD geral, K filtrado, K geral).

**Implicação:** a triagem IBSC requer informação eletrônica estrutural.
A análise DOS (Fase 4) é necessária, não complementar, para caracterizar
candidatos IBSC.

### Datasets exportados para Fase 3

| Arquivo | n | Features |
|---|---|---|
| `data/fase2/perovskita_ml_ready.csv` | 924 | 88 Magpie + fase1 + dummies regime |
| `data/fase2/kesterita_ml_ready.csv` | 97 | 81 Magpie + fase1 + dummies regime |

### Figura gerada

| Figura | Status |
|---|---|
| Fig. 7 — Heatmap correlação Magpie × gap (top 20 features, ambas famílias) | Gerado |
| Fig. 8 — Box-plots candidatos PV vs outros (top 6 features) | Gerado como tabela |

### Decisões tomadas
- Categoria "outra" excluída das análises Magpie (heterogeneidade estrutural
  inviabiliza interpretação composicional coerente); reservada para trabalho futuro
- Conjunto geral (sem hull) mantido em paralelo ao filtrado para análise de
  sensibilidade — diferença entre os dois é resultado analítico em si
- Correlações calculadas separadamente por regime (GGA/GGA+U) como verificação
  de robustez obrigatória em todas as análises subsequentes
- Formulação ML da Fase 3: classificação binária (candidato PV vs outros) +
  caracterização não-supervisionada dos candidatos (PCA/UMAP)

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
