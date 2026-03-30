# 07 — Análise de Descritores Composicionais — Fase 2

**Data:** 2026-03  
**Notebook:** `v3_descritores_magpie.ipynb`  
**Status:** análise concluída — datasets exportados para Fase 3

---

## Contexto

Esta nota registra os resultados da aplicação do preset Magpie (matminer 0.10.0)
aos subconjuntos filtrado e geral das duas famílias, após a Fase 1 estabelecer
as bases de candidatos PV e IBSC.

**Subconjuntos utilizados:**

| Subconjunto | Critério adicional | PD (n) | K (n) |
|---|---|---|---|
| Filtrado | hull < 0.05 eV/átomo | 924 | 97 |
| Geral | sem restrição de hull | 1.850 | 117 |

Ambos: usar_em_analise=True (estrutura confirmada/relacionada + regime conhecido)
+ não-metal. Categoria "outra" excluída de ambos.

---

## 1. Características dos subconjuntos de trabalho

### 1.1 Subconjunto filtrado (hull < 0.05 eV/átomo)

**Perovskitas Duplas (n=924):**

| Regime | n | Gap médio | Gap mediana |
|---|---|---|---|
| GGA | 737 | — | — |
| GGA+U | 172 | — | — |
| HSE06 | 15 | — | — |

Gap médio: 2.090 eV | Gap mediana: 2.124 eV | Hull médio: 0.013 eV/át.

Candidatos PV: 203 | Candidatos IBSC: 215

**Kesteritas (n=97):**

| Regime | n |
|---|---|
| GGA | 94 |
| GGA+U | 2 |
| HSE06 | 1 |

Gap médio: 0.910 eV | Gap mediana: 0.641 eV | Hull médio: 0.007 eV/át.

Candidatos PV: 15 | Candidatos IBSC: 13

### 1.2 Subconjunto geral (sem restrição de hull)

**Perovskitas Duplas (n=1.850):**

| Regime | n |
|---|---|
| GGA | 1.477 |
| GGA+U | 354 |
| HSE06 | 19 |

Gap médio: 1.847 eV | Hull médio: 0.113 eV/át.

**Kesteritas (n=117):**

| Regime | n |
|---|---|
| GGA | 114 |
| GGA+U | 2 |
| HSE06 | 1 |

Gap médio: 0.865 eV | Hull médio: 0.041 eV/át.

---

## 2. Seleção de features Magpie

Dois passos aplicados a cada subconjunto independentemente:
1. Remover features com std < 0.01
2. Remover uma de cada par com |r| > 0.95 (manter primeira)

| Subconjunto | Inicial | Pós-variância | Pós-colinearidade |
|---|---|---|---|
| PD filtrado | 132 | 124 | **88** |
| K filtrado | 132 | 120 | **81** |
| PD geral | 132 | 124 | **88** |
| K geral | 132 | 121 | **86** |

Features comuns PD/K (geral): **78** — base para comparação inter-família.

---

## 3. Correlações feature × gap por subconjunto

### 3.1 Subconjunto filtrado — top 10 por |corr_PD|

| Feature | corr_PD | corr_K | Sinal igual |
|---|---|---|---|
| mean NdValence | -0.238 | -0.606 | Sim |
| mean NValence | -0.218 | -0.473 | Sim |
| avg_dev Column | +0.186 | +0.349 | Sim |
| avg_dev NdValence | -0.171 | +0.291 | **Não** |
| avg_dev CovalentRadius | +0.170 | +0.407 | Sim |
| mode MeltingT | -0.170 | -0.513 | Sim |
| minimum Number | -0.168 | -0.493 | Sim |
| mean Number | -0.160 | -0.449 | Sim |
| avg_dev GSbandgap | +0.158 | +0.361 | Sim |
| mean Column | -0.158 | -0.178 | Sim |

**Observação sobre magnitude:** correlações fracas nas PD (máx |r|=0.24),
moderadas nas K (máx |r|=0.61). O teto baixo para PD é esperado: distribuição
de gap aproximadamente plana (Fase 1) combinada com subestimação DFT
não-uniforme comprime o sinal independentemente da qualidade dos descritores.
As correlações representam limite inferior do sinal real.

### 3.2 Subconjunto geral — top 10 por |corr_PD|

