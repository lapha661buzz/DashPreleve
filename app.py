"""
Plateforme de Suivi des Pertes de Revenu — Baobab
==================================================
Application Streamlit permettant d'explorer les revenus non prélevés
par Client, par Agence et par Type de revenu.
"""

import base64
import os

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------------------
# CHEMINS
# --------------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "Resultat.xlsx")
LOGO_PATH = os.path.join(BASE_DIR, "logo-dark.png")
BRANCH_PATH = os.path.join(BASE_DIR, "data", "MADA MCR.BRANCH.TABLE.csv")

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
# CHARGEMENT DU MAPPING DAO -> NOM D'AGENCE
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_branch_mapping(path: str) -> dict:
    """Retourne un dict {DAO (str): Branch name} depuis MADA MCR.BRANCH.TABLE.csv."""
    try:
        br = pd.read_csv(path, skiprows=1, dtype=str)
        br.columns = [c.strip() for c in br.columns]
        br["Rec"] = br["Rec"].astype(str).str.strip()
        br["Branch name"] = br["Branch name"].astype(str).str.strip()
        return dict(zip(br["Rec"], br["Branch name"]))
    except Exception:
        return {}


# --------------------------------------------------------------------------------------
# CHARGEMENT DES DONNEES
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner="Chargement des données...")
def load_data(path: str):
    detail = pd.read_excel(path, sheet_name="Vu détail")
    detail["Date d'identification"] = pd.to_datetime(detail["Date d'identification"])

    # Mapping DAO -> Nom d'agence
    branch_map = load_branch_mapping(BRANCH_PATH)
    detail["DAO"] = detail["DAO"].astype(str).str.strip()
    detail["Agence"] = detail["DAO"].map(branch_map).fillna(detail["DAO"])

    try:
        consolide = pd.read_excel(path, sheet_name="Vu consolidé")
    except Exception:
        consolide = None
    return detail, consolide


if not os.path.exists(DATA_PATH):
    st.error(f"Fichier de données introuvable : {DATA_PATH}")
    st.stop()

df, df_consolide = load_data(DATA_PATH)


def fmt_money(x):
    try:
        return f"{x:,.0f} FCFA".replace(",", " ")
    except Exception:
        return x


def type_pill(t):
    c = color_for_type(t)
    return f'<span class="type-pill" style="color:{c};">{t}</span>'


# --------------------------------------------------------------------------------------
# ETAT — CLIENTS REGULARISES (session en cours)
# --------------------------------------------------------------------------------------
st.session_state.setdefault("regularises", set())


@st.dialog("Confirmer la régularisation")
def confirm_regularize(client_id, montant):
    st.write(
        f"Le client **{client_id}** ({fmt_money(montant)}) sera retiré de la liste "
        "des pertes de revenu."
    )
    st.caption("Vous pourrez le réintégrer depuis la barre latérale, section « Clients régularisés ».")
    c1, c2 = st.columns(2)
    if c1.button("Confirmer", type="primary", use_container_width=True):
        st.session_state.regularises.add(client_id)
        st.rerun()
    if c2.button("Annuler", use_container_width=True):
        st.rerun()


@st.dialog("Confirmer la réintégration")
def confirm_reintegrate(client_id):
    st.write(
        f"Voulez-vous réintégrer le client **{client_id}** dans la liste des pertes de revenu ?"
    )
    c1, c2 = st.columns(2)
    if c1.button("Confirmer", type="primary", use_container_width=True, key=f"confirm_reint_{client_id}"):
        st.session_state.regularises.discard(client_id)
        st.rerun()
    if c2.button("Annuler", use_container_width=True, key=f"cancel_reint_{client_id}"):
        st.rerun()


@st.dialog("Réinitialiser les régularisations")
def confirm_reset_all():
    st.write("Voulez-vous réintégrer **tous** les clients régularisés dans la liste ?")
    c1, c2 = st.columns(2)
    if c1.button("Confirmer", type="primary", use_container_width=True, key="confirm_reset_all_btn"):
        st.session_state.regularises.clear()
        st.rerun()
    if c2.button("Annuler", use_container_width=True, key="cancel_reset_all_btn"):
        st.rerun()


# --------------------------------------------------------------------------------------
# BARRE LATERALE — LOGO & FILTRES
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
st.sidebar.markdown(
    "<div style='color:#9CA3AF; font-size:0.82rem; margin-bottom:18px;'>Filtres</div>",
    unsafe_allow_html=True,
)

