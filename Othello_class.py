"""
Othello — Classe Plateau
Auteur : Haison HONG

Ce fichier contient la classe Plateau pour le jeu Othello.
On gere le plateau 8x8, les regles du jeu, les coups possibles etc.

0 = case vide, 1 = noir, 2 = blanc
"""

import copy


class Plateau:
    """Classe qui represente le plateau d'Othello."""

    # Les 8 directions possibles pour vérifier les captures :
    # haut, bas, gauche, droite et les 4 diagonales
    DIRECTIONS = [
        (-1, 0),   # haut
        (1, 0),    # bas
        (0, -1),   # gauche
        (0, 1),    # droite
        (-1, -1),  # diagonale haut-gauche
        (-1, 1),   # diagonale haut-droite
        (1, -1),   # diagonale bas-gauche
        (1, 1),    # diagonale bas-droite
    ]

    def __init__(self):
        """On cree le plateau 8x8 et on place les 4 pions du debut."""
        # Création d'un plateau 8x8 vide
        self.grille = [[0 for _ in range(8)] for _ in range(8)]

        # Placement des 4 pions centraux (position standard d'Othello)
        self.grille[3][3] = 2  # blanc
        self.grille[3][4] = 1  # noir
        self.grille[4][3] = 1  # noir
        self.grille[4][4] = 2  # blanc

        # Le joueur noir commence toujours
        self.joueur_courant = 1

    def copier(self):
        """Fait une copie du plateau pour que l'IA puisse tester des coups."""
        nouveau = Plateau()
        # Copie profonde de la grille pour éviter les références partagées
        nouveau.grille = copy.deepcopy(self.grille)
        nouveau.joueur_courant = self.joueur_courant
        return nouveau

    def adversaire(self, joueur):
        """Renvoie l'adversaire du joueur (si 1 alors 2, si 2 alors 1)."""
        return 2 if joueur == 1 else 1

    def est_dans_grille(self, ligne, col):
        """Verifie si la position est bien dans le plateau 8x8."""
        return 0 <= ligne < 8 and 0 <= col < 8

    def pions_a_retourner(self, ligne, col, joueur):
        """Regarde quels pions on peut retourner si on joue a cette position.
        On cherche dans les 8 directions les pions adverses a capturer.
        Renvoie la liste des pions retournes (vide si coup pas valide).
        """
        # On ne peut jouer que sur une case vide
        if self.grille[ligne][col] != 0:
            return []

        adversaire = self.adversaire(joueur)
        pions = []

        # Exploration dans les 8 directions
        for dl, dc in self.DIRECTIONS:
            pions_direction = []
            l, c = ligne + dl, col + dc

            # Avancer dans la direction tant qu'on trouve des pions adverses
            while self.est_dans_grille(l, c) and self.grille[l][c] == adversaire:
                pions_direction.append((l, c))
                l += dl
                c += dc

            # S'il y a des pions adverses ET qu'ils sont suivis d'un pion allié,
            # alors tous ces pions adverses sont capturés
            if pions_direction and self.est_dans_grille(l, c) and self.grille[l][c] == joueur:
                pions.extend(pions_direction)

        return pions

    def est_coup_valide(self, ligne, col, joueur):
        """Verifie si le joueur peut jouer a cette case.
        Il faut que ce soit dans la grille, que la case soit vide,
        et qu'on retourne au moins un pion.
        """
        if not self.est_dans_grille(ligne, col):
            return False
        if self.grille[ligne][col] != 0:
            return False
        # Le coup est valide s'il retourne au moins un pion
        return len(self.pions_a_retourner(ligne, col, joueur)) > 0

    def coups_valides(self, joueur):
        """Renvoie la liste de tous les coups possibles pour le joueur.
        On parcourt tout le plateau et on teste chaque case.
        """
        coups = []
        for ligne in range(8):
            for col in range(8):
                if self.est_coup_valide(ligne, col, joueur):
                    coups.append((ligne, col))
        return coups

    def jouer_coup(self, ligne, col, joueur):
        """Joue le coup : pose le pion et retourne les pions captures.
        Renvoie la liste des pions retournes.
        """
        pions = self.pions_a_retourner(ligne, col, joueur)

        # Si aucun pion à retourner, le coup n'est pas valide
        if not pions:
            return []

        # Poser le pion du joueur sur la case
        self.grille[ligne][col] = joueur

        # Retourner tous les pions capturés
        for l, c in pions:
            self.grille[l][c] = joueur

        return pions

    def est_fin_de_partie(self):
        """Verifie si la partie est finie (quand personne ne peut jouer)."""
        return len(self.coups_valides(1)) == 0 and len(self.coups_valides(2)) == 0

    def compter_pions(self):
        """Compte les pions noirs et blancs sur le plateau."""
        noirs = 0
        blancs = 0
        for ligne in range(8):
            for col in range(8):
                if self.grille[ligne][col] == 1:
                    noirs += 1
                elif self.grille[ligne][col] == 2:
                    blancs += 1
        return noirs, blancs

    def gagnant(self):
        """Renvoie qui a gagne : 1 pour noir, 2 pour blanc, None si egalite."""
        noirs, blancs = self.compter_pions()
        if noirs > blancs:
            return 1
        elif blancs > noirs:
            return 2
        else:
            return None  # Égalité

    def cases_vides(self):
        """Compte le nombre de cases vides sur le plateau."""
        count = 0
        for ligne in range(8):
            for col in range(8):
                if self.grille[ligne][col] == 0:
                    count += 1
        return count

    def __str__(self):
        """Affiche le plateau en texte pour le debug."""
        symboles = {0: '.', 1: 'N', 2: 'B'}
        lignes = []
        lignes.append("  0 1 2 3 4 5 6 7")
        for i in range(8):
            ligne = f"{i} " + " ".join(symboles[self.grille[i][j]] for j in range(8))
            lignes.append(ligne)
        return "\n".join(lignes)