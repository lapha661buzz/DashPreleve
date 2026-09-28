"""
Plateforme de Suivi des Pertes de Revenu — Baobab
==================================================
Application Streamlit permettant d'explorer les revenus non prélevés
par Client, par Agence et par Type de revenu, filiale par filiale.

Pour ajouter une filiale : déposer son fichier de résultats dans le dossier `data/`
puis ajouter une entrée dans le dictionnaire FILIALES ci-dessous.
"""

import base64
import csv
import fnmatch
import os
import re

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------------------
# CHEMINS
# --------------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGO_PATH = os.path.join(BASE_DIR, "logo-dark.png")

# --------------------------------------------------------------------------------------
# FILIALES — une entrée par filiale
#   data     : motifs (dans l'ordre) du fichier Excel de résultats, dossier data/
#   branches : motifs du fichier CSV « code agence -> nom d'agence » (facultatif)
#   currency : devise affichée
# --------------------------------------------------------------------------------------
FILIALES = {
    "Madagascar": {
        "data": ["Resultat.xlsx"],
        "branches": ["MADA MCR.BRANCH.TABLE.csv", "MADA*BRANCH*.csv"],
        "currency": "MGA",
    },
    "Mali": {
        "data": ["ResultatML.xlsx", "ResultatML*.xls*"],
        "branches": ["MLagence*.csv", "ML*agence*.csv", "ML*BRANCH*.csv", "MALI*BRANCH*.csv"],
        "currency": "FCFA",
    },
}

REQUIRED_COLUMNS = [
    "Pays", "ID Contrat", "Numero de compte", "ID Client", "Type de revenu",
    "Solde du compte", "Montant non prélevé", "Date d'identification",
]


def find_file(patterns):
    """Retourne le premier fichier de data/ correspondant aux motifs (insensible à la casse)."""
    if not os.path.isdir(DATA_DIR):
        return None
    names = os.listdir(DATA_DIR)
    for pat in patterns or []:
        for n in sorted(names):
            if fnmatch.fnmatch(n.lower(), pat.lower()):
                return os.path.join(DATA_DIR, n)
    return None


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


# --------------------------------------------------------------------------------------
# CONFIGURATION GENERALE
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Baobab | Pertes de Revenu",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------------------
# PALETTE & TYPOGRAPHIE (couleur de marque extraite du logo Baobab)
# --------------------------------------------------------------------------------------
INK = "#101828"
MUTED = "#6B7280"
PAPER = "#F7F7F4"
CARD = "#FFFFFF"
LINE = "#E3E2DD"
BRAND = "#E40473"        # rose Baobab — Intérêt / identité de marque
BRAND_SOFT = "#FCE4F0"
RUST = "#C1553A"         # Pénalité / signal de fuite
RUST_SOFT = "#F7E9E4"

TYPE_COLOR = {"Intérêt": BRAND, "Pénalité": RUST}


def color_for_type(t: str) -> str:
    return TYPE_COLOR.get(str(t), INK)


def get_base64_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


logo_b64 = get_base64_image(LOGO_PATH) if os.path.exists(LOGO_PATH) else None

