# Othello - Projet L2

## Auteur
* Haison HONG & Antoine Dis

## Description
Ce projet est une implémentation du jeu de stratégie classique Othello, développé en Python avec une interface graphique utilisant la bibliothèque Pygame.

## Fonctionnalités
- **Interface graphique complète** (Pygame) avec animations, affichage des pions, score et menus.
- **Modes de jeu** :
  - Joueur contre Joueur (JvJ)
  - Joueur contre IA (JvIA)
  - IA contre IA (IAvIA)
- **Niveaux de difficulté de l'IA** :
  - Facile : Parité simple.
  - Moyen : Recherche de profondeur 3 avec évaluation des positions, contrôle des coins et parité.
  - Difficile : Recherche algorithmique (Min-Max avec élagage Alpha-Beta) de profondeur 5 combinant des heuristiques avancées (mobilité, stabilité, évaluation dynamique).

## Exécution
Pour lancer le jeu, placez-vous à la racine du projet et exécutez le script principal :
```bash
python Othello_projet.py
```