| Feature | corr_PD | corr_K | Sinal igual |
|---|---|---|---|
| avg_dev Column | +0.222 | +0.201 | Sim |
| mean Column | -0.195 | -0.080 | Sim |
| avg_dev CovalentRadius | +0.170 | +0.321 | Sim |
| minimum GSvolume_pa | +0.159 | +0.049 | Sim |
| avg_dev Electronegativity | +0.156 | +0.477 | Sim |
| mean MendeleevNumber | -0.156 | -0.174 | Sim |
| mean NValence | -0.147 | -0.405 | Sim |
| mean NdValence | -0.141 | -0.473 | Sim |
| avg_dev GSvolume_pa | +0.116 | +0.237 | Sim |
| maximum CovalentRadius | +0.111 | +0.204 | Sim |

Features com sinal oposto entre famílias (|r|>0.10 em ambas):
`avg_dev NpValence` (PD: +0.111, K: -0.218) — único caso limpo após
controle de pureza estrutural.

### 3.3 Comparação entre subconjuntos

A mudança de features dominantes entre filtrado (NdValence, NValence) e
geral (CovalentRadius, Column, Electronegativity) tem interpretação física:

- **Subconjunto filtrado:** materiais todos estáveis e estruturalmente homogêneos.
  A variância no gap é explicada por features eletrônicas (ocupação d, valência).
- **Subconjunto geral:** maior diversidade composicional. Features de tamanho
  atômico e período dominam porque capturam a variação entre compostos de
  períodos diferentes — efeito de longo alcance.

Os dois subconjuntos revelam camadas diferentes da mesma física composicional.

---

## 4. Análise por regime de cálculo — PD filtrado

Teste Mann-Whitney confirmou que GGA e GGA+U são composicionalmente distintos
nas PD (5 de 6 top features com p < 0.05).

### 4.1 Tabela de correlações por regime

| Feature | corr_misto | corr_GGA | corr_GGA+U | Padrão |
|---|---|---|---|---|
| mean NdValence | -0.238 | -0.245 | -0.162 | Estável |
| mean NValence | -0.218 | -0.250 | **+0.155** | Inversão |
| avg_dev Column | +0.186 | +0.210 | -0.010 | Atenuado |
| avg_dev NdValence | -0.171 | -0.157 | -0.178 | **Estável** |
| avg_dev CovalentRadius | +0.170 | +0.170 | +0.166 | **Estável** |
| mode MeltingT | -0.170 | -0.181 | -0.044 | Atenuado |
| minimum Number | -0.168 | -0.186 | **+0.092** | Inversão |
| mean Number | -0.160 | -0.191 | **+0.173** | Inversão |

### 4.2 Interpretação do padrão de inversão

Features de número atômico médio e elétrons de valência total invertem sinal
entre regimes. A causa não é mudança de física, mas diferença composicional
entre grupos: materiais GGA+U têm `mean NdValence` = 1.37 vs 3.25 (GGA) —
metais de transição d com ocupação restrita. Dentro do subconjunto GGA+U,
a variação de gap é dirigida principalmente pelo parâmetro U (não captado
pelo Magpie), não pela composição elementar.

### 4.3 Descritores robustos entre regimes

`avg_dev CovalentRadius` e `avg_dev NdValence` mantêm sinal e magnitude
entre GGA e GGA+U. São os descritores composicionais mais confiáveis para
uso em modelos que combinam materiais de diferentes regimes.

**Nota sobre `mode NdValence` — GGA+U:** retornou NaN, provavelmente
por variância quase nula (moda zero para maioria dos materiais GGA+U).
Verificar com `value_counts()` antes de usar em modelos.

---

## 5. Discriminação candidatos por features Magpie

### 5.1 Perovskitas Duplas — PV vs outros

**Subconjunto filtrado:**

| Feature | Média cand. PV | Média outros | Δ% |
|---|---|---|---|
| mean NValence | 10.12 ± 3.90 | 8.24 ± 2.76 | +23% |
| avg_dev CovalentRadius | 36.47 ± 12.93 | 42.43 ± 13.10 | -14% |
| avg_dev Column | 4.44 ± 2.03 | 5.53 ± 1.60 | -20% |
| avg_dev NdValence | 3.05 ± 1.47 | 2.58 ± 1.36 | +18% |
| mode MeltingT | 192.85 ± 185.71 | 151.05 ± 126.84 | +28% |

**Subconjunto geral:**