# --------------------------------------------------------------------------------------
# STYLE
# --------------------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        .stApp {{ background-color: {PAPER}; }}
        .block-container {{ padding-top: 2.4rem; padding-bottom: 3rem; max-width: 1180px; }}

        h1, h2, h3, h4 {{
            font-family: 'Inter', sans-serif;
            color: {INK};
            font-weight: 600;
        }}

        /* ---------- Barre latérale ---------- */
        section[data-testid="stSidebar"] {{
            background-color: {INK};
        }}
        section[data-testid="stSidebar"] * {{
            color: #E7E7E2 !important;
        }}
        section[data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.12);
        }}
        section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
            background-color: {BRAND} !important;
        }}
        /* Champs à fond clair : texte foncé pour rester lisible */
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] *,
        section[data-testid="stSidebar"] .stDateInput input {{
            color: {INK} !important;
        }}
        section[data-testid="stSidebar"] .streamlit-expanderHeader,
        section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
            background-color: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 6px;
            font-size: 0.9rem;
        }}
        section[data-testid="stSidebar"] [data-testid="stExpander"] {{
            border: none;
            margin-bottom: 2px;
        }}
        section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {{
            color: #9CA3AF !important;
            margin-bottom: 10px;
            display: block;
        }}
        .sidebar-logo {{
            height: 46px;
            width: auto;
            margin-top: 6px;
            margin-bottom: 16px;
        }}

        /* ---------- En-tête / hero ---------- */
        .hero {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid {LINE};
            padding-top: 18px;
            padding-bottom: 22px;
            margin-top: 8px;
            margin-bottom: 28px;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .hero-brand {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .hero-logo {{
            height: 64px;
            width: auto;
        }}
        .hero-mark {{
            display: inline-block;
            width: 10px; height: 10px;
            background: linear-gradient(135deg, {BRAND}, {RUST});
            border-radius: 3px;
        }}
        .hero-title {{
            font-family: 'Fraunces', serif;
            font-size: 2.1rem;
            font-weight: 500;
            color: {INK};
            margin: 0;
            line-height: 1.15;
        }}
        .hero-subtitle {{
            color: {MUTED};
            font-size: 0.95rem;
            margin-top: 6px;
        }}
        .hero-stat-label {{
            color: {MUTED};
            font-size: 0.8rem;
            margin-bottom: 2px;
        }}
        .hero-stat-value {{
            font-family: 'Fraunces', serif;
            font-size: 2.3rem;
            font-weight: 500;
            color: {BRAND};
            line-height: 1;
        }}

        /* ---------- Metrics natifs Streamlit ---------- */
        div[data-testid="stMetric"] {{
            background-color: {CARD};
            border: 1px solid {LINE};
            border-radius: 8px;
            padding: 14px 18px;
        }}
        div[data-testid="stMetric"] label {{
            color: {MUTED} !important;
            font-weight: 500;
        }}
        div[data-testid="stMetricValue"] {{
            font-family: 'Fraunces', serif;
            color: {INK};
        }}

        /* ---------- Onglets (style souligné, sobre) ---------- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 28px;
            border-bottom: 1px solid {LINE};
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            padding: 4px 2px 12px 2px;
            font-weight: 500;
            color: {MUTED};
            border-bottom: 2px solid transparent;
        }}
        .stTabs [aria-selected="true"] {{
            color: {INK} !important;
            border-bottom: 2px solid {BRAND} !important;
            background-color: transparent !important;
        }}

        /* ---------- Carte de synthèse (client / agence / type) ---------- */
        .summary-card {{
            background: {CARD};
            border: 1px solid {LINE};
            border-left: 3px solid {INK};
            border-radius: 6px;
            padding: 20px 24px;
            margin-bottom: 18px;
        }}
        .summary-card .name {{
            font-size: 0.85rem;
            color: {MUTED};
            margin-bottom: 4px;
        }}
        .summary-card .amount {{
            font-family: 'Fraunces', serif;
            font-size: 2rem;
            font-weight: 500;
            color: {INK};
            margin-bottom: 6px;
        }}
        .summary-card .meta {{
            color: {MUTED};
            font-size: 0.88rem;
        }}

        /* ---------- Badge type de revenu (contour, pas de fond plein) ---------- */
        .type-pill {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            border: 1px solid currentColor;
        }}

        /* ---------- Boutons ---------- */
        .stDownloadButton button {{
            background-color: {CARD};
            color: {INK};
            border: 1px solid {LINE};
            border-radius: 6px;
            font-weight: 500;
        }}
        .stDownloadButton button:hover {{
            border-color: {BRAND};
            color: {BRAND};
        }}
        div[data-testid="stButton"] button {{
            border-radius: 6px;
            font-weight: 500;
        }}
        div[data-testid="stButton"] button[kind="primary"] {{
            background-color: {BRAND};
            border-color: {BRAND};
        }}
        div[data-testid="stButton"] button[kind="primary"]:hover {{
            background-color: #C4045F;
            border-color: #C4045F;
        }}
        div[data-testid="stButton"] button:not([kind="primary"]) {{
            background-color: {CARD};
            color: {INK};
            border: 1px solid {LINE};
        }}
        div[data-testid="stButton"] button:not([kind="primary"]):hover {{
            border-color: {BRAND};
            color: {BRAND};
        }}

        section.main > div {{ padding-top: 0rem; }}
        [data-testid="stDataFrame"] {{ border: 1px solid {LINE}; border-radius: 6px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_LAYOUT = dict(
    font_family="Inter, sans-serif",
    font_color=INK,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=40, b=10, l=10, r=10),
)


def style_fig(fig, title=None):
    fig.update_layout(**PLOTLY_LAYOUT)
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=15, family="Inter, sans-serif")))
    fig.update_xaxes(showgrid=False, linecolor=LINE)
    fig.update_yaxes(showgrid=True, gridcolor=LINE, zeroline=False)
    return fig


