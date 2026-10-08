from classes.Document import RedditDocument, ArxivDocument


class DocumentFactory:
    @staticmethod
    def create(source, **attributs):
        if source == "reddit":
            return RedditDocument(**attributs)

        if source == "arxiv":
            return ArxivDocument(**attributs)

        raise ValueError(f"Source inconnue : {source}")