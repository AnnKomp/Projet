import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from tqdm import tqdm


class SearchEngine:
    def __init__(self, corpus):
        self.corpus = corpus
        self.docs = list(corpus.documents.values())
        self._construire_vocab_et_tf()
        self._construire_tfidf()

    # --- Construction -------------------------------------------------
    def _construire_vocab_et_tf(self):
        textes = [self.corpus.nettoyer_texte(d.texte).split() for d in self.docs]

        mots = sorted(set(m for t in textes for m in t))
        self.vocab = {mot: {"id": i} for i, mot in enumerate(mots)}

        lignes, colonnes, valeurs = [], [], []
        for i, mots_doc in enumerate(tqdm(textes, desc="Construction de la matrice")):
            comptes = {}
            for m in mots_doc:
                comptes[m] = comptes.get(m, 0) + 1
            for m, c in comptes.items():
                lignes.append(i)
                colonnes.append(self.vocab[m]["id"])
                valeurs.append(c)

        self.mat_TF = csr_matrix(
            (valeurs, (lignes, colonnes)), shape=(len(self.docs), len(mots))
        )

        totaux = self.mat_TF.sum(axis=0).A1
        nb_docs = self.mat_TF.getnnz(axis=0)
        for infos in self.vocab.values():
            j = infos["id"]
            infos["total"] = int(totaux[j])
            infos["nb_docs"] = int(nb_docs[j])

    def _construire_tfidf(self):
        N = self.mat_TF.shape[0]
        nb_docs = self.mat_TF.getnnz(axis=0)
        self.idf = np.log(N / nb_docs)
        self.mat_TFxIDF = csr_matrix(self.mat_TF.multiply(self.idf))
        self.normes = np.sqrt(
            self.mat_TFxIDF.multiply(self.mat_TFxIDF).sum(axis=1)
        ).A1

    # --- Recherche ----------------------------------------------------
    def _vecteur_requete(self, requete):
        vec = np.zeros(len(self.vocab))
        for mot in self.corpus.nettoyer_texte(requete).split():
            if mot in self.vocab:
                vec[self.vocab[mot]["id"]] += 1
        return vec * self.idf

    def search(self, mots_cles, n=5):
        q = self._vecteur_requete(mots_cles)
        norme_q = np.linalg.norm(q)
        if norme_q == 0:
            return pd.DataFrame(columns=["titre", "auteur", "source", "score"])

        produits = self.mat_TFxIDF.dot(q)
        scores = np.zeros(len(self.docs))
        ok = self.normes > 0
        scores[ok] = produits[ok] / (self.normes[ok] * norme_q)

        meilleurs = np.argsort(scores)[::-1][:n]
        return pd.DataFrame({
            "titre": [self.docs[i].titre for i in meilleurs],
            "auteur": [self.docs[i].auteur for i in meilleurs],
            "source": [self.docs[i].getType() for i in meilleurs],
            "score": [round(float(scores[i]), 4) for i in meilleurs],
        })