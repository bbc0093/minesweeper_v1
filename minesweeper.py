#!/usr/bin/env python
#title           :minesweeper
#description     :The file contains characteristics of the game minesweeper
#author          :William Burdick-Crow
#date            :Aug 26, 2016
#usage           :
#notes           :
#python_version  :3.5
#=============================================================================
class game_board:
    def __init__(self, difficulty, height, width, mines, pic, pic2):
        self.difficulty = difficulty
        self.width = width
        self.height = height
        self.mines = mines
        self.boardImage = pic
        self.fullBoardImage = pic2

std_boards = {"expert": game_board("expert", 16,30,99, "expert.png", "expert_full.png"), "intermediate": \
              game_board("intermediate", 16,16,40, "intermediate.png", "intermediate_full.png"), \
              "beginner": game_board("beginner", 9,9,10, "beginner.png","beginner_full.png") }

cell_rel = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
cell_types = {0:"0.png", 1:"1.png", 2:"2.png", 3:"3.png", 4:"4.png", 5:"5.png", 6:"6.png", 7:"7.png", \
              8:"8.png", 9:"flag.png", 10:"bomb.png"}

class cell:
    def __init__(self, boardX, boardY, x, y, mines, screenDem):
    
        if (x == 0):                            #defines type of tile (corner, edge, ect.)
            if(y == 0):
               self.type = "TLC"
               self.__cell_rel = cell_rel[4:5]+cell_rel[6:8] #defines cells that effect bomb counter
            elif(y == boardY-1):
                self.type = "BLC"
                self.__cell_rel = cell_rel[3:4]+cell_rel[5:7] 
            else:
                self.type = "LE"
                self.__cell_rel = cell_rel[3:8]
        elif(x == boardX-1):
            if(y == 0):
               self.type = "TRC"
               self.__cell_rel = cell_rel[1:3]+cell_rel[4:5]
            elif(y == boardY-1):
                self.type = "BRC"
                self.__cell_rel = cell_rel[0:2]+cell_rel[3:4]
            else:
                self.type = "RE"
                self.__cell_rel = cell_rel[0:5]
        elif(y == 0):
            self.type = "TE"
            self.__cell_rel = cell_rel[1:3]+cell_rel[4:5]+cell_rel[6:8]
        elif(y == boardY-1):
            self.type = "BE"
            self.__cell_rel = cell_rel[0:2]+cell_rel[3:4]+cell_rel[5:7]
        else: 
            self.type = "N"
            self.__cell_rel = cell_rel
        self.currentValue = 10                               #0-8 are possible values, 9 is flagged, 10 is unknown
        self.isSafe = False
        self.isBomb = False
        self.x = x
        self.y = y
        self.screenLocX = screenDem[0]+(screenDem[2]*((2*x+1)/(2*boardX)))
        self.screenLocY = screenDem[1]+(screenDem[3]*((2*y+1)/(2*boardY)))
        self.mineProb = None
        self.adjMines = 0
        self.adjUn = 8
        
    def eval(self, myList):
        """Logic used to solve minesweeper game
        Input: current board state list
        Output: returns True if anything was changed 
        """
        changed = []
        self.adjMines = self.getAdjBombs(myList)
        if (self.adjMines==self.currentValue):
            for rel in self.__cell_rel:
                x = self.x+rel[0]
                y = self.y+rel[1]
                if(not myList[x][y].isSafe and not myList[x][y].isBomb):
                    myList[x][y].isSafe = True
                    changed.append((x,y))
        
        self.adjUn = self.getAdj(myList, 10)
        if ((self.adjUn+self.adjMines)==self.currentValue and self.currentValue != 10 and self.currentValue != 9):                    #counts number of adjacent unknown tiles 
            for rel in self.__cell_rel:
                x = self.x+rel[0]
                y = self.y+rel[1]
                if(not myList[x][y].isBomb and myList[x][y].currentValue == 10 and not myList[x][y].isSafe):
                    myList[x][y].isBomb = True
                    changed.append((x,y))   
        #TODO rest of logic 
        return changed
            
    def getAdjBombs(self, myList):
        """ finds number of adjacent bombs 
        Input: current board state list
        Output: returns number found
        """
        sum = 0
        for rel in self.__cell_rel:
            if(myList[self.x+rel[0]][self.y+rel[1]].isBomb):
                sum += 1
        return sum
    
    def getAdj(self, myList, value):
        """ finds number of adjacent tile that have a currentValue = value 
        Input: current board state list, value that you are looking for
        Output: returns number found
        """            
        sum = 0
        for rel in self.__cell_rel:
            if((myList[self.x+rel[0]][self.y+rel[1]].currentValue == value) and \
              (not myList[self.x+rel[0]][self.y+rel[1]].isSafe)):
                sum += 1
        return sum                
                
    def setProb(self, myList, adjUN, adjBomb):
        """ Function that sets probability that a cell is a mine only overwrites if probability is greater than current value
        Input: list of cell objects, number of adjacent unknowns
        Output: sets probability in adjacent cells 
        """            
        prob = (self.currentValue-adjBomb)/adjUN
        for rel in self.__cell_rel:        
            if(myList[self.x+rel[0]][self.y+rel[1]].currentValue == 10):
               if (prob < myList[self.x+rel[0]][self.y+rel[1]].mineProb):
                   myList[self.x+rel[0]][self.y+rel[1]].mineProb = prob
                
def setup():
    """ sets up directory for which minesweeper version is being used
    Input:none
    Output:string containing name of directory 
    """
    print("Choose Minesweeper Version: \n1) XP_Minesweeper \n2) Mines \n3) Other")
    version = int(input("Choose one : "))
    if(version == 1):
        folder = "MSsweeper"
    elif(version == 2):
        folder = "Mines"
    elif(version == 3):
        folder = input("Enter folder name: ")
    else:
        print("Invalid option")
        folder = setup()
    return folder