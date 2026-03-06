"""
extraction.py
=============
Funções reutilizáveis para extração, limpeza e preparação de dados
do Materials Project em projetos de materials informatics.

Uso típico em qualquer notebook do projeto:

    from extraction import conectar_api, extrair_familia, adicionar_features

    mpr = conectar_api()
    df  = extrair_familia(mpr, "perovskita")
    df  = adicionar_features(df)

Dependências:
    pip install mp-api pymatgen pandas python-dotenv
"""

import os
import warnings
import pandas as pd
from dotenv import load_dotenv
from mp_api.client import MPRester

warnings.filterwarnings("ignore")

# ─── Constantes físicas do domínio ───────────────────────────────────────────
# Centralizar aqui garante que todos os notebooks usem os mesmos valores.
# Se você decidir mudar a janela PV, muda em um único lugar.

PV_GAP_MIN   = 1.0   # eV — limite inferior Shockley-Queisser
PV_GAP_MAX   = 1.8   # eV — limite superior Shockley-Queisser
IBSC_GAP_MAX = 2.6   # eV — limite superior para candidatos a banda intermediária
HULL_THRESH  = 0.05  # eV/átomo — limiar de quasi-estabilidade termodinâmica

# ─── Campos extraídos do endpoint summary ────────────────────────────────────
# Lista canônica do projeto. Qualquer campo novo discutido e aprovado
# deve ser adicionado aqui — todos os notebooks herdam automaticamente.
CAMPOS_SUMMARY = [
    # Identificação
    "material_id",
    "formula_pretty",
    "chemsys",
    "elements",
    # Estrutura
    "nelements",
    "nsites",
    "volume",
    "density",
    "symmetry",
    # Eletrônica
    "band_gap",
    "is_gap_direct",
    "is_metal",
    "efermi",
    # Óptica / dielétrica
    "e_electronic",
    "e_ionic",
    "e_total",
    "n",                                        # índice de refração
    # Superfície e interface
    "weighted_work_function",                   # crítico para alinhamento em heterojunções
    "weighted_surface_energy",
    # Termodinâmica
    "energy_per_atom",
    "formation_energy_per_atom",
    "energy_above_hull",
    "is_stable",
    "equilibrium_reaction_energy",
    # Magnetismo
    "total_magnetization",
    "total_magnetization_normalized_vol",
    "ordering",
    "num_magnetic_sites",
    # Elasticidade (disponível para subconjunto)
    "bulk_modulus",
    "shear_modulus",
    "universal_anisotropy",
    "poisson_ratio",
    # Metadados de qualidade
    "theoretical",                              # True = sem síntese experimental reportada
    "deprecated",                               # True = versão desatualizada no MP
    "has_props",                                # lista de propriedades adicionais disponíveis
    "possible_species",                         # espécies com estados de oxidação inferidos
    "database_IDs",                             # IDs cruzados (ICSD, COD, etc.)
]

# ─── Parâmetros de extração por família ──────────────────────────────────────
# Dicionário que define como cada família é buscada na API.
# Adicionar novas famílias aqui sem tocar nas funções abaixo.
FAMILIAS = {
    "perovskita": {
        "descricao":  "Double Perovskites Halogenadas (A2B'B''X6)",
        "marcadores": ["F", "Cl", "Br", "I"],   # ao menos um desses deve estar presente
        "nelements":  (4, 4),                    # exatamente 4 elementos distintos
        "band_gap":   (0.0, 4.0),               # eV
        "nsites_max": 40,                        # remove supercélulas expandidas
    },
    "kesterita": {
        "descricao":  "Kesteritas e Quaternários A2BCX4",
        "marcadores": ["S", "Se"],
        "nelements":  (4, 4),
        "band_gap":   (0.0, 3.5),
        "nsites_max": 50,
    },
}


# ─── 1. Autenticação ─────────────────────────────────────────────────────────

def conectar_api(chave: str | None = None) -> MPRester:
    """
    Retorna uma instância autenticada do MPRester.

    Ordem de prioridade para a chave:
      1. Argumento explícito `chave`
      2. Variável de ambiente MP_API_KEY
      3. Arquivo .env na raiz do projeto (carregado via python-dotenv)

    Raises:
        EnvironmentError: se nenhuma chave for encontrada.

    Exemplo:
        mpr = conectar_api()
        # ou, durante desenvolvimento rápido:
        mpr = conectar_api("minha_chave_temporaria")
    """
    load_dotenv()  # carrega .env se existir — sem efeito se já estiver no ambiente

    api_key = chave or os.environ.get("MP_API_KEY")

    if not api_key or api_key == "SUA_CHAVE_AQUI":
        raise EnvironmentError(
            "Chave de API não encontrada. Configure a variável de ambiente MP_API_KEY "
            "ou crie um arquivo .env com MP_API_KEY=sua_chave."
        )

    return MPRester(api_key)


