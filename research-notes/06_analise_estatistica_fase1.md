# 06 — Análise Estatística Descritiva — Fase 1

**Data:** 2026-03  
**Notebook:** `v2_eda_campos_expandidos.ipynb` — Seções 8 e 9  
**Status:** análise inicial concluída — subconjuntos definidos, análise
por regime e por categoria estrutural concluídas

---

## Contexto

Esta nota registra a análise dos dados estatísticos descritivos obtidos
após aplicação de todos os filtros de qualidade:
- `usar_em_analise == True` (estrutura confirmada/relacionada + regime conhecido)
- Valores DFT-GGA/GGA+U — subestimação sistemática documentada

---

## 1. Tamanho dos subconjuntos

| Família | n (subconjunto) | n (dataset total) | Redução |
|---|---|---|---|
| Perovskitas Duplas | 2.719 | 6.033 | ~55% excluído |
| Kesteritas | 234 | 4.367 | ~95% excluído |

A diferença de uma ordem de grandeza reflete o espaço composicional
intrínseco: perovskitas duplas A₂B'B''X₆ têm alto grau de liberdade
combinatório nos sítios B' e B''. Kesteritas são estruturalmente mais
restritivas — Cu e Zn ocupam posições específicas com pouca variação.

A redução drástica nas kesteritas (~95%) indica que a extração
composicional trouxe majoritariamente compostos de outras famílias.

**Implicação para Fase 3 (ML):** subconjunto de kesteritas (n=234) é
pequeno para modelos complexos. Considerar regularização agressiva,
transfer learning a partir do modelo de perovskitas, ou restrição a
modelos mais simples.

---

## 2. Estatísticas descritivas — features principais

### 2.1 Band gap

| Métrica | Perovskitas Duplas | Kesteritas |
|---|---|---|
| Média | 1.257 eV | 0.432 eV |
| Mediana | 0.969 eV | 0.000 eV |
| Desvio padrão | 1.250 eV | 0.718 eV |
| CV (std/mean) | ~99% | ~166% |
| Q1 | 0.000 eV | 0.000 eV |
| Q3 | 2.286 eV | 0.609 eV |
| Máximo | 3.999 eV | 2.830 eV |

**Perovskitas Duplas:** CV próximo de 100% indica distribuição ampla
e diversa. A distribuição é aproximadamente plana entre 0 e 4 eV —
incomum e positivo para triagem, pois a família tem representantes
em todas as janelas de interesse sem concentração excessiva em
regiões de menor relevância. Mediana abaixo da média indica
assimetria à direita.

**Kesteritas:** CV > 100% e mediana zero revelam que mais de 50% das
kesteritas têm gap = 0 no nível DFT-GGA. Isso é parcialmente artefato
do funcional — GGA é impreciso para kesteritas (CZTS: GGA 0.09 eV →
HSE06 1.18 eV → experimental ~1.5 eV). O critério de janela de gap
não funciona para kesteritas sem correção HSE06.

### 2.2 Estabilidade termodinâmica

| Métrica | Perovskitas Duplas | Kesteritas |
|---|---|---|
| hull médio (eV/át.) | 0.167 | 0.095 |
| hull mediano (eV/át.) | 0.065 | 0.024 |
| hull máximo (eV/át.) | 6.659 | 1.020 |

Kesteritas apresentam maior estabilidade termodinâmica média,
consistente com família mais estabelecida experimentalmente. O hull
máximo de 6.659 eV nas perovskitas indica materiais muito instáveis
que sobreviveram ao filtro estrutural — considerar filtro adicional
hull < 0.5 eV nas análises quantitativas da Fase 3.

### 2.3 Energia de formação

Perovskitas duplas têm formação média mais negativa (-1.859 eV/átomo)
que kesteritas (-0.733 eV/átomo). Nas kesteritas, compostos em "outra"
estrutura têm formação mais negativa que a kesterita confirmada,
indicando que a estrutura kesterita não é necessariamente a mais
favorável quimicamente para todas as composições — o que eleva o hull
relativo da família confirmada.

### 2.4 Nível de Fermi (efermi)

Diferença sistemática de ~3 eV entre famílias (perovskitas ~0.96 eV,
kesteritas ~3.88 eV) reflete composição e estrutura eletrônica
distintas. Não comparável entre famílias mas internamente consistente.

---

## 3. Band gap por regime de cálculo

### 3.1 Perovskitas Duplas (não-metais)

| Regime | n | Média (eV) | Mediana (eV) | Std |
|---|---|---|---|---|
| GGA | 1.477 | 1.848 | 1.826 | 1.114 |
| GGA+U | 354 | 1.857 | 1.893 | 1.050 |
| HSE06 | 19 | 1.582 | 1.426 | 0.740 |

