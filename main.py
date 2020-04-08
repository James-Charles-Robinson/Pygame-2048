import pygame
import time
import threading

# Class for the board and calculations todo with the game
class Board():

    def __init__(self):

        self.boardSize = 4
        self.startingAmount = 2
        self.createBoard()
        self.score = 0
        self.AIRuns = 70
        self.AIMaxMoves = 15
        self.AiMode = 0
        self.start = time.time()

    # creates an empty board
    def createBoard(self):
        self.matrix = [[0 for j in range(self.boardSize)] for i in range(self.boardSize)]
        for i in range(self.startingAmount):
            self.new()

    # calculates if the board is full
    def full(self): 
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if self.matrix[i][j] == 0:
                    return False
        return True

    # moves all the numbers in a direction
    def move(self, direction): 

        # the function to move all the numbers up
        def up():
            # moves all the pieces together in the direction
            def slide():
                for i in range(self.boardSize):
                    for j in range(self.boardSize):
                        if i != 0 and self.matrix[i][j] > 0:
                           for g in range(i):
                               if self.matrix[g][j] == 0:
                                   self.matrix[g][j] = self.matrix[i][j]
                                   self.matrix[i][j] = 0
            # combines the neighbours
            def combine():
                for i in range(self.boardSize-1):
                    for j in range(self.boardSize):
                        if self.matrix[i][j] > 0 and self.matrix[i][j] == self.matrix[i+1][j]:
                            self.score += (self.matrix[i][j])*2
                            self.matrix[i][j] = self.matrix[i][j]*2
                            self.matrix[i+1][j] = 0
            slide()
            combine()
            slide()

        # instead of making a function for each direction
        # you can just rotate the board and then perform the same
        # operations as if the numbers were being moved up
        before = [i[:] for i in self.matrix]
        if direction == "up":
            up()
        elif direction == "right":
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            up()
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
        elif direction == "down":
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            up()
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
        else:
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            up()
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]
            self.matrix = [list(r) for r in zip(*self.matrix[::-1])]

        # if the board has actually changed
        if before != self.matrix:
            self.new() # adds a new number
            return False
        else:
            return True
            
    # checks if the player has lost
    def checkLoss(self):
        if self.full() == True:
            if (self.move("up") == True and self.move("right") == True
                and self.move("down") == True and self.move("left") == True):
                return True
        return False

    # adds a new tile to the board in random position
    def new(self): 

        count = 0
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if self.matrix[i][j] == 0:
                    count += 1

        selectedTile = random.randint(1, count)
        count = 0
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if self.matrix[i][j] == 0:
                    count += 1
                    if count == selectedTile:
                        if random.randint(1, 10) == 1:
                            self.matrix[i][j] = 4
                        else:
                            self.matrix[i][j] = 2
                        return

    # finds the highest tile on the board
    def highestTile(self):
        highest = 0
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if self.matrix[i][j] > highest:
                    highest = self.matrix[i][j]
        return highest

    # the first AI, simply tries to move always up and left
    # this is how most players play the game
    # doesnt perform that well, usually only gets to either 512 or 1024
    def AI1(self):
        choices = ["up", "left", "right", "down", ]
        keys = {"up":273, "right":275, "left":276, "down":274}
        bestMove = "up"
        originalMatrix = [i[:] for i in self.matrix]
        originalScore = self.score
        for choice in choices:
            if self.move(choice):
                if self.checkLoss():
                    continue
            else:
                bestMove = choice
                break
            

        self.matrix = [i[:] for i in originalMatrix]
        self.score = originalScore
                    
        return keys[bestMove]

    # the better ai that for each move plays the game and finds out which
    # move on average results in a better score
    # much slower than AI1 but gets to 2048 most of the time
    def AI2(self):
        originalMatrix = [i[:] for i in self.matrix]
        originalScore = self.score
        scores = [[self.score],[self.score],[self.score],[self.score]]
        keys = {"up":273, "right":275, "left":276, "down":274}
        choices = ["right", "down", "up", "left"]
        for i,choice in enumerate(choices):

            if self.move(choices[i]):
                if self.checkLoss():
                    continue
                scores[i] = [1]
            else: # if the move is actually valid
                
                firstMoveMatrix = [j[:] for j in self.matrix]

                # play the game multiple times and add the score
                # to a list
                for g in range(self.AIRuns):
                    count = 0
                    
                    while True:
                        # takes move untill a loss or until it hits max amount
                        # of moves allowed
                        if self.move(random.choice(choices)):
                            if self.checkLoss():
                                scores[i].append(0)
                                break

                        else:
                            count += 1

                        if count >= self.AIMaxMoves:
                            scores[i].append(self.score)
                            break

                                
                    self.matrix = [j[:] for j in firstMoveMatrix]
                    self.score = originalScore

            self.matrix = [j[:] for j in originalMatrix]

        # resets the actual game matrix back to what it was originally
        self.matrix = [j[:] for j in originalMatrix]
        self.score = originalScore
        largestScore = 0
        largestMove = "up"
        # find the move with the highest avg score
        for i,move in enumerate(scores):
            total = 0
            for g in range(len(move)):
                total += move[g]
            avg = total / len(move)
            if avg > largestScore:
                largestScore = avg
                largestMove = choices[i]
        # return the key value
        return keys[largestMove]

