# 01 — Revisão da API do Materials Project e Campos Disponíveis

**Data:** 2026-03  
**Status:** concluído — campos definidos para v1 do pipeline

---

## Formas de acesso à API

### Três abordagens disponíveis

| Abordagem | Como usar | Quando usar |
|---|---|---|
| REST direto via `requests` | GET com header `X-API-KEY` | Exploração pontual, integração com outras linguagens |
| `MPRester` (cliente oficial) | `from mp_api.client import MPRester` | Padrão recomendado — todos os notebooks do projeto |
| Métodos de conveniência | `mpr.get_structure_by_material_id()` | Acesso a objetos pymatgen (estrutura, band structure, DOS) |

### Autenticação
- Chave obtida em materialsproject.org → dashboard do perfil
- **Nunca versionar a chave** — usar `.env` + `python-dotenv` localmente
- No Google Colab: usar aba **Secrets** (ver nota `05_ambiente_colab_github.md`)
- Variável de ambiente: `MP_API_KEY`

### Documentação de referência
- Swagger UI: `https://api.materialsproject.org/docs`
- Documentação Python: `https://materialsproject.github.io/api/`

---

## Endpoint principal: `materials.summary`

Agrega as propriedades mais usadas em triagem computacional em uma única query.
Alternativa a fazer múltiplas chamadas para endpoints separados.

### Campos adotados no projeto (CAMPOS_SUMMARY em extraction.py)

#### Identificação
| Campo | Tipo | Notas |
|---|---|---|
| `material_id` | str | ID único (ex: mp-149) |
| `formula_pretty` | str | Fórmula reduzida (ex: SiO₂) |
| `chemsys` | str | Sistema químico (ex: Si-O) |
| `elements` | list | Lista de elementos presentes |

#### Estrutura cristalina
| Campo | Tipo | Notas |
|---|---|---|
| `nelements` | int | Usado no filtro de extração (= 4 para quaternários) |
| `nsites` | int | Nº de sítios na célula unitária |
| `volume` | float (Ų) | Base para site_density (feature derivada) |
| `density` | float (g/cm³) | Proxy de compacidade e tipo de ligação |
| `symmetry` | objeto | Contém crystal_system, symbol, number — extraído manualmente |

#### Propriedades eletrônicas
| Campo | Tipo | Notas |
|---|---|---|
| `band_gap` | float (eV) | **Target principal** — calculado via DFT-PBE (subestima ~30%) |
| `is_gap_direct` | bool | Gap direto = absorção sem necessidade de fônon |
| `is_metal` | bool | band_gap = 0 |
| `efermi` | float (eV) | **Novo v2** — posição do nível de Fermi; indica tipo n ou p |

#### Óptica e dielétrica
| Campo | Tipo | Notas |
|---|---|---|
| `e_electronic` | float | **Novo v2** — contribuição eletrônica da constante dielétrica |
| `e_ionic` | float | **Novo v2** — contribuição iônica |
| `e_total` | float | **Novo v2** — soma das duas; ~40% cobertura na base |
| `n` (→ `n_refractive`) | float | **Novo v2** — índice de refração; afeta reflectância da célula |

#### Superfície e interface
| Campo | Tipo | Notas |
|---|---|---|
| `weighted_work_function` | float (eV) | **Novo v2** — crítico para alinhamento de bandas em heterojunções (afeta Voc) |
| `weighted_surface_energy` | float (J/m²) | **Novo v2** — relevante para crescimento de filme fino |

#### Termodinâmica
| Campo | Tipo | Notas |
|---|---|---|
| `energy_per_atom` | float (eV) | Energia DFT total |
| `formation_energy_per_atom` | float (eV) | Negativo = composto favorável em relação aos elementos |
| `energy_above_hull` | float (eV/átomo) | **Feature central de estabilidade** — 0 = no hull |
| `is_stable` | bool | True = energy_above_hull = 0 |
| `equilibrium_reaction_energy` | float (eV) | Energia de reação no equilíbrio |

#### Magnetismo
| Campo | Tipo | Notas |
|---|---|---|
| `total_magnetization` | float (µB) | Magnetização total |
| `total_magnetization_normalized_vol` | float | **Novo v2** — por volume |
| `ordering` | str | FM / AFM / FiM / NM |
| `num_magnetic_sites` | int | **Novo v2** |

#### Elasticidade (subconjunto dos materiais)
| Campo | Tipo | Notas |
|---|---|---|
| `bulk_modulus` (→ `bulk_modulus_vrh`) | float (GPa) | Extraído valor VRH |
| `shear_modulus` (→ `shear_modulus_vrh`) | float (GPa) | Extraído valor VRH |
| `universal_anisotropy` | float | Antes `elastic_anisotropy` |
| `poisson_ratio` | float | |

#### Metadados de qualidade
| Campo | Tipo | Notas |
|---|---|---|
| `theoretical` | bool | **Novo v2** — True = sem síntese experimental reportada |
| `deprecated` | bool | **Sempre filtrar** — materiais desatualizados no MP |
| `has_props` | list | **Novo v2** — indica quais propriedades adicionais existem |
| `possible_species` | list | **Novo v2** — espécies com estados de oxidação (ex: Ag+, Bi3+) |
| `database_IDs` | dict | **Novo v2** — IDs em ICSD, COD, etc. (indica referência experimental) |

---

## Campos disponíveis mas não adotados

| Campo | Motivo de exclusão |
|---|---|
| `k_reuss`, `k_voigt` | Redundante com bulk_modulus_vrh para nossos fins |
| `g_reuss`, `g_voigt` | Idem para shear_modulus |
| `piezoelectric_modulus` | Baixa relevância para PV convencional |
| `shape_factor` | Não relevante para triagem PV |
| `surface_energy_anisotropy` | Baixa prioridade nesta fase |
| `num_unique_magnetic_sites` | Granularidade excessiva para EDA inicial |

---

## Outros endpoints disponíveis (uso futuro)

| Endpoint | Uso planejado |
|---|---|
| `materials.electronic_structure` | Fase 4 — DOS projetada dos candidatos finais |
| `materials.thermo` | Detalhamento de decomposição termodinâmica |
| `materials.phonon` | Verificação de estabilidade dinâmica (modos imaginários) |
| `mpr.get_bandstructure_by_material_id()` | Análise de dispersão dos top candidatos |
| `mpr.get_dos_by_material_id()` | Confirmação de estados dentro do gap (IBSC) |

---

## Decisão de versionamento dos campos

- **v1 (notebook EDA inicial):** campos originais sem efermi, dielétricos, work_function
- **v2 (notebook EDA revisado + extraction.py):** lista completa acima
- Versão v1 preservada no repositório como `notebooks/v1_eda_exploratoria.ipynb`
- Alterações documentadas no commit do extraction.py