# --------------------------------------------------------------------------------------
# CHARGEMENT DES DONNEES
# --------------------------------------------------------------------------------------
CODE_ALIASES = {"rec", "dao", "code", "code agence", "code_agence", "codeagence", "agence code",
                "branch code", "branch", "id", "id agence", "num agence", "numero agence"}
NAME_ALIASES = {"branch name", "nom agence", "nom de l'agence", "nom_agence", "nomagence", "agence",
                "nom", "libelle", "libellé", "name", "agency", "agency name", "designation", "désignation"}


def norm_code(x) -> str:
    """Normalise un code agence : espaces, '.0' final et zéros de tête ('011' -> '11')."""
    x = str(x).strip()
    if x.endswith(".0"):
        x = x[:-2]
    return x.lstrip("0") or "0" if x.isdigit() else x


@st.cache_data(show_spinner=False)
def load_branch_mapping(path, mtime: float) -> dict:
    """Retourne {code agence normalisé: nom d'agence} depuis un CSV (séparateur/colonnes détectés)."""
    if not path:
        return {}
    text = None
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, encoding=enc, newline="") as f:
                text = f.read()
            break
        except Exception:
            continue
    if not text:
        return {}
    try:
        delim = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|").delimiter
    except Exception:
        delim = ";" if text.count(";") > text.count(",") else ","
    parsed = []
    for r in csv.reader(text.splitlines(), delimiter=delim):
        # ligne entière entre guillemets avec séparateurs à l'intérieur : on la redécoupe
        if len(r) == 1:
            for sep in ("\t", ";", "|"):
                if sep in r[0]:
                    r = r[0].split(sep)
                    break
        r = [c.strip().strip('"').strip() for c in r]
        if any(r):
            parsed.append(r)
    rows = parsed

    # ligne d'en-tête : celle qui contient un nom de colonne « code » connu (ignore un titre éventuel)
    hdr_i = next((i for i, r in enumerate(rows[:6]) if any(c.lower() in CODE_ALIASES for c in r)), None)
    if hdr_i is not None:
        header, body = [c.lower() for c in rows[hdr_i]], rows[hdr_i + 1:]
        code_i = next(i for i, c in enumerate(header) if c in CODE_ALIASES)
        name_i = next((i for i, c in enumerate(header) if c in NAME_ALIASES and i != code_i), None)
        if name_i is None:
            name_i = next((i for i in range(len(header)) if i != code_i), None)
    else:  # pas d'en-tête reconnu : 1re colonne = code, 2e colonne = nom
        body = [r for r in rows if len(r) >= 2]
        code_i, name_i = 0, 1
    if name_i is None:
        return {}
    return {
        norm_code(r[code_i]): r[name_i]
        for r in body
        if len(r) > max(code_i, name_i) and r[code_i] and r[name_i]
    }


@st.cache_data(show_spinner="Chargement des données...")
def load_data(path: str, mtime: float, branch_path, branch_mtime: float):
    xls = pd.ExcelFile(path)
    sheet = "Vu détail" if "Vu détail" in xls.sheet_names else xls.sheet_names[0]
    detail = xls.parse(sheet)
    detail.columns = [str(c).strip() for c in detail.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in detail.columns]
    if missing:
        return None, None, missing

    detail["Date d'identification"] = pd.to_datetime(detail["Date d'identification"])

    # Code agence (DAO) -> nom d'agence
    if "DAO" in detail.columns:
        branch_map = load_branch_mapping(branch_path, branch_mtime)
        detail["DAO"] = detail["DAO"].astype(str).str.strip()
        detail["Agence"] = detail["DAO"].map(norm_code).map(branch_map).fillna(detail["DAO"])
    elif "Agence" not in detail.columns:
        detail["Agence"] = "Non renseignée"

    consolide = None
    if "Vu consolidé" in xls.sheet_names:
        consolide = xls.parse("Vu consolidé").astype(str)
    return detail, consolide, []