# ─── 2. Conversão de documentos ──────────────────────────────────────────────

def docs_para_df(docs: list) -> pd.DataFrame:
    """
    Converte lista de SummaryDoc (retornada pela API) em DataFrame pandas.

    O objeto `symmetry` é um sub-objeto aninhado — extraímos seus campos
    manualmente. Campos ausentes em algum documento recebem None.

    Args:
        docs: lista de objetos SummaryDoc retornados por mpr.materials.summary.search()

    Returns:
        DataFrame com uma linha por material e colunas para cada campo extraído.
    """
    registros = []

    for d in docs:
        sym = d.symmetry if d.symmetry else None

        # Campos aninhados em symmetry
        crystal_system     = getattr(sym, "crystal_system", None)
        spacegroup_symbol  = getattr(sym, "symbol", None)
        spacegroup_number  = getattr(sym, "number", None)

        # bulk_modulus e shear_modulus podem ser objetos com sub-campos (vrh, reuss, voigt)
        # Extraímos apenas o valor VRH (média de Voigt-Reuss-Hill), o mais usado
        bm = getattr(d, "bulk_modulus",  None)
        sm = getattr(d, "shear_modulus", None)
        bulk_modulus_vrh  = getattr(bm, "vrh", None) if bm else None
        shear_modulus_vrh = getattr(sm, "vrh", None) if sm else None

        registros.append({
            # Identificação
            "material_id":                          d.material_id,
            "formula":                              d.formula_pretty,
            "chemsys":                              d.chemsys,
            "elements":                             [str(e) for e in (d.elements or [])],
            # Estrutura
            "nelements":                            d.nelements,
            "nsites":                               d.nsites,
            "volume":                               d.volume,
            "density":                              d.density,
            "crystal_system":                       str(crystal_system) if crystal_system else None,
            "spacegroup_symbol":                    spacegroup_symbol,
            "spacegroup_number":                    spacegroup_number,
            # Eletrônica
            "band_gap":                             d.band_gap,
            "is_gap_direct":                        d.is_gap_direct,
            "is_metal":                             d.is_metal,
            "efermi":                               getattr(d, "efermi", None),
            # Óptica
            "e_electronic":                         getattr(d, "e_electronic", None),
            "e_ionic":                              getattr(d, "e_ionic",      None),
            "e_total":                              getattr(d, "e_total",      None),
            "n_refractive":                         getattr(d, "n",            None),
            # Superfície
            "weighted_work_function":               getattr(d, "weighted_work_function",  None),
            "weighted_surface_energy":              getattr(d, "weighted_surface_energy", None),
            # Termodinâmica
            "energy_per_atom":                      d.energy_per_atom,
            "formation_energy_per_atom":            d.formation_energy_per_atom,
            "energy_above_hull":                    d.energy_above_hull,
            "is_stable":                            d.is_stable,
            "equilibrium_reaction_energy":          getattr(d, "equilibrium_reaction_energy", None),
            # Magnetismo
            "total_magnetization":                  d.total_magnetization,
            "total_magnetization_normalized_vol":   getattr(d, "total_magnetization_normalized_vol", None),
            "ordering":                             str(d.ordering) if d.ordering else None,
            "num_magnetic_sites":                   getattr(d, "num_magnetic_sites", None),
            # Elasticidade
            "bulk_modulus_vrh":                     bulk_modulus_vrh,
            "shear_modulus_vrh":                    shear_modulus_vrh,
            "universal_anisotropy":                 getattr(d, "universal_anisotropy", None),
            "poisson_ratio":                        getattr(d, "poisson_ratio",        None),
            # Metadados
            "theoretical":                          getattr(d, "theoretical",  None),
            "deprecated":                           getattr(d, "deprecated",   None),
            "has_props":                            list(d.has_props) if d.has_props else [],
            "possible_species":                     [str(s) for s in (d.possible_species or [])],
            "database_IDs":                         dict(d.database_IDs) if getattr(d, "database_IDs", None) else {},
        })

    return pd.DataFrame(registros)


# ─── 3. Extração por família ──────────────────────────────────────────────────

