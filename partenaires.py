import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestion Stocks - Multi-Boutiques", layout="wide")

DB_FILE = "stocks_data.csv"

# --- CHARGEMENT DES DONNÉES ---
if os.path.exists(DB_FILE):
    df_db = pd.read_csv(DB_FILE)
    if "Prix_HT" not in df_db.columns:
        df_db["Prix_HT"] = 0.0
else:
    data = {
        "Partenaire": ["FERME DE BEAUREGARD"],
        "Produit": ["Rillettes de canard"],
        "Cible_Feytiat": [20], "Cible_StLeo": [10],
        "Reste_Feytiat": [20], "Reste_StLeo": [10],
        "Prix_HT": [4.50], "Contact": ["05 55 70 01 90"]
    }
    df_db = pd.DataFrame(data)
    df_db.to_csv(DB_FILE, index=False)

def save_data(dataframe):
    dataframe.to_csv(DB_FILE, index=False)

# --- NAVIGATION ---
st.sidebar.title("📦 Menu de Gestion")
page = st.sidebar.radio("Navigation", ["📍 Boutique Feytiat", "📍 Boutique St-Léonard", "📊 Récapitulatif Commande", "⚙️ Administration (Prix & Cibles)"])

# --- PAGES BOUTIQUES (FEYTIAT & ST-LEO) ---
if page in ["📍 Boutique Feytiat", "📍 Boutique St-Léonard"]:
    loc = "Feytiat" if "Feytiat" in page else "StLeo"
    st.title(f"Inventaire - {page}")
    
    for p in df_db["Partenaire"].unique():
        with st.expander(f"🏢 Partenaire : {p}", expanded=True):
            h1, h2, h3, h4, h5 = st.columns([3, 1, 1, 1, 1])
            h1.write("**Produit**"); h2.write("**Prix Unitaire**"); h3.write("**Cible**"); h4.write("**Reste**"); h5.write("**À Commander**")
            st.divider()
            
            items = df_db[df_db["Partenaire"] == p]
            for i, row in items.iterrows():
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                c1.write(row['Produit'])
                c2.write(f"{row['Prix_HT']:.2f} €")
                c3.write(f"{int(row[f'Cible_{loc}'])}")
                new_reste = c4.number_input("Saisir", value=int(row[f"Reste_{loc}"]), key=f"in_{loc}_{i}", label_visibility="collapsed", step=1)
                a_cmd = max(0, int(row[f'Cible_{loc}']) - new_reste)
                color = "red" if a_cmd > 0 else "gray"
                c5.markdown(f":{color}[**{a_cmd}**]")
                
                if new_reste != row[f"Reste_{loc}"]:
                    df_db.at[i, f"Reste_{loc}"] = new_reste
                    save_data(df_db)

# --- PAGE RÉCAPITULATIF ---
elif page == "📊 Récapitulatif Commande":
    st.title("A COMMANDER - Centralisation")
    for p in df_db["Partenaire"].unique():
        df_p = df_db[df_db["Partenaire"] == p].copy()
        df_p['Cmd_Fey'] = (df_p['Cible_Feytiat'] - df_p['Reste_Feytiat']).clip(lower=0)
        df_p['Cmd_StLeo'] = (df_p['Cible_StLeo'] - df_p['Reste_StLeo']).clip(lower=0)
        df_p['Total'] = df_p['Cmd_Fey'] + df_p['Cmd_StLeo']
        
        if df_p['Total'].sum() > 0:
            with st.expander(f"📦 COMMANDE : {p}", expanded=True):
                h1, h2, h3, h4 = st.columns([3, 1, 1, 1])
                h1.write("**PRODUIT**"); h2.write("**FEYTIAT**"); h3.write("**ST LÉO**"); h4.write("**TOTAL**")
                st.divider()
                for _, row in df_p[df_p['Total'] > 0].iterrows():
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    c1.write(row['Produit']); c2.write(str(int(row['Cmd_Fey']))); c3.write(str(int(row['Cmd_StLeo']))); c4.write(f"**{int(row['Total'])}**")

# --- PAGE ADMINISTRATION (RETOUR À LA PRÉSENTATION PAR BLOCS) ---
elif page == "⚙️ Administration (Prix & Cibles)":
    st.title("⚙️ Gestion des Produits & Tarifs")
    
    # 1. Ajouter un nouveau produit
    with st.expander("➕ AJOUTER UN NOUVEAU PRODUIT", expanded=False):
        with st.form("new_prod_form"):
            f_part = st.text_input("Partenaire")
            f_prod = st.text_input("Nom du Produit")
            f_prix = st.number_input("Prix d'achat HT (€)", min_value=0.0, step=0.01)
            c_a, c_b = st.columns(2)
            f_c_fey = c_a.number_input("Cible Feytiat", min_value=0, value=20)
            f_c_st = c_b.number_input("Cible St-Léonard", min_value=0, value=20)
            f_cont = st.text_input("Contact")
            if st.form_submit_button("Créer le produit"):
                new_row = {"Partenaire": f_part.upper(), "Produit": f_prod, "Prix_HT": f_prix, "Cible_Feytiat": f_c_fey, "Cible_StLeo": f_c_st, "Reste_Feytiat": f_c_fey, "Reste_StLeo": f_c_st, "Contact": f_cont}
                df_db = pd.concat([df_db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_db)
                st.rerun()

    st.subheader("Modifier les produits existants")
    st.info("Les modifications de prix ou de cibles sont enregistrées dès que vous changez de case.")

    # 2. Modifier les produits par partenaire
    for p in df_db["Partenaire"].unique():
        with st.expander(f"🛠️ Modifier : {p}", expanded=False):
            h1, h2, h3, h4, h5 = st.columns([3, 1, 1, 1, 1])
            h1.write("**Produit**"); h2.write("**Prix HT**"); h3.write("**Cible Fey**"); h4.write("**Cible StLéo**"); h5.write("**Action**")
            st.divider()
            
            items = df_db[df_db["Partenaire"] == p]
            for i, row in items.iterrows():
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
                
                # Modification Nom
                new_name = c1.text_input("Nom", value=row['Produit'], key=f"name_{i}", label_visibility="collapsed")
                # Modification Prix
                new_p_ht = c2.number_input("Prix", value=float(row['Prix_HT']), key=f"prix_{i}", label_visibility="collapsed", step=0.05)
                # Modification Cibles
                new_cf = c3.number_input("C_Fey", value=int(row['Cible_Feytiat']), key=f"cf_{i}", label_visibility="collapsed", step=1)
                new_cs = c4.number_input("C_St", value=int(row['Cible_StLeo']), key=f"cs_{i}", label_visibility="collapsed", step=1)
                
                # Bouton de suppression
                if c5.button("🗑️", key=f"del_{i}"):
                    df_db = df_db.drop(i)
                    save_data(df_db)
                    st.rerun()

                # Sauvegarde auto si changement de l'une des valeurs
                if (new_name != row['Produit'] or new_p_ht != row['Prix_HT'] or 
                    new_cf != row['Cible_Feytiat'] or new_cs != row['Cible_StLeo']):
                    df_db.at[i, 'Produit'] = new_name
                    df_db.at[i, 'Prix_HT'] = new_p_ht
                    df_db.at[i, 'Cible_Feytiat'] = new_cf
                    df_db.at[i, 'Cible_StLeo'] = new_cs
                    save_data(df_db)