def mtime_of(path):
    return os.path.getmtime(path) if path and os.path.exists(path) else 0.0


def fmt_money(x):
    try:
        return f"{x:,.0f} {CURRENCY}".replace(",", " ")
    except Exception:
        return x


def type_pill(t):
    c = color_for_type(t)
    return f'<span class="type-pill" style="color:{c};">{t}</span>'


# --------------------------------------------------------------------------------------
# ETAT — CLIENTS REGULARISES (session en cours, séparés par filiale)
# --------------------------------------------------------------------------------------
st.session_state.setdefault("regularises", {})


def get_reg(filiale_name: str) -> set:
    return st.session_state.regularises.setdefault(filiale_name, set())


@st.dialog("Confirmer la régularisation")
def confirm_regularize(filiale_name, client_id, montant):
    st.write(
        f"Le client **{client_id}** ({fmt_money(montant)}) sera retiré de la liste "
        f"des pertes de revenu — filiale {filiale_name}."
    )
    st.caption("Vous pourrez le réintégrer depuis la barre latérale, section « Clients régularisés ».")
    c1, c2 = st.columns(2)
    if c1.button("Confirmer", type="primary", use_container_width=True):
        get_reg(filiale_name).add(client_id)
        st.rerun()
    if c2.button("Annuler", use_container_width=True):
        st.rerun()


@st.dialog("Confirmer la réintégration")
def confirm_reintegrate(filiale_name, client_id):
    st.write(
        f"Voulez-vous réintégrer le client **{client_id}** dans la liste des pertes de revenu ?"
    )
    c1, c2 = st.columns(2)
    if c1.button("Confirmer", type="primary", use_container_width=True, key=f"confirm_reint_{client_id}"):
        get_reg(filiale_name).discard(client_id)
        st.rerun()
    if c2.button("Annuler", use_container_width=True, key=f"cancel_reint_{client_id}"):
        st.rerun()


@st.dialog("Réinitialiser les régularisations")
def confirm_reset_all(filiale_name):
    st.write(f"Voulez-vous réintégrer **tous** les clients régularisés de {filiale_name} ?")
    c1, c2 = st.columns(2)
    if c1.button("Confirmer", type="primary", use_container_width=True, key="confirm_reset_all_btn"):
        get_reg(filiale_name).clear()
        st.rerun()
    if c2.button("Annuler", use_container_width=True, key="cancel_reset_all_btn"):
        st.rerun()


# --------------------------------------------------------------------------------------
# BARRE LATERALE — LOGO, FILIALE & FILTRES
# --------------------------------------------------------------------------------------
if logo_b64:
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{logo_b64}" class="sidebar-logo" />',
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown(
        "<div style='font-family:Fraunces,serif; font-size:1.3rem;'>Baobab</div>",
        unsafe_allow_html=True,
    )

filiale = st.sidebar.selectbox("Filiale", list(FILIALES.keys()), key="filiale_select")
cfg = FILIALES[filiale]
fk = slug(filiale)
CURRENCY = cfg.get("currency", "FCFA")

DATA_PATH = find_file(cfg["data"])
BRANCH_PATH = find_file(cfg.get("branches"))

if not DATA_PATH:
    st.error(
        f"Fichier de données introuvable pour la filiale **{filiale}**. "
        f"Déposez-le dans le dossier `data/` (nom attendu : {' ou '.join(cfg['data'])})."
    )
    st.stop()

df, df_consolide, missing_cols = load_data(DATA_PATH, mtime_of(DATA_PATH), BRANCH_PATH, mtime_of(BRANCH_PATH))
if missing_cols:
    st.error(
        f"Le fichier **{os.path.basename(DATA_PATH)}** ne contient pas les colonnes attendues : "
        + ", ".join(missing_cols)
    )
    st.stop()

st.sidebar.markdown(
    "<div style='color:#9CA3AF; font-size:0.82rem; margin:6px 0 18px 0;'>Filtres</div>",
    unsafe_allow_html=True,
)

reg = get_reg(filiale)

