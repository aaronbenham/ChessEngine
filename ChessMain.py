"""main basis of game to play chess"""

import pygame as p  # very good library for games
import ChessEngine, AI   # now can access AI python file
import tkinter as tk

width = height = 512
dimension = 8
square_size = height // dimension  # equal square size
IMAGES = {}

"""
Assigns pieces to an image
"""


def loadimages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("D:/Documents/CODE/Chess/images/" + piece + ".png"),
                                          (square_size, square_size))
    # now we can access an image by just calling 'IMAGES[" "]' and has them scaled to the squares on the board


"""
Handle user input and updating the board
"""


def maingame():
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()  # current status of board
    print(gs.board)
    loadimages()
    running = True

    square_selected = ()  # keep track of the last click of the user (row, column)
    player_clicks = []  # where the player clicks [(5,6), (6,6)] - moving piece to new square
    # stores two values of starting square (piece) and location

    validMoves = gs.getValidMoves() # now we have it in the main so that we can compare the move inputted to check if the move is valid
    moveMade = False  # only moves valid moves (flag variable)

    playerOne = True    # if a human is playing white then this will be true, if AI is playing then Fasle
    playerTwo = False   # same but for black

    while running:
        humanTurn = ((gs.whitetomove and playerOne) or (not gs.whitetomove and playerTwo)) # boolean expression to make sure its a human playing
        for events in p.event.get():
            if events.type == p.QUIT:
                quit()
                running = False
                # MOUSE OPERATIONS
            elif events.type == p.MOUSEBUTTONDOWN:
                if humanTurn:  # now person can only interact if it is their turn
                    location = p.mouse.get_pos()  # gets the (x, y) location of the mouse where it clicks
                    column = location[0]//square_size
                    row = location[1]//square_size  # uses the (x, y) coordinates to allocate a square being clicked
                    if square_selected == (row, column):  # user selecting the same square twice
                        square_selected = ()  # deselects
                        player_clicks = []  # clears player clicks
                    else:
                        square_selected = (row, column)
                        player_clicks.append(square_selected)  # appends for both clicks (selection of piece and move)

                    if len(player_clicks) == 2:  # second click (player wanting to move the piece)
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:   # prevents bugs for en passant and promotion
                                gs.makeMove(validMoves[i])
                                print(move.ChessNotation())
                                moveMade = True
                                # move current square into new square and updates board accordingly
                                square_selected = ()  # resets user clicks so next user can click
                                player_clicks = []
                        if not moveMade:
                            player_clicks = [square_selected]  # the second click of an invalid move is not registered

                    # KEYBOARD OPERATIONS
            elif events.type == p.KEYDOWN:
                if events.key == p.K_z:  # when "z" key is pressed, undo move
                    gs.undoMove()
                    moveMade = True

        #AI move generator
        if running and not humanTurn:
            AIMove = AI.findGreedyMove(gs, validMoves)  # greedy algorithm
            if AIMove is None:
                AIMove = AI.findRandomMove(validMoves)  # close to checkmate and the engine somewhat gives up
            gs.makeMove(AIMove)
            moveMade = True

        if moveMade:    # needs to generate new valid moves since new moves will be made
            validMoves = gs.getValidMoves()
            moveMade = False

        drawgamestate(screen, gs)  # gs = game state
        p.display.flip()


"""
Responsible for the graphics
"""


def drawgamestate(screen, gs):
    drawboard(screen)  # draw squares on the board
    # can add piece highlighting and move suggestion here
    drawpieces(screen, gs.board)  # draw pieces on top of the squares


def drawboard(screen):
    colors = [p.Color("white"), p.Color("dark gray")]
    for rows in range(dimension):
        for columns in range(dimension):
            color = colors[((rows + columns) % 2)]
            # can determine the colour by thinking of the board as coordinates with this formula remainder 1 = black and remainder 0 = white
            p.draw.rect(screen, color, p.Rect(columns * square_size, rows * square_size, square_size, square_size))
            # draws a rectangle of the row 8 times which creates the square board


def drawpieces(screen, board):
    for rows in range(dimension):
        for columns in range(dimension):
            piece = board[rows][columns]
            if piece != "--":  # not an empty square
                screen.blit(IMAGES[piece], p.Rect(columns * square_size, rows * square_size, square_size, square_size))


"""
Login System into the program
"""

