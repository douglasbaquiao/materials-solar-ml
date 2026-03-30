# 02 — Decisões Metodológicas do Pipeline

**Data:** 2026-03  
**Status:** Fase 1 consolidada; Fase 2 (descritores composicionais) consolidada

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
que não são necessariamente double perovskitas (podem ter estrutura de
rutilo, fluorita, etc.). Refinamento possível: verificar grupo espacial
Fm-3m ou I4/mmm (protótipos cúbico e tetragonal de double perovskita)
via pymatgen na Fase 2.

**Alternativa considerada:** buscar por `possible_species` contendo dois
cátions com estados de oxidação complementares (ex: B'+ + B'''+ = 4+).
Mais preciso, mas mais lento — reservado para refinamento pós-EDA.

---

### Filtro `nelements = 4`

**Decisão:** exigir exatamente 4 elementos distintos (A, B', B'', X).

**Justificativa:** double perovskitas têm 4 sítios cristalograficamente
distintos ocupados por 4 espécies diferentes. Kesteritas igualmente (Cu, Zn,
Sn, S no caso do CZTS).

**Impacto:** elimina perovskitas simples ABX₃ (3 elementos) e compostos
mais complexos com dopantes (5+ elementos).

---

### Filtro `nsites ≤ 40` (perovskitas) e `nsites ≤ 50` (kesteritas)

**Decisão:** remover materiais com célula unitária acima desses limites.

**Justificativa:** no Materials Project, supercélulas expandidas artificialmente
(2×2×2 da célula primitiva, por exemplo) aparecem como materiais distintos com
o mesmo composto. Para EDA e ML com features composicionais, elas são duplicatas
funcionais que inflariam o dataset sem adicionar informação nova.

**Validação:** inspeção manual de 10 materiais removidos pelo filtro confirmou
que eram supercélulas (nsites = 8×, 16× ou 32× da célula primitiva esperada).

**Risco:** pode remover estruturas genuinamente complexas com ordering
específico. Aceitável para triagem inicial — candidatos finais serão verificados
individualmente.

---

### `deprecated = False` sempre ativo

**Decisão:** filtrar materiais marcados como deprecated na query da API.

**Justificativa:** materiais deprecated foram substituídos por versões com
cálculo mais preciso ou corrigidas. Usar versões antigas introduziria ruído
desnecessário e potencialmente resultados incorretos.

**Implementação:** parâmetro nativo do `search()` — custo zero de performance.

---

## Decisões de feature engineering

### Janela fotovoltaica: 1.0–1.8 eV

**Decisão:** PV_GAP_MIN = 1.0 eV, PV_GAP_MAX = 1.8 eV

**Justificativa:** deriva diretamente do limite de Shockley-Queisser (1961).
A eficiência teórica máxima (~33.7%) ocorre em ~1.34 eV (GaAs). A janela
1.0–1.8 eV cobre materiais com eficiência teórica >25%.

**Atenção DFT:** os valores de band_gap do Materials Project são calculados
via DFT-PBE, que sistematicamente subestima gaps em ~30–50% para
semicondutores. Isso se aplica a **ambas as famílias**, não apenas às
kesteritas. Para double perovskitas halogenadas, a subestimação documentada
é de ~38% (Cs₂AgBiBr₆: DFT 1.35 eV → experimental 2.2 eV). Para kesteritas,
a subestimação é ainda mais severa em magnitude absoluta (CZTS: DFT 0.09 eV
→ HSE06 1.18 eV → experimental ~1.5 eV), chegando a classificar
incorretamente semicondutores como metais.

A consequência analítica é que a subestimação não é uniforme entre compostos —
varia sistematicamente com a composição e com o funcional usado (GGA vs
GGA+U). Qualquer correlação calculada com `band_gap` como target incorpora
esse ruído não-uniforme. Os candidatos identificados devem ser interpretados
como candidatos à janela de interesse após correção do funcional, não como
materiais com gap experimental confirmado na janela.

**Referência:** correções HSE06 disponíveis para subconjunto de materiais
no MP — usar para validar top candidatos na Fase 4.

---

### Janela IBSC: 1.8–2.6 eV

**Decisão:** PV_GAP_MAX = 1.8 eV como limite inferior, IBSC_GAP_MAX = 2.6 eV

**Justificativa:** materiais com banda intermediária precisam de gap do
hospedeiro maior que a janela S-Q convencional, pois a absorção ocorre em
dois passos (VB→IB e IB→CB). O limite superior de 2.6 eV permite que ambas
as sub-transições cubram parte relevante do espectro solar.

**Conexão com doutorado:** esta janela é diretamente motivada pela experiência
do pesquisador com IBSC — diferencia o artigo de triagens genéricas de gap.

**Nota metodológica:** candidatos IBSC identificados nesta fase precisarão de
análise de DOS projetada (Fase 4) para confirmar a existência de estados dentro
do gap. O gap largo sozinho não garante o mecanismo IBSC. Esta necessidade é
reforçada pelo achado da Fase 2: features composicionais Magpie não discriminam
candidatos IBSC dos demais em nenhuma condição de filtragem testada —
a triagem IBSC depende de informação eletrônica estrutural que os descritores
composicionais não capturam.

---

### Limiar de quasi-estabilidade: 0.05 eV/átomo

**Decisão:** HULL_THRESH = 0.05 eV/átomo

**Justificativa:** valor amplamente adotado na literatura de materials
informatics (Sun et al., 2016; Aykol et al., 2018 — verificar referências
exatas). Materiais com energy_above_hull < 50 meV/átomo são considerados
potencialmente sintetizáveis sob condições controladas de temperatura e
pressão.

**Alternativa mais restritiva:** usar is_stable = True (hull = 0) reduziria
significativamente o número de candidatos — aceitar ~50 meV captura
metaestáveis com relevância prática (muitos materiais funcionais conhecidos
estão nessa faixa).

**Nota:** o limiar de 0.50 eV/átomo considerado inicialmente para o conjunto
de treinamento ML foi descartado por ausência de respaldo sistemático na
literatura para síntese nessa faixa. O subconjunto ML usa o mesmo limiar
de 0.05 eV/átomo dos candidatos.

---

### Feature `site_density = nsites / volume`

**Decisão:** incluir como feature derivada.

**Justificativa:** captura informação sobre compacidade estrutural independente
do tamanho da célula unitária. Correlaciona com tipo de ligação (iônica tende
a ser mais compacta que covalente para mesma composição) e pode ser preditor
relevante para modelos de gap.

---

### Features de disponibilidade de dados

**Decisão:** adicionar `has_dielectric_data`, `has_elastic_data`,
`has_experimental_ref` como flags booleanas.

**Justificativa:** permitem triagem em dois estágios nos notebooks de análise —
identificar candidatos PV pelo gap, depois filtrar quais têm dados suficientes
para análise mais profunda sem fazer queries adicionais à API.

---

## Decisões de descritores composicionais — Fase 2

### Preset Magpie completo

**Decisão:** usar o preset `magpie` do matminer sem seleção a priori de features.

**Justificativa:** reprodutível e sem viés de seleção subjetiva. A versão
0.10.0 do matminer retorna 132 features (não 114 como em versões anteriores
— diferença decorre de propriedades atômicas adicionadas). Registrar versão
exata no `requirements.txt`.

**Limitação:** features Magpie são estritamente composicionais — não capturam
informação estrutural (simetria, distâncias de ligação, ângulos). Este limite
é discutido explicitamente no artigo.

---

### Seleção de features em dois passos

**Decisão:** (1) remover features com std < 0.01; (2) remover uma de cada par
com |r| > 0.95, mantendo a primeira.

**Resultado por subconjunto:**

| Subconjunto | Inicial | Pós-variância | Pós-colinearidade |
|---|---|---|---|
| PD filtrado (hull<0.05) | 132 | 124 | 88 |
| K filtrado (hull<0.05) | 132 | 120 | 81 |
| PD geral (sem hull) | 132 | 124 | 88 |
| K geral (sem hull) | 132 | 121 | 86 |

**Features comuns entre famílias (base comparativa):**
- PD e K filtrados: verificar interseção no notebook
- PD e K gerais: 78 features em comum

---

### Dois subconjuntos paralelos por família

**Decisão:** manter análises paralelas para (a) subconjunto filtrado
(usar_em_analise=True + não-metal + hull<0.05 eV/átomo) e (b) subconjunto
geral (usar_em_analise=True + não-metal, sem restrição de hull).

**Justificativa:** os dois subconjuntos revelam física complementar. No
subconjunto estável, features de elétrons (NdValence, NValence) dominam a
correlação com gap. No subconjunto geral, features de tamanho e período
(CovalentRadius, Row, Column) passam a dominar — refletindo maior diversidade
composicional. A comparação entre os dois é um resultado analítico em si.

**Importante:** ambos os subconjuntos usam apenas estruturas confirmadas
ou relacionadas (usar_em_analise=True). A categoria "outra" foi excluída
de ambos para garantir comparabilidade estrutural. Análise da categoria
"outra" reservada para trabalho futuro.

---

### Separação por regime de cálculo nas correlações

**Decisão:** calcular correlações Magpie × gap separadamente para GGA e
GGA+U, além do conjunto misto.

**Justificativa:** testes Mann-Whitney confirmam que GGA e GGA+U não são
amostras da mesma população composicional nas PD. `mean NdValence` difere
por fator ~2.4 entre regimes (GGA: 3.25, GGA+U: 1.37), refletindo que
materiais com metais de transição d são composicionalmente distintos dos
demais.

**Resultado:** features de número atômico médio e elétrons de valência
total invertem sinal de correlação com gap entre regimes (`mean NValence`:
-0.250 GGA vs +0.155 GGA+U). Features de dispersão de raio covalente e
elétrons d (`avg_dev CovalentRadius`, `avg_dev NdValence`) mantêm sinal
e magnitude entre regimes — são os descritores composicionais mais robustos
identificados.

**Para HSE06:** n=15–19 nos subconjuntos PD — insuficiente para correlações
estáveis. Reportado apenas descritivamente.

---

### Descritores robustos identificados (candidatos para o artigo)

Os dois descritores mais consistentes entre subconjuntos, regimes e famílias:

**`avg_dev CovalentRadius`:** menor dispersão de raio covalente associada
a gap menor nas PD (sinal estável em GGA e GGA+U). Interpretação: compostos
com átomos de tamanho mais homogêneo têm sobreposição orbital mais uniforme
e estados eletrônicos mais dispersos, fechando o gap. Robusto em todos os
subconjuntos testados.

**`avg_dev NdValence`:** maior heterogeneidade de elétrons d associada a
gap menor em ambas as famílias (sinal negativo consistente). Interpretação:
quando dois metais d com ocupações muito diferentes coexistem na composição,
a hibridização entre orbitais d cria separação mais clara entre estados
ocupados e vazios — abrindo o gap. Único descritor estável entre regimes
GGA e GGA+U nas PD.

---

### Discriminação PV vs IBSC por features composicionais

**Achado:** features composicionais Magpie discriminam candidatos PV dos
demais nas PD com sinal físico interpretável. Candidatos IBSC não mostram
discriminação composicional em nenhum subconjunto ou regime testado.

**Implicação metodológica:** a triagem IBSC não pode ser baseada em
descritores composicionais. A análise de DOS projetada (Fase 4) é necessária,
não opcional, para caracterizar candidatos IBSC. Isso reforça a contribuição
específica do projeto em relação ao background de doutorado do pesquisador.

**Robustez:** o padrão (PV discriminável, IBSC não discriminável) foi
observado em quatro condições independentes: subconjunto filtrado PD,
subconjunto geral PD, subconjunto filtrado K, subconjunto geral K.

---

## Decisões de arquitetura do código

### Separação notebook / extraction.py

**Decisão:** lógica reutilizável em `src/extraction.py`; análise narrativa
nos notebooks.

**Justificativa:** notebooks de análise (Fase 2, 3, 4) precisarão dos mesmos
dados sem repetir código de extração. Evita inconsistências por copy-paste e
garante que todos os notebooks usem as mesmas constantes físicas.

**Regra prática:** se um trecho de código responderia "como eu obtenho os
dados", vai para extraction.py. Se responderia "o que eu descobri com esses
dados", fica no notebook.

---

### Notebooks por fase

**Decisão:** um notebook principal por fase analítica.

- `v1_eda_exploratoria.ipynb` — campos originais (preservado para rastreabilidade)
- `v2_eda_campos_expandidos.ipynb` — EDA completa Fase 1 (estrutura, gap, hull, gráficos)
- `v3_descritores_magpie.ipynb` — Fase 2 (Magpie, seleção, correlações, datasets ML)
- `v4_modelos_ml.ipynb` — Fase 3 (classificação binária + caracterização) *(próximo)*

---

## Decisões pendentes (próximas fases)

| Decisão | Opções em consideração | Fase |
|---|---|---|
| Formulação ML principal | Classificação binária (candidato PV vs outros) + caracterização não-supervisionada (PCA/UMAP nos candidatos) | 3 |
| Tratamento kesteritas no ML | Modelo simples regularizado (Ridge/Lasso) ou apenas análise descritiva dado n=97 e problema GGA | 3 |
| Split de validação | Aleatório estratificado por regime vs split composicional | 3 |
| Interpretabilidade | SHAP values (preferencial) vs importância de permutação | 3 |
| Validação HSE06 top candidatos | Usar os 15–19 pontos HSE06 disponíveis como conjunto de teste externo | 3/4 |
| DOS projetada | Endpoint `materials.electronic_structure` para top candidatos PV e IBSC | 4 |
| Correção gap DFT→experimental | Fator empírico ~38% para PD vs HSE06 disponível | 4 |
| Materiais Mn/Fe/Co com gap=0 | Revisão de estado magnético inicial — candidatos a recálculo | 4 |