pays_options = sorted(df["Pays"].dropna().unique().tolist())
with st.sidebar.expander("Pays", expanded=False):
    sel_pays = st.multiselect("Pays", pays_options, default=pays_options,
                              label_visibility="collapsed", key=f"pays_{fk}")
st.sidebar.caption(f"{len(sel_pays)} / {len(pays_options)} sélectionné(s)")

agence_options = sorted(df["Agence"].dropna().unique().tolist())
with st.sidebar.expander("Agence", expanded=False):
    sel_agences = st.multiselect("Agence", agence_options, default=agence_options,
                                 label_visibility="collapsed", key=f"agences_{fk}")
st.sidebar.caption(f"{len(sel_agences)} / {len(agence_options)} sélectionnée(s)")

type_options = sorted(df["Type de revenu"].dropna().unique().tolist())
with st.sidebar.expander("Type de revenu", expanded=False):
    sel_types = st.multiselect("Type de revenu", type_options, default=type_options,
                               label_visibility="collapsed", key=f"types_{fk}")
st.sidebar.caption(f"{len(sel_types)} / {len(type_options)} sélectionné(s)")

date_min = df["Date d'identification"].min()
date_max = df["Date d'identification"].max()
date_range = None
if pd.notnull(date_min) and pd.notnull(date_max) and date_min != date_max:
    date_range = st.sidebar.date_input("Période", value=(date_min, date_max), key=f"periode_{fk}")

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

if reg:
    with st.sidebar.expander(f"Clients régularisés ({len(reg)})", expanded=False):
        for cid in sorted(reg, key=str):
            rc1, rc2 = st.columns([3, 1])
            rc1.write(str(cid))
            if rc2.button("↺", key=f"restore_{fk}_{cid}", help="Réintégrer ce client dans la liste"):
                confirm_reintegrate(filiale, cid)
        st.markdown("---")
        if st.button("Réinitialiser tout", key=f"reset_all_reg_{fk}", use_container_width=True):
            confirm_reset_all(filiale)
    st.sidebar.caption("Régularisations valables pour cette session.")

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.caption(
    f"Données au {date_max.strftime('%d/%m/%Y')}" if pd.notnull(date_max) else ""
)

mask = (
    df["Pays"].isin(sel_pays)
    & df["Agence"].isin(sel_agences)
    & df["Type de revenu"].isin(sel_types)
)
if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    mask &= df["Date d'identification"].between(pd.Timestamp(start), pd.Timestamp(end))

fdf = df[mask].copy()
if reg:
    fdf = fdf[~fdf["ID Client"].isin(reg)]

# --------------------------------------------------------------------------------------
# EN-TETE / HERO
# --------------------------------------------------------------------------------------
total_non_preleve = fdf["Montant non prélevé"].sum() if not fdf.empty else 0

logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" class="hero-logo" />'
    if logo_b64 else '<span class="hero-mark"></span>'
)

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-brand">
            {logo_html}
            <div>
                <p class="hero-title">Suivi des pertes de revenu</p>
                <p class="hero-subtitle">Détection des revenus non prélevés — Client, Agence, Type de revenu</p>
            </div>
        </div>
        <div style="text-align:right;">
            <div class="hero-stat-label">Montant non prélevé · {filiale} (filtres actifs)</div>
            <div class="hero-stat-value">{fmt_money(total_non_preleve)}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if fdf.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# --------------------------------------------------------------------------------------
# ONGLETS
# --------------------------------------------------------------------------------------
tab_overview, tab_client, tab_agence, tab_type, tab_data = st.tabs(
    ["Vue d'ensemble", "Client", "Agence", "Type de revenu", "Données"]
)

