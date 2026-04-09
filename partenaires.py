import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Gestion Stocks & Commandes", layout="wide")

# --- INITIALISATION DES DONNÉES (Mémoire Session) ---
if "df_stocks" not in st.session_state:
    data = {
        "Partenaire": ["PASCALAIN", "PASCALAIN", "AGNEAU DU LIMOUSIN", "AGNEAU DU LIMOUSIN"],
        "Produit": ["Jambon Blanc", "Saucisson Sec", "Gigot d'Agneau", "Côtelettes"],
        "Cible_Feytiat": [10, 15, 5, 20],
        "Cible_StLeo": [8, 12, 4, 15],
        "Reste_Feytiat": [10, 15, 5, 20],
        "Reste_StLeo": [8, 12, 4, 15],
        "Prix_HT": [12.50, 18.00, 25.00, 15.00],
        "Afficher": [True, True, True, True]
    }
    st.session_state.df_stocks = pd.DataFrame(data)

# --- NAVIGATION LATERALE (SIDEBAR) ---
st.sidebar.title("🏪 Menu Navigation")
page = st.sidebar.radio("Aller vers :", [
    "📊 Récapitulatif Commandes", 
    "🏬 Stock Feytiat", 
    "🏬 Stock St-Léonard", 
    "⚙️ Administration"
])

# --- 1. PAGE RÉCAPITULATIF (AFFICHE UNIQUEMENT LES RUPTURES) ---
if page == "📊 Récapitulatif Commandes":
    st.title("📋 État des Commandes")
    df_active = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True].copy()
    
    # Calculs des besoins
    df_active["Besoin_Feytiat"] = (df_active["Cible_Feytiat"] - df_active["Reste_Feytiat"]).clip(lower=0)
    df_active["Besoin_StLeo"] = (df_active["Cible_StLeo"] - df_active["Reste_StLeo"]).clip(lower=0)
    df_active["Total_A_Commander"] = df_active["Besoin_Feytiat"] + df_active["Besoin_StLeo"]

    partenaires = df_active["Partenaire"].unique()
    for p in partenaires:
        df_p = df_active[(df_active["Partenaire"] == p) & (df_active["Total_A_Commander"] > 0)]
        if not df_p.empty:
            with st.expander(f"🛒 À commander chez : {p}", expanded=True):
                st.table(df_p[["Produit", "Besoin_Feytiat", "Besoin_StLeo", "Total_A_Commander"]])

# --- 2. PAGE FEYTIAT (UN TABLEAU PAR PARTENAIRE) ---
elif page == "🏬 Stock Feytiat":
    st.title("📍 Inventaire Feytiat")
    st.info("Modifiez les quantités dans les tableaux et cliquez sur le bouton en bas pour enregistrer.")
    
    df_fey = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True].copy()
    partenaires = df_fey["Partenaire"].unique()
    
    # Dictionnaire pour stocker les modifications de chaque tableau
    all_edited_fey = {}

    for p in partenaires:
        with st.expander(f"📦 Produits de : {p}", expanded=True):
            df_p = df_fey[df_fey["Partenaire"] == p]
            
            edited = st.data_editor(
                df_p[["Produit", "Cible_Feytiat", "Reste_Feytiat"]],
                column_config={
                    "Reste_Feytiat": st.column_config.NumberColumn("Stock Restant", min_value=0, step=1),
                    "Cible_Feytiat": st.column_config.NumberColumn("Objectif", disabled=True),
                    "Produit": st.column_config.TextColumn(disabled=True),
                },
                use_container_width=True,
                hide_index=True,
                key=f"editor_fey_{p}"
            )
            all_edited_fey[p] = edited

    if st.button("💾 Enregistrer TOUS les stocks Feytiat", type="primary"):
        for p, edited_df in all_edited_fey.items():
            for _, row in edited_df.iterrows():
                idx = st.session_state.df_stocks[(st.session_state.df_stocks["Partenaire"] == p) & 
                                                (st.session_state.df_stocks["Produit"] == row["Produit"])].index
                st.session_state.df_stocks.loc[idx, "Reste_Feytiat"] = row["Reste_Feytiat"]
        st.success("✅ Stocks Feytiat mis à jour !")
        st.rerun()

# --- 3. PAGE ST-LÉONARD (UN TABLEAU PAR PARTENAIRE) ---
elif page == "🏬 Stock St-Léonard":
    st.title("📍 Inventaire Saint-Léonard")
    st.info("Modifiez les quantités dans les tableaux et cliquez sur le bouton en bas pour enregistrer.")
    
    df_leo = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True].copy()
    partenaires = df_leo["Partenaire"].unique()
    
    all_edited_leo = {}

    for p in partenaires:
        with st.expander(f"📦 Produits de : {p}", expanded=True):
            df_p = df_leo[df_leo["Partenaire"] == p]
            
            edited = st.data_editor(
                df_p[["Produit", "Cible_StLeo", "Reste_StLeo"]],
                column_config={
                    "Reste_StLeo": st.column_config.NumberColumn("Stock Restant", min_value=0, step=1),
                    "Cible_StLeo": st.column_config.NumberColumn("Objectif", disabled=True),
                    "Produit": st.column_config.TextColumn(disabled=True),
                },
                use_container_width=True,
                hide_index=True,
                key=f"editor_leo_{p}"
            )
            all_edited_leo[p] = edited

    if st.button("💾 Enregistrer TOUS les stocks St-Léonard", type="primary"):
        for p, edited_df in all_edited_leo.items():
            for _, row in edited_df.iterrows():
                idx = st.session_state.df_stocks[(st.session_state.df_stocks["Partenaire"] == p) & 
                                                (st.session_state.df_stocks["Produit"] == row["Produit"])].index
                st.session_state.df_stocks.loc[idx, "Reste_StLeo"] = row["Reste_StLeo"]
        st.success("✅ Stocks Saint-Léonard mis à jour !")
        st.rerun()

# --- 4. PAGE ADMINISTRATION ---
elif page == "⚙️ Administration":
    st.title("🛠 Administration")
    
    with st.expander("➕ Ajouter un nouveau produit"):
        with st.form("add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            part = c1.text_input("Partenaire")
            prod = c2.text_input("Produit")
            c3, c4, c5 = st.columns(3)
            cf = c3.number_input("Cible Feytiat", min_value=0)
            cs = c4.number_input("Cible St-Leo", min_value=0)
            px = c5.number_input("Prix HT", min_value=0.0)
            if st.form_submit_button("Enregistrer"):
                new_line = pd.DataFrame([{
                    "Partenaire": part.upper(), "Produit": prod,
                    "Cible_Feytiat": cf, "Cible_StLeo": cs,
                    "Reste_Feytiat": cf, "Reste_StLeo": cs,
                    "Prix_HT": px, "Afficher": True
                }])
                st.session_state.df_stocks = pd.concat([st.session_state.df_stocks, new_line], ignore_index=True)
                st.rerun()

    st.divider()
    st.subheader("👀 Visibilité du catalogue")
    edited_vis = st.data_editor(
        st.session_state.df_stocks[["Partenaire", "Produit", "Afficher"]],
        use_container_width=True,
        hide_index=True,
        key="admin_editor"
    )
    if st.button("Appliquer les changements de visibilité"):
        st.session_state.df_stocks["Afficher"] = edited_vis["Afficher"]
        st.rerun()
