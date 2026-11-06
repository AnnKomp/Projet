import json
import pandas as pd
import re

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
        
        self._chaine_unique = None
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
        self._chaine_unique = None        
        
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
        self._chaine_unique = None

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
        
    def nettoyer_texte(self, texte):
        texte = texte.lower()                        # minuscules
        texte = texte.replace("\n", " ")             # sauts de ligne -> espace
        texte = re.sub(r"[^\w\s]", " ", texte)       # ponctuation -> espace
        texte = re.sub(r"\d+", " ", texte)           # chiffres -> espace
        texte = re.sub(r"\s+", " ", texte).strip()   # espaces multiples -> un seul
        return texte
        
    
    def construire_freq(self):
        tf = {}   # nombre total d'occurrences
        df = {}   # nombre de documents contenant le mot

        for doc in self.documents.values():
            mots = self.nettoyer_texte(doc.texte).split()
            for mot in mots:
                tf[mot] = tf.get(mot, 0) + 1
            for mot in set(mots):          # chaque mot compté une fois par document
                df[mot] = df.get(mot, 0) + 1

        self.freq = pd.DataFrame({
            "mot": list(tf),
            "term frequency": list(tf.values()),
            "document frequency": [df[m] for m in tf],
        }).sort_values("mot").reset_index(drop=True)
        return self.freq
    
    def stats(self, n=10):
        freq = self.construire_freq()
        print(f"Nombre de mots différents : {len(freq)}")
        print(f"\n{n} mots les plus fréquents :")
        top = freq.sort_values("term frequency", ascending=False).head(n)
        print(top.to_string(index=False))
        
        
    def _construire_chaine(self):
    # Construite une seule fois, puis réutilisée
        if self._chaine_unique is None:
            self._chaine_unique = " ".join(
                doc.texte for doc in self.documents.values()
            )
        return self._chaine_unique
    
   
    def search(self, mot_cle):
        chaine = self._construire_chaine()
        motif = r"[^.]*\b" + re.escape(mot_cle) + r"\b[^.]*\."
        return re.findall(motif, chaine, flags=re.IGNORECASE)
    
    def concorde(self, expression, taille_contexte=30):
        chaine = self._construire_chaine()
        motif = r"\b" + re.escape(expression) + r"\b"

        lignes = []
        for m in re.finditer(motif, chaine, flags=re.IGNORECASE):
            debut, fin = m.start(), m.end()
            gauche = chaine[max(0, debut - taille_contexte):debut]
            droite = chaine[fin:fin + taille_contexte]
            lignes.append([gauche, m.group(), droite])

        return pd.DataFrame(
            lignes,
            columns=["contexte gauche", "motif trouvé", "contexte droit"],
        )

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
            
    