# the class that controls the gui and inputs for the game
class Gui():

    def __init__(self):
        self.fps = 60
        self.width = 800

        pygame.init()
        self.win = pygame.display.set_mode((self.width, self.width))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 100)
        self.display = 0

    # the gui main function that runs every tick
    def run(self, board):

        self.board = board
        pygame.display.set_caption("2048 - By James Robinson - Score: "
                                   + str(self.board.score) + " - Largest Tile: " + str(self.board.highestTile()))
        self.clock.tick(self.fps)

        # gets key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                self.keyDown(event.key)
                
        # if game isnt lost
        if self.display == 0:

            self.redraw()
            pygame.display.update()

        # if game is lost
        elif self.display == 1:
            
            self.displayLoss()
            pygame.display.update()
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            # if the reset button is clicked, reset
            if (self.width/2)+100 > mouse[0] > (self.width/2)-100 and (self.width/2)+100 > mouse[1] > (self.width/2)-100:

                if click[0] == 1:
                    self.display = 0
                    self.board.createBoard()
                    self.board.score = 0

    # colour dict
    def colours(self, num):
        colorDict = {
            0:(255,255,255),
            2:(255,0,0),
            4:(255,0,128),
            8:(255,0,255),
            16:(128,0,255),
            32:(0,0,255),
            64:(0,128,255),
            128:(0,255,255),
            256:(0,255,128),
            512:(255,255,0),
            1024:(255,128,0),
            2048:(211,175,55),
            4096:(211,175,55)
        }
        return colorDict[num]

    # handles all the keypresses
    def keyDown(self, key):
        if key == 273:
            if self.board.move("up"):
                if self.board.checkLoss():
                    self.display = 1
        elif key == 275:
            if self.board.move("right"):
                if self.board.checkLoss():
                    self.display = 1
        elif key == 274:
            if self.board.move("down"):
                if self.board.checkLoss():
                    self.display = 1
        elif key == 276:
            if self.board.move("left"):
                if self.board.checkLoss():
                    self.display = 1
        elif key == 49:
            self.board.AiMode = 1
        elif key == 50:
            self.board.AiMode = 2
        elif key == 48:
            self.board.AiMode = 0

    # redraws the board
    def redraw(self):

        self.win.fill((255,255,255))
        self.drawBoard()

    # displays text
    def displayText(self, txt, colour, center):
        textSurf = self.font.render(txt, True, colour)
        textRect = textSurf.get_rect()
        textRect.center = (center)
        self.win.blit(textSurf, textRect)

    # draws the board with the lines, colours and numbers
    def drawBoard(self):

        width = self.win.get_width()
        height = self.win.get_height()
        boardSize = self.board.boardSize
        matrix = self.board.matrix


        for i in range(boardSize):
            for j in range(boardSize):
                pygame.draw.rect(self.win, self.colours(matrix[i][j]),
                                 (j*(width/self.board.boardSize), i*(width/self.board.boardSize), (width/self.board.boardSize), (height/self.board.boardSize)))
        for i in range(boardSize-1):
            pygame.draw.rect(self.win, (0, 0, 0), ((i+1)*(width/self.board.boardSize)-2.5, 0, 5, height))
            pygame.draw.rect(self.win, (0, 0, 0), (0, (i+1)*(width/self.board.boardSize)-2.5, width, 5))
        for i in range(boardSize):
            for j in range(boardSize):
                num = matrix[i][j]
                self.displayText(str(num), (0,0,0), ((((width/self.board.boardSize)*j)+100),(((height/self.board.boardSize)*i)+100)))

    # the loss screen
    def displayLoss(self):
        width = self.win.get_width()
        height = self.win.get_height()
        
        self.win.fill((255,255,255))
        self.displayText("Game Over", (0,0,0), ((width/2), ((height/2)-200)))
        self.displayText("Restart?", (0,0,0), ((width/2), (height/2)))

# creates the board and gui objects
board = Board()
gui = Gui()
while True:
    # run the gui loop
    gui.run(board)
    # run the ai
    if gui.display == 0:
        if board.AiMode == 1:
            key = board.AI1()
            gui.keyDown(key)
        elif board.AiMode == 2:
            key = board.AI2()
            gui.keyDown(key)