pays_options = sorted(df["Pays"].dropna().unique().tolist())
with st.sidebar.expander("Pays", expanded=False):
    sel_pays = st.multiselect("Pays", pays_options, default=pays_options, label_visibility="collapsed")
st.sidebar.caption(f"{len(sel_pays)} / {len(pays_options)} sélectionné(s)")

agence_options = sorted(df["Agence"].dropna().unique().tolist())
with st.sidebar.expander("Agence", expanded=False):
    sel_agences = st.multiselect("Agence", agence_options, default=agence_options, label_visibility="collapsed")
st.sidebar.caption(f"{len(sel_agences)} / {len(agence_options)} sélectionnée(s)")

type_options = sorted(df["Type de revenu"].dropna().unique().tolist())
with st.sidebar.expander("Type de revenu", expanded=False):
    sel_types = st.multiselect("Type de revenu", type_options, default=type_options, label_visibility="collapsed")
st.sidebar.caption(f"{len(sel_types)} / {len(type_options)} sélectionné(s)")

date_min = df["Date d'identification"].min()
date_max = df["Date d'identification"].max()
date_range = None
if pd.notnull(date_min) and pd.notnull(date_max) and date_min != date_max:
    date_range = st.sidebar.date_input("Période", value=(date_min, date_max))

st.sidebar.markdown("<hr>", unsafe_allow_html=True)

if st.session_state.regularises:
    with st.sidebar.expander(f"Clients régularisés ({len(st.session_state.regularises)})", expanded=False):
        for cid in sorted(st.session_state.regularises, key=str):
            rc1, rc2 = st.columns([3, 1])
            rc1.write(str(cid))
            if rc2.button("↺", key=f"restore_{cid}", help="Réintégrer ce client dans la liste"):
                confirm_reintegrate(cid)
        st.markdown("---")
        if st.button("Réinitialiser tout", key="reset_all_reg", use_container_width=True):
            confirm_reset_all()
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
if st.session_state.regularises:
    fdf = fdf[~fdf["ID Client"].isin(st.session_state.regularises)]

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
            <div class="hero-stat-label">Montant non prélevé (filtres actifs)</div>
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
        fig_bar.update_xaxes(type="category", title="Agence")
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
    sel_client = st.selectbox("Sélectionner un client", clients, key="client_select")

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
        if st.button("✓ Marquer régularisé", key=f"reg_btn_{sel_client}", use_container_width=True):
            confirm_regularize(sel_client, total_client)

    show_cols = ["ID Contrat", "Numero de compte", "Agence", "Type de revenu",
                 "Solde du compte", "Montant non prélevé", "Date d'identification"]
    st.dataframe(cdf[show_cols].sort_values("Montant non prélevé", ascending=False),
                 use_container_width=True, hide_index=True)

    st.download_button(
        "Télécharger le détail (CSV)",
        data=cdf[show_cols].to_csv(index=False).encode("utf-8-sig"),
        file_name=f"client_{sel_client}_detail.csv", mime="text/csv",
    )

# ========================================================================================
# PAR AGENCE
# ========================================================================================
with tab_agence:
    agences = sorted(fdf["Agence"].unique().tolist())
    sel_agence = st.selectbox("Sélectionner une agence", agences, key="agence_select")

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
        file_name=f"agence_{sel_agence}_clients.csv", mime="text/csv",
    )

# ========================================================================================
# PAR TYPE DE REVENU
# ========================================================================================
with tab_type:
    types_ = sorted(fdf["Type de revenu"].unique().tolist())
    sel_type = st.selectbox("Sélectionner un type de revenu", types_, key="type_select")

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
        fig.update_xaxes(type="category", title="Agence")
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
        file_name=f"type_{sel_type}_clients.csv", mime="text/csv",
    )

# ========================================================================================
# DONNEES COMPLETES
# ========================================================================================
with tab_data:
    st.dataframe(fdf, use_container_width=True, hide_index=True)
    st.download_button(
        "Télécharger toutes les données filtrées (CSV)",
        data=fdf.to_csv(index=False).encode("utf-8-sig"),
        file_name="donnees_filtrees.csv", mime="text/csv",
    )
    st.caption(
        "Utilisez les filtres de la barre latérale pour restreindre les données affichées dans tous les onglets. "
        "Les clients régularisés sont automatiquement exclus de cette table."
    )