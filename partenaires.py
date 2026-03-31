import streamlit as st
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestion des Stocks Partenaires", layout="wide")

# --- INITIALISATION DES DONNÉES (Mémoire temporaire) ---
if "df_stocks" not in st.session_state:
    # Création d'un tableau vide avec tes colonnes
    st.session_state.df_stocks = pd.DataFrame(columns=[
        "Partenaire", "Produit", "Cible_Feytiat", "Cible_StLeo", 
        "Reste_Feytiat", "Reste_StLeo", "Prix_HT"
    ])

# --- TITRE ---
st.title("📦 Gestion des Stocks - Partenaires")
st.markdown("---")

# --- AFFICHAGE DU TABLEAU ---
st.subheader("📊 État des Stocks Actuels")
if not st.session_state.df_stocks.empty:
    st.dataframe(st.session_state.df_stocks, use_container_width=True)
else:
    st.info("Le stock est vide. Ajoutez votre premier produit ci-dessous.")

st.divider()

# --- FORMULAIRE D'AJOUT ---
st.subheader("➕ Ajouter un nouveau produit")

with st.form("form_ajout", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        partenaire = st.text_input("Nom du Partenaire (ex: PASCALAIN)")
        produit = st.text_input("Nom du Produit (ex: Jambon)")
        prix_ht = st.number_input("Prix HT (€)", min_value=0.0, step=0.10, format="%.2f")
        
    with col2:
        c_feytiat = st.number_input("Objectif Feytiat (Quantité)", min_value=0, step=1)
        c_stleo = st.number_input("Objectif St-Léonard (Quantité)", min_value=0, step=1)

    submit_button = st.form_submit_button("Enregistrer le produit")

    if submit_button:
        if partenaire and produit:
            # Création de la nouvelle ligne
            nouvelle_ligne = pd.DataFrame([{
                "Partenaire": partenaire.upper(),
                "Produit": produit,
                "Cible_Feytiat": int(c_feytiat),
                "Cible_StLeo": int(c_stleo),
                "Reste_Feytiat": int(c_feytiat), # Au début, le reste est égal à la cible
                "Reste_StLeo": int(c_stleo),
                "Prix_HT": float(prix_ht)
            }])
            
            # Ajout au tableau dans la session
            st.session_state.df_stocks = pd.concat([st.session_state.df_stocks, nouvelle_ligne], ignore_index=True)
            
            st.success(f"✅ Produit '{produit}' ajouté avec succès !")
            st.rerun()
        else:
            st.error("Veuillez remplir au moins le nom du Partenaire et du Produit.")

# --- OPTIONS SUPPLÉMENTAIRES ---
with st.expander("🗑️ Zone de danger (Réinitialiser)"):
    if st.button("Effacer tout le tableau"):
        st.session_state.df_stocks = pd.DataFrame(columns=[
            "Partenaire", "Produit", "Cible_Feytiat", "Cible_StLeo", 
            "Reste_Feytiat", "Reste_StLeo", "Prix_HT"
        ])
        st.rerun()
