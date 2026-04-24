"""
Haison HONG
Othello — Interface graphique Pygame

Ce fichier c'est l'interface du jeu Othello avec Pygame.
On affiche le plateau, on gere les clics et on fait jouer l'IA.

Il y a 3 modes : Joueur vs Joueur, Joueur vs IA, IA vs IA.
"""

import pygame
import sys
import time
from Othello_class import Plateau
from Othello_ia import meilleur_coup


#  INITIALISATION DE PYGAME

pygame.init()


#  CONSTANTES D'AFFICHAGE

# Dimensions de la fenêtre
LARGEUR_FENETRE = 800       # largeur totale (plateau + panneau latéral)
HAUTEUR_FENETRE = 650       # hauteur totale
TAILLE_CASE = 60            # taille d'une case du plateau en pixels
MARGE_PLATEAU_X = 40        # décalage horizontal du plateau
MARGE_PLATEAU_Y = 60        # décalage vertical du plateau
RAYON_PION = 24             # rayon des pions dessinés
TAILLE_PLATEAU = 8 * TAILLE_CASE  # 480 pixels

# Panneau latéral (à droite du plateau)
PANNEAU_X = MARGE_PLATEAU_X + TAILLE_PLATEAU + 20  # position X du panneau


#  COULEURS (tuples RGB)

NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
VERT_PLATEAU = (0, 150, 0)          # vert du plateau
VERT_FONCE = (0, 100, 0)            # lignes de la grille
VERT_CLAIR = (100, 255, 100)        # coups valides
FOND_FENETRE = (30, 30, 30)         # fond sombre
GRIS = (128, 128, 128)
GRIS_CLAIR = (200, 200, 200)
BLEU = (0, 0, 200)                  # boutons
BLEU_SURVOL = (50, 50, 255)         # boutons au survol
ROUGE = (200, 0, 0)                 # bouton quitter
ROUGE_SURVOL = (255, 50, 50)
VERT_BOUTON = (0, 180, 0)           # bouton jouer
VERT_BOUTON_SURVOL = (0, 220, 0)
JAUNE = (255, 255, 0)               # dernier coup


#  POLICES DE TEXTE


# On utilise la police par défaut de Pygame 
POLICE_TITRE = pygame.font.Font(None, 48)
POLICE_SOUS_TITRE = pygame.font.Font(None, 30)
POLICE_BOUTON = pygame.font.Font(None, 26)
POLICE_INFO = pygame.font.Font(None, 24)
POLICE_SCORE = pygame.font.Font(None, 36)
POLICE_PETIT = pygame.font.Font(None, 20)

#  CRÉATION DE LA FENÊTRE

ecran = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
pygame.display.set_caption("Othello")
horloge = pygame.time.Clock()



#  FONCTIONS UTILITAIRES DE DESSIN

def dessiner_texte(texte, police, couleur, x, y, centrer=True):
    """Affiche du texte a l'ecran a la position donnee."""
    surface = police.render(texte, True, couleur)
    if centrer:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))
    ecran.blit(surface, rect)


