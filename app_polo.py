import streamlit as st
import pandas as pd
from datetime import date

# ===================
# PARAMÈTRES
# ===================
EXCEL_FILE = "calendrier_blagues_anniv_2024.xlsx"

# À MODIFIER : choisis ton code secret ici
SECRET_CODE = "BANANE2025"

# ===================
# CHARGEMENT DES DONNÉES
# ===================
@st.cache_data
def load_jokes(path):
    df = pd.read_excel(path)
    # On force le format date si jamais Excel fait des siennes
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

df = load_jokes(EXCEL_FILE)

# ===================
# INTERFACE
# ===================
st.set_page_config(page_title="Calendrier de blagues 🎉", page_icon="🎈", layout="centered")

st.title("🎂 Calendrier de blagues personnalisées")
st.write("Une blague par jour, mais **surtout** le 20 juillet... 😉")

# -------------------
# ÉTAPE 1 : CODE SECRET
# -------------------
if "authorized" not in st.session_state:
    st.session_state["authorized"] = False

if not st.session_state["authorized"]:
    st.subheader("🔐 Espace privé")
    code_input = st.text_input("Entre le code secret :", type="password")

    if st.button("Valider le code"):
        if code_input == SECRET_CODE:
            st.session_state["authorized"] = True
            st.success("Code correct, bienvenue ! 🎉")
        else:
            st.error("Code incorrect... Essaie encore 😈")
    # On bloque la suite tant que le code n’est pas bon
    st.stop()

# -------------------
# ÉTAPE 2 : CHOIX DE LA DATE
# -------------------
st.subheader("📅 Choisis une date")

min_date = min(df["Date"])
max_date = max(df["Date"])

selected_date = st.date_input(
    "Date du jour à découvrir :",
    value=date(2024, 7, 20),
    min_value=min_date,
    max_value=max_date,
    format="DD/MM/YYYY"
)

# -------------------
# AFFICHAGE DE LA BLAGUE
# -------------------
# On récupère la blague correspondante
row = df[df["Date"] == selected_date]

if row.empty:
    st.warning("Pas de blague trouvée pour cette date. 😱")
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
