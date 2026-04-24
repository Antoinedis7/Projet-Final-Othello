"""
Othello — Intelligence Artificielle
Auteur : Haison HONG

Ce fichier contient l'IA du jeu d'Othello.
On utilise l'algorithme minimax avec alpha-beta pour que l'IA joue.
Il y a 3 niveaux de difficulte : facile, moyen et difficile.
"""

import math
import random


# ============================================================================
#  MATRICES DE POIDS POSITIONNELS
# ============================================================================

# Matrice de poids pour chaque case du plateau
# Les coins valent beaucoup (+100) car on peut pas les retourner
# Les cases a cote des coins sont dangereuses (-25)
MATRICE_POIDS = [
    [100, -25,  10,   5,   5,  10, -25, 100],
    [-25, -25,   2,   2,   2,   2, -25, -25],
    [ 10,   2,   5,   1,   1,   5,   2,  10],
    [  5,   2,   1,   0,   0,   1,   2,   5],
    [  5,   2,   1,   0,   0,   1,   2,   5],
    [ 10,   2,   5,   1,   1,   5,   2,  10],
    [-25, -25,   2,   2,   2,   2, -25, -25],
    [100, -25,  10,   5,   5,  10, -25, 100],
]

# Les 4 coins
COINS = [(0, 0), (0, 7), (7, 0), (7, 7)]

# Cases en diagonale des coins (dangereuses)
CASES_X = [(1, 1), (1, 6), (6, 1), (6, 6)]

# Cases a cote des coins sur les bords
CASES_C = [
    (0, 1), (1, 0),   # coin (0,0)
    (0, 6), (1, 7),   # coin (0,7)
    (6, 0), (7, 1),   # coin (7,0)
    (6, 7), (7, 6),   # coin (7,7)
]


# ============================================================================
#  FONCTIONS D'ÉVALUATION (HEURISTIQUES)
# ============================================================================

def evaluer_parite(plateau, joueur_ia):
    """Calcule la difference entre les pions de l'IA et de l'adversaire.
    On normalise entre -100 et 100.
    """
    adversaire = 2 if joueur_ia == 1 else 1
    noirs, blancs = plateau.compter_pions()

    # Récupérer les pions selon le joueur IA
    pions_ia = noirs if joueur_ia == 1 else blancs
    pions_adv = noirs if adversaire == 1 else blancs

    # Normalisation pour éviter la division par zéro
    total = pions_ia + pions_adv
    if total == 0:
        return 0
    return 100 * (pions_ia - pions_adv) / total


def evaluer_position(plateau, joueur_ia):
    """Evalue la position en utilisant la matrice de poids.
    Chaque case a un poids different selon si elle est strategique ou pas.
    """
    adversaire = 2 if joueur_ia == 1 else 1
    score = 0

    for ligne in range(8):
        for col in range(8):
            if plateau.grille[ligne][col] == joueur_ia:
                score += MATRICE_POIDS[ligne][col]
            elif plateau.grille[ligne][col] == adversaire:
                score -= MATRICE_POIDS[ligne][col]

    return score


def evaluer_mobilite(plateau, joueur_ia):
    """Evalue combien de coups chaque joueur peut faire.
    Plus on a de coups possibles, mieux c'est.
    """
    adversaire = 2 if joueur_ia == 1 else 1

    # Compter les coups valides pour chaque joueur
    mouvements_ia = len(plateau.coups_valides(joueur_ia))
    mouvements_adv = len(plateau.coups_valides(adversaire))

    total = mouvements_ia + mouvements_adv
    if total == 0:
        return 0
    return 100 * (mouvements_ia - mouvements_adv) / total


def evaluer_coins(plateau, joueur_ia):
    """Regarde qui controle les coins du plateau.
    Les coins c'est tres important car on peut pas les reprendre.
    """
    adversaire = 2 if joueur_ia == 1 else 1
    coins_ia = 0
    coins_adv = 0

    for l, c in COINS:
        if plateau.grille[l][c] == joueur_ia:
            coins_ia += 1
        elif plateau.grille[l][c] == adversaire:
            coins_adv += 1

    total = coins_ia + coins_adv
    if total == 0:
        return 0
    return 100 * (coins_ia - coins_adv) / total


