import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Gestion Stocks Boutiques", layout="wide")

# --- INITIALISATION DES DONNÉES (Simulé sans GSheets pour l'instant) ---
if "df_stocks" not in st.session_state:
    # On recrée ta structure de base
    data = {
        "Partenaire": ["PASCALAIN", "PASCALAIN", "AGNEAU DU LIMOUSIN"],
        "Produit": ["Jambon Blanc", "Saucisson Sec", "Gigot d'Agneau"],
        "Cible_Feytiat": [10, 15, 5],
        "Cible_StLeo": [8, 12, 4],
        "Reste_Feytiat": [10, 15, 5],
        "Reste_StLeo": [8, 12, 4],
        "Prix_HT": [12.50, 18.00, 25.00],
        "Afficher": [True, True, True]
    }
    st.session_state.df_stocks = pd.DataFrame(data)

st.title("📦 Gestion des Stocks Partenaires")

# --- SYSTÈME D'ONGLETS ---
tab_recap, tab_feytiat, tab_stleo, tab_admin = st.tabs([
    "📑 Récapitulatif Global", 
    "🛒 Stock Feytiat", 
    "🛒 Stock St-Léonard", 
    "⚙️ Paramètres & Ajout"
])

# --- 1. ONGLET RÉCAPITULATIF (Tableaux par Partenaire) ---
with tab_recap:
    st.subheader("📊 État des lieux par Partenaire")
    
    # On ne filtre que ce qui est coché "Afficher"
    df_active = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True]
    
    if df_active.empty:
        st.info("Aucun produit à afficher. Allez dans l'onglet Paramètres.")
    else:
        partenaires = df_active["Partenaire"].unique()
        for p in partenaires:
            with st.expander(f"🤝 PARTENAIRE : {p}", expanded=True):
                df_p = df_active[df_active["Partenaire"] == p]
                # Calcul des totaux ou affichage propre
                st.table(df_p[["Produit", "Reste_Feytiat", "Cible_Feytiat", "Reste_StLeo", "Cible_StLeo"]])

# --- 2. ONGLET FEYTIAT (Saisie rapide) ---
with tab_feytiat:
    st.subheader("📍 Boutique de Feytiat")
    df_f = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True]
    
    for idx, row in df_f.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{row['Produit']}** ({row['Partenaire']})")
        with col2:
            new_reste = st.number_input(f"Reste", value=int(row['Reste_Feytiat']), key=f"fey_{idx}", step=1)
            st.session_state.df_stocks.at[idx, "Reste_Feytiat"] = new_reste

# --- 3. ONGLET ST-LÉONARD (Saisie rapide) ---
with tab_stleo:
    st.subheader("📍 Boutique de Saint-Léonard")
    df_s = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True]
    
    for idx, row in df_s.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{row['Produit']}** ({row['Partenaire']})")
        with col2:
            new_reste = st.number_input(f"Reste", value=int(row['Reste_StLeo']), key=f"stleo_{idx}", step=1)
            st.session_state.df_stocks.at[idx, "Reste_StLeo"] = new_reste

# --- 4. ONGLET PARAMÈTRES (Ajout et Masquage) ---
with tab_admin:
    st.subheader("➕ Ajouter un nouveau produit")
    with st.form("ajout_nouveau"):
        c1, c2, c3 = st.columns(3)
        p_name = c1.text_input("Nom Partenaire")
        prod_name = c2.text_input("Nom Produit")
        p_ht = c3.number_input("Prix HT (€)", min_value=0.0)
        
        c4, c5 = st.columns(2)
        t_fey = c4.number_input("Objectif Feytiat", min_value=0)
        t_leo = c5.number_input("Objectif St-Leo", min_value=0)
        
        if st.form_submit_button("Enregistrer le produit"):
            new_data = pd.DataFrame([{
                "Partenaire": p_name.upper(), "Produit": prod_name,
                "Cible_Feytiat": t_fey, "Cible_StLeo": t_leo,
                "Reste_Feytiat": t_fey, "Reste_StLeo": t_leo,
                "Prix_HT": p_ht, "Afficher": True
            }])
            st.session_state.df_stocks = pd.concat([st.session_state.df_stocks, new_data], ignore_index=True)
            st.success("Produit ajouté !")
            st.rerun()

    st.divider()
    st.subheader("🚫 Gérer la visibilité")