# ========================================================================================
# VUE D'ENSEMBLE
# ========================================================================================
with tab_overview:
    nb_clients = fdf["ID Client"].nunique()
    nb_contrats = fdf["ID Contrat"].nunique()
    nb_agences = fdf["Agence"].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("Clients concernés", f"{nb_clients}")
    c2.metric("Contrats concernés", f"{nb_contrats}")
    c3.metric("Agences concernées", f"{nb_agences}")

    st.write("")
    colA, colB = st.columns([1, 1.2])

    with colA:
        by_type = fdf.groupby("Type de revenu", as_index=False)["Montant non prélevé"].sum()
        fig_pie = px.pie(
            by_type, values="Montant non prélevé", names="Type de revenu", hole=0.62,
            color="Type de revenu", color_discrete_map=TYPE_COLOR,
        )
        fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
        style_fig(fig_pie, "Répartition par type de revenu")
        st.plotly_chart(fig_pie, use_container_width=True)

    with colB:
        by_agence = (
            fdf.groupby("Agence", as_index=False)["Montant non prélevé"].sum()
            .sort_values("Montant non prélevé", ascending=False).head(12)
        )
        fig_bar = px.bar(
            by_agence, x="Agence", y="Montant non prélevé", text_auto=".2s",
            color_discrete_sequence=[BRAND],
        )
        fig_bar.update_xaxes(type="category", title="Agence", tickangle=-35)
        fig_bar.update_yaxes(title="")
        style_fig(fig_bar, "Top agences par montant non prélevé")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.write("")
    top_clients = (
        fdf.groupby("ID Client", as_index=False)["Montant non prélevé"].sum()
        .sort_values("Montant non prélevé", ascending=False).head(10)
    )
    fig_top = px.bar(
        top_clients, x="ID Client", y="Montant non prélevé", text_auto=".2s",
        color_discrete_sequence=[INK],
    )
    fig_top.update_xaxes(type="category", title="")
    fig_top.update_yaxes(title="")
    style_fig(fig_top, "Top 10 clients par montant non prélevé")
    st.plotly_chart(fig_top, use_container_width=True)

    if df_consolide is not None:
        st.write("")
        st.markdown("##### Vue consolidée")
        st.dataframe(df_consolide, use_container_width=True, hide_index=True)

# ========================================================================================
# PAR CLIENT
# ========================================================================================
with tab_client:
    clients = sorted(fdf["ID Client"].unique().tolist())
    sel_client = st.selectbox("Sélectionner un client", clients, key=f"client_select_{fk}")

    cdf = fdf[fdf["ID Client"] == sel_client]
    total_client = cdf["Montant non prélevé"].sum()
    nb_contrats_client = cdf["ID Contrat"].nunique()
    agences_client = ", ".join(str(a) for a in sorted(cdf["Agence"].unique()))

    card_col, action_col = st.columns([4, 1.3])
    with card_col:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="name">Client {sel_client}</div>
                <div class="amount">{fmt_money(total_client)}</div>
                <div class="meta">à prélever · {nb_contrats_client} contrat(s) · agence(s) {agences_client}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with action_col:
        st.write("")
        st.write("")
        if st.button("✓ Marquer régularisé", key=f"reg_btn_{fk}_{sel_client}", use_container_width=True):
            confirm_regularize(filiale, sel_client, total_client)

    show_cols = ["ID Contrat", "Numero de compte", "Agence", "Type de revenu",
                 "Solde du compte", "Montant non prélevé", "Date d'identification"]
    st.dataframe(cdf[show_cols].sort_values("Montant non prélevé", ascending=False),
                 use_container_width=True, hide_index=True)

    st.download_button(
        "Télécharger le détail (CSV)",
        data=cdf[show_cols].to_csv(index=False).encode("utf-8-sig"),
        file_name=f"client_{sel_client}_detail_{fk}.csv", mime="text/csv",
    )