def evaluer_stabilite(plateau, joueur_ia):
    """Evalue les pions stables (ceux qui peuvent plus etre retournes).
    Un pion dans un coin est toujours stable.
    On propage la stabilite le long des bords depuis les coins.
    """
    adversaire = 2 if joueur_ia == 1 else 1
    stables_ia = 0
    stables_adv = 0

    # Vérification de la stabilité à partir de chaque coin
    # Un pion dans un coin est toujours stable
    # Les pions adjacents à un coin contrôlé sur un bord sont aussi stables
    for coin_l, coin_c in COINS:
        joueur_coin = plateau.grille[coin_l][coin_c]
        if joueur_coin == 0:
            continue  # Coin vide, pas de stabilité à propager

        # Le coin lui-même est stable
        if joueur_coin == joueur_ia:
            stables_ia += 1
        else:
            stables_adv += 1

        # Propager la stabilité le long des bords depuis ce coin
        # Direction horizontale
        dl_h = 0
        dc_h = 1 if coin_c == 0 else -1
        c = coin_c + dc_h
        while 0 <= c < 8 and plateau.grille[coin_l][c] == joueur_coin:
            if joueur_coin == joueur_ia:
                stables_ia += 1
            else:
                stables_adv += 1
            c += dc_h

        # Direction verticale
        dl_v = 1 if coin_l == 0 else -1
        l = coin_l + dl_v
        while 0 <= l < 8 and plateau.grille[l][coin_c] == joueur_coin:
            if joueur_coin == joueur_ia:
                stables_ia += 1
            else:
                stables_adv += 1
            l += dl_v

    total = stables_ia + stables_adv
    if total == 0:
        return 0
    return 100 * (stables_ia - stables_adv) / total


def evaluer_cases_dangereuses(plateau, joueur_ia):
    """Penalise les cases dangereuses (a cote des coins).
    Si on joue a cote d'un coin vide, ca peut donner le coin a l'adversaire.
    """
    adversaire = 2 if joueur_ia == 1 else 1
    score = 0

    # Association des cases X avec leurs coins respectifs
    x_to_coin = {
        (1, 1): (0, 0), (1, 6): (0, 7),
        (6, 1): (7, 0), (6, 6): (7, 7),
    }

    for case_x, coin in x_to_coin.items():
        # Pénaliser uniquement si le coin est vide (sinon c'est moins grave)
        if plateau.grille[coin[0]][coin[1]] == 0:
            if plateau.grille[case_x[0]][case_x[1]] == joueur_ia:
                score -= 25
            elif plateau.grille[case_x[0]][case_x[1]] == adversaire:
                score += 25

    return score


# ============================================================================
#  HEURISTIQUE COMBINÉE PAR NIVEAU DE DIFFICULTÉ
# ============================================================================

def evaluer_facile(plateau, joueur_ia):
    """Heuristique facile : on regarde juste qui a le plus de pions."""
    return evaluer_parite(plateau, joueur_ia)


def evaluer_moyen(plateau, joueur_ia):
    """Heuristique moyen : on combine position, coins et parite."""
    score_position = evaluer_position(plateau, joueur_ia)
    score_coins = evaluer_coins(plateau, joueur_ia)
    score_parite = evaluer_parite(plateau, joueur_ia)

    return (3 * score_position +
            10 * score_coins +
            1 * score_parite)


def evaluer_difficile(plateau, joueur_ia):
    """Heuristique difficile : on combine tout (position, mobilite, coins,
    stabilite, cases dangereuses) avec des poids qui changent
    selon ou on en est dans la partie.
    """
    vides = plateau.cases_vides()

    # Calcul de chaque composante heuristique
    score_parite = evaluer_parite(plateau, joueur_ia)
    score_position = evaluer_position(plateau, joueur_ia)
    score_mobilite = evaluer_mobilite(plateau, joueur_ia)
    score_coins = evaluer_coins(plateau, joueur_ia)
    score_stabilite = evaluer_stabilite(plateau, joueur_ia)
    score_danger = evaluer_cases_dangereuses(plateau, joueur_ia)

    # Pondération dynamique selon la phase de jeu
    if vides > 45:
        # OUVERTURE (< 19 pions posés) : mobilité et position cruciales
        poids = {
            'parite': 1,
            'position': 30,
            'mobilite': 50,
            'coins': 1000,
            'stabilite': 25,
            'danger': 30,
        }
    elif vides > 15:
        # MILIEU DE PARTIE : coins et stabilité deviennent importants
        poids = {
            'parite': 5,
            'position': 20,
            'mobilite': 40,
            'coins': 1000,
            'stabilite': 50,
            'danger': 20,
        }
    else:
        # FIN DE PARTIE (< 15 cases restantes) : maximiser les pions
        poids = {
            'parite': 50,
            'position': 10,
            'mobilite': 10,
            'coins': 1000,
            'stabilite': 30,
            'danger': 5,
        }

    return (poids['parite'] * score_parite +
            poids['position'] * score_position +
            poids['mobilite'] * score_mobilite +
            poids['coins'] * score_coins +
            poids['stabilite'] * score_stabilite +
            poids['danger'] * score_danger)


# ============================================================================
#  ALGORITHME MINIMAX AVEC ÉLAGAGE ALPHA-BETA
# ============================================================================

