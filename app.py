import math
from pathlib import Path
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from classes.Corpus import Corpus
from classes.SearchEngine import SearchEngine

MOTS_VIDES = {
    "that", "with", "from", "have", "their", "these", "those", "when",
    "where", "this", "what", "which", "will", "would", "there", "been",
    "were", "they", "them", "then", "than", "your", "into", "some",
    "just", "like", "also", "about", "after", "because", "while",
    "more", "other", "such", "only", "over", "much", "here", "well",
    "the", "and", "she", "but", "for", "are", "her", "was", "our",
    "him", "can", "not", "has", "his", "you"
}


st.set_page_config(page_title="Moteur de recherche", layout="wide")
RACINE = Path(__file__).resolve().parent


@st.cache_resource
def charger():
    corpus = Corpus("Animaux")
    corpus.load(RACINE / "corpus_objets.csv")
    moteur = SearchEngine(corpus)
    return corpus, moteur


corpus, moteur = charger()


def afficher_documents(tableau):
    """Lire le texte sauvegardé et accéder au document d'origine."""
    st.caption("Ouvrez un document ci-dessous pour lire le texte du corpus.")
    for identifiant in tableau["id_document"].drop_duplicates():
        doc = corpus.documents[identifiant]
        with st.expander(f"{doc.titre} ({doc.getType()})"):
            st.write(f"Auteur : {doc.auteur}")
            st.write(f"Date : {doc.date}")
            if doc.getType() == "arxiv":
                st.caption("Le corpus contient le résumé, pas le texte intégral de l'article.")
            # st.text ne traite pas le contenu des documents comme du HTML.
            st.text(doc.texte)
            url = str(doc.url)
            if urlparse(url).scheme in {"http", "https"} and urlparse(url).netloc:
                st.link_button("Ouvrir le document original", url)
            else:
                st.caption("Lien d'origine indisponible.")


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
            resultats = moteur.search(mots, n=n, source=source)
            if resultats.empty:
                st.info("Aucun document trouvé.")
            else:
                st.dataframe(resultats.style.format({"score": "{:.6g}"}))
                st.caption(f"{len(resultats)} document(s) avec un score strictement positif.")
                afficher_documents(resultats)

# --- Onglet 2 : concordancier -------------------------------------
with onglets[1]:
    mot_concorde = st.text_input("Mot à chercher dans les contextes")
    taille = st.slider("Taille du contexte (caractères)", 10, 80, 30)
    limite = st.slider("Nombre d'occurrences à afficher", 1, 50, 10)
    source_concorde = st.selectbox(
        "Source du concordancier", ["Toutes", "reddit", "arxiv"]
    )

    if st.button("Afficher les occurrences"):
        if not mot_concorde.strip():
            st.warning("Entrez un mot.")
        else:
            tableau = corpus.concorde(mot_concorde.strip().split()[0],
                                      taille_contexte=taille, source=source_concorde)
            if tableau.empty:
                st.info(f"Aucune occurrence de « {mot_concorde} ».")
            else:
                st.caption(
                    f"{len(tableau)} occurrence(s) dans "
                    f"{tableau['id_document'].nunique()} document(s). "
                    f"Affichage des {min(limite, len(tableau))} premières occurrences."
                )
                affiches = tableau.head(limite)
                st.dataframe(affiches)
                afficher_documents(affiches)

# --- Onglet 3 : statistiques --------------------------------------
with onglets[2]:
    st.caption("Analyse du corpus entier, indépendante des mots-clés et des filtres des autres onglets.")
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
        plt.close(fig)

# --- Onglet 4 : évolution temporelle ------------------------------
with onglets[3]:
    mot_evolution = st.text_input("Mot à suivre dans le temps")
    source_evolution = st.selectbox(
        "Source de l'évolution", ["Toutes", "reddit", "arxiv"]
    )
    st.caption("Occurrences brutes par mois de publication, pas une mesure de popularité générale.")

    if st.button("Tracer l'évolution"):
        if not mot_evolution.strip():
            st.warning("Entrez un mot.")
        else:
            evolution = corpus.evolution_mot(mot_evolution, source=source_evolution)
            if evolution.empty:
                st.info("Aucune occurrence exploitable dans cette source (dates valides requises).")
            else:
                mot = corpus.nettoyer_texte(mot_evolution).split()[0]
                fig, ax = plt.subplots(figsize=(9, 4))
                dates = pd.to_datetime(evolution["periode"])
                ax.plot(dates, evolution["occurrences"],
                        marker="o", color="#6d5843")
                ax.set_title(f"Évolution du mot « {mot} »")
                ax.set_ylabel("Occurrences dans le corpus")
                fig.autofmt_xdate()
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

# --- Onglet 5 : comparaison Reddit / arXiv ------------------------
with onglets[4]:
    st.caption("Comparaison globale Reddit / arXiv, indépendante des mots-clés et des filtres.")
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
                    if df == 1:
                        scores[src][mot] = nb_occ * math.log(2)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for axe, src in zip(axes, ["reddit", "arxiv"]):
            top = sorted(scores[src].items(), key=lambda x: x[1], reverse=True)[:12]
            if top:
                axe.barh([m for m, _ in top][::-1],
                         [v for _, v in top][::-1], color="#6d5843")
            else:
                axe.text(0.5, 0.5, "Aucun mot spécifique", ha="center",
                         transform=axe.transAxes)
            axe.set_title(f"Mots spécifiques — {src}")
            axe.set_facecolor("#c2b49b")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        communs = set(tf["reddit"]) & set(tf["arxiv"])
        st.write(f"Mots communs aux deux sources : {len(communs)}")
        st.write(f"Mots propres à Reddit : "
                 f"{len(set(tf['reddit']) - set(tf['arxiv']))}")
        st.write(f"Mots propres à arXiv : "
                 f"{len(set(tf['arxiv']) - set(tf['reddit']))}")
