import streamlit as st
import pandas as pd
from datetime import date
import random
import calendar

# ===================
# PARAMÈTRES
# ===================
# On revient sur ton fichier de base
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

# ===================
# CONFIG
# ===================
st.set_page_config(page_title="Calendrier de blagues 🎉", page_icon="🎂", layout="centered")

st.title("🎂 Calendrier de blagues personnalisées")
st.write("Une blague par jour, mais **surtout** le 20 juillet... 😏")

# ===================
# INIT ÉTAT SESSION
# ===================
if "authorized" not in st.session_state:
    st.session_state["authorized"] = False

if "fail_count" not in st.session_state:
    st.session_state["fail_count"] = 0

if "secret_code" not in st.session_state or "secret_hint" not in st.session_state:
    code_choice = random.choice(list(SECRET_CODES.keys()))
    st.session_state["secret_code"] = code_choice
    st.session_state["secret_hint"] = SECRET_CODES[code_choice]

if "random_joke" not in st.session_state:
    st.session_state["random_joke"] = None
if "random_joke_date" not in st.session_state:
    st.session_state["random_joke_date"] = None

# pour stocker les blagues alternatives par date (mode calendrier)
if "calendar_alt_jokes" not in st.session_state:
    st.session_state["calendar_alt_jokes"] = {}

# ===================
# CODE SECRET + INDICE
# ===================
if not st.session_state["authorized"]:
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
            <b>Indice :</b> {st.session_state["secret_hint"]}
        </div>
    </div>
    """
    st.markdown(wheel_html, unsafe_allow_html=True)

    code_input = st.text_input("Entre le code secret :", type="password")

    if st.session_state["fail_count"] > 0:
        msg = f"Tu t'es déjà trompé {st.session_state['fail_count']} fois 😏"
        if st.session_state["fail_count"] >= 5:
            msg += " (tu commences à m'inquiéter…)"
        st.info(msg)

    if st.button("Valider le code"):
        if code_input.strip().lower() == st.session_state["secret_code"]:
            st.session_state["authorized"] = True
            st.success("Code correct, bienvenue ! 🎉")
        else:
            st.session_state["fail_count"] += 1
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

    # Par défaut : 1er janvier (mois index 0, jour index 0)
    month = st.selectbox(
        "Mois :",
        options=list(range(1, 13)),
        format_func=lambda m: MONTH_NAMES[m - 1],
        index=0  # janvier
    )

    days_in_month = calendar.monthrange(2024, month)[1]
    default_day = 0  # 1er du mois

    day = st.selectbox(
        "Jour :",
        options=list(range(1, days_in_month + 1)),
        index=default_day
    )

    selected_date = date(2024, month, day)
    st.caption(f"Tu as choisi le {day} {MONTH_NAMES[month - 1]}.")

    row = df[df["Date"] == selected_date]

    if row.empty:
        st.warning("Pas de blague trouvée pour ce jour 😱")
    else:
        base_joke = row["Blague"].iloc[0]
        date_key = selected_date.isoformat()

        # 20 juillet = jour sacré → pas de reroll
        is_birthday = (selected_date.day == 20 and selected_date.month == 7)

        if not is_birthday:
            if st.button("Une autre blague pour ce jour 🙃"):
                all_jokes = df["Blague"].unique().tolist()
                candidates = [j for j in all_jokes if j != base_joke]
                if not candidates:
                    candidates = all_jokes
                alt = random.choice(candidates)
                st.session_state["calendar_alt_jokes"][date_key] = alt

        if not is_birthday and date_key in st.session_state["calendar_alt_jokes"]:
            joke_to_show = st.session_state["calendar_alt_jokes"][date_key]
        else:
            joke_to_show = base_joke

        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align:center; font-size: 26px; line-height: 1.5;">
                {str(joke_to_show).replace("\\n", "<br>")}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ===================
# MODE 2 : BLAGUE ALÉATOIRE
# ===================
else:
    st.subheader("🎲 Blague aléatoire")

    if st.button("Tire-moi une blague aléatoire 🎲") or st.session_state["random_joke"] is None:
        random_row = df.sample(1).iloc[0]
        st.session_state["random_joke"] = random_row["Blague"]
        st.session_state["random_joke_date"] = random_row["Date"]

    if st.session_state["random_joke"] is not None:
        d = st.session_state["random_joke_date"]
        day_r = d.day
        month_r = d.month
        st.caption(f"Cette blague vient du {day_r} {MONTH_NAMES[month_r - 1]}.")

        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align:center; font-size: 26px; line-height: 1.5;">
                {str(st.session_state["random_joke"]).replace("\\n", "<br>")}
            </div>
            """,
            unsafe_allow_html=True,
        )
