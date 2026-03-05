# 04 — Referências Bibliográficas

**Formato:** autor(es), ano, título resumido, onde encontrar, anotação de relevância.  
**Status:** em construção — adicionar à medida que o projeto avança.

---

## Fundamentos teóricos

### Limite de eficiência fotovoltaica
**Shockley, W. & Queisser, H.J. (1961)**  
"Detailed Balance Limit of Efficiency of p‐n Junction Solar Cells"  
*Journal of Applied Physics*, 32, 510  
> Base do limite S-Q. A janela 1.0–1.8 eV adotada no projeto deriva diretamente 
> deste artigo. Eficiência máxima teórica ~33.7% para gap ~1.34 eV.

### Teoria da banda intermediária
**Luque, A. & Martí, A. (1997)**  
"Increasing the Efficiency of Ideal Solar Cells by Photon Induced Transitions 
at Intermediate Levels"  
*Physical Review Letters*, 78, 5014  
> Artigo fundador do conceito IBSC. Mostra que uma banda intermediária parcialmente 
> preenchida pode aumentar o limite S-Q para ~63%. Base conceitual para a janela 
> 1.8–2.6 eV adotada no projeto.

---

## Materials informatics — panorama

### Crescimento da área
**Wang, et al. (2021)**  
"Machine learning for solar cell materials"  
*(buscar referência exata)*  
> Documentou crescimento de 19 para 180+ publicações ML × células solares entre 
> 2015 e 2021. Usado para justificar o contexto do artigo.

---

## Double perovskitas halogenadas

### Protótipo Cs₂AgBiBr₆
**Greul, E. et al. (2017)** *(verificar autoria e título exatos)*  
> Cs₂AgBiBr₆ é a double perovskita halogenada livre de Pb mais estudada. 
> PCE máximo ~3% limitado pelo gap indireto largo. Referência baseline para 
> comparar candidatos identificados no projeto.

### Triagem computacional com ML
***(buscar artigo específico sobre screening de 7.056 estruturas A₂B'B''X₆)***  
> Usado redes neurais para triagem de espaço composicional. Metodologia de 
> referência para nossa abordagem.

### Geração de estruturas + triagem em 3 estágios
***(buscar artigo: 488 DFT → 177.264 via geração generativa → 434 candidatos)***  
> Pipeline mais completo encontrado na revisão. Combina geração generativa com 
> triagem por estabilidade → band gap → SLME. Referência metodológica chave.

---

## Kesteritas

### Eficiência certificada
***(buscar referência eficiência >14% certificada)***  
> Benchmark atual para kesteritas. Distância ao limite S-Q justifica esforço 
> de otimização composicional via ML.

### Triagem com XGBoost / LightGBM
***(buscar artigo: A₂BCX₄ com R² ~0.93)***  
> Modelos de gradient boosting para predição de band gap em kesteritas quaternárias. 
> Referência metodológica para a Fase 3 do projeto.

---

## Ferramentas e bases de dados

### Materials Project
**Jain, A. et al. (2013)**  
"Commentary: The Materials Project: A materials genome approach to accelerating 
materials innovation"  
*APL Materials*, 1, 011002  
> Artigo de referência principal da base de dados. **Citar obrigatoriamente** no artigo.

### pymatgen
**Ong, S.P. et al. (2013)**  
"Python Materials Genomics (pymatgen): A robust, open-source python library for 
materials analysis"  
*Computational Materials Science*, 68, 314–319  
> Biblioteca central do projeto. Citar se usar estruturas cristalinas diretamente.

### Matminer / Magpie
**Ward, L. et al. (2016)**  
"A general-purpose machine learning framework for predicting properties of 
inorganic materials"  
*npj Computational Materials*, 2, 16028  
> Introduz os descritores Magpie (114 features composicionais). Referência 
> central para a Fase 2.

### 2DMatPedia
**Zhou, J. et al. (2019)**  
"2DMatPedia, an open computational database of two-dimensional materials from 
top-down and bottom-up approaches"  
*Scientific Data*, 6, 86  
> Base de dados de materiais 2D com >6.000 estruturas. Relevante se o projeto 
> for expandido para materiais 2D.

---

## Revistas-alvo para submissão

| Revista | Fator de impacto (aprox.) | Perfil |
|---|---|---|
| npj Computational Materials | ~12 | Materials informatics, DFT + ML |
| Journal of Chemical Information and Modeling | ~6 | ML para propriedades moleculares/materiais |
| Computational Materials Science | ~4 | Cálculos e triagem computacional |
| Solar Energy Materials and Solar Cells | ~7 | Aplicações PV diretas |
| Physical Chemistry Chemical Physics | ~4 | Propriedades eletrônicas de materiais |

---

## A buscar (pendências)

- [ ] Artigo fundador do Materials Project (Jain 2013) — verificar versão mais citada
- [ ] Referência para limiar quasi-estabilidade 50 meV (Sun et al. 2016? Aykol et al. 2018?)
- [ ] Artigo de triagem double perovskitas com 177.264 estruturas geradas
- [ ] Artigo de kesteritas com R² ~0.93 via XGBoost
- [ ] Artigo de eficiência certificada >14% para CZTS
- [ ] Revisão recente (2023–2025) sobre ML para perovskitas livres de Pb
