# 06 — Análise Estatística Descritiva — Fase 1

**Data:** 2026-03  
**Notebook:** `v2_eda_campos_expandidos.ipynb` — Seção 8  
**Status:** análise inicial concluída — subconjuntos de análise definidos

---

## Contexto

Esta nota registra a análise dos dados estatísticos descritivos obtidos
após a aplicação de todos os filtros de qualidade definidos até o momento:
- `usar_em_analise == True` (estrutura confirmada/relacionada + regime de cálculo conhecido)
- Valores DFT-GGA/GGA+U — subestimação sistemática documentada

---

## 1. Tamanho dos subconjuntos

| Família | n (subconjunto) | n (dataset total) | Redução |
|---|---|---|---|
| Perovskitas Duplas | 2.719 | 6.033 | ~55% excluído |
| Kesteritas | 234 | 4.367 | ~95% excluído |

A diferença de uma ordem de grandeza entre as famílias reflete o espaço
composicional intrínseco de cada uma:

- **Perovskitas Duplas A₂B'B''X₆:** alto grau de liberdade combinatório
  nos sítios B' e B'' com os quatro haletos (F, Cl, Br, I)
- **Kesteritas A₂BCX₄:** estruturalmente mais restritivas — Cu e Zn
  ocupam posições específicas com pouca variação composicional

A redução drástica nas kesteritas (~95%) indica que a extração composicional
(presença de S ou Se, 4 elementos) trouxe majoritariamente compostos de
outras famílias estruturais. O subconjunto de 234 materiais representa
apenas os grupos espaciais canônicos (82, 121, 119) e relacionados.

**Implicação para Fase 3 (ML):** o subconjunto de kesteritas é pequeno
para treinamento de modelos complexos. Estratégias a considerar:
regularização agressiva, transfer learning a partir do modelo de
perovskitas, ou restrição a modelos mais simples (regressão linear,
árvores rasas).

---

## 2. Estatísticas descritivas — features principais

### 2.1 Band gap

| Métrica | Perovskitas Duplas | Kesteritas |
|---|---|---|
| Média | 1.257 eV | 0.432 eV |
| Mediana | 0.969 eV | 0.000 eV |
| Desvio padrão | 1.250 eV | 0.718 eV |
| CV (std/mean) | ~99% | ~166% |
| Mínimo | 0.000 eV | 0.000 eV |
| Q1 | 0.000 eV | 0.000 eV |
| Q3 | 2.286 eV | 0.609 eV |
| Máximo | 3.999 eV | 2.830 eV |

**Perovskitas Duplas:** CV próximo de 100% indica distribuição ampla e
diversa — há representação em todas as faixas de interesse (PV, IBSC,
gap estreito e largo). Mediana (0.969 eV) abaixo da média (1.257 eV)
indica assimetria à direita: materiais com gaps grandes puxam a média
para cima, mas o centro da distribuição está próximo da janela PV.
Q1 = 0 confirma que uma fração significativa do subconjunto é metálica
ou semimetálica no nível DFT.

**Kesteritas:** CV > 100% indica distribuição altamente heterogênea
onde a média não representa bem a população. A mediana zero revela que
**mais de 50% das kesteritas no subconjunto têm gap = 0 no nível DFT-GGA**.
Isso é parcialmente artefato do funcional — o GGA é notoriamente
impreciso para kesteritas (CZTS: GGA 0.09 eV → HSE06 1.18 eV →
experimental ~1.5 eV). O gap máximo de 2.83 eV indica que há materiais
com gap real potencialmente interessante para IBSC.

### 2.2 Estabilidade termodinâmica

| Métrica | Perovskitas Duplas | Kesteritas |
|---|---|---|
| hull médio (eV/át.) | 0.167 | 0.095 |
| hull mediano (eV/át.) | 0.065 | 0.024 |
| hull máximo (eV/át.) | 6.659 | 1.020 |

Kesteritas apresentam maior estabilidade termodinâmica média, consistente
com ser uma família mais bem estabelecida experimentalmente. O hull máximo
de 6.659 eV nas perovskitas indica materiais muito instáveis que
sobreviveram ao filtro de estrutura — provavelmente compostos com
estrutura espacial confirmada mas composição termodinamicamente
desfavorável. Vale considerar um filtro adicional de hull < 1.0 eV
para análises quantitativas.

### 2.3 Energia de formação

Perovskitas duplas têm formação média mais negativa (-1.859 eV/átomo)
que kesteritas (-0.733 eV/átomo), indicando maior estabilidade química
relativa. No entanto, a kesterita tem formação mínima mais negativa
(-3.052 eV/átomo vs -3.972 eV/átomo), sugerindo que os compostos mais
estáveis de cada família são comparáveis.

### 2.4 Nível de Fermi (efermi)

| Métrica | Perovskitas Duplas | Kesteritas |
|---|---|---|
| Média | 0.961 eV | 3.880 eV |
| Mediana | 0.794 eV | 3.929 eV |

A diferença sistemática de ~3 eV no nível de Fermi entre as famílias
reflete a diferença de composição e estrutura eletrônica — não é
diretamente comparável entre famílias, mas é internamente consistente
dentro de cada uma. O efermi das kesteritas concentrado entre 2.9–4.9 eV
(Q1–Q3) sugere uma família mais uniforme eletronicamente.

---

## 3. Band gap por regime de cálculo

### 3.1 Perovskitas Duplas (não-metais)