# ========================================================================================
# PAR AGENCE
# ========================================================================================
with tab_agence:
    agences = sorted(fdf["Agence"].unique().tolist())
    sel_agence = st.selectbox("Sélectionner une agence", agences, key=f"agence_select_{fk}")

    adf = fdf[fdf["Agence"] == sel_agence]
    total_agence = adf["Montant non prélevé"].sum()
    nb_clients_agence = adf["ID Client"].nunique()
    nb_contrats_agence = adf["ID Contrat"].nunique()

    st.markdown(
        f"""
        <div class="summary-card">
            <div class="name">Agence {sel_agence}</div>
            <div class="amount">{fmt_money(total_agence)}</div>
            <div class="meta">{nb_clients_agence} client(s) · {nb_contrats_agence} contrat(s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    colA, colB = st.columns([1, 1.2])
    with colA:
        by_type_agence = adf.groupby("Type de revenu", as_index=False)["Montant non prélevé"].sum()
        fig = px.pie(by_type_agence, values="Montant non prélevé", names="Type de revenu",
                     hole=0.6, color="Type de revenu", color_discrete_map=TYPE_COLOR)
        style_fig(fig, "Répartition par type")
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        by_client_agence = (
            adf.groupby("ID Client", as_index=False)["Montant non prélevé"].sum()
            .sort_values("Montant non prélevé", ascending=False)
        )
        fig2 = px.bar(by_client_agence, x="ID Client", y="Montant non prélevé",
                      text_auto=".2s", color_discrete_sequence=[BRAND])
        fig2.update_xaxes(type="category", title="")
        fig2.update_yaxes(title="")
        style_fig(fig2, "Montant par client")
        st.plotly_chart(fig2, use_container_width=True)

    show_cols_agence = ["ID Client", "ID Contrat", "Numero de compte", "Type de revenu",
                        "Solde du compte", "Montant non prélevé", "Date d'identification"]
    st.dataframe(adf[show_cols_agence].sort_values("Montant non prélevé", ascending=False),
                 use_container_width=True, hide_index=True)

    st.download_button(
        "Télécharger la liste (CSV)",
        data=adf[show_cols_agence].to_csv(index=False).encode("utf-8-sig"),
        file_name=f"agence_{slug(str(sel_agence))}_clients_{fk}.csv", mime="text/csv",
    )

# ========================================================================================
# PAR TYPE DE REVENU
# ========================================================================================
with tab_type:
    types_ = sorted(fdf["Type de revenu"].unique().tolist())
    sel_type = st.selectbox("Sélectionner un type de revenu", types_, key=f"type_select_{fk}")

    tdf = fdf[fdf["Type de revenu"] == sel_type]
    total_type = tdf["Montant non prélevé"].sum()
    nb_clients_type = tdf["ID Client"].nunique()
    nb_agences_type = tdf["Agence"].nunique()
    accent = color_for_type(sel_type)

    st.markdown(
        f"""
        <div class="summary-card" style="border-left-color:{accent};">
            <div class="name">{type_pill(sel_type)}</div>
            <div class="amount">{fmt_money(total_type)}</div>
            <div class="meta">{nb_clients_type} client(s) · {nb_agences_type} agence(s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    colA, colB = st.columns([1, 1.2])
    with colA:
        by_agence_type = (
            tdf.groupby("Agence", as_index=False)["Montant non prélevé"].sum()
            .sort_values("Montant non prélevé", ascending=False)
        )
        fig = px.bar(by_agence_type, x="Agence", y="Montant non prélevé", text_auto=".2s",
                     color_discrete_sequence=[accent])
        fig.update_xaxes(type="category", title="Agence", tickangle=-35)
        fig.update_yaxes(title="")
        style_fig(fig, "Montant par agence")
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        by_client_type = (
            tdf.groupby("ID Client", as_index=False)["Montant non prélevé"].sum()
            .sort_values("Montant non prélevé", ascending=False).head(15)
        )
        fig2 = px.bar(by_client_type, x="ID Client", y="Montant non prélevé", text_auto=".2s",
                      color_discrete_sequence=[INK])
        fig2.update_xaxes(type="category", title="")
        fig2.update_yaxes(title="")
        style_fig(fig2, "Top clients")
        st.plotly_chart(fig2, use_container_width=True)

    show_cols_type = ["ID Client", "ID Contrat", "Agence", "Numero de compte",
                      "Solde du compte", "Montant non prélevé", "Date d'identification"]
    st.dataframe(tdf[show_cols_type].sort_values("Montant non prélevé", ascending=False),
                 use_container_width=True, hide_index=True)

    st.download_button(
        "Télécharger la liste (CSV)",
        data=tdf[show_cols_type].to_csv(index=False).encode("utf-8-sig"),
        file_name=f"type_{slug(str(sel_type))}_clients_{fk}.csv", mime="text/csv",
    )

# ========================================================================================
# DONNEES COMPLETES
# ========================================================================================
with tab_data:
    st.dataframe(fdf, use_container_width=True, hide_index=True)
    st.download_button(
        "Télécharger toutes les données filtrées (CSV)",
        data=fdf.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"donnees_filtrees_{fk}.csv", mime="text/csv",
    )
    st.caption(
        "Utilisez les filtres de la barre latérale pour restreindre les données affichées dans tous les onglets. "
        "Les clients régularisés sont automatiquement exclus de cette table."
    )