def mainmenu():  # after logging into the program, displays the main menu for the game for players to select what to do

    def play():
        maingame()

    def exitwindow():
        menu.destroy()

    menu = tk.Tk()

    canvas2 = tk.Canvas(menu, height=300, width=300, bg="#263D42").pack()

    frame2 = tk.Frame(menu, bg="White")
    frame2.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

    play_button = tk.Button(frame2, text="Train", padx=10, pady=5, fg="White", bg="#263D42", command=play).pack()
    learn_button = tk.Button(frame2, text="Learn", padx=10, pady=5, fg="White", bg="#263D42").pack()
    window_exit_button = tk.Button(frame2, text="Exit", padx=10, pady=5, fg="White", bg="#263D42",
                                   command=exitwindow).pack()
    menu.mainloop()


"""
#Login
"""

def login():  # login system which allows the user to enter a password and username read from a text file
    user = user_name_box.get()
    password = password_box.get()

    UserInformation = (user + "," + password + "\n")
    CorrectUser = False

    file = open("D:/Documents/CODE/Chess/Usernames.TXT", "r")
    data = file.readlines()
    line = 0

    while CorrectUser is False and (user != "" and password != ""):
        lineString = data[line]
        if not lineString:
            welcome_label = tk.Label(root, text="Your Information is not in the file: Incorrect or Create Account")
            welcome_label.pack()
            break
        if lineString == UserInformation:
            CorrectUser = True
            root.destroy()
            mainmenu()
        else:
            line +=1


def exitlogin():
    root.destroy()


"""
#Create Account
"""


def createaccountMENU():

    def createaccount():
        username = user_name_box.get()
        password = password_box2.get()
        confirm = confirmpass.get()
        file = open("D:/Documents/CODE/Chess/Usernames.TXT", "a")

        passwordnumber = password.isnumeric()  # checks if all the characters are integers
        passwordlettes = password.isalpha()  # checks if all characters are letters

        lowerpassword = password.islower()  # this checks to see if the password contains both upper and lower cases
        upperpassword = password.isupper()
        if lowerpassword is True or upperpassword is True:
            CaseRange = False
        else:
            CaseRange = True

        if username != "" and password != "":
            if len(password) >= 6 and CaseRange is True and passwordnumber is False and passwordlettes is False:  # checks if the password is secure (matches the set requirments)
                if password == confirm:
                    file.write(username + "," + password + "\n")
                    file.close()
                    print("Account Created Successfully")
                    account.destroy()
                else:
                    print("Passwords do not match up")
            else:
                print("Need to complete the password requirements")
        else:
            print("All boxes are required to be filled")

    def exitaccount():
        account.destroy()

    account = tk.Tk()

    canvas3 = tk.Canvas(account, height=300, width=300, bg="#263D42").pack()
    frame3 = tk.Frame(account, bg="White")
    frame3.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)
    UserNameLabel2 = tk.Label(frame3, text="Username:").pack()
    user_name_box = tk.Entry(frame3, bd="3")
    user_name_box.pack()
    PasswordLabel2 = tk.Label(frame3, text="Password:").pack()
    password_box2 = tk.Entry(frame3, bd="3")
    password_box2.pack()
    confirmpassLabel = tk.Label(frame3, text="Confirm Password:").pack()
    confirmpass = tk.Entry(frame3, bd=3)
    confirmpass.pack()
    accountcreate = tk.Button(frame3, text="Create Account", padx=10, pady=5, fg="White", bg="#263D42", command=createaccount).pack()
    accountexit = tk.Button(frame3, text="Exit", padx=10, pady=5, fg="White", bg="#263D42", command=exitaccount).pack()
    account.mainloop()


"""
# GUI for the login page
"""


root = tk.Tk()

canvas = tk.Canvas(root, height=300, width=300, bg="#263D42").pack()

frame = tk.Frame(root, bg="White")
frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

Login_Button = tk.Button(frame, text="Login", padx=10, pady=5, fg="White", bg="#263D42", command=login).pack()

Create_Account_Button = tk.Button(frame, text="Create account", padx=10, pady=5, fg="White", bg="#263D42",
                                      command=createaccountMENU).pack()

UserNameLabel = tk.Label(frame, text="User Name:").pack()

user_name_box = tk.Entry(frame, bd=3)
user_name_box.pack()

PasswordLabel = tk.Label(frame, text="Password:").pack()

password_box = tk.Entry(frame, bd=3, show="*")
password_box.pack()

exitlogin = tk.Button(frame, text="Exit", padx=10, pady=5, fg="White", bg="#263D42", command=exitlogin).pack()

root.mainloop()