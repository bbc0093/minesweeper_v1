#!/usr/bin/env python
#title           :find
#description     :This is used to find an image on the current screen
#author          :William Burdick-Crow
#date            :Aug 26, 2016
#usage           :
#notes           :Support for multiple monitors is limited
#python_version  :3.5
#=============================================================================
import math
import pyautogui as auto
from minesweeper import cell_types 
from minesweeper import cell_rel
import time
import random
import copy


def find_image(image):
    """ find Image on Screen
    Input: Image to be found
    Output: Coords where image is found (left, top, width, height)
    """
    location = auto.locateOnScreen(image, grayscale=True)
    return location

def read_board(reg, gameBoard, game_info, direct):
    """ Updates internal list from board read 
    Input: reg - location of board, gameBoard - object tuple of board state, game_info - information about current game settings
    Output: makes changes to array returns notheing
    """
    mines = 0
    other = 0
    auto.moveTo(1, 1)                                   #move mouse out of the way for screen shot 
    #TODO make so game board in top left dosn't cause errors
    currentGameState = auto.screenshot(region=reg)
    for key in cell_types:
        foundCells = auto.locateAll(direct +"/"+cell_types[key], currentGameState)
        if(foundCells!=None):
            for tup in foundCells:
                x = int((tup[0])/(reg[2]/(game_info.width)))
                y = int((tup[1])/(reg[3]/(game_info.height)))
                gameBoard[x][y].currentValue = key

def click(cell, sleeptime):
    """ clicks on cells 
    Input: cell object (from minesweeper.py), time between clicks
    Output: mouse clicks 
    """
    if(cell.isBomb and cell.currentValue == 10):
        auto.click(cell.screenLocX, cell.screenLocY, button = "right")
        time.sleep(sleeptime)
        print("RClicking " +str(cell.x) +","+str(cell.y))          
    elif(cell.isSafe and cell.currentValue == 10):
        auto.click(cell.screenLocX, cell.screenLocY, button = "left")
        print("Clicking " +str(cell.x) +","+str(cell.y))
        time.sleep(sleeptime)

def gameEnd(FullGameBoard, direct):
    """ Looks for end game notifications from minesweeper client
    Input: none
    Output: game state (lost, won, or None)
    """
    currentGameState = auto.screenshot(region=FullGameBoard)
    if(auto.locate(direct +"/reset_lost.png", currentGameState)!=None):
        return "Lost"
    elif(auto.locate(direct +"/reset_won.png", currentGameState)!=None):
        return "Won"
    else:
        return None
               
def randClick(gameBoard, thisGame, stdProb, listOfUnk):
    """ randomly clicks on a cell in game board
    Input: gameBoard - list of board characteristics, thisGame - game settigns
    Output: click on a random cell in the game board
    """
    while (True):
        nonRand = probCalc(gameBoard, stdProb)
        for cell in listOfUnk:
            startX = cell[0]
            startY = cell[1]
            if(gameBoard[startX][startY].mineProb == None): 
                break
        else:
            stdProb = 1                            #checks for cells where no information is known 
            nonRand = probCalc(gameBoard, stdProb)
        
        if(nonRand[0]!= None):
            startX = nonRand[0]
            startY = nonRand[1]
            print("NRandClick ("+str(startX)+","+str(startY)+")")
        else:
            a = 0
            while(a<50):                  #prevent program from getting hung in while(True)
                cell = listOfUnk[random.randint(0, len(listOfUnk)-1)]
                startX = cell[0]
                startY = cell[1]
                if(gameBoard[startX][startY].currentValue == 10 and (gameBoard[startX][startY].mineProb == None or stdProb == 1)):
                    print("RandClick ("+str(startX)+","+str(startY)+")")
                    break
                a=a+1
        if(gameBoard[startX][startY].currentValue == 10):
            auto.click(gameBoard[startX][startY].screenLocX, gameBoard[startX][startY].screenLocY)      #First click make the game the active window
            auto.click(gameBoard[startX][startY].screenLocX, gameBoard[startX][startY].screenLocY)       
            break
            
