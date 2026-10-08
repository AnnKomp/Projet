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

Le classement des résultats de recherche sera ajouté dans la version 2.

## Installation

Version cible : Python 3.13.

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

## Utilisation

Ouvrir `Untitled-1.ipynb` dans un environnement prenant en charge
les notebooks Jupyter, avec le dossier du projet comme dossier de travail.

Exécuter les cellules dans l’ordre, puis choisir :
- `1` pour charger le corpus sauvegardé, sans appeler les API ;
- `2` pour collecter de nouveaux documents sur Reddit et arXiv.

La collecte nécessite une connexion Internet et une configuration Reddit.

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

- `collecte.py` : acquisition des données.
- `classes/Document.py` : documents et classes filles Reddit/arXiv.
- `classes/Author.py` : gestion des auteurs.
- `classes/Corpus.py` : gestion et sauvegarde du corpus.
- `factories/DocumentFactory.py` : création des documents selon leur source.
- `Untitled-1.ipynb` : parcours d’utilisation et vérifications.