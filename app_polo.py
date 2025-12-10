import streamlit as st
import pandas as pd
from datetime import date
import random
import calendar

# ===================
# PARAMÈTRES
# ===================
DATA_FILE = "calendrier_blagues_anniv_2024.xlsx"

SECRET_CODES = {
    "hossegor": "village paisible cher à ton coeur",
    "mawen10": "groupuscule influent de mawenzi niché au coeur de la ville lumière",
    "cail": "délicieuse rue qui a pu accueillir les afters les plus intéressants de l'année 2024",
    "maintenon": "village d'origine cher à ton coeur",
    "losbocazas": "ton equipe de football de coeur",
    "auriane": "prenom d'une femme chère à ton coeur",
}

MONTH_NAMES = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]

# ===================
# CHARGEMENT
# ===================
@st.cache_data
def load_jokes(path):
    df = pd.read_excel(path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

df = load_jokes(DATA_FILE)

# pool de toutes les blagues possibles
ALL_JOKES = list({str(b) for b in df["Blague"].dropna().tolist()})

# ===================
# CONFIG
# ===================
st.set_page_config(
    page_title="Calendrier de blagues 🎉",
    page_icon="🎂",
    layout="centered"
)

st.title("🎂 Calendrier de blagues personnalisées")
st.write("Une blague par jour, mais **surtout** le 20 juillet... 😏")

# ===================
# INIT ÉTAT SESSION
# ===================
ss = st.session_state

if "authorized" not in ss:
    ss["authorized"] = False
if "fail_count" not in ss:
    ss["fail_count"] = 0
if "secret_code" not in ss or "secret_hint" not in ss:
    code_choice = random.choice(list(SECRET_CODES.keys()))
    ss["secret_code"] = code_choice
    ss["secret_hint"] = SECRET_CODES[code_choice]

# blague actuellement affichée par date (mode calendrier)
if "current_joke_by_date" not in ss:
    ss["current_joke_by_date"] = {}

# blague aléatoire globale
if "random_joke" not in ss:
    ss["random_joke"] = None
if "random_joke_date" not in ss:
    ss["random_joke_date"] = None

# ===================
# CODE SECRET + INDICE
# ===================
if not ss["authorized"]:
    st.subheader("🔐 Espace privé")

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
            <b>Indice :</b> {ss["secret_hint"]}
        </div>
    </div>
    """
    st.markdown(wheel_html, unsafe_allow_html=True)

    code_input = st.text_input("Entre le code secret :", type="password")

    if ss["fail_count"] > 0:
        msg = f"Tu t'es déjà trompé {ss['fail_count']} fois 😏"
        if ss["fail_count"] >= 5:
            msg += " (tu commences à m'inquiéter…)"
        st.info(msg)

    if st.button("Valider le code"):
        if code_input.strip().lower() == ss["secret_code"]:
            ss["authorized"] = True
            st.success("Code correct, bienvenue ! 🎉")
        else:
            ss["fail_count"] += 1
            st.error("Code incorrect... Essaie encore 😈")

    st.stop()

# ===================
# UNE FOIS CONNECTÉ : CHOIX DU MODE
# ===================
st.subheader("😏 Comment veux-tu découvrir ta blague ?")

mode = st.radio(
    "",
    ["Par jour du calendrier", "Blague aléatoire"],
    index=0
)

# ===================
# MODE 1 : PAR JOUR DU CALENDRIER
# ===================
if mode == "Par jour du calendrier":
    st.subheader("📅 Choisis un jour")

    # par défaut : 1er janvier (et pas le 20 juillet)
    month = st.selectbox(
        "Mois :",
        options=list(range(1, 13)),
        format_func=lambda m: MONTH_NAMES[m - 1],
        index=0  # janvier
    )

    days_in_month = calendar.monthrange(2024, month)[1]
    day = st.selectbox(
        "Jour :",
        options=list(range(1, days_in_month + 1)),
        index=0  # 1er du mois
    )

    selected_date = date(2024, month, day)
    st.caption(f"Tu as choisi le {day} {MONTH_NAMES[month - 1]}.")

    row = df[df["Date"] == selected_date]

    if row.empty:
        st.warning("Pas de blague trouvée pour ce jour 😱")
    else:
        base_joke = str(row["Blague"].iloc[0])
        date_key = selected_date.isoformat()
        is_birthday = (selected_date.day == 20 and selected_date.month == 7)

        # initialisation de la blague affichée pour ce jour
        if date_key not in ss["current_joke_by_date"]:
            ss["current_joke_by_date"][date_key] = base_joke

        # bouton spin (sauf le 20 juillet)
        if not is_birthday:
            if st.button("Une autre blague pour ce jour 🙃"):
                # on évite la blague actuelle ET la blague de base si possible
                current = ss["current_joke_by_date"][date_key]
                candidates = [
                    j for j in ALL_JOKES
                    if j != current and j != base_joke
                ]
                if not candidates:
                    # fallback : on évite juste la blague actuelle
                    candidates = [j for j in ALL_JOKES if j != current] or ALL_JOKES
                ss["current_joke_by_date"][date_key] = random.choice(candidates)

        joke_to_show = ss["current_joke_by_date"][date_key] if not is_birthday else base_joke

        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align:center; font-size: 26px; line-height: 1.5;">
                {joke_to_show.replace("\n", "<br>")}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ===================
# MODE 2 : BLAGUE ALÉATOIRE
# ===================
else:
    st.subheader("🎲 Blague aléatoire")

    if st.button("Tire-moi une blague aléatoire 🎲") or ss["random_joke"] is None:
        random_row = df.sample(1).iloc[0]
        ss["random_joke"] = str(random_row["Blague"])
        ss["random_joke_date"] = random_row["Date"]

    if ss["random_joke"] is not None:
        d = ss["random_joke_date"]
        day_r = d.day
        month_r = d.month
        st.caption(f"Cette blague vient du {day_r} {MONTH_NAMES[month_r - 1]}.")

        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align:center; font-size: 26px; line-height: 1.5;">
                {ss["random_joke"].replace("\n", "<br>")}
            </div>
            """,
            unsafe_allow_html=True,
        )