def extrair_familia(
    mpr:     MPRester,
    familia: str,
    campos:  list | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Extrai materiais de uma família pré-definida usando os parâmetros em FAMILIAS.

    Args:
        mpr:     instância autenticada do MPRester
        familia: chave do dicionário FAMILIAS ("perovskita" ou "kesterita")
        campos:  lista de campos a extrair (padrão: CAMPOS_SUMMARY)
        verbose: se True, imprime progresso da extração

    Returns:
        DataFrame limpo (sem duplicatas, nsites filtrado, deprecated removido)

    Raises:
        KeyError: se `familia` não existir em FAMILIAS

    Exemplo:
        mpr = conectar_api()
        df  = extrair_familia(mpr, "perovskita")
    """
    if familia not in FAMILIAS:
        raise KeyError(f"Família '{familia}' não definida. Opções: {list(FAMILIAS.keys())}")

    params   = FAMILIAS[familia]
    _campos  = campos or CAMPOS_SUMMARY

    if verbose:
        print(f"\n{'─'*60}")
        print(f"Extraindo: {params['descricao']}")
        print(f"{'─'*60}")

    todos = []
    for marcador in params["marcadores"]:
        docs = mpr.materials.summary.search(
            elements=   [marcador],
            nelements=  params["nelements"],
            band_gap=   params["band_gap"],
            deprecated= False,              # sempre excluir materiais deprecados
            fields=     _campos,
        )
        todos.extend(docs)
        if verbose:
            print(f"  [{marcador}] {len(docs):>5} documentos")

    if verbose:
        print(f"  Total bruto: {len(todos)}")

    df = docs_para_df(todos)

    # ── Limpeza ──────────────────────────────────────────────────────────────
    # 1. Remover supercélulas artificialmente grandes
    df = df[df["nsites"] <= params["nsites_max"]].copy()

    # 2. Remover duplicatas — podem surgir se um material contém dois marcadores
    n_antes = len(df)
    df = df.drop_duplicates(subset="material_id").reset_index(drop=True)
    n_duplas = n_antes - len(df)

    # 3. Remover materiais deprecados que passaram pelo filtro (segurança extra)
    if "deprecated" in df.columns:
        df = df[df["deprecated"] != True].copy()

    if verbose:
        print(f"  Após filtro nsites≤{params['nsites_max']}: {len(df) + n_duplas}")
        print(f"  Duplicatas removidas: {n_duplas}")
        print(f"  ✓ Final: {len(df)} materiais\n")

    return df


# ─── 4. Engenharia de features ────────────────────────────────────────────────

def adicionar_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas derivadas ao DataFrame.

    Features adicionadas:
        site_density         : nsites / volume — proxy de compacidade
        is_pv_candidate      : gap ∈ [PV_GAP_MIN, PV_GAP_MAX] e não-metal
        is_ibsc_candidate    : gap ∈ (PV_GAP_MAX, IBSC_GAP_MAX] e não-metal
        near_hull            : energy_above_hull < HULL_THRESH
        gap_category         : rótulo categórico do gap (útil para plots e groupby)
        has_dielectric_data  : True se e_total está disponível
        has_elastic_data     : True se bulk_modulus_vrh está disponível
        has_experimental_ref : True se database_IDs não está vazio (tem referência experimental)

    Args:
        df: DataFrame retornado por extrair_familia() ou docs_para_df()

    Returns:
        DataFrame com colunas adicionais (operação não-destrutiva — retorna cópia)
    """
    df = df.copy()

    # ── Estrutural ────────────────────────────────────────────────────────────
    df["site_density"] = df["nsites"] / df["volume"]

    # ── Fotovoltaico ──────────────────────────────────────────────────────────
    nao_metal = ~df["is_metal"]

    df["is_pv_candidate"] = (
        nao_metal &
        (df["band_gap"] >= PV_GAP_MIN) &
        (df["band_gap"] <= PV_GAP_MAX)
    )
    df["is_ibsc_candidate"] = (
        nao_metal &
        (df["band_gap"] >  PV_GAP_MAX) &
        (df["band_gap"] <= IBSC_GAP_MAX)
    )

    # ── Termodinâmica ─────────────────────────────────────────────────────────
    df["near_hull"] = df["energy_above_hull"] < HULL_THRESH

    # ── Categórico de gap ─────────────────────────────────────────────────────
    def _categorizar(row):
        if row["is_metal"]:
            return "Metal"
        g = row["band_gap"]
        if g < PV_GAP_MIN:
            return f"Gap estreito (<{PV_GAP_MIN} eV)"
        if g <= PV_GAP_MAX:
            return "Janela PV (1.0–1.8 eV)"
        if g <= IBSC_GAP_MAX:
            return "Janela IBSC (1.8–2.6 eV)"
        return f"Gap largo (>{IBSC_GAP_MAX} eV)"

    df["gap_category"] = df.apply(_categorizar, axis=1)

    # ── Disponibilidade de dados adicionais ───────────────────────────────────
    # Útil para decidir quais análises são possíveis para cada subconjunto
    df["has_dielectric_data"]  = df["e_total"].notna()
    df["has_elastic_data"]     = df["bulk_modulus_vrh"].notna()
    df["has_experimental_ref"] = df["database_IDs"].apply(
        lambda x: isinstance(x, dict) and len(x) > 0
    )

    return df


# ─── 5. Exportação ────────────────────────────────────────────────────────────

def exportar(df: pd.DataFrame, nome: str, pasta: str = "data/processed") -> str:
    """
    Exporta DataFrame para CSV na pasta especificada, criando-a se necessário.

    Args:
        df:    DataFrame a exportar
        nome:  nome do arquivo (sem extensão)
        pasta: caminho relativo da pasta de destino

    Returns:
        Caminho completo do arquivo gerado.

    Exemplo:
        exportar(df_p, "double_perovskitas")
        # salva em data/processed/double_perovskitas.csv
    """
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, f"{nome}.csv")
    df.to_csv(caminho, index=False)
    print(f"  Exportado: {caminho}  ({len(df)} linhas, {len(df.columns)} colunas)")
    return caminho