| Feature | Média cand. PV | Média outros | Δ% |
|---|---|---|---|
| avg_dev Column | 4.89 ± 1.87 | 5.50 ± 1.63 | -11% |
| mean Column | 12.73 ± 1.66 | 12.30 ± 1.55 | +3% |
| avg_dev CovalentRadius | 37.04 ± 12.60 | 40.34 ± 13.61 | -8% |
| avg_dev Electronegativity | 0.855 ± 0.275 | 0.922 ± 0.278 | -7% |

O padrão central (menor dispersão de raio covalente e menor heterogeneidade
de coluna nos candidatos PV) persiste em ambos os subconjuntos, confirmando
robustez ao filtro de hull.

**Interpretação física:**
- Menor `avg_dev CovalentRadius`: compostos com átomos de tamanho mais
  homogêneo têm sobreposição orbital mais uniforme — banda de condução
  mais dispersa, gap menor → janela PV.
- Menor `avg_dev Column`: menor heterogeneidade de coluna implica menos
  contraste de elétrons de valência entre os átomos da composição —
  ligação menos polar, gap mais moderado.
- Maior `mean NValence` no filtrado: mais elétrons de valência médios
  associados a transição metal-isolante mais suave, favorecendo gaps
  na janela 1.0–1.8 eV.

### 5.2 Perovskitas Duplas — IBSC vs outros

**Resultado consistente em ambos os subconjuntos:** diferenças < 5% em todas
as features, desvios padrão completamente sobrepostos. Não há discriminação
composicional para candidatos IBSC.

Este resultado foi observado em quatro condições independentes (PD filtrado,
PD geral, K filtrado, K geral) — é um achado robusto, não artefato de filtragem.

### 5.3 Kesteritas — PV vs outros

**Subconjunto filtrado:**

| Feature | Média cand. PV | Média outros |
|---|---|---|
| range Electronegativity | 1.321 ± 0.420 | 1.105 ± 0.424 |
| minimum Number | 15.60 ± 2.13 | 18.34 ± 9.80 |

**Subconjunto geral:**

| Feature | Média cand. PV | Média outros |
|---|---|---|
| range Electronegativity | 1.309 ± 0.392 | 1.132 ± 0.430 |
| avg_dev Electronegativity | 0.435 ± 0.093 | 0.408 ± 0.142 |
| mean NdValence | 5.289 ± 2.388 | 5.757 ± 3.541 |

`range Electronegativity` persiste como discriminador em ambos os subconjuntos.
Maior amplitude de eletronegatividade implica maior caráter iônico — kesteritas
mais iônicas têm gaps maiores, saindo da zona de gap zero do GGA.

**Ressalva:** a subestimação severa do GGA para kesteritas contamina o grupo
de controle ("não-candidatos" GGA que seriam candidatos com HSE06). As
diferenças observadas são indicadores de direção, não triagem definitiva.

---

## 6. Conclusões e encaminhamentos

### Descritores composicionais robustos identificados

| Descritor | Sinal | Estável entre regimes | Presente em ambas famílias |
|---|---|---|---|
| avg_dev CovalentRadius | + (gap maior) | Sim | Sim |
| avg_dev NdValence | - (gap menor) | Sim | Sim |
| avg_dev Electronegativity | + (gap maior) | — | Sim (K mais forte) |
| mean NValence | - (gap menor) | **Não** (inverte GGA+U) | Sim |

### Posicionamento analítico para o artigo

A análise Magpie tem valor como **análise exploratória descritiva** que motiva
as fases subsequentes, não como resultado central:

1. Features composicionais discriminam parcialmente candidatos PV (PD) com
   sinais fisicamente interpretáveis.
2. Features composicionais não discriminam candidatos IBSC — justificando
   a análise DOS como necessária.
3. Correlações Magpie × gap são atenuadas pela subestimação DFT não-uniforme
   — representam limite inferior do sinal real.
4. A separação por regime revela que a robustez dos descritores varia:
   features de tamanho/dispersão são mais confiáveis que features de
   elétrons de valência médio para uso em modelos que combinam regimes.

### Próximos passos confirmados — Fase 3

- **Classificação binária:** Random Forest / XGBoost para predizer candidato
  PV vs outros, com as 88 features selecionadas + dummies de regime
- **Caracterização não-supervisionada:** PCA ou UMAP no espaço Magpie dos
  candidatos PV+IBSC, colorido por haleto, regime e estrutura
- **Regressão de gap:** análise complementar com ressalva explícita sobre
  subestimação DFT; estratificada por regime
- **Validação:** os 15–19 pontos HSE06 disponíveis como conjunto de teste
  externo para verificar consistência interna
