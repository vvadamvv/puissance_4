import numpy as np
import pygame
import random
import sys
import math 
from puissance_4 import *
from parametre import*
from keras.models import Sequential
from keras.layers import Dense
from bot import*



def create_model():
    model = Sequential()
    model.add(Dense(128, input_dim=42, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(7, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def get_model_move(board, model, epsilon):
    if np.random.rand() < epsilon:
        # exploration : choisit une colonne au hasard
        col = np.random.randint(0, 7)
        while not is_valid_location(board, col):
            col = np.random.randint(0, 7)
    else:
        # exploitation : utilise le réseau de neurones pour choisir la meilleure colonne
        inputs = np.reshape(board, (1, 128))
        outputs = model.predict(inputs)
        valid_moves = get_valid_locations(board)
        mask = np.ones(outputs.shape)
        mask[0][np.logical_not(valid_moves)] = 0
        outputs *= mask
        col = np.argmax(outputs)
    return col


def get_best_move(board, nn, turn):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, turn)
        score = nn.predict(temp_board.reshape(1, -1))[0]
        if max(score) > best_score:
            best_score = max(score)
            best_col = col
    return best_col



def get_valid_locations(board):
    valid_locations = []
    for col in range(TAB_COLONNE):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations



def player_vs_IA():
    # Initialisation du tableau de jeu
    board = np.zeros((TAB_LIGNE, TAB_COLONNE))

    # Détermination du premier joueur
    turn = random.randint(1, 2)

    # Chargement du réseau de neurones
    model = create_model()

    # Boucle principale du jeu
    while True:
        # Gestion des événements Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(WINDOW, (0, 0, 0), (0, 0, LARGEUR, TAILLE_CARRE))
                posx = event.pos[0]
                if turn == 1:
                    pygame.draw.circle(WINDOW, PLAYER_1_COLOR, (posx, int(TAILLE_CARRE/2)), RAYON)
                else:
                    pygame.draw.circle(WINDOW, BOT_COLOR, (posx, int(TAILLE_CARRE/2)), RAYON)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(WINDOW, (0, 0, 0), (0, 0, LARGEUR, TAILLE_CARRE))
                # Tour du joueur humain
                if turn == 1:
                    posx = event.pos[0]
                    col = int(math.floor(posx/TAILLE_CARRE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 1)

                        if check_victory(board, 1):
                            draw_board(board)
                            pygame.display.update()
                            pygame.time.wait(3000)
                            print("Vous avez gagné !")
                            return

                        # Vérifiez si le joueur a trois pièces d'affilée
                        if check_three_in_a_row(board, 1):
                            # Bloquer le prochain coup du joueur
                             
                            block_col = find_blocking_column(board, 1)
                            if block_col is not None:
                                row = get_next_open_row(board, block_col)
                                drop_piece(board, row, block_col, 2)
                                turn = 2
                                break

                        turn = 2

                # Tour du bot
                else:
                    col = get_best_move(board, model, 2)

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 2)

                        if check_victory(board, 2):
                            draw_board(board)
                            pygame.display.update()
                            pygame.time.wait(3000)
                            print("L'IA a gagné !")
                            return

                        turn = 1

                draw_board(board)

                if check_board_full(board):
                    pygame.time.wait(3000)
                    print("Match nul , Attention l'IA vous ratrape !")
                    return 


'''def player_vs_IA():
    # Initialisation des scores
    player_score = 0
    bot_score = 0

    # Boucle principale pour jouer 5 parties
    for i in range(5):
        # Initialisation du tableau de jeu
        board = np.zeros((TAB_LIGNE, TAB_COLONNE))

        # Détermination du premier joueur
        turn = random.randint(1, 2)

        # Chargement du réseau de neurones
        model = create_model()

        # Boucle principale du jeu
        while True:
            # Gestion des événements Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(WINDOW, (0, 0, 0), (0, 0, LARGEUR, TAILLE_CARRE))
                    posx = event.pos[0]
                    if turn == 1:
                        pygame.draw.circle(WINDOW, PLAYER_1_COLOR, (posx, int(TAILLE_CARRE/2)), RAYON)
                    else:
                        pygame.draw.circle(WINDOW, BOT_COLOR, (posx, int(TAILLE_CARRE/2)), RAYON)
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(WINDOW, (0, 0, 0), (0, 0, LARGEUR, TAILLE_CARRE))
                    # Tour du joueur humain
                    if turn == 1:
                        posx = event.pos[0]
                        col = int(math.floor(posx/TAILLE_CARRE))

                        if is_valid_location(board, col):
                            row = get_next_open_row(board, col)
                            drop_piece(board, row, col, 1)

                            if check_victory(board, 1):
                                draw_board(board)
                                pygame.display.update()
                                pygame.time.wait(3000)
                                print("Vous avez gagné !")
                                player_score += 1
                                break

                            # Check if the player has three pieces in a row
                            if check_three_in_a_row(board, 1):
                                # Block the player's next move half the time
                                if random.randint(0, 1) == 0:
                                    block_col = find_blocking_column(board, 1)
                                    if block_col is not None:
                                        row = get_next_open_row(board, block_col)
                                        drop_piece(board, row, block_col, 2)
                                        turn = 2
                                        break

                            turn = 2

                    # Tour du bot
                    else:
                        col = get_best_move(board, model, 2)

                        if is_valid_location(board, col):
                            row = get_next_open_row(board, col)
                            drop_piece(board, row, col, 2)

                            if check_victory(board, 2):
                                draw_board(board)
                                pygame.display.update()
                                pygame.time.wait(3000)
                                print("L'IA a gagné !")
                                bot_score += 1
                                break

                            turn = 1

                    draw_board(board)

                    if check_board_full(board):
                        pygame.time.wait(3000)
                        print("Match nul, Attention l'IA vous ratrape !")
                        break
                # Réinitialisation du tableau de jeu pour la prochaine partie
    for x in range(TAB_LIGNE):
        for y in range(TAB_COLONNE):
            board[x][y] = 0
            draw_board(board)

    if player_score == 3:
        print("Le joueur a gagné la partie !")
        return
    elif bot_score == 3:
        print("L'IA a gagné la partie !")
        return

    # Affichage du grand vainqueur
    if player_score > bot_score:
        print("Vous avez gagné", player_score, "parties sur 5 !")
    elif bot_score > player_score:
        print("L'IA a gagné", bot_score, "parties sur 5 !")
    else:
        print("Match nul !")
        return'''





