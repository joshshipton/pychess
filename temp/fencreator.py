import json
import random
import chess.pgn

games = []
with open('data/lichess.pgn') as pgn_file:
    game = chess.pgn.read_game(pgn_file)

    count = 0
    while game is not None and count < 10000:
        if count % 1000 == 0:
            print(f"Progress: {count/1000}%")
        # Calculates the length of the game
        game_length = 0
        node = game
        while not node.is_end():
            game_length += 1
            node = node.variations[0]

        # Progresses the board state a random number of moves
        # between 0 and the length of the game
        random_move = random.randint(0, game_length)
        node = game
        for i in range(random_move):
            node = node.variations[0]
        
        # Gets the fen
        fen = node.board().fen()
        count += 1

        # Adds the game to the list of games
        games.append(fen)

        game = chess.pgn.read_game(pgn_file)

        
# Write games to file in json format
with open('random_fens.json', 'w') as pgn_file:
    # Json dumps
    json.dump(games, pgn_file)