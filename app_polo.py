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
    "hossegor": "village paisible cher à ton cœur",
    "mawen10": "groupuscule influent de mawenzi niché au cœur de la ville lumière",
    "cail": "délicieuse rue ayant accueilli les afters les plus intéressants de 2024",
    "maintenon": "village d’origine cher à ton cœur",
    "losbocazas": "ton équipe de football de cœur",
    "auriane": "prénom d’une femme chère à ton cœur"
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

# Pool complet de blagues pour le bouton reroll
ALL_JOKES = list({str(b) for b in df["Blague"].dropna().tolist()})

# ===================
# CONFIG STREAMLIT
# ===================

st.set_page_config(page_title="Calendrier de blagues 🎉", page_icon="🎂", layout="centered")
st.title("🎂 Calendrier de blagues personnalisées")
st.write("Une blague par jour… mais **surtout** le 20 juillet 😏")

# ===================
# SESSION STATE
# ===================

ss = st.session_state

if "authorized" not in ss:
    ss["authorized"] = False
if "fail_count" not in ss:
    ss["fail_count"] = 0
if "secret_code" not in ss:
    code = random.choice(list(SECRET_CODES.keys()))
    ss["secret_code"] = code
    ss["secret_hint"] = SECRET_CODES[code]

# Pour blague alternative par date
if "current_joke_by_date" not in ss:
    ss["current_joke_by_date"] = {}

# Pour blague aléatoire
if "random_joke" not in ss:
    ss["random_joke"] = None
if "random_joke_date" not in ss:
    ss["random_joke_date"] = None

# RESET AUTOMATIQUE SI FICHIER EXCEL CHANGE
data_hash = hash(tuple(df["Blague"].astype(str).tolist()))
if ss.get("data_hash") != data_hash:
    ss["data_hash"] = data_hash
    ss["current_joke_by_date"] = {}
    ss["random_joke"] = None
    ss["random_joke_date"] = None

# ===================
# CODE SECRET
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
        <div class="hint-text"><b>Indice :</b> {ss['secret_hint']}</div>
    </div>
    """
    st.markdown(wheel_html, unsafe_allow_html=True)

    code_input = st.text_input("Entre le code secret :", type="password")

    if ss["fail_count"] > 0:
        st.info(f"Échecs : {ss['fail_count']} fois 😏")

    if st.button("Valider le code"):
        if code_input.strip().lower() == ss["secret_code"]:
            ss["authorized"] = True
            st.success("Accès autorisé 🎉")
        else:
            ss["fail_count"] += 1
            st.error("Code incorrect 😈")

    st.stop()

# ===================
# CHOIX DU MODE
# ===================

st.subheader("😏 Comment veux-tu découvrir ta blague ?")

mode = st.radio("", ["Par jour du calendrier", "Blague aléatoire"], index=0)

# ===================
# MODE CALENDRIER
# ===================

if mode == "Par jour du calendrier":

    st.subheader("📅 Choisis un jour")

    # par défaut → janvier / 1
    month = st.selectbox(
        "Mois :", list(range(1, 13)),
        index=0,
        format_func=lambda m: MONTH_NAMES[m - 1]
    )

    days_in_month = calendar.monthrange(2024, month)[1]
    day = st.selectbox("Jour :", list(range(1, days_in_month + 1)), index=0)

    selected_date = date(2024, month, day)
    date_key = selected_date.isoformat()

    row = df[df["Date"] == selected_date]
    base_joke = str(row["Blague"].iloc[0])

    # 20 juillet : verrouillé
    is_bday = (selected_date.month == 7 and selected_date.day == 20)

    # initialisation si jamais
    if date_key not in ss["current_joke_by_date"]:
        ss["current_joke_by_date"][date_key] = base_joke

    # bouton reroll
    if not is_bday:
        if st.button("Une autre blague pour ce jour 🙃"):
            current = ss["current_joke_by_date"][date_key]
            candidates = [j for j in ALL_JOKES if j != current and j != base_joke]
            if not candidates:
                candidates = [j for j in ALL_JOKES if j != current] or ALL_JOKES
            ss["current_joke_by_date"][date_key] = random.choice(candidates)

    final_joke = base_joke if is_bday else ss["current_joke_by_date"][date_key]

    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center; font-size:26px;">
            {final_joke.replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

# ===================
# MODE BLAGUE ALÉATOIRE
# ===================

else:
    st.subheader("🎲 Blague aléatoire")

    if st.button("Tire-moi une blague 🎲") or ss["random_joke"] is None:
        row = df.sample(1).iloc[0]
        ss["random_joke"] = str(row["Blague"])
        ss["random_joke_date"] = row["Date"]

    d = ss["random_joke_date"]
    st.caption(f"Blague provenant du {d.day} {MONTH_NAMES[d.month - 1]}")

    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center; font-size:26px;">
            {ss["random_joke"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )
