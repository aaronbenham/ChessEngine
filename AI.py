import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0       # values for pieces and results for games


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) -1)]


def findGreedyMove(gs, validMoves):   # greedy algorithm (looks at material alone)
    turnMultiplier = 1 if gs.whitetomove else -1    # using this makes that both sides
                                                    # are trying to get a high positive score
    OpponentsMinMaxScore = CHECKMATE    # black's perspective (start with worst case then lower it) using minimax
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves() # looking at opponents move (looking 1 move further)
        OpponentsMaxScore = -CHECKMATE
        for opponentsMoves in opponentsMoves:
            gs.makeMove(opponentsMoves)
            if gs.Checkmate:
                score = -turnMultiplier * CHECKMATE   # make sure that checkmate will be best move if possible
            elif gs.Stalemate:
                score = STALEMATE   # bad score since stalemate ends in draw and not win
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)   # turned negative since we are looking an extra move
            if score > OpponentsMaxScore:    # since black wants negative score
                OpponentsMaxScore = score
            gs.undoMove()
        if OpponentsMaxScore < OpponentsMinMaxScore:
            OpponentsMinMaxScore = OpponentsMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

"""
Scoring the board based on the material of each side
"""


def scoreMaterial(board):  # only scoring the material and not the position of the material
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]   # positive number = winning for white
            elif square[0] == "b":
                score -= pieceScore[square[1]]   # negative number = winning for black
    return score
