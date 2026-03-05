# 05 — Ambiente de Trabalho: Google Colab + GitHub

**Data:** 2026-03  
**Contexto:** trabalho em múltiplas instituições; necessidade de ambiente 
reproduzível sem dependência de máquina específica.

---

## Decisão de ambiente

| Opção | Prós | Contras | Decisão |
|---|---|---|---|
| Máquina local | Controle total, Git nativo | Depende da máquina, SSH a configurar | Usar para revisões ocasionais |
| Google Colab | Multi-instituição, zero setup | Sessão temporária, integração Git via UI | **Principal** |
| JupyterHub institucional | Persistente, seguro | Disponibilidade depende da instituição | Avaliar futuramente |

---

## Gerenciamento da chave de API no Colab

### O problema
O arquivo `.env` com a chave MP_API_KEY não pode ir para o repositório público 
(ou mesmo privado sem cuidado). O Colab não persiste arquivos entre sessões.

### Solução adotada: Colab Secrets

A aba **Secrets** (ícone de chave no menu lateral esquerdo do Colab) armazena 
variáveis de forma persistente vinculadas à conta Google — **persiste entre sessões**.

**Como configurar (uma única vez):**
1. Abrir qualquer notebook no Colab
2. Clicar no ícone de chave (🔑) na barra lateral esquerda
3. Clicar em "Add new secret"
4. Nome: `MP_API_KEY`  
5. Valor: sua chave do Materials Project
6. Ativar o toggle "Notebook access"

**Como usar no notebook:**
```python
from google.colab import userdata

MP_API_KEY = userdata.get("MP_API_KEY")
```

**Por que é segura:** os secrets ficam na conta Google, não no código nem no 
repositório. Mesmo que o notebook seja compartilhado publicamente, a chave 
não fica exposta.

### Compatibilidade com extraction.py

A função `conectar_api()` em `extraction.py` usa `os.environ.get("MP_API_KEY")`.
Para compatibilidade com o Colab, adicionar no início do notebook antes de 
importar o módulo:

```python
import os
from google.colab import userdata

# Injeta o secret como variável de ambiente para o extraction.py usar normalmente
os.environ["MP_API_KEY"] = userdata.get("MP_API_KEY")

# A partir daqui, extraction.py funciona sem modificação
from extraction import conectar_api, extrair_familia
```

---

## Importação do extraction.py no Colab

O Colab não tem o arquivo local. Duas opções:

### Opção A — Clonar o repositório (recomendada para sessões de trabalho)
```python
!git clone https://github.com/seuusuario/materials-solar-ml.git
import sys
sys.path.insert(0, "/content/materials-solar-ml/src")
from extraction import pipeline_completo, carregar
```

### Opção B — Baixar apenas o arquivo (mais rápido para testes)
```python
!wget -q https://raw.githubusercontent.com/seuusuario/materials-solar-ml/main/src/extraction.py
from extraction import pipeline_completo, carregar
```

**Atenção:** a Opção B sempre baixa a versão do branch `main`. Se você estiver 
trabalhando em um branch diferente, ajuste a URL.

---

## Instalação de dependências no Colab

O Colab já tem pandas, numpy e matplotlib. Instalar apenas o que falta:

```python
!pip install mp-api pymatgen python-dotenv -q
```

Adicionar essa célula no início de todo notebook — é rápida (~30s) e 
garante versões corretas.

---

## Workflow de versionamento via interface gráfica

### Salvar notebook no GitHub
`Arquivo → Salvar uma cópia no GitHub`
- Selecionar repositório: `materials-solar-ml`
- Branch: `main` (ou branch específico se estiver experimentando)
- Escrever mensagem de commit no campo disponível
- Confirmar

### Abrir notebook do GitHub no Colab
- Opção 1: na URL do GitHub, substituir `github.com` por `colab.research.google.com/github`
- Opção 2: `Arquivo → Abrir notebook → GitHub` → buscar pelo repositório

### Editar arquivos .py (extraction.py, etc.)
- Editar diretamente na interface web do GitHub (lápis no canto superior direito)
- Ou clonar no Colab, editar, e fazer push via terminal:
  ```bash
  !git config --global user.email "seu@email.com"
  !git config --global user.name "Seu Nome"
  !git add src/extraction.py
  !git commit -m "mensagem"
  !git push
  ```
  *(o push via terminal no Colab exige Personal Access Token — ver abaixo)*

---

## Personal Access Token (PAT) para push via terminal

Se precisar usar o terminal do Colab para push (edições em `.py`):

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → selecionar escopo `repo`
3. Copiar o token gerado
4. Adicionar como secret no Colab com nome `GITHUB_TOKEN`

Uso no terminal do Colab:
```bash
!git remote set-url origin https://$GITHUB_TOKEN@github.com/seuusuario/materials-solar-ml.git
!git push origin main
```

**Nunca colocar o token diretamente no código** — sempre via secret ou variável de ambiente.

---

## Estrutura do repositório

```
materials-solar-ml/
│
├── .gitignore
├── README.md
├── requirements.txt
│
├── src/
│   └── extraction.py          ← módulo de extração (versionar sempre)
│
├── notebooks/
│   ├── v1_eda_exploratoria.ipynb    ← versão inicial (campos originais)
│   └── v2_eda_campos_expandidos.ipynb  ← versão com extraction.py + novos campos
│
├── data/
│   ├── raw/                   ← no .gitignore
│   └── processed/             ← no .gitignore (CSVs grandes)
│
└── research-notes/
    ├── 00_contexto_e_objetivos.md
    ├── 01_revisao_api_campos.md
    ├── 02_decisoes_metodologicas.md
    ├── 03_experimentos_e_resultados.md
    ├── 04_referencias.md
    └── 05_ambiente_colab_github.md   ← este arquivo
```

---

## .gitignore recomendado

```gitignore
# Chave de API e secrets
.env
*.env
config.py

# Dados (podem ser grandes e são reproduzíveis via extraction.py)
data/raw/
data/processed/
*.csv
*.json

# Python
__pycache__/
*.pyc
.ipynb_checkpoints/
venv/
.venv/

# Sistema
.DS_Store
Thumbs.db
```

**Exceção:** se quiser versionar os CSVs dos candidatos finais (pequenos, 
relevantes para reprodutibilidade do artigo), remover `*.csv` do .gitignore 
e adicionar explicitamente só os grandes:
```gitignore
data/raw/*.csv
data/processed/double_perovskitas_raw.csv
data/processed/kesteritas_raw.csv
```