def probCalc(myList, stdProb):
    """ Calculates the probability of any cell being a mine 
    Input: list of cell objects
    Output: writes .mineProb values to cells, returns cell with lowest probability of being a mine 
    """
    lowest = [None,None,1]
    for row in myList:
        for cell in row:
            if(cell.currentValue == 10):
                finalProb = 0
                for coord in cell._cell__cell_rel:
                    adjCell = myList[cell.x+coord[0]][cell.y+coord[1]]
                    if(adjCell.currentValue != 9 and adjCell.currentValue != 10):         #includes a check for there being no true random cells
                        try:
                            prob = (adjCell.currentValue-adjCell.adjMines)/adjCell.adjUn                    
                            if(prob>finalProb):
                                    finalProb = prob
                        except ZeroDivisionError:
                            pass
                if(finalProb != 0):
                    if(prob < lowest[2] and finalProb < stdProb):
                        lowest[0]=cell.x                       
                        lowest[1]=cell.y
                        lowest[2]=prob
                    cell.mineProb = finalProb
                
    return lowest 

def listContains(A, B):
    contains = False
    for i in range(0, len(A)):
        if (A[i] == B[0]):
            if (len(B) + i > len(A)):
                break
            for j in range(0, len(B)):
                if (B[j] == A[i + j]):
                    contains = True
                else:
                    contains = False
                    break
    return contains            
                
def findEdge(gameBoard, thisGame):
    """used to find edges in board 
    Input:gameboard, thisGame
    Output:list containing edge, returns true if changes were made 
    """
    edgeList = []
    for row in gameBoard:
        for cell in row:
            for orient in range(0,4):
                cellList = []
                edgeLoc(gameBoard, thisGame, orient, cell.x, cell.y, cellList)
                if(len(cellList)>2):
                    if (edgeList == []):
                        edgeList.append((cellList, orient))
                    else:
                        cont = False
                        for list in edgeList:
                            if(listContains(list[0], cellList)):
                                cont = True
                        if(cont==False):
                            edgeList.append((cellList, orient))
    toRet = False
    if (edgeList != []):
        print(edgeList)
        for pair in edgeList:
            if(edgeSim(gameBoard, thisGame, pair[0], pair[1])):
                toRet = True
    return toRet    
        
def edgeSim(gameBoard, thisGame, cellList, orient):
    """Simulates bomb placement on a given edge 
    Input:gameBoard, thisGame, list containing edge, orientation of edge, (0-left, 1-right, 2-top, 3-bottom) 
    Output:changes isSafe and isBomb of relevant cells, returns true if changes were made
    """
    testList = []
    eval = []
    ending = []
    
    normalize(gameBoard, eval, orient, cellList, thisGame, testList, ending)
    
    for pair in testList:           
        if (pair[0].isBomb):         #mines in edge represented by 0
            eval.append(0)
        else:        
            eval.append(pair[0].currentValue - pair[0].adjMines)
        
    eval.extend(ending)                         #adds ending to end of eval
    
    results = []
    mines = [] 
    simIter(eval,mines, results)                 #runs through sim
        
    passed = []
    for result in results:
        if(not result[1]):             #look at passed results
            passed.append(result[0])
    
    final = []    
    if(passed != []):
        for i in range(0, len(results[0][0])):
            hold = passed[0][i]
            held = True
            if(eval[i] != -1):
                for items in passed:
                    if(items[i] != hold):
                        held = False
                if(held and hold[1]):
                    final.append(hold[0])
                else:
                    final.append(-1)
    print(eval)
    print(results)
    print(passed)            
    print("Final = "+str(final))
    
    toRet = False
    for i in range (0,len(final)):
        if(final[i] == 1):
            testList[i][1].isBomb = True
            click(testList[i][1], .1)
            toRet = True
        elif(final[i] == 0):
            testList[i][1].isSafe = True
            click(testList[i][1], .1)
            toRet = True
    return toRet

