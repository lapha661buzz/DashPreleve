"""
Plateforme de Suivi des Pertes de Revenu
==========================================
Application Streamlit permettant d'explorer les revenus non prélevés
par Client, par Agence (DAO) et par Type de revenu.
"""

import os

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------------------
# CONFIGURATION GENERALE
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Pertes de Revenu",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "Resultat.xlsx")

# --------------------------------------------------------------------------------------
# PALETTE & TYPOGRAPHIE
# --------------------------------------------------------------------------------------
INK = "#101828"
MUTED = "#6B7280"
PAPER = "#F7F7F4"
CARD = "#FFFFFF"
LINE = "#E3E2DD"
EMERALD = "#1E7A5C"     # Intérêt / valeurs saines
EMERALD_SOFT = "#E7F1EC"
RUST = "#C1553A"        # Pénalité / signal de fuite
RUST_SOFT = "#F7E9E4"

TYPE_COLOR = {"Intérêt": EMERALD, "Pénalité": RUST}


def color_for_type(t: str) -> str:
    return TYPE_COLOR.get(str(t), INK)


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
        .block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1180px; }}

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
            background-color: {EMERALD} !important;
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

        /* ---------- En-tête / hero ---------- */
        .hero {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 1px solid {LINE};
            padding-bottom: 22px;
            margin-bottom: 28px;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .hero-mark {{
            display: inline-block;
            width: 10px; height: 10px;
            background: linear-gradient(135deg, {EMERALD}, {RUST});
            border-radius: 3px;
            margin-right: 10px;
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
            color: {RUST};
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
            border-bottom: 2px solid {EMERALD} !important;
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

        /* ---------- Boutons de téléchargement ---------- */
        .stDownloadButton button {{
            background-color: {CARD};
            color: {INK};
            border: 1px solid {LINE};
            border-radius: 6px;
            font-weight: 500;
        }}
        .stDownloadButton button:hover {{
            border-color: {EMERALD};
            color: {EMERALD};
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
@st.cache_data(show_spinner="Chargement des données...")
def load_data(path: str):
    detail = pd.read_excel(path, sheet_name="Vu détail")
    detail["Date d'identification"] = pd.to_datetime(detail["Date d'identification"])
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
# BARRE LATERALE — FILTRES
# --------------------------------------------------------------------------------------
st.sidebar.markdown(
    "<div style='font-family:Fraunces,serif; font-size:1.3rem; margin-bottom:2px;'>Pertes de revenu</div>"
    "<div style='color:#9CA3AF; font-size:0.82rem; margin-bottom:18px;'>Filtres</div>",
    unsafe_allow_html=True,
)

pays_options = sorted(df["Pays"].dropna().unique().tolist())
with st.sidebar.expander("Pays", expanded=False):
    sel_pays = st.multiselect("Pays", pays_options, default=pays_options, label_visibility="collapsed")
st.sidebar.caption(f"{len(sel_pays)} / {len(pays_options)} sélectionné(s)")

agence_options = sorted(df["DAO"].dropna().unique().tolist())
with st.sidebar.expander("Agence (DAO)", expanded=False):
    sel_agences = st.multiselect("Agence (DAO)", agence_options, default=agence_options, label_visibility="collapsed")
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
st.sidebar.caption(
    f"Données au {date_max.strftime('%d/%m/%Y')}" if pd.notnull(date_max) else ""
)

mask = (
    df["Pays"].isin(sel_pays)
    & df["DAO"].isin(sel_agences)
    & df["Type de revenu"].isin(sel_types)
)
if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    mask &= df["Date d'identification"].between(pd.Timestamp(start), pd.Timestamp(end))

fdf = df[mask].copy()

# --------------------------------------------------------------------------------------
# EN-TETE / HERO
# --------------------------------------------------------------------------------------
total_non_preleve = fdf["Montant non prélevé"].sum() if not fdf.empty else 0

st.markdown(
    f"""
    <div class="hero">
        <div>
            <p class="hero-title"><span class="hero-mark"></span>Suivi des pertes de revenu</p>
            <p class="hero-subtitle">Détection des revenus non prélevés — Client, Agence, Type de revenu</p>
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
    nb_agences = fdf["DAO"].nunique()

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
            fdf.groupby("DAO", as_index=False)["Montant non prélevé"].sum()
            .sort_values("Montant non prélevé", ascending=False).head(12)
        )
        fig_bar = px.bar(
            by_agence, x="DAO", y="Montant non prélevé", text_auto=".2s",
            color_discrete_sequence=[EMERALD],
        )
        fig_bar.update_xaxes(type="category", title="Agence (DAO)")
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
    agences_client = ", ".join(str(a) for a in sorted(cdf["DAO"].unique()))

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

    show_cols = ["ID Contrat", "Numero de compte", "DAO", "Type de revenu",
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
    agences = sorted(fdf["DAO"].unique().tolist())
    sel_agence = st.selectbox("Sélectionner une agence (DAO)", agences, key="agence_select")

    adf = fdf[fdf["DAO"] == sel_agence]
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
                      text_auto=".2s", color_discrete_sequence=[EMERALD])
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
    nb_agences_type = tdf["DAO"].nunique()
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
            tdf.groupby("DAO", as_index=False)["Montant non prélevé"].sum()
            .sort_values("Montant non prélevé", ascending=False)
        )
        fig = px.bar(by_agence_type, x="DAO", y="Montant non prélevé", text_auto=".2s",
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

    show_cols_type = ["ID Client", "ID Contrat", "DAO", "Numero de compte",
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
        "Utilisez les filtres de la barre latérale pour restreindre les données affichées dans tous les onglets."
    )
