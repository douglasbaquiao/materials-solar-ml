# 02 — Decisões Metodológicas do Pipeline

**Data:** 2026-03  
**Status:** Fases 1, 2 e 3 consolidadas — Fase 4 (DOS) pendente

---

## Filosofia geral

Cada parâmetro do pipeline tem uma justificativa física ou estatística.
Esta nota registra o raciocínio por trás de cada escolha para que possa
ser reproduzida, questionada ou ajustada por revisores ou colaboradores.

> "Um artigo de materials informatics não é apenas sobre o modelo —
> é sobre as escolhas de triagem que determinam o que o modelo vê."

---

## Decisões de extração

### Filtro de famílias por marcador elementar

**Decisão:** usar presença de haleto (F, Cl, Br, I) como proxy para double
perovskitas, e calcogeneto (S, Se) para kesteritas.

**Justificativa:** o Materials Project não possui campo "tipo estrutural"
indexado no endpoint summary. Filtro composicional é a alternativa viável
sem verificação estrutura-a-estrutura.

**Limitação conhecida:** o filtro captura compostos quaternários com haleto
que não são necessariamente double perovskitas. Refinamento via grupo espacial
(Fm-3m, I4/mmm) seria mais preciso — reservado para trabalho futuro.

---

### Filtro `nelements = 4` e `nsites ≤ 40/50`

