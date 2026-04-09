import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Gestion Stocks & Commandes", layout="wide")

# --- INITIALISATION DES DONNÉES (Mémoire Session) ---
if "df_stocks" not in st.session_state:
    data = {
        "Partenaire": ["PASCALAIN", "PASCALAIN", "AGNEAU DU LIMOUSIN"],
        "Produit": ["Jambon Blanc", "Saucisson Sec", "Gigot d'Agneau"],
        "Cible_Feytiat": [10, 15, 5],
        "Cible_StLeo": [8, 12, 4],
        "Reste_Feytiat": [2, 15, 1],
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

# --- 1. PAGE RÉCAPITULATIF (COMMANDES) ---
if page == "📊 Récapitulatif Commandes":
    st.title("📋 État des Commandes")
    df_active = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True].copy()
    
    # Calculs
    df_active["A_Commander_Feytiat"] = (df_active["Cible_Feytiat"] - df_active["Reste_Feytiat"]).clip(lower=0)
    df_active["A_Commander_StLeo"] = (df_active["Cible_StLeo"] - df_active["Reste_StLeo"]).clip(lower=0)
    df_active["Total_A_Commander"] = df_active["A_Commander_Feytiat"] + df_active["A_Commander_StLeo"]

    partenaires = df_active["Partenaire"].unique()
    for p in partenaires:
        df_p = df_active[df_active["Partenaire"] == p]
        if df_p["Total_A_Commander"].sum() > 0:
            with st.expander(f"🛒 À commander chez : {p}", expanded=True):
                df_order = df_p[df_p["Total_A_Commander"] > 0]
                st.table(df_order[["Produit", "A_Commander_Feytiat", "A_Commander_StLeo", "Total_A_Commander"]])

# --- 2. PAGE FEYTIAT (TABLEAU ÉDITABLE) ---
elif page == "🏬 Stock Feytiat":
    st.title("📍 Inventaire Feytiat")
    st.write("Modifiez les quantités directement dans la colonne **Reste_Feytiat**.")
    
    # On prépare le tableau pour l'édition
    df_fey = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True].copy()
    
    # Affichage du tableau éditable
    edited_df = st.data_editor(
        df_fey[["Partenaire", "Produit", "Cible_Feytiat", "Reste_Feytiat"]],
        column_config={
            "Reste_Feytiat": st.column_config.NumberColumn("Stock Restant", min_value=0, step=1),
            "Cible_Feytiat": st.column_config.NumberColumn("Objectif", disabled=True),
            "Partenaire": st.column_config.TextColumn(disabled=True),
            "Produit": st.column_config.TextColumn(disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_fey"
    )
    
    # Bouton pour sauvegarder les changements dans la session
    if st.button("Enregistrer les modifications Feytiat"):
        for i, row in edited_df.iterrows():
            # On retrouve l'index original dans le dataframe principal
            original_idx = df_fey.index[i]
            st.session_state.df_stocks.at[original_idx, "Reste_Feytiat"] = row["Reste_Feytiat"]
        st.success("✅ Stocks Feytiat mis à jour !")
        st.rerun()

# --- 3. PAGE ST-LÉONARD (TABLEAU ÉDITABLE) ---
elif page == "🏬 Stock St-Léonard":
    st.title("📍 Inventaire Saint-Léonard")
    st.write("Modifiez les quantités directement dans la colonne **Reste_StLeo**.")
    
    df_leo = st.session_state.df_stocks[st.session_state.df_stocks["Afficher"] == True].copy()
    
    edited_df_leo = st.data_editor(
        df_leo[["Partenaire", "Produit", "Cible_StLeo", "Reste_StLeo"]],
        column_config={
            "Reste_StLeo": st.column_config.NumberColumn("Stock Restant", min_value=0, step=1),
            "Cible_StLeo": st.column_config.NumberColumn("Objectif", disabled=True),
            "Partenaire": st.column_config.TextColumn(disabled=True),
            "Produit": st.column_config.TextColumn(disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_leo"
    )
    
    if st.button("Enregistrer les modifications St-Léonard"):
        for i, row in edited_df_leo.iterrows():
            original_idx = df_leo.index[i]
            st.session_state.df_stocks.at[original_idx, "Reste_StLeo"] = row["Reste_StLeo"]
        st.success("✅ Stocks Saint-Léonard mis à jour !")
        st.rerun()

# --- 4. PAGE ADMINISTRATION ---
elif page == "⚙️ Administration":
    st.title("🛠 Administration")
    
    with st.expander("➕ Ajouter un nouveau produit"):
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
    st.subheader("👀 Visibilité du catalogue")
    # Tableau simple pour cocher/décocher
    edited_vis = st.data_editor(
        st.session_state.df_stocks[["Partenaire", "Produit", "Afficher"]],
        use_container_width=True,
        hide_index=True
    )
    if st.button("Mettre à jour la visibilité"):
        st.session_state.df_stocks["Afficher"] = edited_vis["Afficher"]
        st.rerun()