**Observação contraintuitiva:** GGA e GGA+U apresentam médias quase
idênticas apesar de funcionais diferentes. Causa: **viés composicional**
— materiais que recebem GGA+U (com Mn, Fe, Co no sítio B'') são
composicionalmente distintos dos materiais GGA e já teriam gaps maiores
por razões estruturais. As distribuições têm formas diferentes (violin
plot confirma — GGA+U mais concentrado em gap baixo, GGA mais plano)
mas médias que convergem por acidente estatístico. Comparação direta
GGA vs GGA+U seria metodologicamente incorreta — estratificação por
regime na Fase 3 é obrigatória.

A cauda do GGA+U abaixo de zero no violin plot é artefato numérico de
convergência, não física real.

**HSE06 (n=19):** distribuição mais estreita, concentrada entre 1–2 eV.
Seleção não-aleatória — calculados com HSE06 por serem candidatos de
interesse já identificados pela comunidade. Concentração na janela PV
é evidência indireta de relevância fotovoltaica reconhecida previamente.

### 3.2 Kesteritas (não-metais)

| Regime | n | Média (eV) | Mediana (eV) | Std |
|---|---|---|---|---|
| GGA | 114 | 0.834 | 0.586 | 0.796 |
| GGA+U | 2 | 2.325 | 2.325 | 0.473 |
| HSE06 | 1 | 1.478 | — | — |

GGA+U (n=2) e HSE06 (n=1) são estatisticamente irrelevantes. Análise
de kesteritas na Fase 3 conduzida exclusivamente com GGA (n=114
não-metais). O único ponto HSE06 (~1.6 eV) confirma que HSE06 empurra
gaps de kesteritas para a janela PV, enquanto GGA os mantém abaixo de
1 eV na maioria dos casos.

---

## 4. Análise por elemento composicional

### 4.1 Materiais com Bismuto (Bi)

Histograma mostra pico bem definido em 1.3–1.5 eV (DFT-GGA),
correspondendo a ~1.9–2.1 eV experimental (correção ~38%). Confirma
que Bi³⁺ no sítio B'' é marcador composicional de gap na janela
PV/IBSC superior.

A distribuição é **bimodal**: pico principal em 1.3–1.5 eV e grupos
secundários em 0.5–1.0 eV e 3.0–3.7 eV.
- Gap baixo (0.5–1.0 eV): compostos com haletos pesados (I, Br)
  que reduzem o gap por maior polarizabilidade
- Gap alto (3.0–3.7 eV): compostos com haletos leves (F, Cl) onde
  maior ionicidade abre o gap

Os poucos pontos GGA+U com Bi indicam compostos com Bi e metal de
transição simultaneamente — o U é aplicado pelo segundo elemento.

**Implicação para Fase 2:** filtrar por haleto específico dentro do
subconjunto com Bi revelará subgrupos mais coerentes para feature
engineering.

### 4.2 Materiais com Mn, Fe ou Co

Histograma mostra pico dominante em gap = 0 para GGA+U (10 materiais),
contra distribuição mais plana nos demais valores. As oscilações ao
longo da faixa de gap refletem sobreposição de três distribuições
distintas — cada metal de transição (Mn²⁺ d⁵, Fe³⁺ d⁵, Co²⁺ d⁷)
produz gaps em faixas características diferentes.

**Ponto metodológico importante:** materiais com Mn/Fe/Co e gap = 0
no GGA+U não devem ser classificados automaticamente como metais.
O estado magnético inicial (MAGMOM fixo) pode não ser o estado
fundamental correto — estado antiferromagnético ou ferrimagnético
poderia dar gap diferente. São candidatos a revisão de estado
magnético na Fase 4.

---

## 5. Candidatos por janela de gap

### 5.1 Impacto das janelas ampliadas

| Critério | Perovskitas Duplas | Kesteritas |
|---|---|---|
| PV restrito (1.0–1.8 eV) | 393 (14.5%) | 18 (7.7%) |
| PV ampliado (0.7–2.0 eV) | 652 (24.0%) | 37 (15.8%) |
| Exclusivos ampliados PV | 259 (+66%) | 19 (+106%) |
| IBSC restrito (1.8–2.6 eV) | 430 (15.8%) | 15 (6.4%) |
| IBSC ampliado (1.4–3.2 eV) | 897 (33.0%) | 27 (11.5%) |
| Exclusivos ampliados IBSC | 467 (+109%) | 12 (+80%) |

A ampliação quase dobra os candidatos — os exclusivos ampliados são
materiais com gap real potencialmente na janela de interesse que a
subestimação DFT escondia.

**Sobreposição intencional:** janelas ampliadas se sobrepõem na faixa
1.4–2.0 eV. Materiais nessa faixa são zona de incerteza DFT —
classificação definitiva requer HSE06 ou GW (Fase 4).

### 5.2 Estabilidade e referências experimentais

| Critério | Perovskitas Duplas | Kesteritas |
|---|---|---|
| Estáveis (hull=0) | 500 (18.4%) | 54 (23.1%) |
| Quasi-estáveis (<50 meV) | 1182 (43.5%) | 141 (60.3%) |
| Com ref. experimental | 717 (26.4%) | 55 (23.5%) |

