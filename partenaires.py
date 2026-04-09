import streamlit as st

import pandas as pd


# Configuration de la page

st.set_page_config(page_title="Gestion Stock Multi-Boutiques", layout="wide")


# --- SIMULATION DE LA BASE DE DONNÉES ---

# Dans une version réelle, on utiliserait un fichier Excel ou une vraie base de données

if 'db' not in st.session_state:

    st.session_state.db = pd.DataFrame([

        {"Partenaire": "FERME DE BEAUREGARD", "Produit": "Grillons de canard", "Cible_Feytiat": 20, "Cible_StLeo": 15, "Reste_Feytiat": 20, "Reste_StLeo": 15, "Contact": "05 55 70 01 90"},

        {"Partenaire": "FERME DE BEAUREGARD", "Produit": "Rillettes de canard", "Cible_Feytiat": 20, "Cible_StLeo": 10, "Reste_Feytiat": 3, "Reste_StLeo": 8, "Contact": "05 55 70 01 90"},

        {"Partenaire": "CLARISSE CONFITURE", "Produit": "Confiture Fraise", "Cible_Feytiat": 12, "Cible_StLeo": 12, "Reste_Feytiat": 12, "Reste_StLeo": 12, "Contact": "05 55 47 37 26"},

    ])


# --- NAVIGATION ---

st.sidebar.title("Menu Gestion")

page = st.sidebar.radio("Aller vers :", ["📍 Boutique Feytiat", "📍 Boutique St-Léonard", "📊 Récapitulatif & Commande", "⚙️ Paramètres (Ajouter Produits)"])


# --- PAGE FEYTIAT ---

if page == "📍 Boutique Feytiat":

    st.title("Inventaire - Magasin de Feytiat")

    for i, row in st.session_state.db.iterrows():

        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:

            st.write(f"**{row['Produit']}** ({row['Partenaire']})")

        with col2:

            st.write(f"Cible: {row['Cible_Feytiat']}")

        with col3:

            # Mise à jour du stock restant

            new_reste = st.number_input(f"Reste à Feytiat", value=int(row['Reste_Feytiat']), key=f"fey_{i}")

            st.session_state.db.at[i, 'Reste_Feytiat'] = new_reste

    st.success("Stocks Feytiat mis à jour automatiquement.")


# --- PAGE ST LEONARD ---

elif page == "📍 Boutique St-Léonard":

    st.title("Inventaire - Magasin de St-Léonard")

    for i, row in st.session_state.db.iterrows():

        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:

            st.write(f"**{row['Produit']}** ({row['Partenaire']})")

        with col2:

            st.write(f"Cible: {row['Cible_StLeo']}")

        with col3:

            new_reste = st.number_input(f"Reste à St-Léonard", value=int(row['Reste_StLeo']), key=f"stleo_{i}")

            st.session_state.db.at[i, 'Reste_StLeo'] = new_reste

    st.success("Stocks St-Léonard mis à jour automatiquement.")


# --- PAGE RÉCAPITULATIF ---

elif page == "📊 Récapitulatif & Commande":

    st.title("Tableau de Commande Global")

    

    df = st.session_state.db.copy()

    df['Manquant_Feytiat'] = df['Cible_Feytiat'] - df['Reste_Feytiat']

    df['Manquant_StLeo'] = df['Cible_StLeo'] - df['Reste_StLeo']

    df['TOTAL_A_COMMANDER'] = df['Manquant_Feytiat'] + df['Manquant_StLeo']

    

    # On ne garde que ce qu'il faut commander

    a_commander = df[df['TOTAL_A_COMMANDER'] > 0]

    

    if not a_commander.empty:

        st.table(a_commander[['Partenaire', 'Produit', 'Manquant_Feytiat', 'Manquant_StLeo', 'TOTAL_A_COMMANDER', 'Contact']])

        st.info("💡 Ce tableau vous donne le total pour la commande ET le détail pour préparer le dispatch une fois reçu.")

    else:

        st.write("✅ Tous les stocks sont au maximum. Rien à commander.")


# --- PAGE PARAMÈTRES ---

elif page == "⚙️ Paramètres (Ajouter Produits)":

    st.title("Ajouter un nouveau produit / partenaire")

    with st.form("new_product"):

        part = st.text_input("Nom du Partenaire")

        prod = st.text_input("Nom du Produit")

        c_fey = st.number_input("Stock Cible Feytiat", value=20)

        c_st = st.number_input("Stock Cible St-Léonard", value=20)

        cont = st.text_input("Contact (Tél/Mail)")

        

        if st.form_submit_button("Ajouter à la liste"):

            new_entry = {"Partenaire": part, "Produit": prod, "Cible_Feytiat": c_fey, "Cible_StLeo": c_st, "Reste_Feytiat": c_fey, "Reste_StLeo": c_st, "Contact": cont}

            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)

            st.experimental_rerun() 
