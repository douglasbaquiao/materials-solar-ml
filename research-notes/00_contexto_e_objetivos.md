# 00 — Contexto e Objetivos do Projeto

**Iniciado em:** 2026-03  
**Pesquisador principal:** Douglas Baquião  
**Status:** exploração inicial

---

## Origem do projeto

Este projeto nasceu de dois objetivos paralelos:

1. **Artigo solo** — retomar conceitos de análise exploratória de dados (EDA) e 
   machine learning na prática, indo além do que é ensinado em aula. Serve também 
   como base metodológica para projetos futuros.

2. **Contexto institucional** — o pesquisador já orienta um aluno que trabalha com 
   dados do CAGED/SENAI-SP (clustering de empregos industriais). O artigo solo segue 
   caminho independente para não sobrepor os temas.

## Por que materials informatics?

- Pesquisador tem doutorado em materiais para células solares com **bandas intermediárias (IBSC)**
- Materials Project oferece dados DFT limpos, bem documentados e API acessível via Python
- Campo com boa tração internacional e menor saturação no Brasil que análise de emprego
- Não requer acesso a supercomputadores — contribuição via ML e engenharia de descritores

## Posicionamento metodológico

> Utilizar dados pré-calculados via DFT disponíveis no Materials Project como 
> matéria-prima. A contribuição científica reside na engenharia de descritores, 
> na triagem sistemática e na interpretação física dos padrões encontrados.

Isso é prática padrão em materials informatics — não é limitação, é o modelo do campo.

---

## Objetivos do artigo

### Objetivo principal
Explorar computacionalmente famílias de materiais candidatos a aplicações 
fotovoltaicas usando dados do Materials Project, combinando EDA com modelos 
preditivos de ML.

### Objetivos específicos (a refinar)
- [ ] Extrair e comparar duas famílias: double perovskitas halogenadas e kesteritas
- [ ] Identificar candidatos com gap na janela Shockley-Queisser (1.0–1.8 eV)
- [ ] Identificar candidatos para banda intermediária (gap 1.8–2.6 eV)
- [ ] Construir descritores composicionais (Magpie/Matminer) — Fase 2
- [ ] Treinar modelos preditivos de band gap e estabilidade — Fase 3
- [ ] Analisar DOS projetada dos candidatos finais — Fase 4

---

## Famílias de materiais em consideração

| Família | Fórmula geral | Motivação principal |
|---|---|---|
| Double perovskitas halogenadas | A₂B'B''X₆ | Livre de Pb, gap tunável, espaço composicional enorme |
| Kesteritas / A₂BCX₄ | Cu₂ZnSnS₄ e variantes | Elementos abundantes, não tóxicos, eficiências >14% reportadas |

### Famílias descartadas nesta fase
- **OSC (orgânicas):** dados de dispositivo ausentes no Materials Project
- **DSSC:** base não cobre bem moléculas orgânicas
- **2D materials:** reservado para fase futura se houver desdobramento

---

## Conexão com doutorado anterior

O mecanismo de **banda intermediária** estudado no doutorado é diretamente 
relevante para double perovskitas duplas: substituições no sítio B (dois metais 
diferentes) podem gerar estados dentro do gap por hibridização de orbitais d.

Isso diferencia o artigo de triagens genéricas de gap — há justificativa física 
para a janela estendida (1.8–2.6 eV) adotada como critério IBSC.

---

## Ferramentas e ambiente

| Ferramenta | Uso |
|---|---|
| Python + mp-api | Extração de dados do Materials Project |
| pymatgen | Manipulação de estruturas cristalinas |
| pandas / numpy | Processamento de dados |
| matplotlib / seaborn | Visualizações |
| matminer | Descritores composicionais (Fase 2) |
| Google Colab | Ambiente de execução (multi-instituição) |
| GitHub | Versionamento de código e notas |

## Referências iniciais relevantes

- Shockley & Queisser (1961) — limite teórico de eficiência célula solar
- Luque & Martí (1997) — teoria da célula de banda intermediária
- Wang et al. (2021) — crescimento de publicações ML × células solares (~10× em 6 anos)
- Double perovskitas livres de Pb: Cs₂AgBiBr₆ como protótipo mais estudado
- Kesteritas: eficiência certificada >14% reportada recentemente