Kesteritas mostram maior estabilidade proporcional. Proporção similar
de referências experimentais (~25%) indica cobertura comparável do
Materials Project para as duas famílias.

---

## 6. Análise por categoria estrutural

### 6.1 Resumo comparativo

**Perovskitas Duplas:**

| Categoria | n | Gap médio | Gap mediana | Hull médio | Hull máx | Cand. PV |
|---|---|---|---|---|---|---|
| outra | 3.293 | 1.105 eV | 0.877 eV | 0.227 eV | 5.813 eV | 20.0% |
| perovskita dupla | 2.105 | 1.243 eV | 0.911 eV | 0.127 eV | 2.732 eV | 13.7% |
| relacionada | 635 | 1.272 eV | 1.092 eV | 0.303 eV | 6.659 eV | 16.7% |

**Kesteritas:**

| Categoria | n | Gap médio | Gap mediana | Hull médio | Hull máx | Cand. PV |
|---|---|---|---|---|---|---|
| outra | 4.126 | 0.800 eV | 0.416 eV | 0.128 eV | 3.092 eV | 17.0% |
| kesterita | 148 | 0.486 eV | 0.062 eV | 0.074 eV | 1.020 eV | 9.5% |
| relacionada | 93 | 0.397 eV | 0.000 eV | 0.136 eV | 0.713 eV | 6.5% |

### 6.2 O paradoxo da categoria "outra"

A categoria "outra" tem proporção maior de candidatos PV que as
famílias confirmadas em ambos os casos (20% vs 13.7% nas perovskitas,
17% vs 9.5% nas kesteritas). Três mecanismos explicam:

**1. Viés de distribuição:** a família confirmada tem distribuição plana
cobrindo 0–4 eV, diluindo a proporção na janela 1.0–1.8 eV. "Outra"
agrupa famílias heterogêneas que têm maior densidade acidental nessa faixa.

**2. Química compartilhada:** compostos em "outra" contêm os mesmos
elementos do filtro composicional. A química que favorece gaps na
janela PV não é exclusiva da estrutura perovskita dupla — depende dos
elementos, que aparecem em várias estruturas.

**3. Seleção do Materials Project:** materiais com gap na janela PV
podem ter sido calculados pelo MP por interesse fotovoltaico prévio,
independentemente da estrutura.

**Ressalva crítica:** candidatos PV em "outra" têm hull médio
sistematicamente maior (0.227 eV vs 0.127 eV nas confirmadas) —
são menos sintetizáveis em média. Maior proporção não implica maior
relevância prática.

**Para o artigo:** reportar candidatos de "outra" como achado
secundário, separados das famílias alvo, indicando que representam
compostos de interesse para investigação futura em seus próprios
contextos estruturais.

**Para trabalhos futuros:** conjunto "outra" das kesteritas (4.126
compostos, hull mediano 0.043 eV) é candidato a triagem sistemática
com classificação estrutural secundária — pode revelar famílias
inteiras não exploradas para PV.

### 6.3 Heterogeneidade interna da categoria "relacionada"

Nas perovskitas, "relacionada" tem hull máximo de 6.659 eV (o maior
de todas as categorias) mas mediana similar à confirmada (0.066 vs
0.065 eV). Indica núcleo estável (distorções monoclínicas reais) e
cauda de compostos muito instáveis que entraram por coincidência de
grupo espacial. Considerar separar "relacionada" em dois subgrupos
pelo hull (< 0.1 eV e ≥ 0.1 eV) antes das análises da Fase 2.

Nas kesteritas, "relacionada" tem gap mediano zero e apenas 6.5% de
candidatos PV — provavelmente compostos de calcopirita (grupo 122)
com gap acidental na janela PV, não kesteritas verdadeiras.

---

## 7. Conclusões e decisões para as próximas fases

### Decisões metodológicas confirmadas
- Estratificação por regime (GGA vs GGA+U) obrigatória na Fase 3
- Flag `usar_em_analise` eficaz — exclui materiais sem impactar
  os candidatos relevantes
- Janelas ampliadas justificadas: adicionam ~66–109% de candidatos
  que a subestimação DFT escondia

### Decisões pendentes identificadas nesta análise

| Decisão | Prazo |
|---|---|
| Filtro adicional hull < 0.5 eV para análises quantitativas | Fase 3 |
| Separar "relacionada" em subgrupos por hull | Fase 2 |
| Materiais Mn/Fe/Co com gap = 0: revisão de estado magnético | Fase 4 |
| Subgrupo com Bi: filtrar por haleto para feature engineering | Fase 2 |
| Conjunto "outra" das kesteritas: triagem estrutural secundária | Trabalho futuro |

### Estado geral do pipeline
Metodologia clara, decisões documentadas, resultados com interpretação
física coerente. Pronto para análises gráficas detalhadas (Seção 9 do
notebook) e para Fase 2 — descritores composicionais via Matminer/Magpie.
