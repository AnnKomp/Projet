class Document:
    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte        
        self.type = "document"

    def afficher(self):
        print("Titre :", self.titre)
        print("Auteur :", self.auteur)
        print("Date :", self.date)
        print("URL :", self.url)
        print("Texte :", self.texte)

    def __str__(self):
        return self.titre
    
class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nb_commentaires):
        super().__init__(titre, auteur, date, url, texte)
        self.type = "reddit"
        self.nb_commentaires = nb_commentaires

    def get_nb_commentaires(self):
        return self.nb_commentaires

    def set_nb_commentaires(self, nombre):
        self.nb_commentaires = nombre

    def getType(self):
        return self.type

    def __str__(self):
        return f"[Reddit] {self.titre} ({self.nb_commentaires} commentaires)"


class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, coauteurs):
        super().__init__(titre, auteur, date, url, texte)
        self.type = "arxiv"
        self.coauteurs = list(coauteurs)

    def get_coauteurs(self):
        return self.coauteurs.copy()

    def set_coauteurs(self, coauteurs):
        self.coauteurs = list(coauteurs)

    def getType(self):
        return self.type

    def __str__(self):
        return f"[arXiv] {self.titre}"