def normalize(gameBoard, eval, orient, cellList, thisGame, testList, ending):
    """ normalizes edges to standard format 
    Input:gameBoard, eval, orient, cellList, thisGame, testList
    Output: updated testList and eval 
    """
    if(orient == 0):                                          #converts cells to a standard form for sim
        if(gameBoard[cellList[0][0]][cellList[0][1]].y == 0 or all(gameBoard[cellList[0][0]+n][cellList[0][1]-1].currentValue != 10 for n in range(-1,2))):
            eval.append(-1)
        if(gameBoard[cellList[-1][0]][cellList[-1][1]].y == thisGame.height-1 or all(gameBoard[cellList[-1][0]+n][cellList[-1][1]+1].currentValue != 10 for n in range(-1,2))):
            ending.append(-1)    
        for cell in cellList:       #left
            testList.append((gameBoard[cell[0]][cell[1]],gameBoard[cell[0]+1][cell[1]]))
    elif(orient == 1):
        if(gameBoard[cellList[0][0]][cellList[0][1]].y == 0 or all(gameBoard[cellList[0][0]+n][cellList[0][1]-1].currentValue != 10 for n in range(-1,2))):
            eval.append(-1)
        if(gameBoard[cellList[-1][0]][cellList[-1][1]].y == thisGame.height-1 or all(gameBoard[cellList[-1][0]+n][cellList[-1][1]+1].currentValue != 10 for n in range(-1,2))):
            ending.append(-1)  
        for cell in cellList:       #right
            testList.append((gameBoard[cell[0]][cell[1]],gameBoard[cell[0]-1][cell[1]]))
    elif(orient == 2):
        if(gameBoard[cellList[0][0]][cellList[0][1]].x == 0 or all(gameBoard[cellList[0][0]-1][cellList[0][1]-n].currentValue != 10 for n in range(-1,2))):
            eval.append(-1)
        if(gameBoard[cellList[-1][0]][cellList[-1][1]].x == thisGame.width-1 or all(gameBoard[cellList[-1][0]+1][cellList[-1][1]+n].currentValue != 10 for n in range(-1,2))):
            ending.append(-1)  
        for cell in cellList:       #top
            testList.append((gameBoard[cell[0]][cell[1]],gameBoard[cell[0]][cell[1]+1]))
    elif(orient == 3):
        if(gameBoard[cellList[0][0]][cellList[0][1]].x == 0 or all(gameBoard[cellList[0][0]-1][cellList[0][1]-n].currentValue != 10 for n in range(-1,2))):
            eval.append(-1)
        if(gameBoard[cellList[-1][0]][cellList[-1][1]].x == thisGame.width-1 or all(gameBoard[cellList[-1][0]+1][cellList[-1][1]+n].currentValue != 10 for n in range(-1,2))):
            ending.append(-1) 
        for cell in cellList:       #bottom
            testList.append((gameBoard[cell[0]][cell[1]],gameBoard[cell[0]][cell[1]-1]))   
            
def simIter(eval, mines, results):
    """ contain simulation iterations 
    Input:eval, mines, results
    Output:appeded results
    """ 
    for sim in range(0,3):
        if(eval[sim]==-1 and eval[sim+1] != 0):                      #skips first scenario if on an edge
            continue
        mines = []
        for cell in eval:
            if(cell == -1):
                mines.append([0,1])
            else:
                mines.append([0,0])
        
        simoffset = -1                           #offset used to skip mines at beginning of edge
        for val in eval:
            if(val == 0 or val == -1):
                simoffset +=1
            else:
                break 
            
        if(simoffset == -1):
            simoffset = 0
            
        elif(simoffset == (len(mines)-1)):
            break
            #TODO: look at this
        try:
            mines[sim+simoffset]=[1,1]                        #seeds the sims - eval on a edge can only be 1 or 2
            if(eval[1] == 2):               
                if(sim == 2):
                    mines[0+simoffset] = [1,1]
                else:
                    mines[sim+1+simoffset]=[1,1]
        except IndexError:                                   #if sim is out of range skip it usually happen with an edge of mines   
            continue
               
        partial = []                           #allows the function to pass back a incomplete state
        failedSim,breakOff = simEval(eval, mines, partial)        
        results.append((mines,failedSim))
        
        while(breakOff):
            print("Re-Running")
            for list in partial:
                mines = list[:]
                (failedSim,breakOff) = simEval(eval, mines, partial)
                results.append((mines,failedSim))
          