# ─── 6. Carregamento ──────────────────────────────────────────────────────────

def carregar(nome: str, pasta: str = "data/processed") -> pd.DataFrame:
    """
    Carrega um CSV exportado anteriormente, evitando re-extrair da API.

    Útil para notebooks de análise que não precisam repetir a extração.

    Args:
        nome:  nome do arquivo (sem extensão)
        pasta: caminho relativo da pasta

    Returns:
        DataFrame carregado do CSV.

    Raises:
        FileNotFoundError: se o arquivo não existir.

    Exemplo:
        df_p = carregar("double_perovskitas")
    """
    caminho = os.path.join(pasta, f"{nome}.csv")
    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Arquivo '{caminho}' não encontrado. "
            "Execute a extração primeiro com extrair_familia()."
        )
    df = pd.read_csv(caminho)
    print(f"  Carregado: {caminho}  ({len(df)} linhas, {len(df.columns)} colunas)")
    return df


# ─── 7. Pipeline completo ─────────────────────────────────────────────────────

def pipeline_completo(
    familias:   list | None = None,
    exportar_:  bool = True,
    verbose:    bool = True,
) -> dict[str, pd.DataFrame]:
    """
    Executa extração, limpeza e feature engineering para todas as famílias.

    Ponto de entrada conveniente para o primeiro notebook de um projeto novo
    ou para re-extrair dados após atualização do Materials Project.

    Args:
        familias:  lista de famílias a extrair (padrão: todas em FAMILIAS)
        exportar_: se True, salva CSVs em data/processed/
        verbose:   se True, imprime progresso

    Returns:
        Dicionário {nome_familia: DataFrame} com features já adicionadas.

    Exemplo:
        dados = pipeline_completo()
        df_p  = dados["perovskita"]
        df_k  = dados["kesterita"]
    """
    _familias = familias or list(FAMILIAS.keys())
    resultados = {}

    mpr = conectar_api()

    for fam in _familias:
        df = extrair_familia(mpr, fam, verbose=verbose)
        df = adicionar_features(df)
        resultados[fam] = df
        if exportar_:
            exportar(df, fam)

    if verbose:
        print("\n" + "="*60)
        print("Pipeline concluído:")
        for fam, df in resultados.items():
            cands_pv   = df["is_pv_candidate"].sum()
            cands_ibsc = df["is_ibsc_candidate"].sum()
            estaveis   = df["is_stable"].sum()
            print(f"  {fam:15s}: {len(df):>5} materiais  |  "
                  f"PV: {cands_pv:>4}  |  IBSC: {cands_ibsc:>4}  |  Estáveis: {estaveis:>4}")
        print("="*60)

    return resultados

!git config --global user.email "douglasbaquiao@gmail.com"
!git config --global user.name "Douglas Baquião"
!git add src/extraction.py
!git commit -m "Atualização com inclusão de acesso ao Github"
!git push


# ─── Execução direta (teste rápido) ───────────────────────────────────────────

if __name__ == "__main__":
    """
    Executar diretamente para testar a extração:
        python extraction.py
    """
    dados = pipeline_completo(exportar_=True, verbose=True)
