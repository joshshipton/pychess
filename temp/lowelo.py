import chess.pgn

games = []
with open('data/lichess_elo_below_1000.pgn') as pgn_file:
    game = chess.pgn.read_game(pgn_file)

    count = 0
    while game is not None:
        # Prints game length
        moves = str(game.mainline_moves()).split(" ")

        game = chess.pgn.read_game(pgn_file)