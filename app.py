import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Vie Étudiante Pro", page_icon="🎓", layout="wide")

# --- STYLE CSS (Design Pro) ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 18px; }
    .stButton button { font-size: 20px; font-weight: bold; width: 100%; }
    .urgent-box { border: 2px solid red; padding: 10px; border-radius: 5px; background-color: #ffe6e6; color: red; font-weight: bold; }
    .success-box { padding: 15px; border-radius: 10px; background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONSTANTES & FICHIERS
FICHIER_DONNEES = 'avis_etudiants_ultimate.csv'
FICHIER_SUCCES = 'message_succes.txt' # Fichier pour sauvegarder le message de victoire
DOSSIER_IMAGES = 'preuves_images'

if not os.path.exists(DOSSIER_IMAGES):
    os.makedirs(DOSSIER_IMAGES)

# Fonction de chargement
def charger_donnees():
    if os.path.exists(FICHIER_DONNEES):
        return pd.read_csv(FICHIER_DONNEES)
    else:
        return pd.DataFrame(columns=["Date", "Catégorie", "Message", "Note", "Urgence", "Image"])

# Fonction pour lire le message de succès
def lire_succes():
    if os.path.exists(FICHIER_SUCCES):
        with open(FICHIER_SUCCES, "r", encoding="utf-8") as f:
            return f.read()
    return "Bienvenue ! Aucun problème résolu pour le moment."

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2995/2995620.png", width=100)
    st.title("Espace Vie Scolaire")
    st.info("Zone de Feedback M1. Upgrade le campus. Latence : 0ms.")
    
    st.markdown("---")
    st.subheader("🔐 Accès Délégués")
    mot_de_passe = st.text_input("Mot de passe admin :", type="password")

# --- PAGE PRINCIPALE ---

# 1. LE MUR DES SUCCÈS (Affichage dynamique)
st.title("🎓 Tableau de Bord Étudiant")
message_victoire = lire_succes()
if message_victoire:
    st.markdown(f'<div class="success-box">🏆 <b>Dernières Victoires :</b><br>{message_victoire}</div>', unsafe_allow_html=True)

# 2. LE FORMULAIRE (Disposé en colonnes)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Exprimer un avis ou un problème")
    
    with st.form("formulaire_avis"):
        # Case Urgence stylisée
        est_urgent = st.checkbox("🚨 C'est une URGENCE ")
        
        categorie = st.selectbox(
            "Sujet :",
            ["Cours & Profs 📚", "Locaux & Matériel 🏫", "Ambiance & Vie Scolaire 🎉", "Autre 💡"]
        )

        message = st.text_area("Détails du message :")
        
        cols_note = st.columns(2)
        with cols_note[0]:
            note = st.slider("Satisfaction globale :", 1, 5, 3)
        with cols_note[1]:
            photo = st.file_uploader("Preuve (Photo)", type=['png', 'jpg', 'jpeg'])

        submit_btn = st.form_submit_button("Envoyer mon avis 🚀")

    if submit_btn:
        if message:
            date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M")
            nom_image = "Aucune"
            if photo is not None:
                chemin_image = os.path.join(DOSSIER_IMAGES, photo.name)
                with open(chemin_image, "wb") as f:
                    f.write(photo.getbuffer())
                nom_image = photo.name

            txt_urgence = "🚨 OUI" if est_urgent else "Non"

            nouvelle_donnee = pd.DataFrame({
                "Date": [date_actuelle],
                "Catégorie": [categorie],
                "Message": [message],
                "Note": [note],
                "Urgence": [txt_urgence],
                "Image": [nom_image]
            })
            
            df = charger_donnees()
            df = pd.concat([df, nouvelle_donnee], ignore_index=True)
            df.to_csv(FICHIER_DONNEES, index=False)
            
            st.success("Merci ! Ton avis a été enregistré.")
            st.balloons() # Petite animation sympa
        else:
            st.error("Le message est vide !")

with col2:
    st.warning(" 👋 Bienvenue ! \n\nCet espace est anonyme. Si tu coches 'Urgence', les délégués seront averti en priorité.")

# --- ZONE ADMIN (Affichage conditionnel) ---
MOT_DE_PASSE_SECRET = "playstation5"

if mot_de_passe == MOT_DE_PASSE_SECRET:
    st.markdown("---")
    st.header("📊 Analyse des Données (Admin)")
    
    df = charger_donnees()
    
    if not df.empty:
        # A. Gestion du Mur des Succès
        with st.expander("🏆 Mettre à jour le 'Mur des Succès' (Annonces)"):
            nouveau_message = st.text_area("Message à afficher en haut de page :", value=lire_succes())
            if st.button("Mettre à jour l'annonce"):
                with open(FICHIER_SUCCES, "w", encoding="utf-8") as f:
                    f.write(nouveau_message)
                st.success("Annonce mise à jour ! Recharge la page pour voir.")

        # B. Les KPIs
        total_avis = len(df)
        total_urgences = len(df[df['Urgence'] == "🚨 OUI"])
        moyenne_notes = df['Note'].mean()
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Avis", total_avis)
        kpi2.metric("Urgences", total_urgences, delta_color="inverse")
        kpi3.metric("Note Moyenne", f"{moyenne_notes:.1f}/5")
        
        # C. Graphiques Avancés
        tab1, tab2, tab3 = st.tabs(["📈 Évolution", "🥧 Répartition", "📋 Données Brutes"])
        
        with tab1:
            st.subheader("Évolution des plaintes dans le temps")
            # Conversion de la date pour le graphique
            df['Date_Clean'] = pd.to_datetime(df['Date']).dt.date
            daily_counts = df['Date_Clean'].value_counts().sort_index()
            st.line_chart(daily_counts)
            
        with tab2:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.write("**Par Catégorie**")
                st.bar_chart(df['Catégorie'].value_counts())
            with col_g2:
                st.write("**Par Note**")
                st.bar_chart(df['Note'].value_counts())

        with tab3:
            # Filtres
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtre_cat = st.multiselect("Filtrer par catégorie", df['Catégorie'].unique())
            with col_f2:
                voir_urgences = st.checkbox("Voir seulement les URGENCES")
            
            df_filtre = df.copy()
            if voir_urgences:
                df_filtre = df_filtre[df_filtre['Urgence'] == "🚨 OUI"]
            if filtre_cat:
                df_filtre = df_filtre[df_filtre['Catégorie'].isin(filtre_cat)]
                
            st.dataframe(df_filtre, use_container_width=True)
            
            st.download_button(
                "📥 Télécharger CSV",
                df_filtre.to_csv(index=False).encode('utf-8'),
                "export_vie_etudiante.csv",
                "text/csv"
            )
    else:
        st.info("Aucune donnée pour l'instant.")