import unittest
from unittest.mock import patch

from classes.Corpus import Corpus
from classes.SearchEngine import SearchEngine


class DocumentFictif:
    """Uniquement les attributs nécessaires à search et concorde."""

    def __init__(self, titre, texte, source):
        self.titre = titre
        self.texte = texte
        self.auteur = "Auteur test"
        self.url = ""
        self.type = source

    def getType(self):
        return self.type


class TestRechercheEtConcordancier(unittest.TestCase):
    def setUp(self):
        # Isoler le singleton sans modifier une éventuelle instance existante.
        singleton = patch.object(Corpus, "_instance", None)
        singleton.start()
        self.addCleanup(singleton.stop)

        self.corpus = Corpus("Corpus de test")
        # On prépare directement les données : add et les auteurs ne sont pas
        # les méthodes testées ici.
        self.corpus.documents = {
            0: DocumentFictif("Chat A", "cat cat gentle friend.", "reddit"),
            1: DocumentFictif("Chat B", "CAT little friend bobcat.", "reddit"),
            2: DocumentFictif("Oiseau A", "bird bird scientific study.", "arxiv"),
            3: DocumentFictif("Oiseau B", "bird tracking motion.", "arxiv"),
            4: DocumentFictif("Oiseau C", "bird.", "reddit"),
        }
        self.moteur = SearchEngine(self.corpus)

    # Tests individuels de SearchEngine.search
    def test_search_scores_positifs_et_tries(self):
        resultats = self.moteur.search("cat", n=20)

        self.assertEqual(len(resultats), 2)
        self.assertTrue((resultats["score"] > 0).all())
        self.assertTrue(resultats["score"].is_monotonic_decreasing)
        self.assertEqual(set(resultats["titre"]), {"Chat A", "Chat B"})

    def test_search_limite_de_resultats(self):
        resultats = self.moteur.search("cat", n=1)

        self.assertEqual(len(resultats), 1)
        self.assertEqual(
            resultats.iloc[0]["titre"],
            self.moteur.search("cat", n=20).iloc[0]["titre"],
        )

    def test_search_requete_inconnue_ou_vide(self):
        for requete in ("xyzabc", ""):
            with self.subTest(requete=requete):
                self.assertTrue(self.moteur.search(requete).empty)

    def test_search_source_sans_correspondance(self):
        resultats = self.moteur.search("cat", n=20, source="arxiv")

        self.assertTrue(resultats.empty)

    def test_search_filtre_avant_la_limite(self):
        # Le meilleur résultat global est Reddit ; il ne doit pas empêcher
        # de trouver un résultat arXiv lorsque le filtre est actif.
        global_ = self.moteur.search("bird", n=1)
        self.assertEqual(global_.iloc[0]["source"], "reddit")

        resultats = self.moteur.search("bird", n=1, source="arxiv")
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats.iloc[0]["source"], "arxiv")
        self.assertGreater(resultats.iloc[0]["score"], 0)

    # Tests individuels de Corpus.concorde
    def test_concorde_occurrences_et_documents(self):
        resultats = self.corpus.concorde("cat")

        # Deux occurrences dans Chat A, une dans Chat B.
        # CAT est reconnu, mais bobcat n'est pas compté.
        self.assertEqual(len(resultats), 3)
        self.assertEqual(resultats["id_document"].nunique(), 2)
        self.assertEqual(
            resultats.groupby("titre").size().to_dict(),
            {"Chat A": 2, "Chat B": 1},
        )

    def test_concorde_filtre_source(self):
        reddit = self.corpus.concorde("cat", source="reddit")
        arxiv = self.corpus.concorde("cat", source="arxiv")

        self.assertEqual(len(reddit), 3)
        self.assertTrue((reddit["source"] == "reddit").all())
        self.assertTrue(arxiv.empty)

    def test_concorde_taille_du_contexte(self):
        resultats = self.corpus.concorde("cat", taille_contexte=4)

        self.assertEqual(len(resultats), 3)
        for colonne in ("contexte gauche", "contexte droit"):
            with self.subTest(colonne=colonne):
                self.assertTrue((resultats[colonne].str.len() <= 4).all())


if __name__ == "__main__":
    unittest.main(verbosity=2)
