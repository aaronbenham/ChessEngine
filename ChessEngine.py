"""
Storing the information of the current state of the chess game. Also responsible for checking valid moves.
While also storing a move log for players
"""
class GameState():
    # bored is an 8x8 dimensional list (first character represents colour of piece and the second represents the type)
    # "--" means that no current piece is holding this position
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.whitetomove = True
        self.movelog = []

        self.whiteKingLocation = (7, 4)  # this is being used for checks and castling
        self.blackKingLocation = (0, 4)
        #  we are going to need to update the kings location so that valid moves are made throughout

        self.Checkmate = False  # king is in check and no way of stopping it (winning the game)
        self.Stalemate = False  # king is not in check yet no valid moves can be played (drawing the game)

        self.enPassantPossible = ()  # coordinates for the square when an en passant is possible

        self.currentCastlingRights = CastleRights(True, True, True, True)  # able to castle any side at the start of the game
        # does not mean that castling is valid move, just if they have the right to castle when possible
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]
        # helps with modifying the list of the castling rights since we will know when it happends

    """
    Takes a move then executes it however it does not work for castling, en-passant and pawn promotion"""
    def makeMove(self, move):
        self.board[move.startRow][move.startColumn] = "--"
        # when moving a piece the location of that piece after it is moved will always be blank
        self.board[move.endRow][move.endColumn] = move.pieceMoved
        # moves selected piece into selected location
        self.movelog.append(move)  # logs the move which can be edited later
        self.whitetomove = not self.whitetomove  # changes players turn since the turn is done

        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endColumn)  # updates the kings location on the board
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endColumn)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0] + "Q"  # changes the piece to a queen

        #enpassant
        if move.isenPassantMove:
            self.board[move.startRow][move.endColumn] = "--"  # capturing the pawn instead of just moving to blank space

        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: # helps for black and white pawns
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startColumn) # average between squares
        else:
            self.enPassantPossible = ()

        # castling
        if move.isCastleMove:
            if move.endColumn - move.startColumn == 2:  # this is a king side castle
                self.board[move.endRow][move.endColumn-1] = self.board[move.endRow][move.endColumn+1] # "new" rook being placed
                self.board[move.endRow][move.endColumn+1] = "--"  # deletes old rook
            else:   # queen side castle
                self.board[move.endRow][move.endColumn+1] = self.board[move.endRow][move.endColumn-2] # moves the rook
                self.board[move.endRow][move.endColumn - 2] = "--"  # deletes old rook

        # update castling rights - whether a king or a rook moves
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        # adds the castle rights to rights log

    """
    This will undo the last move so beginners can learn from mistakes and go back
    """
    def undoMove(self):
        if len(self.movelog) != 0:  # makes sure that there is a move which can be undone
            move = self.movelog.pop()   # removes it from the move log list
            self.board[move.startRow][move.startColumn] = move.pieceMoved   # opposite of line 26 since it reverses it
            self.board[move.endRow][move.endColumn] = move.pieceCaptured    # captured piece places back on the board
            self.whitetomove = not self.whitetomove     # change moves back

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startColumn)
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startColumn)

            # undo enpassant move
            if move.isenPassantMove:
                self.board[move.endRow][move.endColumn] = "--"  # the piece captured is not where it would be placed
                self.board[move.startRow][move.endColumn] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endColumn)  # makes sure you can redo the enpassant

            # undo two square pawn advance
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                    self.enPassantPossible = ()

            # undo castling (rights)
            self.castleRightsLog.pop()  # pops the castle rights of the last move
            self.currentCastlingRights = self.castleRightsLog[-1]  # sets them back to how they were before

            if move.isCastleMove:
                if move.endColumn - move.startColumn == 2:  # kingside castle
                    self.board[move.endRow][move.endColumn+1] = self.board[move.endRow][move.endColumn-1]
                    self.board[move.endRow][move.endColumn - 1] = "--"  # reversing the castling
                else:   # queenside castling
                    self.board[move.endRow][move.endColumn-2] = self.board[move.endRow][move.endColumn+1]
                    self.board[move.endRow][move.endColumn + 1] = "--"

    """         
    Update the castle rights given the move which has just been played
    """
    def updateCastleRights(self, move):
        if move.pieceMoved == "wK": # if king is moved it loses both king side and queen side castling
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:  # white pieces row
                if move.startColumn == 0:  # queen side rook (left rook)
                    self.currentCastlingRights.wqs = False
                elif move.startColumn == 7:  # king side rook (right rook)
                    self.currentCastlingRights.wks = False
            elif move.startRow == 7:
                if move.startColumn == 0:  # queen side rook (left rook)
                    self.currentCastlingRights.bqs = False
                elif move.startColumn == 7:  # king side rook (right rook)
                    self.currentCastlingRights.bks = False

    def getValidMoves(self):    # All moves considering checks (valid moves)
        tempEnpassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        # generate all possible moves
        moves = self.getAllPossibleMoves()

        if self.whitetomove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # makes each move which is possible
        for i in range(len(moves) -1, -1, -1):  # when removing from a list: start at the back to help with indexing
            self.makeMove(moves[i])

            # generate all of opponents moves

            # see if any opponents moves attack the king
            self.whitetomove = not self.whitetomove
            if self.inCheck():
                moves.remove(moves[i])  # if they do attack the king, it is not a valid move
            self.whitetomove = not self.whitetomove
            self.undoMove()  # make sure it does not physically moves piece on the board

        if len(moves) == 0:  # stalemate or checkmate situation
            if self.inCheck():
                self.Checkmate = True
            else:
                self.Stalemate = True
        else:
            self.Checkmate = False
            self.Stalemate = False

            self.enPassantPossible = tempEnpassantPossible  # save the value while we change and manipulate it
            self.currentCastlingRights = tempCastleRights
        return moves

    """
    Determines whether the current player is in check
    """

    def inCheck(self):
        if self.whitetomove:    # if in check it returns the kings current location to calculate the valid moves
            return self.sqaureBeingAttacked(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.sqaureBeingAttacked(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Determines whether an ememy is attacking the square (r, c), invalid for the king to move to
    """
    def sqaureBeingAttacked(self, r, c):  # generates opposite players moves to check if king is under attack
        self.whitetomove = not self.whitetomove  # switches to see opponents moves
        oppMoves = self.getAllPossibleMoves()
        self.whitetomove = not self.whitetomove  # switches back turns
        for move in oppMoves:
            if move.endRow == r and move.endColumn == c:
                return True  # if the r and c match to the end row and column then the square is under attack
        return False  # square is not under attack if an opponents piece does not cover the square

    def getAllPossibleMoves(self):  # All possible moves not considering checks (some may be invalid)
        moves = []
        for r in range(len(self.board)):    # number of rows
            for c in range(len(self.board[r])):  # number of columns in each row of the board
                colour = self.board[r][c][0]    # gives first character of the space (colour): "w" or "b"
                if (colour == "w" and self.whitetomove) or (colour == "b" and not self.whitetomove): # if the piece is able to be moved since its the players turn
                    piece = self.board[r][c][1]  # gives second character of the space (piece): "Q", "K", "B", ...
                    if piece == "p":    # pawn
                        self.getPawnMoves(r, c, moves)
                    elif piece == "R":  # rook
                        self.getRookMoves(r, c, moves)
                    elif piece == "N":  # Knight
                        self.getKnightMoves(r, c, moves)
                    elif piece == "B":  # Bishop
                        self.getBishopMoves(r, c, moves)
                    elif piece == "Q":  # Queen
                        self.getQueenMoves(r, c, moves)
                    elif piece == "K":  # King
                        self.getKingMoves(r, c, moves)

        return moves

    """
    functions for calculate all possible moves for the pieces at (row, column) then add these moves to the list
    """

    def getPawnMoves(self, r, c, moves):
        if self.whitetomove:    # white pawn moves (going up)
            if self.board[r-1][c] == "--":  # 1 square up move
                moves.append(Move((r, c), (r-1, c), self.board))  # (start square, end square, board)
                if r == 6 and self.board[r-2][c] == "--":   # 2 square pawn move  (has to be on starting line)
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c != 0 and r != 0:   # valid diagonally capturing left
                if self.board[r-1][c-1] != "--" and self.board[r-1][c-1][0] != "w": # stops pieces taking their own team
                    moves.append(Move((r, c), (r-1, c-1), self.board))

                # en passant for the white pawns
                elif (r-1, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))

            if c != 7 and r != 0:   # valid diagonally capturing right
                if self.board[r-1][c+1] != "--" and self.board[r-1][c+1][0] != "w":
                    moves.append(Move((r, c), (r-1, c+1), self.board))

                elif (r-1, c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:
            if self.board[r + 1][c] == "--":  # since black pawns move down the properties of the pawns are different
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c != 0 and r != 7:
                if self.board[r+1][c-1] != "--" and self.board[r+1][c-1][0] != "b":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c != 7 and r != 7:
                if self.board[r+1][c+1] != "--" and self.board[r+1][c+1][0] != "b":
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        if r != 7:
            i = 1
            while self.board[r+i][c] == "--" and (r + i) != 7:    # scans for valid downward moves
                moves.append(Move((r, c), (r+i, c), self.board))
                i += 1
            if self.board[r+i][c][0] != self.board[r][c][0]:  # able to take enemy pieces if located and not take your own
                moves.append(Move((r, c), (r+i, c), self.board))

        if r != 0:
            i = 1
            while self.board[r-i][c] == "--" and (r - i) != 0:
                moves.append(Move((r, c), (r-i, c), self.board))    # scans for valid upward moves
                i += 1
            if self.board[r-i][c][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r-i, c), self.board))

        if c != 7:
            i = 1
            while self.board[r][c+i] == "--" and (c + i) != 7:  # scans for valid right moves
                moves.append(Move((r, c), (r, c+i), self.board))
                i += 1
            if self.board[r][c+i][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r, c+i), self.board))

        if c != 0:
            i = 1
            while self.board[r][c-i] == "--" and (c - i) != 0:  # scans for valid left moves
                moves.append(Move((r, c), (r, c-i), self.board))
                i += 1
            if self.board[r][c-i][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r, c-i), self.board))

    def getKnightMoves(self, r, c, moves):
        if r - 2 >= 0 and c - 1 >= 0:
            if self.board[r-2][c-1] == "--" or self.board[r-2][c-1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r-2, c-1), self.board))

        if r - 1 >= 0 and c - 2 >= 0:
            if self.board[r-1][c-2] == "--" or self.board[r-1][c-2][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r-1, c-2), self.board))

        if r + 1 <= 7 and c - 2 >= 0:
            if self.board[r+1][c-2] == "--" or self.board[r+1][c-2][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r+1, c-2), self.board))

        if r + 2 <= 7 and c - 1 >= 0:
            if self.board[r+2][c-1] == "--" or self.board[r+2][c-1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r+2, c-1), self.board))

        if r + 2 <= 7 and c + 1 <= 7:
            if self.board[r+2][c+1] == "--" or self.board[r+2][c+1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r+2, c+1), self.board))

        if r + 1 <= 7 and c + 2 <= 7:
            if self.board[r+1][c+2] == "--" or self.board[r+1][c+2][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r+1, c+2), self.board))

        if r - 1 >= 0 and c + 2 <= 7:
            if self.board[r-1][c+2] == "--" or self.board[r-1][c+2][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r-1, c+2), self.board))

        if r - 2 >= 0 and c + 1 <= 7:
            if self.board[r-2][c+1] == "--" or self.board[r-2][c+1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r-2, c+1), self.board))

    def getBishopMoves(self, r, c, moves):
        if r != 7:
            if c != 0:
                i = 1
                while self.board[r+i][c-i] == "--" and (r+i) != 7 and (c-i) != 0:
                    moves.append(Move((r, c), (r+i, c-i), self.board))
                    i += 1
                if self.board[r+i][c-i][0] != self.board[r][c][0]:
                    moves.append(Move((r, c), (r+i, c-i), self.board))

        if r != 0:
            if c != 0:
                i = 1
                while self.board[r-i][c-i] == "--" and (r-i) != 0 and (c-i) != 0:
                    moves.append(Move((r, c), (r-i, c-i), self.board))
                    i += 1
                if self.board[r-i][c-i][0] != self.board[r][c][0]:
                    moves.append(Move((r, c), (r-i, c-i), self.board))

        if r != 0:
            if c != 7:
                i = 1
                while self.board[r-i][c+i] == "--" and (r-i) != 0 and (c+i) != 7:
                    moves.append(Move((r, c), (r-i, c+i), self.board))
                    i += 1
                if self.board[r-i][c+i][0] != self.board[r][c][0]:
                    moves.append(Move((r, c), (r-i, c+i), self.board))

        if r != 7:
            if c != 7:
                i = 1
                while self.board[r+i][c+i] == "--" and (r+i) != 7 and (c+i) != 7:
                    moves.append(Move((r, c), (r+i, c+i), self.board))
                    i += 1
                if self.board[r+i][c+i][0] != self.board[r][c][0]:
                    moves.append(Move((r, c), (r+i, c+i), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        if r + 1 <= 7 and c + 1 <= 7:
            if self.board[r+1][c+1] == "--" or self.board[r+1][c+1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r+1, c+1), self.board))

        if r + 1 <= 7:
            if self.board[r+1][c] == "--" or self.board[r+1][c][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r+1, c), self.board))

        if r + 1 <= 7 and c - 1 >= 0:
            if self.board[r+1][c-1] == "--" or self.board[r+1][c-1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r+1, c-1), self.board))

        if c - 1 >= 0:
            if self.board[r][c-1] == "--" or self.board[r][c-1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r, c-1), self.board))

        if r - 1 >= 0 and c - 1 >= 0:
            if self.board[r-1][c-1] == "--" or self.board[r-1][c-1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r-1, c-1), self.board))

        if r - 1 >= 0:
            if self.board[r-1][c] == "--" or self.board[r-1][c][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r-1, c), self.board))

        if r - 1 >= 0 and c + 1 <= 7:
            if self.board[r-1][c+1] == "--" or self.board[r-1][c+1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r-1, c+1), self.board))
        if c + 1 <= 7:
            if self.board[r][c+1] == "--" or self.board[r][c+1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r, c+1), self.board))

        """
        generate all valid castle moves for the king
        """

    def getCastleMoves(self, r, c, moves):
        if self.sqaureBeingAttacked(r, c):
            return  # cant castle when in check
        if (self.whitetomove and self.currentCastlingRights.wks) or (not self.whitetomove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whitetomove and self.currentCastlingRights.wqs) or (not self.whitetomove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.sqaureBeingAttacked(r, c+1) and not self.sqaureBeingAttacked(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.sqaureBeingAttacked(r, c-1) and not self.sqaureBeingAttacked(r, c-2): # dont need to check the third because the king does not pass it
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):  # each side a king can castle (king or queen side) for both sets of pieces
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs




class Move():
    # key : value
    NumberDictionary = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsintoRanks = {v: k for k, v in NumberDictionary.items()}
    LetterDictionary = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    columnstoFiles = {v: k for k, v in LetterDictionary.items()}
# since the coordinates for the board is different due to the matrix notation we have to transfer them to the correct
# columns and rows with the correct numbers (ranks) and letters (files)


    def __init__(self, startsq, endsq, board, isEnpassantMove = False, isCastleMove=False):  # storing information for the system
        self.startRow = startsq[0]  # storing selected square to move
        self.startColumn = startsq[1]
        self.endRow = endsq[0]  # storing square to move to
        self.endColumn = endsq[1]
        self.pieceMoved = board[self.startRow][self.startColumn]    # storing piece which is moving
        self.pieceCaptured = board[self.endRow][self.endColumn]     # storing piece captured in the square moved to

        self.moveID = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn # gives unique ID to each move so that it has something to compare to

        self.isPawnPromotion = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7):
            self.isPawnPromotion = True

        self.isenPassantMove = isEnpassantMove
        if self.isenPassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

        self.isCastleMove = isCastleMove

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def ChessNotation(self):
        return self.RankFile(self.startRow, self.startColumn) + self.RankFile(self.endRow, self.endColumn)
        # returning the Chess Notation of moves made - instead of matrix coordinates

    def RankFile(self, r, c):
        return self.columnstoFiles[c] + self.rowsintoRanks[r]