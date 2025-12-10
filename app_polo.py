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
    "auriane": "prénom d’une femme chère à ton cœur",
}

MONTH_NAMES = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]

# ===================
# CHARGEMENT (SANS CACHE)
# ===================

def load_jokes(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

df = load_jokes(DATA_FILE)
ALL_JOKES = df["Blague"].dropna().astype(str).unique().tolist()

# ===================
# CONFIG STREAMLIT
# ===================

st.set_page_config(page_title="Calendrier de blagues 🎉", page_icon="🎂", layout="centered")

st.title("🎂 Calendrier de blagues personnalisées")
st.write("Une blague par jour… mais **surtout** le 20 juillet 😏")

ss = st.session_state

# ===================
# INIT STATE
# ===================

if "authorized" not in ss:
    ss["authorized"] = False
if "fail_count" not in ss:
    ss["fail_count"] = 0
if "secret_code" not in ss:
    code_choice = random.choice(list(SECRET_CODES.keys()))
    ss["secret_code"] = code_choice
    ss["secret_hint"] = SECRET_CODES[code_choice]

# Pour le mode blague aléatoire uniquement
if "random_joke" not in ss:
    ss["random_joke"] = None
if "random_joke_date" not in ss:
    ss["random_joke_date"] = None

# ===================
# ÉCRAN CODE SECRET
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
        st.info(f"Tu t'es déjà trompé {ss['fail_count']} fois 😏")

    if st.button("Valider le code"):
        if code_input.strip().lower() == ss["secret_code"]:
            ss["authorized"] = True
            st.success("Code correct, bienvenue ! 🎉")
        else:
            ss["fail_count"] += 1
            st.error("Code incorrect... Essaie encore 😈")

    st.stop()

# ===================
# CHOIX DU MODE
# ===================

st.subheader("😏 Comment veux-tu découvrir ta blague ?")
mode = st.radio("", ["Par jour du calendrier", "Blague aléatoire"], index=0)

# ===================
# MODE 1 : PAR JOUR DU CALENDRIER
# ===================

if mode == "Par jour du calendrier":
    st.subheader("📅 Choisis un jour")

    # 1er janvier par défaut
    month = st.selectbox(
        "Mois :",
        options=list(range(1, 13)),
        format_func=lambda m: MONTH_NAMES[m - 1],
        index=0,  # janvier
    )

    days_in_month = calendar.monthrange(2024, month)[1]
    day = st.selectbox(
        "Jour :",
        options=list(range(1, days_in_month + 1)),
        index=0,  # 1er
    )

    selected_date = date(2024, month, day)
    st.caption(f"Tu as choisi le {day} {MONTH_NAMES[month - 1]}.")

    row = df[df["Date"] == selected_date]

    if row.empty:
        st.warning("Pas de blague trouvée pour ce jour 😱")
    else:
        base_joke = str(row["Blague"].iloc[0])
        is_birthday = (selected_date.day == 20 and selected_date.month == 7)

        # Blague affichée par défaut = blague du fichier
        joke_to_show = base_joke

        # Bouton reroll uniquement si ce n’est pas le 20 juillet
        if not is_birthday:
            if st.button("Une autre blague pour ce jour 🙃"):
                # Choisit une autre blague différente de celle de base
                candidates = [j for j in ALL_JOKES if j != base_joke]
                if not candidates:
                    candidates = ALL_JOKES
                joke_to_show = random.choice(candidates)

        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align:center; font-size:26px; line-height:1.5;">
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

    if st.button("Tire-moi une blague 🎲") or ss["random_joke"] is None:
        rand_row = df.sample(1).iloc[0]
        ss["random_joke"] = str(rand_row["Blague"])
        ss["random_joke_date"] = rand_row["Date"]

    d = ss["random_joke_date"]
    st.caption(f"Blague provenant du {d.day} {MONTH_NAMES[d.month - 1]}.")

    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center; font-size:26px; line-height:1.5;">
            {ss["random_joke"].replace("\n", "<br>")}
        </div>
        """,
        unsafe_allow_html=True,
    )