| Regime | n | Média (eV) | Mediana (eV) | Std |
|---|---|---|---|---|
| GGA | 1.477 | 1.848 | 1.826 | 1.114 |
| GGA+U | 354 | 1.857 | 1.893 | 1.050 |
| HSE06 | 19 | 1.582 | 1.426 | 0.740 |

**Observação contraintuitiva:** GGA e GGA+U apresentam médias quase
idênticas (1.848 vs 1.857 eV). O esperado seria GGA+U dar gaps maiores
por corrigir a subestimação dos elétrons d. A explicação provável é
**viés composicional**: os materiais que recebem GGA+U (contendo Mn,
Fe, Co no sítio B'') são composicionalmente distintos dos materiais GGA
e já teriam gaps maiores por razões estruturais independentes do
funcional. Isso significa que comparar diretamente as duas populações
como se fossem equivalentes seria incorreto — a estratificação por
regime na Fase 3 é essencial.

O HSE06 (19 materiais) dá média ligeiramente menor (1.582 eV), mas
a amostra é pequena demais para conclusão estatística. É consistente
com o comportamento não-uniforme da correção HSE06 para materiais
com elementos pesados.

### 3.2 Kesteritas (não-metais)

| Regime | n | Média (eV) | Mediana (eV) | Std |
|---|---|---|---|---|
| GGA | 114 | 0.834 | 0.586 | 0.796 |
| GGA+U | 2 | 2.325 | 2.325 | 0.473 |
| HSE06 | 1 | 1.478 | — | — |

Os subconjuntos GGA+U (n=2) e HSE06 (n=1) são estatisticamente
irrelevantes. A análise de kesteritas na Fase 3 será conduzida
exclusivamente com GGA (n=114 não-metais).

---

## 4. Candidatos por janela

### 4.1 Tabela completa

| Critério | Perovskitas Duplas | Kesteritas |
|---|---|---|
| PV restrito (1.0–1.8 eV) | 393 (14.5%) | 18 (7.7%) |
| PV ampliado (0.7–2.0 eV) | 652 (24.0%) | 37 (15.8%) |
| IBSC restrito (1.8–2.6 eV) | 430 (15.8%) | 15 (6.4%) |
| IBSC ampliado (1.4–3.2 eV) | 897 (33.0%) | 27 (11.5%) |
| Estáveis (hull=0) | 500 (18.4%) | 54 (23.1%) |
| Quasi-estáveis (<50 meV) | 1182 (43.5%) | 141 (60.3%) |
| Com ref. experimental | 717 (26.4%) | 55 (23.5%) |

### 4.2 Impacto da ampliação das janelas

A ampliação das janelas quase dobra os candidatos em ambas as famílias:
- PV: +259 perovskitas (+66%) e +19 kesteritas (+106%)
- IBSC: +467 perovskitas (+109%) e +12 kesteritas (+80%)

Esses candidatos adicionais são materiais com gap DFT abaixo do limiar
original que podem ter gap real dentro da janela de interesse —
justamente o tipo de material que a subestimação DFT escondia.

### 4.3 Sobreposição entre janelas ampliadas

As janelas ampliadas têm overlap intencional na faixa 1.4–2.0 eV
(PV_GAP_MAX_AMP = 2.0 eV e IBSC_GAP_MIN_AMP = 1.4 eV). Materiais
nessa faixa aparecem nas contagens de ambas as janelas e representam
a zona de incerteza DFT — o gap real pode colocá-los em qualquer
uma das duas categorias. A classificação definitiva desses materiais
requer valores HSE06 ou GW, a serem buscados na Fase 4.

**Nota para o artigo:** reportar sempre os dois critérios (restrito
e ampliado) com a justificativa de subestimação DFT. O critério
restrito é mais conservador e comparável com a literatura; o ampliado
é mais adequado dado o nível de teoria dos dados.

### 4.4 Estabilidade nos candidatos

A proporção de quasi-estáveis é maior nas kesteritas (60.3%) que nas
perovskitas (43.5%), consistente com a observação da Seção 2.2.
Para candidatos PV/IBSC, o filtro de quasi-estabilidade (<50 meV)
já está aplicado na exportação — os números acima são do subconjunto
completo de análise, não dos candidatos exportados.

---

## 5. Observações para as próximas etapas

### Filtro adicional de hull sugerido
O hull máximo de 6.659 eV nas perovskitas é muito alto para triagem
relevante. Considerar hull < 0.5 eV como filtro adicional nas análises
quantitativas, mantendo o limiar de 50 meV apenas para a exportação
de candidatos finais.

### Tratamento das kesteritas metálicas
Com mediana de gap = 0, mais da metade das kesteritas são metálicas
ou semimetálicas no nível GGA. Para as análises gráficas, filtrar
sempre por `~is_metal` e documentar explicitamente a fração excluída.

### Estratificação por regime obrigatória na Fase 3
A similaridade de gaps médios entre GGA e GGA+U nas perovskitas
(viés composicional) confirma que misturar os dois regimes num único
modelo introduziria ruído sistemático não capturável pelos descritores.
Treinamentos separados por regime ou inclusão de `regime_calc` como
feature categórica são as alternativas a avaliar.

### Próximo passo imediato
Análise gráfica (Seção 9 do notebook) com as distribuições de band gap
estratificadas por: (a) categoria estrutural, (b) regime de cálculo,
e (c) janela de candidatos. As estatísticas desta seção fornecem o
contexto interpretativo para essas figuras.
