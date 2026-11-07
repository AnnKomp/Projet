# Projet — Moteur de recherche

## Version 1

Cette version permet de :

- collecter des textes sur Reddit et arXiv ;
- organiser les documents et les auteurs avec des classes Python ;
- filtrer les textes de moins de 100 caractères lors de la collecte ;
- sauvegarder et recharger le corpus ;
- afficher les documents par titre et par date ;
- compter les mots et les phrases ;
- consulter le nombre de documents et la taille moyenne des textes d’un auteur.

## Version 2

Cette version ajoute :

- la recherche de passages par expressions régulières (`search`, `concorde`) ;
- le nettoyage des textes et les statistiques du corpus (`stats`) ;
- la construction manuelle du vocabulaire et de la matrice Documents × Mots (TF) ;
- la pondération TF-IDF et la matrice creuse correspondante ;
- le classement des documents par similarité cosinus avec la requête.

## Version 3

Cette version ajoute :

- une interface graphique en notebook (ipywidgets) : recherche, filtre par
  source, concordancier, statistiques, évolution temporelle d'un mot,
  comparaison des deux sources ;
- une application web Streamlit (`app.py`) reprenant les mêmes fonctions;
- une barre de progression (tqdm) pendant la construction de la matrice.

Lancer l'application web :

```bash
python -m streamlit run app.py
```

## Installation

Version cible : Python 3.13.

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

## Utilisation

Ouvrir les notebooks dans un environnement prenant en charge Jupyter,
avec le dossier du projet comme dossier de travail. Sélectionner
l’environnement Python dans lequel les dépendances ont été installées,
puis exécuter les cellules dans l’ordre.

### Quel notebook choisir ?

| Besoin                                                              | Notebook à ouvrir |
| ------------------------------------------------------------------- | ----------------- |
| Collecter de nouveaux documents sur Reddit et arXiv                 | `v1.ipynb`        |
| Construire, filtrer et sauvegarder le corpus                        | `v1.ipynb`        |
| Vérifier la gestion des documents, des auteurs et la sauvegarde     | `v1.ipynb`        |
| Tester la recherche, le concordancier et les statistiques           | `v2.ipynb`        |
| Tester le classement des résultats par TF-IDF et similarité cosinus | `v2.ipynb`        |

Les deux notebooks sont complémentaires : `v1.ipynb` présente la
préparation du corpus et les vérifications du projet ; `v2.ipynb`
propose un parcours plus court consacré à l’exploitation du corpus
et au moteur de recherche.

### 1. Préparer ou vérifier le corpus avec `v1.ipynb`

Ce notebook permet de choisir entre deux modes :

- `1` : charger le corpus existant depuis `corpus_objets.csv`,
  sans appeler les API ;
- `2` : collecter de nouveaux documents sur Reddit et arXiv,
  filtrer les textes de moins de 100 caractères, construire les
  objets du corpus et sauvegarder les données.

Utiliser le mode `2` si aucun corpus sauvegardé n’est disponible
ou pour renouveler les données. La collecte nécessite une connexion
Internet et une configuration Reddit.

Le notebook contient également des affichages et des vérifications :
tri des documents, comptage des mots et des phrases, consultation
des auteurs, sauvegarde et rechargement du corpus. Il se termine
par de premiers exemples de recherche.

Pour créer les fichiers nécessaires à la suite du projet, exécuter
toutes les cellules du parcours de collecte, jusqu’à la sauvegarde
de `corpus_objets.csv`.

### 2. Explorer les données avec `v2.ipynb`

Ce notebook charge directement `corpus_objets.csv`, puis présente :

- la recherche de passages par expressions régulières ;
- le concordancier, qui affiche un terme dans son contexte ;
- les statistiques du corpus ;
- la construction du moteur de recherche et la taille de sa matrice TF-IDF ;
- des exemples de classement des documents et de requêtes de test.

Utiliser ce notebook pour tester ou présenter les fonctions de recherche
sans relancer la collecte.

Il nécessite un fichier `corpus_objets.csv` existant et les dépendances
du projet installées. Si ce fichier est déjà fourni ou a été créé lors
d’une exécution précédente, il est possible d’ouvrir directement
`v2.ipynb` : il n’est pas nécessaire de relancer `v1.ipynb`.

### Utiliser l’interface graphique : `interface.ipynb`

Ce notebook permet d’utiliser les fonctionnalités du moteur au moyen
d’une interface graphique.

Il charge lui-même le fichier `corpus_objets.csv` et initialise le
moteur de recherche. Il n’est donc pas nécessaire d’exécuter
`v1.ipynb` ou `v2.ipynb` avant chaque utilisation.

Pour le lancer :

1. Ouvrir `interface.ipynb` avec le dossier du projet comme dossier
   de travail.
2. Sélectionner l’environnement Python du projet.
3. Exécuter les cellules dans l’ordre, depuis le début.

Le fichier `corpus_objets.csv` doit être présent dans le dossier
du projet.

Si ce fichier n’est pas disponible, exécuter d’abord `v1.ipynb`
en choisissant le mode `2` pour collecter les données, puis poursuivre
jusqu’à la sauvegarde du corpus. Cette étape nécessite une connexion
Internet et une configuration Reddit.

`v2.ipynb` constitue une démonstration des fonctions de recherche
par appels de méthodes; son exécution n’est pas un prérequis
pour utiliser l’interface.

## Configuration Reddit

Pour une nouvelle collecte :

1. Copier `praw.ini.example` sous le nom `praw.ini`.
2. Renseigner ses propres identifiants Reddit.
3. Conserver le nom de section `[projet]`.

Ne pas publier ni inclure `praw.ini` dans une archive partagée.

## Données

- `corpus.csv` : tableau des textes et de leurs sources,
  sauvegardé après filtrage.
- `corpus_objets.csv` : documents avec leurs métadonnées,
  utilisé pour le chargement du corpus.

Les fichiers utilisent une tabulation comme séparateur.

## Organisation du code

- `collecte.py` : acquisition des données sur Reddit et arXiv.
- `classes/Document.py` : documents et classes filles Reddit/arXiv.
- `classes/Author.py` : gestion des auteurs.
- `classes/Corpus.py` : gestion, sauvegarde et exploration du corpus.
- `factories/DocumentFactory.py` : création des documents selon leur source.
- `classes/SearchEngine.py` : moteur de recherche
  (vocabulaire, TF, TF-IDF et similarité cosinus).
- `v1.ipynb` : préparation du corpus, collecte ou chargement des données,
  sauvegarde et vérifications du projet.
- `v2.ipynb` : chargement du corpus sauvegardé et démonstration
  des fonctions de recherche, du concordancier et des statistiques.
- `interface.ipynb` : interface graphique du moteur dans un notebook.
- `app.py` : application web Streamlit.
