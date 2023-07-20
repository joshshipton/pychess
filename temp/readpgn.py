import chess.pgn

games = []
with open('lichess.pgn') as pgn_file:
    game = chess.pgn.read_game(pgn_file)

    count = 0
    while game is not None:
        if game.headers["WhiteElo"] == "?" or game.headers["BlackElo"] == "?":
            game = chess.pgn.read_game(pgn_file)
            continue

        # If both elo is below 1400, add to games
        if int(game.headers["WhiteElo"]) < 1400 and int(game.headers["BlackElo"]) < 1400:
            count += 1
            print(count)
            games.append(game)

        game = chess.pgn.read_game(pgn_file)

        
# Write games to file in pgn format
with open('lichess_elo_below_1000.pgn', 'w') as pgn_file:
    for game in games:
        pgn_file.write(str(game) + "\n\n")