from datetime import datetime, timezone
import ssl
import urllib.parse
import urllib.request

import certifi
import xmltodict


def collecter_documents(
    reddit,
    theme_reddit="Cats",
    theme_arxiv="animal",
    taille_reddit=100,
    taille_arxiv=100,
):
    """Récupérer les textes et leurs métadonnées depuis les deux sources."""
    docs = []
    donnees_documents = []

    # Collecte Reddit.
    posts = list(
        reddit.subreddit(theme_reddit).hot(limit=taille_reddit)
    )

    nb_reddit = 0

    for post in posts:
        texte = (post.selftext or "").replace("\n", " ").strip()

        if not texte:
            continue

        docs.append(texte)
        nb_reddit += 1

        donnees_documents.append({
            "source": "reddit",
            "titre": post.title,
            "auteur": (
                str(post.author)
                if post.author is not None
                else "[deleted]"
            ),
            "date": datetime.fromtimestamp(
                post.created_utc, tz=timezone.utc
            ).isoformat(),
            "url": "https://www.reddit.com" + post.permalink,
            "texte": texte,
            "nb_commentaires": post.num_comments,
        })

    if posts:
        print("\nChamps Reddit utilisés :")
        print(
            "title, author, created_utc, permalink, "
            "selftext, num_comments"
        )
        print("Exemple de titre :", posts[0].title)

    # Collecte arXiv.
    parametres = urllib.parse.urlencode({
        "search_query": "all:" + theme_arxiv,
        "start": 0,
        "max_results": taille_arxiv,
    })

    url = "https://export.arxiv.org/api/query?" + parametres
    context = ssl.create_default_context(cafile=certifi.where())

    with urllib.request.urlopen(
        url, context=context, timeout=60
    ) as reponse:
        xml_data = reponse.read().decode("utf-8")

    resultats = xmltodict.parse(xml_data)
    entries = resultats["feed"].get("entry") or []

    if isinstance(entries, dict):
        entries = [entries]

    nb_arxiv = 0

    for article in entries:
        texte = (article.get("summary") or "").replace("\n", " ").strip()

        if not texte:
            continue

        auteurs = article.get("author") or []

        if isinstance(auteurs, dict):
            auteurs = [auteurs]

        noms_auteurs = [auteur["name"] for auteur in auteurs]

        docs.append(texte)
        nb_arxiv += 1

        donnees_documents.append({
            "source": "arxiv",
            "titre": article["title"].replace("\n", " ").strip(),
            "auteur": (
                noms_auteurs[0]
                if noms_auteurs
                else "Auteur inconnu"
            ),
            "date": datetime.fromisoformat(
                article["published"].replace("Z", "+00:00")
            ).isoformat(),
            "url": article["id"],
            "texte": texte,
            "coauteurs": noms_auteurs,
        })

    if entries:
        print("\nChamps arXiv :", list(entries[0].keys()))

    print("\nDocuments Reddit :", nb_reddit)
    print("Documents arXiv :", nb_arxiv)
    print("Total avant filtrage :", len(docs))

    return docs, donnees_documents, nb_reddit, nb_arxiv