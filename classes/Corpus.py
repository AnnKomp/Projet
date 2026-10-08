import json
import pandas as pd

from .Author import Author
from .Document import Document, RedditDocument, ArxivDocument

class Corpus:
    _instance = None

    def __new__(cls, nom):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, nom):
        if getattr(self, "_initialise", False):
            return

        self.nom = nom
        self.documents = {}
        self.id_document = 0
        self.authors = {}

        self._initialise = True

    def add(self, document):
        # Enregistrer le document avec un identifiant unique.
        identifiant = self.id_document
        self.documents[identifiant] = document

        # Créer l'auteur seulement s'il n'existe pas encore.
        if document.auteur not in self.authors:
            self.authors[document.auteur] = Author(document.auteur)

        # Associer le document à son auteur.
        self.authors[document.auteur].add(identifiant, document)

        self.id_document += 1
        
    def save(self, chemin):
        lignes = []

        for document in self.documents.values():
            lignes.append({
                "titre": document.titre,
                "auteur": document.auteur,
                "date": document.date,
                "url": document.url,
                "texte": document.texte,
                "type": document.type,
                "nb_commentaires": (
                    document.nb_commentaires
                    if isinstance(document, RedditDocument)
                    else ""
                ),
                "coauteurs": (
                    json.dumps(document.coauteurs, ensure_ascii=False)
                    if isinstance(document, ArxivDocument)
                    else "[]"
                )
            })

        colonnes = [
            "titre", "auteur", "date", "url", "texte",
            "type", "nb_commentaires", "coauteurs"
        ]

        df = pd.DataFrame(lignes, columns=colonnes)
        df.to_csv(chemin, sep="\t", index=False, encoding="utf-8")

    def load(self, chemin):
        df = pd.read_csv(
            chemin,
            sep="\t",
            encoding="utf-8",
            dtype=str,
            keep_default_na=False
        )

        self.clear()

        for _, ligne in df.iterrows():
            attributs = {
                "titre": ligne["titre"],
                "auteur": ligne["auteur"],
                "date": ligne["date"],
                "url": ligne["url"],
                "texte": ligne["texte"]
            }

            if ligne["type"] == "reddit":
                document = RedditDocument(
                    **attributs,
                    nb_commentaires=int(ligne["nb_commentaires"])
                )
            elif ligne["type"] == "arxiv":
                document = ArxivDocument(
                    **attributs,
                    coauteurs=json.loads(ligne["coauteurs"])
                )
            else:
                document = Document(**attributs)

            self.add(document)
            
    def clear(self):
        """Vider les documents et les auteurs, et réinitialiser le compteur."""
        self.documents.clear()
        self.authors.clear()
        self.id_document = 0

    def __repr__(self):
        return (
            f"Corpus '{self.nom}' : "
            f"{len(self.documents)} document(s), "
            f"{len(self.authors)} auteur(s)"
        )
    
    def afficher_par_titre(self, n=5):
        documents_tries = sorted(
            self.documents.values(),
            key=lambda doc: doc.titre.lower()
        )

        for document in documents_tries[:n]:
            print(document)

    def afficher_par_date(self, n=5):
        documents_tries = sorted(
            self.documents.values(),
            key=lambda doc: doc.date,
            reverse=True
        )

        for document in documents_tries[:n]:
            print(f"{document.date} — {document}")