**Decisão:** exigir exatamente 4 elementos (A, B', B'', X); remover supercélulas.

**Validação:** inspeção manual de 10 materiais removidos confirmou que eram
supercélulas (nsites = 8×, 16× ou 32× da célula primitiva esperada).

---

### `deprecated = False` sempre ativo

Materiais deprecated substituídos por versões mais precisas — usar versões
antigas introduziria ruído. Custo zero de performance.

---

## Decisões de feature engineering

### Janelas fotovoltaicas

**PV:** 1.0–1.8 eV (Shockley-Queisser, eficiência teórica máxima ~33.7% em ~1.34 eV)  
**IBSC:** 1.8–2.6 eV (Luque & Martí 1997 — absorção em dois passos VB→IB→CB)  
**Janelas ampliadas:** PV 0.7–2.0 eV, IBSC 1.4–3.2 eV — compensam subestimação DFT ~30–40%

**Atenção DFT (aplica-se a ambas as famílias):** gaps DFT-GGA/GGA+U subestimam
gaps experimentais sistematicamente — PD ~38% (Cs₂AgBiBr₆: DFT 1.35 → exp 2.2 eV),
kesteritas de forma ainda mais severa (CZTS: DFT 0.09 → HSE06 1.18 → exp ~1.5 eV).
A subestimação não é uniforme entre compostos — varia com composição e funcional.
Qualquer correlação com `band_gap` como target representa limite inferior do sinal real.
Candidatos identificados devem ser interpretados como candidatos após correção do
funcional, não materiais com gap experimental confirmado na janela.

---

### Limiar de quasi-estabilidade: 0.05 eV/átomo

**Justificativa:** valor amplamente adotado na literatura (Sun et al. 2016 —
verificar referência exata). Materiais com hull < 50 meV/átomo considerados
potencialmente sintetizáveis sob condições controladas.

**Limiar 0.5 eV descartado:** sem respaldo sistemático na literatura para
síntese nessa faixa. Subconjunto ML usa mesmo limiar 0.05 eV dos candidatos.

---

## Decisões de descritores composicionais — Fase 2

### Preset Magpie completo (132 features, matminer 0.10.0)

Reprodutível e sem viés de seleção subjetiva. A versão 0.10.0 retorna 132
features (não 114 como em versões anteriores). Registrar versão no `requirements.txt`.

**Limitação:** features Magpie são estritamente composicionais — não capturam
informação estrutural. Limite metodológico a discutir explicitamente no artigo.

**Nota sobre avg_dev SpaceGroupNumber:** é estatística do grupo espacial do
elemento puro (estado fundamental do elemento isolado), não do material de
interesse. Propriedade composicional legítima, nome potencialmente confuso.

---

### Seleção de features em dois passos

1. Remover features com std < 0.01
2. Remover uma de cada par com |r| > 0.95 (manter primeira)

Resultado: 132 → 88 (PD filtrado), 81 (K filtrado), 88 (PD geral), 86 (K geral).
Features comuns PD/K gerais: 78 — base para comparação inter-família.

---

### Dois subconjuntos paralelos por família

Filtrado (hull < 0.05) e geral (sem restrição de hull), ambos com
usar_em_analise=True. Revelam física complementar:
- Filtrado: features eletrônicas (NdValence, NValence) dominam correlação com gap
- Geral: features de tamanho/período (CovalentRadius, Column, Electronegativity) dominam

A comparação entre os dois é um resultado analítico em si.

---

### Separação por regime de cálculo nas correlações

GGA e GGA+U não são amostras da mesma população composicional nas PD
(Mann-Whitney confirmado). `mean NdValence`: GGA=3.25 vs GGA+U=1.37.

Descritores robustos entre regimes: `avg_dev CovalentRadius` e `avg_dev NdValence`
(sinal e magnitude estáveis em GGA e GGA+U). Descritores instáveis: `mean NValence`,
`mean Number` (inversão de sinal entre regimes — causa é diferença composicional
entre grupos, não mudança de física).

---

### Discriminação PV vs IBSC por features composicionais

PV discriminável em PD com sinal físico interpretável (quatro condições testadas).
IBSC não discriminável composicionalmente em nenhuma condição testada.
Implicação: triagem IBSC requer análise eletrônica estrutural (DOS projetada).

---

## Decisões de ML — Fase 3

### Formulação principal: classificação binária

**Por que classificação e não regressão:** target DFT tem erro sistemático
não-uniforme entre compostos. Classificação com janelas ampliadas absorbe parte
dessa incerteza — pergunta "gap está aproximadamente nesta região" em vez de
"qual é o valor exato". Mais robusta ao problema de subestimação.

**Por que Logística + RF:** baseline linear para verificar se sinal é linear;
RF para capturar interações não-lineares. Diferença de AUC entre os dois é
resultado interpretável (presença ou ausência de interações relevantes).

**`class_weight="balanced"`:** com 22% de positivos (PD), sem balanceamento o
modelo aprende a predizer "não-candidato" para quase tudo e ainda acerta ~78%.

---

### CV: RepeatedStratifiedKFold

5 splits × 5 repetições para PD; × 10 repetições para K (n=97, alta variância).
Repetição produz estimativas mais estáveis — diferença entre AUC=0.71±0.15 e
AUC=0.71±0.05 é a diferença entre resultado inconclusivo e reportável.

---

### Métricas: AUC-ROC principal, F1 complementar

AUC mede capacidade de ordenar positivos acima de negativos — independente
de threshold. Para triagem, ordenação é o que importa (candidatos reais no
topo da lista). F1 penaliza erros nas duas direções.

F1 baixo com AUC alto indica threshold padrão (0.5) não é ótimo para o
balanço precision/recall. Correção via curva PR antes de comparar modelos.

---

### SHAP TreeExplainer

Atribui contribuição por material (não apenas por feature) e é consistente
(não inflado por colinearidade como importância de permutação).

---

### Regressão como análise complementar

R² obtido representa limite inferior do poder preditivo real. R²=0.646 para GGA
é consistente com literatura para features composicionais apenas. GGA+U com
R²=0.273 por razão identificada (parâmetro U não captado pelos descritores).

Kesteritas: overfitting severo (R² treino=0.959 vs teste=0.527) com Ridge —
inviabilizado por n=97 e subestimação GGA. Não reportar como resultado quantitativo.

---

### Validação HSE06

Usado como conjunto de teste externo (n=15) — calculados por interesse prévio,
não amostra aleatória. 13/15 concordâncias (87%). Resultado descritivo, não
estatisticamente conclusivo. Erros sistemáticos em compostos atípicos (Au no
sítio B'', GGA+U). Comparação direta gap GGA vs HSE06 indisponível —
nenhuma fórmula calculada em ambos os funcionais no dataset.

---

### PCA/UMAP como caracterização, não evidência de discriminação

Separação clara por regime e estrutura no espaço Magpie. Separação por janela
de gap não aparece. Usado no artigo como: "candidatos PV e IBSC compartilham
o mesmo espaço composicional, organizados por família elementar e tratamento
de correlação eletrônica — não por janela de gap."

Confundimento documentado: estrutura_esperada e regime_calc correlacionados
(GGA+U mais prevalente em relacionadas — ratio 2:1 vs 6:1 nas confirmadas).
Análises por regime têm interpretação parcialmente ambígua com estrutura.

---

### Top candidatos PV: nota sobre composição estrutural

Lista PV dominada pela série REB₂XO₄ (RE = terra rara, Bi, haleto, O) —
óxidos-halogenetos em camadas (tipo Aurivillius/Sillén), não double perovskitas
clássicas A₂B'B''X₆. Reportar como "compostos quaternários halogenados com gap
na janela PV identificados pela triagem", não como "double perovskitas".

Para Fase 4: diversificar seleção por família composicional interna — não apenas
REB₂XO₄. Objetivo é cobrir regiões distintas do espaço composicional.

---

### Otimização de hiperparâmetros (Seção 8, pendente execução)

**Limiar de reportabilidade:** ΔAUC ≥ 0.02 para classificação, ΔR² ≥ 0.05
para regressão. Abaixo disso, manter modelo mais simples.

**Busca:** Optuna (TPE, 50 trials). CV interno (5-fold) separado do CV de
avaliação final (RepeatedStratifiedKFold) — previne otimismo de estimativa.

**Calibração:** Platt scaling (CalibratedClassifierCV, sigmoid) para corrigir
sub-calibração do RF com class_weight=balanced. Probabilidades calibradas
mais confiáveis para priorização de candidatos na Fase 4.

---

## Notebooks por fase

- `v1_eda_exploratoria.ipynb` — campos originais (preservado)
- `v2_eda_campos_expandidos.ipynb` — EDA Fase 1
- `v3_descritores_magpie.ipynb` — Fase 2 (Magpie, seleção, correlações)
- `v4_modelos_ml.ipynb` — Fase 3 (classificação + PCA + regressão + validação HSE06)
- `v4_secao8_otimizacao.ipynb` — Fase 3 seção 8 (otimização, pendente execução)
- `v5_dos_candidatos.ipynb` — Fase 4 (DOS projetada, a criar)

---

## Decisões pendentes

| Decisão | Status | Fase |
|---|---|---|
| Otimização hiperparâmetros (XGBoost, ensembles) | Notebook criado, pendente execução | 3 |
| Threshold ótimo e calibração Platt | Pendente execução | 3 |
| Seleção final dos candidatos para DOS | Pendente — após Seção 8 | 3/4 |
| DOS projetada dos top candidatos PV e IBSC | A iniciar | 4 |
| Verificação estados dentro do gap (IBSC) | A iniciar | 4 |
| Correção gap DFT→experimental para candidatos finais | A iniciar | 4 |
| Materiais Mn/Fe/Co com gap=0 no GGA+U — revisão magnética | A iniciar | 4 |
| Fator de correção empírico GGA→experimental (verificar ~38% para PD) | Pendente | 4 |
| Referências bibliográficas incompletas (Sun 2016, artigo 177k estruturas, etc.) | Pendente | Artigo |