def dessiner_bouton(texte, x, y, largeur, hauteur, couleur_fond,
                    couleur_survol, couleur_texte=BLANC):
    """Dessine un bouton rectangle. Change de couleur quand la souris est dessus.
    Renvoie True si la souris est sur le bouton.
    """
    # Récupérer la position de la souris
    souris_x, souris_y = pygame.mouse.get_pos()

    # Vérifier si la souris est sur le bouton
    survol = (x <= souris_x <= x + largeur and y <= souris_y <= y + hauteur)

    # Choisir la couleur selon le survol
    couleur = couleur_survol if survol else couleur_fond

    # Dessiner le rectangle du bouton (simple, sans coins arrondis)
    rect = pygame.Rect(x, y, largeur, hauteur)
    pygame.draw.rect(ecran, couleur, rect)
    # Bordure noire
    pygame.draw.rect(ecran, NOIR, rect, 2)

    # Dessiner le texte centré dans le bouton
    dessiner_texte(texte, POLICE_BOUTON, couleur_texte,
                   x + largeur // 2, y + hauteur // 2)

    return survol


def case_depuis_souris(souris_x, souris_y):
    """Transforme la position de la souris en case du plateau (ligne, col).
    Renvoie None si le clic est en dehors du plateau.
    """
    # Vérifier que le clic est dans la zone du plateau
    if (souris_x < MARGE_PLATEAU_X or
            souris_x > MARGE_PLATEAU_X + TAILLE_PLATEAU):
        return None
    if (souris_y < MARGE_PLATEAU_Y or
            souris_y > MARGE_PLATEAU_Y + TAILLE_PLATEAU):
        return None

    # Calcul de la case correspondante
    col = (souris_x - MARGE_PLATEAU_X) // TAILLE_CASE
    ligne = (souris_y - MARGE_PLATEAU_Y) // TAILLE_CASE

    # Vérification des limites
    if 0 <= ligne < 8 and 0 <= col < 8:
        return (ligne, col)
    return None



#  DESSIN DU PLATEAU DE JEU


def dessiner_plateau(plateau, coups_possibles, dernier_coup=None):
    """Dessine le plateau avec les pions, la grille et les coups possibles."""
    # Fond vert du plateau
    pygame.draw.rect(ecran, VERT_PLATEAU,
                     (MARGE_PLATEAU_X, MARGE_PLATEAU_Y,
                      TAILLE_PLATEAU, TAILLE_PLATEAU))

    # Dessiner les lignes de la grille (horizontales et verticales)
    for i in range(9):
        # Lignes horizontales
        y = MARGE_PLATEAU_Y + i * TAILLE_CASE
        pygame.draw.line(ecran, NOIR,
                         (MARGE_PLATEAU_X, y),
                         (MARGE_PLATEAU_X + TAILLE_PLATEAU, y), 1)
        # Lignes verticales
        x = MARGE_PLATEAU_X + i * TAILLE_CASE
        pygame.draw.line(ecran, NOIR,
                         (x, MARGE_PLATEAU_Y),
                         (x, MARGE_PLATEAU_Y + TAILLE_PLATEAU), 1)

    # Dessiner les coups valides (petits cercles verts)
    for ligne, col in coups_possibles:
        cx = MARGE_PLATEAU_X + col * TAILLE_CASE + TAILLE_CASE // 2
        cy = MARGE_PLATEAU_Y + ligne * TAILLE_CASE + TAILLE_CASE // 2
        # Petit cercle pour montrer les coups jouables
        pygame.draw.circle(ecran, VERT_CLAIR, (cx, cy), 8)

    # Dessiner les pions sur le plateau
    for ligne in range(8):
        for col in range(8):
            if plateau.grille[ligne][col] != 0:
                # Calculer le centre de la case en pixels
                cx = MARGE_PLATEAU_X + col * TAILLE_CASE + TAILLE_CASE // 2
                cy = MARGE_PLATEAU_Y + ligne * TAILLE_CASE + TAILLE_CASE // 2

                # Couleur du pion (noir ou blanc)
                if plateau.grille[ligne][col] == 1:
                    couleur_pion = NOIR
                else:
                    couleur_pion = BLANC

                # Dessiner le pion
                pygame.draw.circle(ecran, couleur_pion, (cx, cy), RAYON_PION)

    # Mettre en évidence le dernier coup joué avec un contour jaune
    if dernier_coup is not None:
        l, c = dernier_coup
        rect_case = pygame.Rect(
            MARGE_PLATEAU_X + c * TAILLE_CASE,
            MARGE_PLATEAU_Y + l * TAILLE_CASE,
            TAILLE_CASE, TAILLE_CASE
        )
        pygame.draw.rect(ecran, JAUNE, rect_case, 3)

    # Étiquettes des colonnes (A-H) et des lignes (1-8)
    for i in range(8):
        # Colonnes en haut
        lettre = chr(65 + i)  # A, B, C, ..., H
        x = MARGE_PLATEAU_X + i * TAILLE_CASE + TAILLE_CASE // 2
        dessiner_texte(lettre, POLICE_PETIT, BLANC,
                       x, MARGE_PLATEAU_Y - 12)
        # Lignes à gauche
        y = MARGE_PLATEAU_Y + i * TAILLE_CASE + TAILLE_CASE // 2
        dessiner_texte(str(i + 1), POLICE_PETIT, BLANC,
                       MARGE_PLATEAU_X - 12, y)


def dessiner_panneau(plateau, joueur_courant, mode, difficulte,
                     difficulte_blanc='moyen', message=""):
    """Dessine le panneau a droite avec le score, le tour et un bouton rejouer."""
    # Compter les pions
    noirs, blancs = plateau.compter_pions()

    # Afficher le score en texte simple
    dessiner_texte("Score", POLICE_SOUS_TITRE, BLANC, PANNEAU_X + 70, 80)

    # Labels selon le mode
    if mode == 'pvp':
        label_noir = "Joueur 1"
        label_blanc = "Joueur 2"
    elif mode == 'iavia':
        label_noir = "IA Noir"
        label_blanc = "IA Blanc"
    else:
        label_noir = "Noir"
        label_blanc = "Blanc"

    # Score noir
    dessiner_texte(label_noir + " : " + str(noirs), POLICE_INFO, BLANC,
                   PANNEAU_X + 70, 120)
    # Score blanc
    dessiner_texte(label_blanc + " : " + str(blancs), POLICE_INFO, BLANC,
                   PANNEAU_X + 70, 150)

    # Tour actuel
    if joueur_courant == 1:
        texte_tour = "Tour : Noir"
    else:
        texte_tour = "Tour : Blanc"
    dessiner_texte(texte_tour, POLICE_INFO, BLANC, PANNEAU_X + 70, 190)

    # Mode de jeu
    noms_mode = {'pvp': 'JvJ', 'pvia': 'JvIA', 'iavia': 'IAvIA'}
    dessiner_texte("Mode : " + noms_mode.get(mode, mode),
                   POLICE_PETIT, GRIS_CLAIR, PANNEAU_X + 70, 225)

    # Difficulte
    noms_diff = {'facile': 'Facile', 'moyen': 'Moyen', 'difficile': 'Difficile'}
    if mode == 'pvia':
        dessiner_texte("Niveau : " + noms_diff.get(difficulte, difficulte),
                       POLICE_PETIT, GRIS_CLAIR, PANNEAU_X + 70, 245)
    elif mode == 'iavia':
        dessiner_texte("Noir : " + noms_diff.get(difficulte, difficulte),
                       POLICE_PETIT, GRIS_CLAIR, PANNEAU_X + 70, 245)
        dessiner_texte("Blanc : " + noms_diff.get(difficulte_blanc, difficulte_blanc),
                       POLICE_PETIT, GRIS_CLAIR, PANNEAU_X + 70, 265)

    # Bouton Rejouer
    survol_rejouer = dessiner_bouton("Rejouer", PANNEAU_X + 10, 300,
                                      130, 35, BLEU, BLEU_SURVOL)

    # Message en bas
    if message:
        dessiner_texte(message, POLICE_INFO, JAUNE,
                       MARGE_PLATEAU_X + TAILLE_PLATEAU // 2,
                       MARGE_PLATEAU_Y + TAILLE_PLATEAU + 25)

    return survol_rejouer




#  ÉCRAN : MENU PRINCIPAL


def afficher_menu():
    """Affiche le menu pour choisir le mode, la difficulte, et qui commence.
    Renvoie les choix du joueur.
    """
    # Valeurs par défaut
    mode = 'pvia'           # mode par défaut : joueur vs IA
    difficulte = 'moyen'        # difficulté unique (pvia) ou IA Noir (iavia)
    difficulte_blanc = 'moyen'  # difficulté IA Blanc (mode iavia uniquement)
    joueur_commence = True  # True = le joueur humain commence (noir)

    en_cours = True
    while en_cours:
        # Gérer les événements (fermeture de fenêtre, clics)
        clic = False
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                clic = True

        # ---- Dessiner le menu ----
        ecran.fill(FOND_FENETRE)

        # Titre du jeu
        dessiner_texte("OTHELLO", POLICE_TITRE, BLANC,
                       LARGEUR_FENETRE // 2, 50)

        # Sous-titre
        dessiner_texte("Projet L2 - Jeu de strategie", POLICE_PETIT, GRIS_CLAIR,
                       LARGEUR_FENETRE // 2, 85)

        # ---- Section : Mode de jeu ----
        dessiner_texte("Mode de jeu :", POLICE_SOUS_TITRE, BLANC,
                       LARGEUR_FENETRE // 2, 130)

        bouton_l = 150
        bouton_h = 40
        espacement = 15
        debut_x = (LARGEUR_FENETRE - 3 * bouton_l - 2 * espacement) // 2
        y_mode = 155

        # Bouton Joueur vs Joueur
        c_pvp = VERT_BOUTON if mode == 'pvp' else BLEU
        c_pvp_s = VERT_BOUTON_SURVOL if mode == 'pvp' else BLEU_SURVOL
        survol_pvp = dessiner_bouton("Joueur vs Joueur", debut_x, y_mode,
                                      bouton_l, bouton_h, c_pvp, c_pvp_s)
        if clic and survol_pvp:
            mode = 'pvp'

        # Bouton Joueur vs IA
        c_pvia = VERT_BOUTON if mode == 'pvia' else BLEU
        c_pvia_s = VERT_BOUTON_SURVOL if mode == 'pvia' else BLEU_SURVOL
        survol_pvia = dessiner_bouton("Joueur vs IA",
                                       debut_x + bouton_l + espacement, y_mode,
                                       bouton_l, bouton_h, c_pvia, c_pvia_s)
        if clic and survol_pvia:
            mode = 'pvia'

        # Bouton IA vs IA
        c_iavia = VERT_BOUTON if mode == 'iavia' else BLEU
        c_iavia_s = VERT_BOUTON_SURVOL if mode == 'iavia' else BLEU_SURVOL
        survol_iavia = dessiner_bouton("IA vs IA",
                                        debut_x + 2 * (bouton_l + espacement),
                                        y_mode,
                                        bouton_l, bouton_h, c_iavia, c_iavia_s)
        if clic and survol_iavia:
            mode = 'iavia'

        # ---- Section : Difficulté (seulement si IA impliquée) ----
        y_suivant = 230  # position Y pour la section suivante

        if mode == 'pvia':
            # Mode JvIA : un seul sélecteur de difficulté
            dessiner_texte("Difficulte :", POLICE_SOUS_TITRE, BLANC,
                           LARGEUR_FENETRE // 2, y_suivant)

            y_diff = y_suivant + 25

            # Couleurs selon la sélection actuelle
            couleurs_diff = {
                'facile': (VERT_BOUTON if difficulte == 'facile' else BLEU,
                           VERT_BOUTON_SURVOL if difficulte == 'facile' else BLEU_SURVOL),
                'moyen': (VERT_BOUTON if difficulte == 'moyen' else BLEU,
                          VERT_BOUTON_SURVOL if difficulte == 'moyen' else BLEU_SURVOL),
                'difficile': (VERT_BOUTON if difficulte == 'difficile' else BLEU,
                              VERT_BOUTON_SURVOL if difficulte == 'difficile' else BLEU_SURVOL),
            }

            # Bouton Facile
            survol_facile = dessiner_bouton("Facile", debut_x, y_diff,
                                            bouton_l, bouton_h,
                                            couleurs_diff['facile'][0],
                                            couleurs_diff['facile'][1])
            if clic and survol_facile:
                difficulte = 'facile'

            # Bouton Moyen
            survol_moyen = dessiner_bouton("Moyen", debut_x + bouton_l + espacement,
                                           y_diff, bouton_l, bouton_h,
                                           couleurs_diff['moyen'][0],
                                           couleurs_diff['moyen'][1])
            if clic and survol_moyen:
                difficulte = 'moyen'

            # Bouton Difficile
            survol_difficile = dessiner_bouton("Difficile",
                                               debut_x + 2 * (bouton_l + espacement),
                                               y_diff, bouton_l, bouton_h,
                                               couleurs_diff['difficile'][0],
                                               couleurs_diff['difficile'][1])
            if clic and survol_difficile:
                difficulte = 'difficile'

            y_suivant = y_diff + bouton_h + 30

        elif mode == 'iavia':
            # Mode IAvIA : deux sélecteurs de difficulté séparés

            # --- Difficulté IA Noir ---
            dessiner_texte("Niveau IA Noir :", POLICE_SOUS_TITRE, BLANC,
                           LARGEUR_FENETRE // 2, y_suivant)

            y_diff_noir = y_suivant + 25

            couleurs_noir = {
                'facile': (VERT_BOUTON if difficulte == 'facile' else BLEU,
                           VERT_BOUTON_SURVOL if difficulte == 'facile' else BLEU_SURVOL),
                'moyen': (VERT_BOUTON if difficulte == 'moyen' else BLEU,
                          VERT_BOUTON_SURVOL if difficulte == 'moyen' else BLEU_SURVOL),
                'difficile': (VERT_BOUTON if difficulte == 'difficile' else BLEU,
                              VERT_BOUTON_SURVOL if difficulte == 'difficile' else BLEU_SURVOL),
            }

            survol_n_f = dessiner_bouton("Facile", debut_x, y_diff_noir,
                                          bouton_l, bouton_h,
                                          couleurs_noir['facile'][0],
                                          couleurs_noir['facile'][1])
            if clic and survol_n_f:
                difficulte = 'facile'

            survol_n_m = dessiner_bouton("Moyen", debut_x + bouton_l + espacement,
                                          y_diff_noir, bouton_l, bouton_h,
                                          couleurs_noir['moyen'][0],
                                          couleurs_noir['moyen'][1])
            if clic and survol_n_m:
                difficulte = 'moyen'

            survol_n_d = dessiner_bouton("Difficile",
                                          debut_x + 2 * (bouton_l + espacement),
                                          y_diff_noir, bouton_l, bouton_h,
                                          couleurs_noir['difficile'][0],
                                          couleurs_noir['difficile'][1])
            if clic and survol_n_d:
                difficulte = 'difficile'

            # --- Difficulté IA Blanc ---
            y_label_blanc = y_diff_noir + bouton_h + 20
            dessiner_texte("Niveau IA Blanc :", POLICE_SOUS_TITRE, BLANC,
                           LARGEUR_FENETRE // 2, y_label_blanc)

            y_diff_blanc = y_label_blanc + 25

            couleurs_blanc = {
                'facile': (VERT_BOUTON if difficulte_blanc == 'facile' else BLEU,
                           VERT_BOUTON_SURVOL if difficulte_blanc == 'facile' else BLEU_SURVOL),
                'moyen': (VERT_BOUTON if difficulte_blanc == 'moyen' else BLEU,
                          VERT_BOUTON_SURVOL if difficulte_blanc == 'moyen' else BLEU_SURVOL),
                'difficile': (VERT_BOUTON if difficulte_blanc == 'difficile' else BLEU,
                              VERT_BOUTON_SURVOL if difficulte_blanc == 'difficile' else BLEU_SURVOL),
            }

            survol_b_f = dessiner_bouton("Facile", debut_x, y_diff_blanc,
                                          bouton_l, bouton_h,
                                          couleurs_blanc['facile'][0],
                                          couleurs_blanc['facile'][1])
            if clic and survol_b_f:
                difficulte_blanc = 'facile'

            survol_b_m = dessiner_bouton("Moyen", debut_x + bouton_l + espacement,
                                          y_diff_blanc, bouton_l, bouton_h,
                                          couleurs_blanc['moyen'][0],
                                          couleurs_blanc['moyen'][1])
            if clic and survol_b_m:
                difficulte_blanc = 'moyen'

            survol_b_d = dessiner_bouton("Difficile",
                                          debut_x + 2 * (bouton_l + espacement),
                                          y_diff_blanc, bouton_l, bouton_h,
                                          couleurs_blanc['difficile'][0],
                                          couleurs_blanc['difficile'][1])
            if clic and survol_b_d:
                difficulte_blanc = 'difficile'

            y_suivant = y_diff_blanc + bouton_h + 20

        else:
            # Mode PvP : pas de sélecteur de difficulté
            y_suivant = 230

        # ---- Section : Qui commence ? (seulement en mode JvIA) ----
        if mode == 'pvia':
            dessiner_texte("Qui commence ?", POLICE_SOUS_TITRE, BLANC,
                           LARGEUR_FENETRE // 2, y_suivant)

            bouton_choix_l = 180
            debut_choix_x = (LARGEUR_FENETRE - 2 * bouton_choix_l - espacement) // 2
            y_choix = y_suivant + 25

            # Bouton "Moi" (joueur commence)
            couleur_moi = VERT_BOUTON if joueur_commence else BLEU
            couleur_moi_s = VERT_BOUTON_SURVOL if joueur_commence else BLEU_SURVOL
            survol_moi = dessiner_bouton("Moi (Noir)", debut_choix_x, y_choix,
                                          bouton_choix_l, bouton_h,
                                          couleur_moi, couleur_moi_s)
            if clic and survol_moi:
                joueur_commence = True

            # Bouton "Ordinateur"
            couleur_ordi = VERT_BOUTON if not joueur_commence else BLEU
            couleur_ordi_s = VERT_BOUTON_SURVOL if not joueur_commence else BLEU_SURVOL
            survol_ordi = dessiner_bouton("Ordinateur (Noir)",
                                           debut_choix_x + bouton_choix_l + espacement,
                                           y_choix,
                                           bouton_choix_l, bouton_h,
                                           couleur_ordi, couleur_ordi_s)
            if clic and survol_ordi:
                joueur_commence = False

            # Info sur les règles
            dessiner_texte("Le joueur Noir commence toujours.",
                           POLICE_PETIT, GRIS, LARGEUR_FENETRE // 2,
                           y_choix + bouton_h + 15)

            y_suivant = y_choix + bouton_h + 50

        # ---- Bouton JOUER ----
        survol_jouer = dessiner_bouton("JOUER", LARGEUR_FENETRE // 2 - 90,
                                        y_suivant + 20, 180, 50,
                                        VERT_BOUTON, VERT_BOUTON_SURVOL)
        if clic and survol_jouer:
            # Déterminer le joueur humain selon le mode
            if mode == 'pvia':
                joueur_humain = 1 if joueur_commence else 2
            else:
                # En PvP et IAvIA, joueur_humain n'est pas utilisé
                # On met 0 pour indiquer qu'il n'y a pas de joueur humain spécifique
                joueur_humain = 0
            return mode, difficulte, difficulte_blanc, joueur_humain

        # Rafraîchir l'écran
        pygame.display.flip()
        horloge.tick(30)  # 30 images par seconde


# ============================================================================
#  ÉCRAN : FIN DE PARTIE
# ============================================================================

def afficher_fin_de_partie(plateau, mode, joueur_humain):
    """Affiche l'ecran de fin avec le resultat et les boutons rejouer/menu."""
    noirs, blancs = plateau.compter_pions()
    gagnant = plateau.gagnant()

    # Déterminer le message de résultat selon le mode
    if gagnant is None:
        message_resultat = "Egalite !"
        couleur_resultat = GRIS_CLAIR
    elif mode == 'pvia':
        if gagnant == joueur_humain:
            message_resultat = "Vous avez gagne !"
            couleur_resultat = VERT_BOUTON
        else:
            message_resultat = "L'ordinateur a gagne !"
            couleur_resultat = ROUGE
    elif mode == 'pvp':
        if gagnant == 1:
            message_resultat = "Joueur 1 (Noir) gagne !"
        else:
            message_resultat = "Joueur 2 (Blanc) gagne !"
        couleur_resultat = VERT_BOUTON
    else:
        # mode iavia
        if gagnant == 1:
            message_resultat = "IA Noir gagne !"
        else:
            message_resultat = "IA Blanc gagne !"
        couleur_resultat = VERT_BOUTON

    # Labels pour le score
    if mode == 'pvp':
        label_n = "Joueur 1"
        label_b = "Joueur 2"
    elif mode == 'iavia':
        label_n = "IA Noir"
        label_b = "IA Blanc"
    else:
        label_n = "Vous" if joueur_humain == 1 else "IA"
        label_b = "Vous" if joueur_humain == 2 else "IA"

    en_cours = True
    voir_plateau = False  # Si True, on affiche le plateau final

    while en_cours:
        clic = False
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                clic = True

        if voir_plateau:
            # ---- Affichage du plateau final ----
            ecran.fill(FOND_FENETRE)
            dessiner_plateau(plateau, [], None)

            # Score en texte simple
            dessiner_texte("Score final", POLICE_SOUS_TITRE, BLANC,
                           PANNEAU_X + 70, 80)
            dessiner_texte("Noir : " + str(noirs), POLICE_INFO, BLANC,
                           PANNEAU_X + 70, 120)
            dessiner_texte("Blanc : " + str(blancs), POLICE_INFO, BLANC,
                           PANNEAU_X + 70, 150)

            # Bouton Retour
            survol_retour = dessiner_bouton("Retour", PANNEAU_X + 10, 200,
                                             130, 40, BLEU, BLEU_SURVOL)
            if clic and survol_retour:
                voir_plateau = False

        else:
            # ---- Ecran de fin ----
            ecran.fill(FOND_FENETRE)

            # Titre
            dessiner_texte("Partie terminee", POLICE_TITRE, BLANC,
                           LARGEUR_FENETRE // 2, 70)

            # Resultat
            dessiner_texte(message_resultat, POLICE_SOUS_TITRE, couleur_resultat,
                           LARGEUR_FENETRE // 2, 140)

            # Score en texte
            dessiner_texte(label_n + " : " + str(noirs) + "  -  " + label_b + " : " + str(blancs),
                           POLICE_SCORE, BLANC, LARGEUR_FENETRE // 2, 210)

            # Boutons
            survol_rejouer = dessiner_bouton("Rejouer",
                                             LARGEUR_FENETRE // 2 - 200, 280,
                                             170, 45,
                                             VERT_BOUTON, VERT_BOUTON_SURVOL)
            if clic and survol_rejouer:
                return 'rejouer'

            survol_menu = dessiner_bouton("Menu",
                                          LARGEUR_FENETRE // 2 + 30, 280,
                                          170, 45,
                                          BLEU, BLEU_SURVOL)
            if clic and survol_menu:
                return 'menu'

            survol_plateau = dessiner_bouton("Voir plateau",
                                             LARGEUR_FENETRE // 2 - 200, 345,
                                             170, 45,
                                             BLEU, BLEU_SURVOL)
            if clic and survol_plateau:
                voir_plateau = True

            survol_quitter = dessiner_bouton("Quitter",
                                             LARGEUR_FENETRE // 2 + 30, 345,
                                             170, 45,
                                             ROUGE, ROUGE_SURVOL)
            if clic and survol_quitter:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        horloge.tick(30)


# ============================================================================
#  BOUCLE DE JEU PRINCIPALE
# ============================================================================

def boucle_de_jeu(mode, difficulte, difficulte_blanc, joueur_humain):
    """Boucle principale du jeu. Gere les tours de chaque joueur
    selon le mode choisi (pvp, pvia ou iavia).
    """
    # Initialiser un nouveau plateau
    plateau = Plateau()

    # Le joueur noir (1) commence toujours
    joueur_courant = 1

    # Variables d'état du jeu
    dernier_coup = None      # dernière case jouée (pour la surbrillance)
    message = ""             # message affiché en bas du plateau
    partie_finie = False     # flag de fin de partie
    ia_en_reflexion = False  # True pendant que l'IA calcule

    while not partie_finie:
        # ---- Gestion des événements ----
        clic = False
        pos_clic = None

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                clic = True
                pos_clic = evenement.pos

        # ---- Vérifier si la partie est terminée ----
        if plateau.est_fin_de_partie():
            partie_finie = True
            continue

        # ---- Obtenir les coups valides du joueur courant ----
        coups = plateau.coups_valides(joueur_courant)

        # Si le joueur courant ne peut pas jouer, il passe son tour
        if not coups:
            message = "Pas de coup possible, tour passe !"
            # Changer de joueur
            joueur_courant = plateau.adversaire(joueur_courant)
            # Petit délai pour que le message soit visible
            ecran.fill(FOND_FENETRE)
            dessiner_plateau(plateau, [], dernier_coup)
            dessiner_panneau(plateau, joueur_courant, mode,
                             difficulte, difficulte_blanc, message)
            pygame.display.flip()
            pygame.time.wait(1000)
            message = ""
            continue

        # ==============================================================
        #  MODE JOUEUR VS JOUEUR (PVP)
        # ==============================================================
        if mode == 'pvp':
            message = ""
            # Attendre le clic du joueur courant
            if clic and pos_clic is not None:
                case = case_depuis_souris(pos_clic[0], pos_clic[1])
                if case is not None:
                    ligne, col = case
                    if plateau.est_coup_valide(ligne, col, joueur_courant):
                        # Jouer le coup
                        pions_retournes = plateau.jouer_coup(ligne, col,
                                                             joueur_courant)
                        dernier_coup = (ligne, col)



                        # Passer au joueur suivant
                        joueur_courant = plateau.adversaire(joueur_courant)
                    else:
                        message = "Coup invalide !"

        # ==============================================================
        #  MODE JOUEUR VS IA (PVIA)
        # ==============================================================
        elif mode == 'pvia':
            joueur_ia = plateau.adversaire(joueur_humain)

            # ---- TOUR DU JOUEUR HUMAIN ----
            if joueur_courant == joueur_humain:
                message = ""
                if clic and pos_clic is not None:
                    case = case_depuis_souris(pos_clic[0], pos_clic[1])
                    if case is not None:
                        ligne, col = case
                        if plateau.est_coup_valide(ligne, col, joueur_humain):
                            # Jouer le coup
                            pions_retournes = plateau.jouer_coup(ligne, col,
                                                                 joueur_humain)
                            dernier_coup = (ligne, col)



                            # Passer au tour de l'IA
                            joueur_courant = joueur_ia
                            ia_en_reflexion = True
                        else:
                            message = "Coup invalide !"

            # ---- TOUR DE L'IA ----
            elif joueur_courant == joueur_ia:
                if ia_en_reflexion:
                    message = "L'IA reflechit..."

                    # Dessiner l'écran avant le calcul
                    ecran.fill(FOND_FENETRE)
                    dessiner_plateau(plateau, [], dernier_coup)
                    dessiner_panneau(plateau, joueur_courant, mode,
                                     difficulte, difficulte_blanc, message)
                    pygame.display.flip()

                    # Petite pause pour que l'affichage se mette à jour
                    pygame.time.wait(300)

                    # Calculer le meilleur coup de l'IA
                    coup_ia = meilleur_coup(plateau, joueur_ia, difficulte)

                    if coup_ia is not None:
                        ligne, col = coup_ia
                        pions_retournes = plateau.jouer_coup(ligne, col,
                                                             joueur_ia)
                        dernier_coup = (ligne, col)



                    # Passer au tour du joueur humain
                    joueur_courant = joueur_humain
                    ia_en_reflexion = False
                    message = ""
                else:
                    ia_en_reflexion = True

        # ==============================================================
        #  MODE IA VS IA (IAVIA)
        # ==============================================================
        elif mode == 'iavia':
            # Afficher quel IA joue
            if joueur_courant == 1:
                message = "IA Noir reflechit..."
            else:
                message = "IA Blanc reflechit..."

            # Dessiner l'écran avant le calcul
            ecran.fill(FOND_FENETRE)
            dessiner_plateau(plateau, [], dernier_coup)
            dessiner_panneau(plateau, joueur_courant, mode,
                             difficulte, difficulte_blanc, message)
            pygame.display.flip()

            # Pause pour pouvoir suivre la partie visuellement
            pygame.time.wait(500)

            # Choisir la difficulté selon le joueur courant
            diff_courante = difficulte if joueur_courant == 1 else difficulte_blanc

            # Calculer le meilleur coup
            coup_ia = meilleur_coup(plateau, joueur_courant, diff_courante)

            if coup_ia is not None:
                ligne, col = coup_ia
                pions_retournes = plateau.jouer_coup(ligne, col,
                                                     joueur_courant)
                dernier_coup = (ligne, col)



            message = ""
            # Passer au joueur suivant
            joueur_courant = plateau.adversaire(joueur_courant)

        # ---- Dessiner l'écran de jeu ----
        ecran.fill(FOND_FENETRE)

        # En PvP, on affiche toujours les coups possibles
        # En PvIA, seulement pendant le tour du joueur humain
        # En IAvIA, on ne les affiche pas
        if mode == 'pvp':
            coups_a_afficher = coups
        elif mode == 'pvia' and joueur_courant == joueur_humain:
            coups_a_afficher = coups
        else:
            coups_a_afficher = []

        dessiner_plateau(plateau, coups_a_afficher, dernier_coup)
        survol_rejouer = dessiner_panneau(plateau, joueur_courant, mode,
                                          difficulte, difficulte_blanc,
                                          message)

        # Si le joueur clique sur le bouton Rejouer, on relance la partie
        if clic and survol_rejouer:
            return 'rejouer'

        pygame.display.flip()
        horloge.tick(30)

    # ---- La partie est terminée ----
    # Afficher le plateau final pendant quelques secondes
    ecran.fill(FOND_FENETRE)
    dessiner_plateau(plateau, [], dernier_coup)
    dessiner_panneau(plateau, joueur_courant, mode,
                     difficulte, difficulte_blanc, "Partie terminee !")
    pygame.display.flip()
    pygame.time.wait(3000)  # Pause de 3 secondes sur le plateau final

    # Afficher l'écran de fin
    return afficher_fin_de_partie(plateau, mode, joueur_humain)


# ============================================================================
#  POINT D'ENTRÉE DU PROGRAMME
# ============================================================================

def main():
    """Fonction principale. On fait tourner le menu et les parties en boucle."""
    while True:
        # Afficher le menu et récupérer les choix du joueur
        mode, difficulte, difficulte_blanc, joueur_humain = afficher_menu()

        # Lancer la partie
        resultat = boucle_de_jeu(mode, difficulte, difficulte_blanc, joueur_humain)

        # Selon le choix de fin de partie
        while resultat == 'rejouer':
            # Relancer avec les mêmes paramètres
            resultat = boucle_de_jeu(mode, difficulte, difficulte_blanc, joueur_humain)

        # Si 'menu', on retourne au début de la boucle


# Lancer le jeu
if __name__ == "__main__":
    main()
