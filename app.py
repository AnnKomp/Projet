import math
from datetime import datetime

import matplotlib.pyplot as plt
import streamlit as st

from classes.Corpus import Corpus
from classes.SearchEngine import SearchEngine

MOTS_VIDES = {
    "that", "with", "from", "have", "their", "these", "those", "when",
    "where", "this", "what", "which", "will", "would", "there", "been",
    "were", "they", "them", "then", "than", "your", "into", "some",
    "just", "like", "also", "about", "after", "because", "while",
    "more", "other", "such", "only", "over", "much", "here", "well",
}


@st.cache_resource
def charger():
    corpus = Corpus("Animaux")
    corpus.load("corpus_objets.csv")
    moteur = SearchEngine(corpus)
    return corpus, moteur


corpus, moteur = charger()

st.title("Moteur de recherche")
st.caption("Corpus Reddit + arXiv sur les animaux")

onglets = st.tabs(["Recherche", "Concordancier", "Statistiques", "Évolution", "Comparer"])

# --- Onglet 1 : recherche -----------------------------------------
with onglets[0]:
    mots = st.text_input("Mots clés", placeholder="Entrez vos mots-clés")
    n = st.slider("Nombre d'articles à extraire", 1, 20, 5)
    source = st.selectbox("Source", ["Toutes", "reddit", "arxiv"])

    if st.button("Rechercher", type="primary"):
        if not mots.strip():
            st.warning("Entrez au moins un mot-clé.")
        else:
            resultats = moteur.search(mots, n=n)
            if source != "Toutes":
                resultats = resultats[resultats["source"] == source]
            if resultats.empty:
                st.info("Aucun document trouvé.")
            else:
                st.dataframe(resultats)

# --- Onglet 2 : concordancier -------------------------------------
with onglets[1]:
    mot_concorde = st.text_input("Mot à chercher dans les contextes")
    taille = st.slider("Taille du contexte (caractères)", 10, 80, 30)

    if st.button("Afficher les occurrences"):
        if not mot_concorde.strip():
            st.warning("Entrez un mot.")
        else:
            tableau = corpus.concorde(mot_concorde.strip().split()[0],
                                      taille_contexte=taille)
            if tableau.empty:
                st.info(f"Aucune occurrence de « {mot_concorde} ».")
            else:
                st.dataframe(tableau.head(20))

# --- Onglet 3 : statistiques --------------------------------------
with onglets[2]:
    nb = st.slider("Nombre de mots à afficher", 5, 30, 15)

    if st.button("Afficher les statistiques"):
        freq = corpus.construire_freq()
        top = (
            freq[~freq["mot"].isin(MOTS_VIDES) & (freq["mot"].str.len() > 2)]
            .sort_values("term frequency", ascending=False)
            .head(nb)
        )
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.bar(top["mot"], top["term frequency"], color="#6d5843")
        ax.set_title(f"Les {nb} mots les plus fréquents (hors mots vides)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

# --- Onglet 4 : évolution temporelle ------------------------------
with onglets[3]:
    mot_evolution = st.text_input("Mot à suivre dans le temps")

    if st.button("Tracer l'évolution"):
        if not mot_evolution.strip():
            st.warning("Entrez un mot.")
        else:
            mot = mot_evolution.strip().split()[0]
            series = {}
            for doc in corpus.documents.values():
                nb_occ = corpus.nettoyer_texte(doc.texte).split().count(mot)
                if nb_occ == 0:
                    continue
                try:
                    date = datetime.fromisoformat(doc.date.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    continue
                periode = date.strftime("%Y-%m")
                series[periode] = series.get(periode, 0) + nb_occ

            if not series:
                st.info(f"Aucune occurrence de « {mot} ».")
            else:
                periodes = sorted(series)
                fig, ax = plt.subplots(figsize=(9, 4))
                ax.plot(periodes, [series[p] for p in periodes],
                        marker="o", color="#6d5843")
                ax.set_title(f"Évolution du mot « {mot} »")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig)

# --- Onglet 5 : comparaison Reddit / arXiv ------------------------
with onglets[4]:
    if st.button("Comparer les deux sources"):
        tf = {"reddit": {}, "arxiv": {}}
        for doc in corpus.documents.values():
            src = doc.getType()
            if src not in tf:
                continue
            for mot in corpus.nettoyer_texte(doc.texte).split():
                tf[src][mot] = tf[src].get(mot, 0) + 1

        scores = {"reddit": {}, "arxiv": {}}
        for src in tf:
            for mot, nb_occ in tf[src].items():
                if (mot.isalpha() and len(mot) > 3
                        and mot not in MOTS_VIDES):
                    df = sum(mot in tf[s] for s in tf)
                    scores[src][mot] = nb_occ * math.log(2) if df == 1 else 0

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for axe, src in zip(axes, ["reddit", "arxiv"]):
            top = sorted(scores[src].items(), key=lambda x: x[1], reverse=True)[:12]
            if top:
                axe.barh([m for m, _ in top][::-1],
                         [v for _, v in top][::-1], color="#6d5843")
            axe.set_title(f"Mots spécifiques — {src}")
            axe.set_facecolor("#c2b49b")
        plt.tight_layout()
        st.pyplot(fig)

        communs = set(tf["reddit"]) & set(tf["arxiv"])
        st.write(f"Mots communs aux deux sources : {len(communs)}")
        st.write(f"Mots propres à Reddit : "
                 f"{len(set(tf['reddit']) - set(tf['arxiv']))}")
        st.write(f"Mots propres à arXiv : "
                 f"{len(set(tf['arxiv']) - set(tf['reddit']))}")