def simEval(eval, mines, records):
    """Logic in the simulatuion 
    Input:eval - normalized list, mines - list for reporting mine conclusions, hold - used to deal with split offs 
    Output: updated mines and hold, returns (faildsim, breakoff) if the sim was a fail and if there was a split
    """
    breakOff = False
    failedSim = False
    hold = []
    for i in range(1,len(eval)-1):          #test sims
        a = [mines[i+x][0] for x in range(-1,2)]              
        if(eval[i] == 0):                               #if cell is a mine then skip it
            #input("Waiting :")
            continue
        elif(eval[i]==sum(a)):                          #if cell is satisfied then all others are safe
            for j in range(-1,2):
                    mines[i+j][1] = 1
        elif(eval[i]>sum(a)):                           #if cell is needs more mines then add until satisfied
            for j in range(-1,2):
                hold = copy.deepcopy(mines)
                if(mines[i+j] == [0,0]):
                    mines[i+j] = [1,1]
                    a = [mines[i+x][0] for x in range(-1,2)]
                    if(eval[i]==sum(a)):
                        if(j != 1):                                 #allows for multiple possibilities to be considered 
                            breakOff = True
                            hold[i+j] = [0,1]
                            records.append(copy.deepcopy(hold))
                        for j in range(-1,2):
                            if(mines[i+j] == [0,0]):
                                mines[i+j] = [0,1]
                        break
            else:                           #if cell can't be satisfied fail test 
                failedSim = True
                break
        elif(eval[i]<sum(a)):                           #if cell has too many mines fail test
            failedSim = True
            break
    if((eval[0] < sum([mines[0][0],mines[1][0]])) and eval[0] != -1 and eval[0] != 0):
        failedSim = True
    end = len(eval)-1
    if((eval[end] < sum([mines[end-1][0],mines[end][0]])) and eval[end] != -1 and eval[end] != 0):
        failedSim = True
    
    return (failedSim, breakOff)
                
def edgeLoc(gameBoard, thisGame, orient, x, y, cellList): 
    """ used to check if cell is part of an edge
    Input: gameBoard, thisGame, orientation to look for(0-left, 1-right, 2-top, 3-bottom), coords of the cell, an list of cells that are part of this edge
    Output: appends to the list if this cell should be part of the edge
    """
    try:
        cell = gameBoard[x][y]
        if(cell.currentValue != 10):
            if(orient==0):
                if(x == 0 or gameBoard[x-1][y].currentValue != 10):
                    if(x != thisGame.width-1 and gameBoard[x+1][y].currentValue == 10):
                        cellList.append((x,y))
                        edgeLoc(gameBoard, thisGame, orient, x, y+1,cellList)
            elif(orient==1):
                if(x == thisGame.width-1 or gameBoard[x+1][y].currentValue != 10):
                    if(x != 0 and gameBoard[x-1][y].currentValue == 10):
                        cellList.append((x,y))
                        edgeLoc(gameBoard, thisGame, orient, x, y+1,cellList)
            elif(orient==2):
                if(y == 0 or gameBoard[x][y-1].currentValue != 10):
                    if(x != thisGame.height-1 and gameBoard[x][y+1].currentValue == 10):
                        cellList.append((x,y))
                        edgeLoc(gameBoard, thisGame, orient, x+1, y,cellList)
            elif(orient==3):
                if(y == thisGame.height-1 or gameBoard[x][y+1].currentValue != 10):
                    if(y != 0 and gameBoard[x][y-1].currentValue == 10):
                        cellList.append((x,y))
                        edgeLoc(gameBoard, thisGame, orient, x+1, y,cellList)   
    except IndexError:        
            pass     
            
def testMode(gameBoard):
    if(input("Test Mode? (Y/N): ")=="Y"):
        while(True):
            x = int(input("x? :"))
            if(x==10):
                break
            y = int(input("y? :"))
            print("eval = " + str(gameBoard[x][y].eval(gameBoard)))
            print("AdjB = " + str(gameBoard[x][y].getAdjBombs(gameBoard)))
            print("Adj = " + str(gameBoard[x][y].getAdj(gameBoard, 10)))
            print("isS = " + str(gameBoard[x][y].isSafe))
            print("isB = " + str(gameBoard[x][y].isBomb))
            print("currVal = " + str(gameBoard[x][y].currentValue)) 
                      
                