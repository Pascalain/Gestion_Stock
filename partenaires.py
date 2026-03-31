import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Gestion Stocks & Commandes", layout="wide")

# --- INITIALISATION DES DONNÉES ---
if "df_stocks" not in st.session_state:
    # Structure exacte avec la colonne 'Afficher' et les Cibles
    data = {
        "Partenaire": ["PASCALAIN", "PASCALAIN", "AGNEAU DU LIMOUSIN"],
        "Produit": ["Jambon Blanc", "Saucisson Sec", "Gigot d'Agneau"],
        "Cible_Feytiat": [10, 15, 5],
        "Cible_StLeo": [8, 12, 4],
        "Reste_Feytiat": [2, 15, 1], # Exemple pour voir les commandes
        "Reste_StLeo": [1, 12, 4],
        "Prix_HT": [12.50, 18.00, 25.00],
        "Afficher": [True, True, True]
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

# Filtre par partenaire global pour la sidebar si besoin
st.sidebar.divider()
st.sidebar.info("Application de gestion interne")

# --- 1. PAGE RÉCAPITULATIF (CE QU'IL FAUT COMMANDER) ---
if page == "📊 Récapitulatif Commandes":
    st.title("📋 État des Commandes")
    
    df_active = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True].copy()
    
    # Calcul des manques
    df_active["A_Commander_Feytiat"] = df_active["Cible_Feytiat"] - df_active["Reste_Feytiat"]
    df_active["A_Commander_StLeo"] = df_active["Cible_StLeo"] - df_active["Reste_StLeo"]
    df_active["Total_A_Commander"] = df_active["A_Commander_Feytiat"] + df_active["A_Commander_StLeo"]

    partenaires = df_active["Partenaire"].unique()
    
    for p in partenaires:
        df_p = df_active[df_active["Partenaire"] == p]
        # On ne montre le partenaire que s'il y a quelque chose à commander
        if df_p["Total_A_Commander"].sum() > 0:
            with st.expander(f"🛒 À commander chez : {p}", expanded=True):
                # On affiche seulement les produits en rupture
                df_order = df_p[df_p["Total_A_Commander"] > 0]
                st.table(df_order[["Produit", "A_Commander_Feytiat", "A_Commander_StLeo", "Total_A_Commander"]])

# --- 2. PAGE FEYTIAT ---
elif page == "🏬 Stock Feytiat":
    st.title("📍 Inventaire Feytiat")
    df = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True]
    
    for idx, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{row['Produit']}** ({row['Partenaire']})")
        col2.write(f"Cible: {row['Cible_Feytiat']}")
        new_val = col3.number_input(f"Reste", value=int(row['Reste_Feytiat']), key=f"f_{idx}", step=1)
        st.session_state.df_stocks.at[idx, "Reste_Feytiat"] = new_val

# --- 3. PAGE ST-LÉONARD ---
elif page == "🏬 Stock St-Léonard":
    st.title("📍 Inventaire St-Léonard")
    df = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True]
    
    for idx, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{row['Produit']}** ({row['Partenaire']})")
        col2.write(f"Cible: {row['Cible_StLeo']}")
        new_val = col3.number_input(f"Reste", value=int(row['Reste_StLeo']), key=f"s_{idx}", step=1)
        st.session_state.df_stocks.at[idx, "Reste_StLeo"] = new_val

# --- 4. PAGE ADMINISTRATION ---
elif page == "⚙️ Administration":
    st.title("🛠 Administration du catalogue")
    
    # Formulaire d'ajout
    with st.expander("➕ Ajouter un nouveau produit", expanded=False):
        with st.form("add_form"):
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
    
    # Gestion de la visibilité
    st.subheader("👀 Gestion de la visibilité (Cacher/Afficher)")
    for idx, row in st.session_state.df_stocks.iterrows():
        is_visible = st.checkbox(f"{row['Partenaire']} - {row['Produit']}", value=row['Afficher'], key=f"vis_{idx}")
        st.session_state.df_stocks.at[idx, "Afficher"] = is_visible
