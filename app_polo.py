import streamlit as st
import pandas as pd
from datetime import date
import random
import calendar

# ===================
# PARAMÈTRES
# ===================
DATA_FILE = "calendrier_blagues_anniv_2024.xlsx"

# Codes secrets + indices
SECRET_CODES = {
    "hossegor": "village paisible cher à ton coeur",
    "mawen10": "groupuscule influent de mawenzi niché au coeur de la ville lumière",
    "cail": "délicieuse rue qui a pu accueillir les afters les plus intéressants de l'année 2024",
    "maintenon": "village d'origine cher à ton coeur",
    "losbocazas": "ton equipe de football de coeur",
    "auriane": "prenom d'une femme chère à ton coeur",
}

# Noms de mois pour l'affichage
MONTH_NAMES = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]

# ===================
# CHARGEMENT DES DONNÉES
# ===================
@st.cache_data
def load_jokes(path):
    df = pd.read_excel(path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

df = load_jokes(DATA_FILE)

# ===================
# CONFIG GLOBALE
# ===================
st.set_page_config(page_title="Calendrier de blagues 🎉",
                   page_icon="🎂",
                   layout="centered")

st.title("🎂 Calendrier de blagues personnalisées")
st.write("Une blague par jour, mais **surtout** le 20 juillet... 😏")

# ===================
# GESTION DU CODE SECRET + INDICE
# ===================
if "authorized" not in st.session_state:
    st.session_state["authorized"] = False

# On choisit un code + indice au hasard une seule fois par session
if "secret_code" not in st.session_state or "secret_hint" not in st.session_state:
    code_choice = random.choice(list(SECRET_CODES.keys()))
    st.session_state["secret_code"] = code_choice
    st.session_state["secret_hint"] = SECRET_CODES[code_choice]

if not st.session_state["authorized"]:
    st.subheader("🔐 Espace privé")

    # Roue qui tourne avec l'indice
    wheel_html = f"""
    <style>
    .hint-container {{
        display: flex;
        align-items: center;
        margin: 1rem 0;
    }}
    .hint-wheel {{
        border: 6px solid #ffeeba;
        border-top: 6px solid #ff9800;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        animation: spin 1.4s linear infinite;
        margin-right: 12px;
    }}
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    .hint-text {{
        font-size: 16px;
        background-color: #fff3cd;
        padding: 8px 12px;
        border-radius: 8px;
        border-left: 4px solid #ffca2c;
    }}
    </style>
    <div class="hint-container">
        <div class="hint-wheel"></div>
        <div class="hint-text">
            <b>Indice :</b> {st.session_state['secret_hint']}
        </div>
    </div>
    """
    st.markdown(wheel_html, unsafe_allow_html=True)

    code_input = st.text_input("Entre le code secret :", type="password")

    if st.button("Valider le code"):
       .expected = st.session_state["secret_code"]
        if code_input.strip().lower() == .expected:
            st.session_state["authorized"] = True
            st.success("Code correct, bienvenue ! 🎉")
        else:
            st.error("Code incorrect... Essaie encore 😈")

    st.stop()

# ===================
# UNE FOIS LE CODE VALIDÉ : CHOIX DU JOUR
# ===================
st.subheader("📅 Choisis un jour")

# Sélecteur de mois (sans afficher d'année)
month = st.selectbox(
    "Mois :",
    options=list(range(1, 13)),
    format_func=lambda m: MONTH_NAMES[m - 1],
    index=6  # 7e mois = juillet par défaut
)

# Nombre de jours dans le mois (année bissextile 2024 mais on ne l’affiche pas)
days_in_month = calendar.monthrange(2024, month)[1]

# Sélecteur de jour
default_day_index = min(19, days_in_month - 1)  # 20 par défaut quand possible
day = st.selectbox(
    "Jour :",
    options=list(range(1, days_in_month + 1)),
    index=default_day_index
)

# On reconstruit la date interne (année cachée)
selected_date = date(2024, month, day)

st.caption(f"Tu as choisi le {day} {MONTH_NAMES[month - 1]}.")

# ===================
# AFFICHAGE DE LA BLAGUE
# ===================
row = df[df["Date"] == selected_date]

if row.empty:
    st.warning("Pas de blague trouvée pour ce jour. 😱")
else:
    joke = row["Blague"].iloc[0]

    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center; font-size: 26px; line-height: 1.5;">
            {joke.replace('\n', '<br>')}
        </div>
        """,
        unsafe_allow_html=True,
    )
