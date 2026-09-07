import random
import streamlit as st
from datetime import date, timedelta
from statistics import mean

st.set_page_config(page_title="#TILT! - Prototype", page_icon="💡", layout="centered")

st.markdown(
    """
    <style>
    .stApp { max-width: 860px; margin: 0 auto; }
    [data-testid="stSidebar"] { min-width: 250px; }
    .tilt-card {
        border: 1px solid rgba(128,128,128,.28);
        border-radius: 16px;
        padding: 16px;
        margin: 10px 0;
    }
    .tilt-kicker { opacity: .72; font-size: .9rem; }
    .tilt-big { font-size: 1.35rem; font-weight: 700; }
    .tilt-muted { opacity: .72; }
    .tilt-sos {
        border: 1px solid rgba(220,80,80,.45);
        border-radius: 16px;
        padding: 16px;
        margin: 12px 0;
    }
    .nimp-card {
        border: 2px dashed rgba(128,128,128,.38);
        border-radius: 18px;
        padding: 20px;
        margin: 14px 0;
        text-align: center;
    }
    .nimp-title { font-size: 1.5rem; font-weight: 800; margin-bottom: 8px; }
    .nimp-points { font-size: 1.1rem; font-weight: 700; }
    .block-container { padding-top: 2rem; padding-bottom: 4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

MOODS = {
    1: "Très mal",
    2: "Mal",
    3: "Moyen",
    4: "Bien",
    5: "Très bien",
}

NIMP_CARDS = [
    {
        "title": "Le bouton parfaitement inutile",
        "prompt": "Un bouton clignote. Il ne sert strictement à rien. Tu fais quoi ?",
        "choices": [
            "Je clique immédiatement.",
            "J'attends de voir si quelque chose se passe.",
            "Je l'ignore et je continue.",
        ],
        "debrief": "Le cerveau adore les signaux saillants et les promesses de récompense. Le but ici n'est pas de trouver la 'bonne' réponse, mais de remarquer ton premier réflexe.",
    },
    {
        "title": "+3 points de rien du tout",
        "prompt": "L'appli t'annonce : '+3 points de rien du tout'. Quelle est ta réaction ?",
        "choices": [
            "Je veux savoir comment en gagner encore.",
            "Ça me fait rire, mais je continue quand même.",
            "Je me demande pourquoi ce score m'intéresse.",
        ],
        "debrief": "Un score peut suffire à créer une boucle d'engagement, même quand il ne représente aucune valeur réelle. Observer ce petit crochet mental, c'est déjà prendre du recul.",
    },
    {
        "title": "La banane invisible",
        "prompt": "Mission : attrape la banane invisible en moins de 5 secondes.",
        "choices": [
            "Je tente frénétiquement.",
            "Je cherche la règle cachée.",
            "Je refuse cette mission profondément douteuse.",
        ],
        "debrief": "Quand une consigne est absurde mais urgente, l'urgence peut passer devant la réflexion. C'est exactement ce que NIMP veut rendre visible.",
    },
    {
        "title": "Les chaussettes rebelles",
        "prompt": "Range les chaussettes par couleur. Problème : elles changent de couleur dès que tu les touches.",
        "choices": [
            "Je recommence jusqu'à réussir.",
            "Je m'énerve un peu, mais je continue.",
            "Je remarque que la tâche est impossible et j'arrête.",
        ],
        "debrief": "Certaines interfaces exploitent la frustration pour prolonger l'engagement. Ici, on regarde simplement à quel moment tu décides que 'ça suffit'.",
    },
    {
        "title": "Cornichon turbo",
        "prompt": "Ton cornichon virtuel court vers un mur. Tu n'as qu'un bouton : 'PLUS VITE'.",
        "choices": [
            "PLUS VITE, évidemment.",
            "Je cherche un autre bouton.",
            "Je laisse le cornichon assumer ses choix.",
        ],
        "debrief": "Un choix unique présenté comme une action peut donner une illusion de contrôle. NIMP joue avec cette sensation pour qu'on puisse en parler ensuite.",
    },
    {
        "title": "Badge très rare : Presque rien",
        "prompt": "Tu débloques un badge 'Presque rien' avec une animation spectaculaire.",
        "choices": [
            "Je suis quand même un peu fier.",
            "Je veux voir le badge suivant.",
            "Je ris du décalage entre l'animation et la récompense.",
        ],
        "debrief": "Les effets visuels, sons et badges amplifient la valeur perçue d'une récompense. Ce décalage entre forme et contenu est au cœur de la mécanique parodique de NIMP.",
    },
    {
        "title": "Encore une dernière",
        "prompt": "L'appli te propose une dernière partie. Puis une autre. Puis une 'vraie dernière'.",
        "choices": [
            "Je fais la vraie dernière.",
            "Je remarque le piège, mais je continue un peu.",
            "J'arrête dès la première proposition.",
        ],
        "debrief": "Les boucles sans fin réduisent les moments naturels d'arrêt. Le point intéressant est de repérer ce qui t'aide à fermer la boucle.",
    },
    {
        "title": "Notification cosmique",
        "prompt": "Message urgent : 'TON ÉPONGE A BESOIN DE TOI'.",
        "choices": [
            "Je vérifie immédiatement.",
            "Je souris et j'ouvre quand même.",
            "Je classe mentalement l'éponge en non-urgence.",
        ],
        "debrief": "Une notification transforme facilement une information banale en priorité. NIMP exagère ce mécanisme pour le rendre visible.",
    },
    {
        "title": "Le coffre mystère",
        "prompt": "Tu peux ouvrir un coffre gratuit maintenant, ou attendre 10 minutes pour un coffre 'méga'.",
        "choices": [
            "J'ouvre maintenant.",
            "J'attends le méga coffre.",
            "Je me demande pourquoi j'attends quelque chose qui n'existe pas.",
        ],
        "debrief": "Attente, rareté et récompense différée peuvent maintenir l'attention. Ici, aucun choix n'est jugé : on observe juste la mécanique.",
    },
    {
        "title": "Combo éponges x12",
        "prompt": "Tu viens d'éviter 12 éponges volantes. Le jeu crie 'COMBO LÉGENDAIRE !'.",
        "choices": [
            "Je veux battre mon record.",
            "Je profite du moment puis je m'arrête.",
            "Je réalise que je viens d'investir beaucoup d'énergie dans des éponges.",
        ],
        "debrief": "Le combo transforme une série d'actions simples en performance. C'est un moteur classique de répétition et d'engagement.",
    },
]

if "entries" not in st.session_state:
    st.session_state.entries = []
if "nimp_index" not in st.session_state:
    st.session_state.nimp_index = random.randrange(len(NIMP_CARDS))
if "nimp_answer" not in st.session_state:
    st.session_state.nimp_answer = None
if "nimp_rounds" not in st.session_state:
    st.session_state.nimp_rounds = 0


def save_entry(entry):
    existing = next((i for i, item in enumerate(st.session_state.entries) if item["date"] == entry["date"]), None)
    if existing is None:
        st.session_state.entries.append(entry)
    else:
        st.session_state.entries[existing] = entry
    st.session_state.entries.sort(key=lambda item: item["date"], reverse=True)


def load_demo_week():
    today = date.today()
    demo = [
        {"date": today - timedelta(days=6), "mood": 2, "anxiety": 8, "tension": 7, "consumption": True, "substance": "Alcool", "note": "Journée difficile."},
        {"date": today - timedelta(days=5), "mood": 3, "anxiety": 6, "tension": 6, "consumption": False, "substance": "", "note": "Un peu plus stable."},
        {"date": today - timedelta(days=4), "mood": 3, "anxiety": 5, "tension": 5, "consumption": False, "substance": "", "note": "Sortie et appel à un proche."},
        {"date": today - timedelta(days=3), "mood": 4, "anxiety": 4, "tension": 3, "consumption": False, "substance": "", "note": "Bonne journée."},
        {"date": today - timedelta(days=2), "mood": 3, "anxiety": 5, "tension": 4, "consumption": False, "substance": "", "note": "Fatigue."},
        {"date": today - timedelta(days=1), "mood": 4, "anxiety": 3, "tension": 3, "consumption": False, "substance": "", "note": "Ça va mieux."},
        {"date": today, "mood": 4, "anxiety": 4, "tension": 2, "consumption": False, "substance": "", "note": "Entrée fictive de démonstration."},
    ]
    st.session_state.entries = demo[::-1]


def next_nimp_card():
    previous = st.session_state.nimp_index
    choices = [i for i in range(len(NIMP_CARDS)) if i != previous]
    st.session_state.nimp_index = random.choice(choices)
    st.session_state.nimp_answer = None
    st.session_state.nimp_rounds += 1


st.title("#TILT! 💡")
st.caption("Prototype test V0.2 - pair-aidance, émotions, réduction des risques et NIMP")

with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio(
        "Aller à",
        ["Aujourd'hui", "Journal", "Outils & Ressources", "NIMP 🎮", "À propos"],
        label_visibility="collapsed",
    )
    st.divider()
    st.info("Version test : les données restent uniquement dans la session en cours et ne sont pas enregistrées.")

if page == "Aujourd'hui":
    st.subheader("Comment ça va aujourd'hui ?")
    st.caption("Objectif : remplir cette page en moins d'une minute.")

    with st.form("daily_entry"):
        entry_date = st.date_input("Date", value=date.today())
        mood_label = st.select_slider(
            "Humeur",
            options=list(MOODS.values()),
            value="Moyen",
        )
        mood_value = next(k for k, v in MOODS.items() if v == mood_label)
        anxiety = st.slider("Anxiété", 0, 10, 5, help="0 = aucune, 10 = très forte")
        tension = st.slider("Tension / impulsivité", 0, 10, 5, help="0 = calme, 10 = très forte")
        consumption = st.toggle("Consommation aujourd'hui")
        substance = ""
        if consumption:
            substance = st.selectbox("Type", ["Alcool", "Cannabis", "Médicament", "Stimulant", "Autre"])
        note = st.text_input("Une note rapide", max_chars=160, placeholder="Un fait, une émotion, un besoin...")
        submitted = st.form_submit_button("Enregistrer", type="primary", use_container_width=True)

    if submitted:
        save_entry(
            {
                "date": entry_date,
                "mood": mood_value,
                "anxiety": anxiety,
                "tension": tension,
                "consumption": consumption,
                "substance": substance,
                "note": note.strip(),
            }
        )
        st.success("Entrée enregistrée pour cette session.")

    st.markdown("#### Besoin d'un outil maintenant ?")
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("STOP - 1 minute"):
            st.markdown("**S**top.  **T**emps de respirer.  **O**bserve ce qui se passe.  **P**etite action utile maintenant.")
    with col2:
        with st.expander("Ancrage rapide"):
            st.markdown("Regarde autour de toi et nomme 5 choses que tu vois, 4 que tu peux toucher, 3 que tu entends, 2 que tu sens, 1 chose que tu veux faire ensuite.")

elif page == "Journal":
    st.subheader("Journal")
    st.caption("Voir ce qui a été noté, sans statistiques compliquées.")

    if not st.session_state.entries:
        st.info("Aucune entrée pour le moment.")
        if st.button("Charger une semaine fictive pour tester"):
            load_demo_week()
            st.rerun()
    else:
        recent = sorted(st.session_state.entries, key=lambda item: item["date"], reverse=True)
        last_7 = [item for item in recent if item["date"] >= date.today() - timedelta(days=6)]

        if last_7:
            c1, c2, c3 = st.columns(3)
            c1.metric("Humeur moyenne", f"{mean(i['mood'] for i in last_7):.1f}/5")
            c2.metric("Anxiété moyenne", f"{mean(i['anxiety'] for i in last_7):.1f}/10")
            c3.metric("Jours avec consommation", sum(1 for i in last_7 if i["consumption"]))

        st.markdown("#### Entrées")
        for item in recent:
            conso = f"Oui - {item['substance']}" if item["consumption"] else "Non"
            st.markdown(
                f"""
                <div class="tilt-card">
                  <div class="tilt-kicker">{item['date'].strftime('%d/%m/%Y')}</div>
                  <div class="tilt-big">{MOODS[item['mood']]}</div>
                  <div class="tilt-muted">Anxiété {item['anxiety']}/10 · Tension {item['tension']}/10 · Consommation : {conso}</div>
                  <div style="margin-top:8px">{item['note'] or 'Pas de note.'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()
        if st.button("Effacer les données de cette session"):
            st.session_state.entries = []
            st.rerun()

elif page == "Outils & Ressources":
    st.subheader("Outils & Ressources")
    st.caption("Des outils courts. Pas de diagnostic, pas de traitement médical automatisé.")

    with st.expander("Quand l'envie de consommer monte", expanded=True):
        st.markdown(
            """
            1. Mettre quelques minutes entre l'envie et l'action.
            2. Changer de lieu si possible.
            3. Boire ou manger quelque chose si c'est adapté à ta situation.
            4. Contacter une personne ressource.
            5. Revenir à une action très courte : douche, marche, musique, respiration, appeler quelqu'un.
            """
        )

    with st.expander("Nommer ce qui se passe"):
        st.markdown("**Temps** : depuis quand ?  **Intensité** : 0 à 10 ?  **Lieu** : où es-tu ?  **Tension** : que fait ton corps ?")

    with st.expander("Ce que j'aurais aimé entendre"):
        st.markdown(
            """
            - Tu n'as pas besoin de résoudre toute ta journée maintenant.
            - Une envie peut être forte sans devoir être suivie d'une action.
            - Demander du soutien est une action concrète.
            """
        )

    st.markdown("### Aide immédiate")
    st.markdown(
        """
        <div class="tilt-sos">
          <b>Urgence médicale immédiate : 15 ou 112</b><br>
          Prévention du suicide : <b>3114</b>, gratuit, 24h/24 et 7j/7.<br>
          Drogues Info Service : <b>0 800 23 13 13</b>, appel anonyme et gratuit, 7j/7 de 8h à 2h.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Coordonnées vérifiées le 7 septembre 2026 sur les sites officiels du ministère de la Santé et de Drogues Info Service.")

elif page == "NIMP 🎮":
    st.subheader("NIMP 🎮")
    st.caption("Un mini-jeu volontairement absurde pour observer ce qui capte l'attention, déclenche un réflexe ou donne envie de continuer.")

    card = NIMP_CARDS[st.session_state.nimp_index]
    st.markdown(
        f"""
        <div class="nimp-card">
          <div class="tilt-kicker">CARTE NIMP #{st.session_state.nimp_index + 1}</div>
          <div class="nimp-title">{card['title']}</div>
          <div>{card['prompt']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    answer = st.radio(
        "Ton premier réflexe ?",
        card["choices"],
        index=None,
        key=f"nimp_choice_{st.session_state.nimp_index}_{st.session_state.nimp_rounds}",
    )

    if answer is not None:
        st.session_state.nimp_answer = answer
        st.success(f"Réponse choisie : {answer}")
        st.markdown("#### Mini-débrief")
        st.write(card["debrief"])
        st.caption("Il n'y a pas de bonne ou de mauvaise réponse. NIMP sert à rendre visibles des réflexes d'attention, d'impulsivité, de frustration ou de recherche de récompense.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Nouvelle carte", type="primary", use_container_width=True):
            next_nimp_card()
            st.rerun()
    with c2:
        if st.button("Carte au hasard", use_container_width=True):
            next_nimp_card()
            st.rerun()

    with st.expander("À quoi sert NIMP dans #TILT! ?"):
        st.markdown(
            """
            NIMP est une **parodie des mécaniques d'engagement** : urgence artificielle, scores inutiles, récompenses, combos, frustration, notifications et envie de faire "encore une dernière".

            L'objectif n'est pas de mesurer ou diagnostiquer quoi que ce soit. On joue quelques secondes, puis on met des mots sur ce qui s'est passé :

            - Est-ce que j'ai cliqué sans réfléchir ?
            - Est-ce que j'ai voulu finir une tâche absurde ?
            - Est-ce qu'un score inutile m'a quand même accroché ?
            - À quel moment ai-je eu envie d'arrêter ?

            En atelier, ces réactions peuvent devenir un point de départ pour parler d'attention, d'impulsivité, de récompense et de comportements automatiques.
            """
        )

elif page == "À propos":
    st.subheader("À propos de cette version")
    st.markdown(
        """
        **#TILT! V0.2** est une maquette fonctionnelle destinée à tester l'idée, pas un dispositif médical.

        Cette version cherche à répondre à quatre questions :

        1. Est-ce que la saisie quotidienne est assez simple pour être utilisée réellement ?
        2. Est-ce que le journal aide à relire sa semaine sans noyer l'utilisateur dans les chiffres ?
        3. Est-ce que les outils courts sont accessibles au bon moment ?
        4. Est-ce que NIMP permet d'ouvrir une discussion utile sur l'attention, l'impulsivité et les mécaniques de récompense ?

        Ce qui n'est volontairement **pas** dans cette version : communauté, chat, mentor pair-aidant, espace professionnel, notifications intelligentes, compte utilisateur et synchronisation cloud.
        """
    )
    st.warning("Prototype local : ne pas utiliser comme dossier médical ni comme stockage de données sensibles.")
