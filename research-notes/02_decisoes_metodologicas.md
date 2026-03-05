# 02 — Decisões Metodológicas do Pipeline

**Data:** 2026-03  
**Status:** em andamento — decisões da Fase 1 consolidadas

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
semicondutores. Um gap DFT de 1.0 eV pode corresponder a ~1.3–1.5 eV 
experimental. Isso deve ser discutido na seção de limitações do artigo.

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
do gap. O gap largo sozinho não garante o mecanismo IBSC.

---

### Limiar de quasi-estabilidade: 0.05 eV/átomo

**Decisão:** HULL_THRESH = 0.05 eV/átomo

**Justificativa:** valor amplamente adotado na literatura de materials 
informatics (Sun et al., 2016; Aykol et al., 2018). Materiais com 
energy_above_hull < 50 meV/átomo são considerados potencialmente sintetizáveis 
sob condições controladas de temperatura e pressão.

**Alternativa mais restritiva:** usar is_stable = True (hull = 0) reduziria 
significativamente o número de candidatos — aceitar ~50 meV captura metaestáveis 
com relevância prática (muitos materiais funcionais conhecidos estão nessa faixa).

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

## Decisões de arquitetura do código

### Separação notebook / extraction.py

**Decisão:** lógica reutilizável em `src/extraction.py`; análise narrativa 
nos notebooks.

**Justificativa:** notebooks de análise (Fase 2, 3, 4) precisarão dos mesmos 
dados sem repetir código de extração. Evita inconsistências por copy-paste e 
garante que todos os notebooks usem as mesmas constantes físicas.

**Regra prática:** se um trecho de código responderia "como eu obtenho os dados", 
vai para extraction.py. Se responderia "o que eu descobri com esses dados", 
fica no notebook.

---

### Dois notebooks de EDA

**Decisão:** manter v1 (campos originais) e v2 (campos expandidos + extraction.py).

**Justificativa:** permite rastrear no repositório a evolução metodológica — 
a diferença entre os dois notebooks documenta as decisões tomadas após a 
revisão completa dos campos disponíveis na API.

**Commits relacionados:** ver histórico do repositório.

---

## Decisões pendentes (próximas fases)

| Decisão | Opções em consideração | Fase |
|---|---|---|
| Validação de estrutura double perovskita | Grupo espacial vs. possible_species | 2 |
| Correção de gap DFT→experimental | HSE06 disponível vs. correção empírica +30% | 2/4 |
| Split de validação para ML | Aleatório vs. split composicional | 3 |
| Descritores composicionais | Magpie (114 features) vs. subset manual | 2 |
| Interpretabilidade do modelo | SHAP values vs. importância de permutação | 3 |