def alphabeta(plateau, profondeur, alpha, beta, est_maximisant, joueur_ia, evaluer_fn):
    """Algorithme minimax avec elagage alpha-beta.
    On explore l'arbre de jeu en coupant les branches inutiles.
    alpha = meilleur score pour le max, beta = meilleur score pour le min.
    Si alpha >= beta on coupe car ca sert a rien de continuer.
    """
    # Condition d'arrêt : profondeur atteinte ou partie terminée
    if profondeur == 0 or plateau.est_fin_de_partie():
        return evaluer_fn(plateau, joueur_ia)

    adversaire = plateau.adversaire(joueur_ia)

    if est_maximisant:
        # Tour du joueur IA : on cherche à MAXIMISER le score
        joueur = joueur_ia
        coups = plateau.coups_valides(joueur)

        # Si aucun coup possible, le joueur passe son tour
        if not coups:
            return alphabeta(plateau, profondeur - 1, alpha, beta,
                             False, joueur_ia, evaluer_fn)

        meilleur_score = -math.inf

        # Trier les coups : coins d'abord pour améliorer l'élagage
        coups = trier_coups(coups)

        for coup in coups:
            # Simuler le coup sur une copie du plateau
            copie = plateau.copier()
            copie.jouer_coup(coup[0], coup[1], joueur)

            # Appel récursif pour le joueur minimisant
            score = alphabeta(copie, profondeur - 1, alpha, beta,
                              False, joueur_ia, evaluer_fn)

            meilleur_score = max(meilleur_score, score)
            alpha = max(alpha, score)

            # Élagage beta : le minimisant ne choisira jamais cette branche
            if alpha >= beta:
                break

        return meilleur_score

    else:
        # Tour de l'adversaire : on cherche à MINIMISER le score
        joueur = adversaire
        coups = plateau.coups_valides(joueur)

        # Si aucun coup possible, l'adversaire passe son tour
        if not coups:
            return alphabeta(plateau, profondeur - 1, alpha, beta,
                             True, joueur_ia, evaluer_fn)

        meilleur_score = math.inf

        coups = trier_coups(coups)

        for coup in coups:
            # Simuler le coup sur une copie du plateau
            copie = plateau.copier()
            copie.jouer_coup(coup[0], coup[1], joueur)

            # Appel récursif pour le joueur maximisant
            score = alphabeta(copie, profondeur - 1, alpha, beta,
                              True, joueur_ia, evaluer_fn)

            meilleur_score = min(meilleur_score, score)
            beta = min(beta, score)

            # Élagage alpha : le maximisant ne choisira jamais cette branche
            if alpha >= beta:
                break

        return meilleur_score


def trier_coups(coups):
    """Trie les coups pour que l'elagage marche mieux.
    On met les coins en premier car c'est souvent les meilleurs coups.
    """
    def priorite(coup):
        if coup in COINS:
            return 0   # Priorité maximale pour les coins
        elif coup in CASES_X:
            return 2   # Priorité basse pour les cases X
        else:
            return 1   # Priorité normale pour le reste
    return sorted(coups, key=priorite)


# ============================================================================
#  CONFIGURATION DES NIVEAUX DE DIFFICULTÉ
# ============================================================================

# Dictionnaire de configuration des niveaux de difficulté
# Chaque niveau a une profondeur de recherche et une fonction d'évaluation
NIVEAUX = {
    'facile': {
        'profondeur': 1,       # Recherche très peu profonde
        'evaluer': evaluer_facile,
        'nom': 'Facile',
    },
    'moyen': {
        'profondeur': 3,       # Recherche modérée
        'evaluer': evaluer_moyen,
        'nom': 'Moyen',
    },
    'difficile': {
        'profondeur': 5,       # Recherche profonde
        'evaluer': evaluer_difficile,
        'nom': 'Difficile',
    },
}


def meilleur_coup(plateau, joueur_ia, difficulte='moyen'):
    """Trouve le meilleur coup pour l'IA.
    On utilise alpha-beta avec la profondeur et l'heuristique du niveau choisi.
    Si plusieurs coups ont le meme score, on en choisit un au hasard.
    """
    # Récupérer la configuration du niveau
    config = NIVEAUX.get(difficulte, NIVEAUX['moyen'])
    profondeur = config['profondeur']
    evaluer_fn = config['evaluer']

    # Obtenir tous les coups valides
    coups = plateau.coups_valides(joueur_ia)

    # Si aucun coup disponible, renvoyer None (le joueur passe)
    if not coups:
        return None

    # S'il ne reste qu'un seul coup, le jouer directement
    if len(coups) == 1:
        return coups[0]

    # Évaluer chaque coup avec l'algorithme alpha-beta
    meilleur_score = -math.inf
    meilleurs_coups = []

    # Trier les coups pour un meilleur élagage
    coups = trier_coups(coups)

    for coup in coups:
        # Simuler le coup
        copie = plateau.copier()
        copie.jouer_coup(coup[0], coup[1], joueur_ia)

        # Évaluer la position résultante (c'est au tour de l'adversaire)
        score = alphabeta(copie, profondeur - 1, -math.inf, math.inf,
                          False, joueur_ia, evaluer_fn)

        # Mettre à jour le meilleur score
        if score > meilleur_score:
            meilleur_score = score
            meilleurs_coups = [coup]
        elif score == meilleur_score:
            # En cas d'égalité, ajouter le coup à la liste
            meilleurs_coups.append(coup)

    # Choisir aléatoirement parmi les meilleurs coups (variété de jeu)
    return random.choice(meilleurs_coups)
