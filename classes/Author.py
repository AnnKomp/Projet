class Author:
    def __init__(self, name):
        self.name = name
        self.nb_docs = 0
        self.production = {}

    def add(self, id_document, document):
        self.production[id_document] = document
        self.nb_docs = len(self.production)

    def __str__(self):
        return f"{self.name} : {self.nb_docs} document(s)"