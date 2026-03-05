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
| Termod. estáveis (hull=0) | — | — |
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
