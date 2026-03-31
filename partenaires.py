import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Gestion Stocks Partenaires", layout="wide")

# --- INITIALISATION DES DONNÉES ---
# (On utilise session_state pour simuler la base de données sans les bugs Google Sheets)
if "df_stocks" not in st.session_state:
    data = {
        "Partenaire": ["PASCALAIN", "PASCALAIN", "AGNEAU DU LIMOUSIN"],
        "Produit": ["Jambon Blanc", "Saucisson Sec", "Gigot d'Agneau"],
        "Cible_Feytiat": [10, 15, 5],
        "Cible_StLeo": [8, 12, 4],
        "Reste_Feytiat": [10, 15, 5],
        "Reste_StLeo": [8, 12, 4],
        "Prix_HT": [12.50, 18.00, 25.00],
        "Actif": [True, True, True] # Pour pouvoir "cacher"
    }
    st.session_state.df_stocks = pd.DataFrame(data)

st.title("📦 Système de Gestion des Stocks")

# --- ONGLETS PRINCIPAUX ---
tab_recap, tab_feytiat, tab_stleo, tab_admin = st.tabs([
    "📊 Récapitulatif Global", 
    "🏬 Magasin Feytiat", 
    "🏬 Magasin St-Léonard", 
    "⚙️ Configuration & Ajout"
])

# --- FILTRE PAR PARTENAIRE (Commun aux onglets) ---
partenaires_existants = st.session_state.df_stocks["Partenaire"].unique()

# --- 1. ONGLET RÉCAPITULATIF ---
with tab_recap:
    st.subheader("État Global des Stocks")
    # On ne montre que les produits "Actifs"
    df_visibles = st.session_state.df_stocks[st.session_state.df_stocks["Actif"] == True]
    
    for p in partenaires_existants:
        df_p = df_visibles[df_visibles["Partenaire"] == p]
        if not df_p.empty:
            with st.expander(f"📍 Partenaire : {p}", expanded=True):
                st.table(df_p[["Produit", "Cible_Feytiat", "Reste_Feytiat", "Cible_StLeo", "Reste_StLeo"]])

# --- 2. ONGLET FEYTIAT ---
with tab_feytiat:
    st.subheader("Gestion Stock - Feytiat")
    df_f = st.session_state.df_stocks[st.session_state.df_stocks["Actif"] == True].copy()
    
    for idx, row in df_f.iterrows():
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"**{row['Partenaire']}** - {row['Produit']}")
        new_val = col2.number_input(f"Reste ({row['Produit']})", value=row['Reste_Feytiat'], key=f"f_{idx}")
        # Mise à jour directe
        st.session_state.df_stocks.at[idx, "Reste_Feytiat"] = new_val

# --- 3. ONGLET ST-LÉONARD ---
with tab_stleo:
    st.subheader("Gestion Stock - St-Léonard")
    df_s = st.session_state.df_stocks[st.session_state.df_stocks["Actif"] == True].copy()
    
    for idx, row in df_s.iterrows():
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{row['Partenaire']}** - {row['Produit']}")
        new_val = col2.number_input(f"Reste", value=row['Reste_StLeo'], key=f"s_{idx}")
        st.session_state.df_stocks.at[idx, "Reste_StLeo"] = new_val

# --- 4. ONGLET CONFIGURATION (Ajout et Cacher) ---
with tab_admin:
    st.subheader("➕ Ajouter un Produit")
    with st.form("new_prod"):
        c1, c2, c3 = st.columns(3)
        p_name = c1.text_input("Partenaire")
        prod_name = c2.text_input("Produit")
        price = c3.number_input("Prix HT", min_value=0.0)
        
        c4, c5 = st.columns(2)
        target_f = c4.number_input("Cible Feytiat", min_value=0)
        target_s = c5.number_input("Cible St-Leo", min_value=0)
        
        if st.form_submit_button("Ajouter"):
            new_row = pd.DataFrame([{
                "Partenaire": p_name.upper(), "Produit": prod_name,
                "Cible_Feytiat": target_f, "Cible_StLeo": target_s,
                "Reste_Feytiat": target_f, "Reste_StLeo": target_s,
                "Prix_HT": price, "Actif": True
            }])
            st.session_state.df_stocks = pd.concat([st.session_state.df_stocks, new_row], ignore_index=True)
            st.rerun()

    st.divider()
    st.subheader("🙈 Masquer des produits")
    # Liste des produits pour cocher/décocher l'activation
    for idx, row in st.session_state.df_stocks.iterrows():
        is_active = st.checkbox(f"{row['Partenaire']} - {row['Produit']}", value=row['Actif'], key=f"hide_{idx}")
        st.session_state.df_stocks.at[idx, "Actif"] = is_active
