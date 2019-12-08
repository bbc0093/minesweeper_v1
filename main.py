#!/usr/bin/env python
#title           :find
#description     :This is the main file used to solve a gmae of mine sweeper
#author          :William Burdick-Crow
#date            :Aug 26, 2016
#usage           :
#notes           :Support for multiple monitors is limited
#python_version  :3.5
#=============================================================================

#import ctypes
import pyautogui as auto
import find
import minesweeper
from minesweeper import std_boards
import random
import time

random.seed()                                   #seeds RNG
class found(Exception): pass                    #allows exiting of embedded loops 
restart = True
runs = 0
evalT, hungT, ClickingT, ScreenReadT, RandClickT = (0,)*5

if (__name__ == "__main__"):
    direct = minesweeper.setup()
    while (restart):
        restart = False
        print("Looking for game board...")
        try:
            while True:
                reset_but = find.find_image(direct +"/NewRecordText.png")
                if (reset_but != None):
                    reset_but = None
                    print("New Record!!")
                    while (reset_but == None):
                        reset_but = find.find_image(direct +"/NewRecord1.png")
                    auto.click((reset_but[0]+reset_but[2]/2),(reset_but[1]+reset_but[3]/2))
                    reset_but = None
                    while (reset_but == None):   
                        reset_but = find.find_image(direct +"/NewRecord2.png")
                    auto.click((reset_but[0]+reset_but[2]/2),(reset_but[1]+reset_but[3]/2))
                if (reset_but == None):
                    reset_but = find.find_image(direct +"/NewRecord2.png")
                if (reset_but == None):
                    reset_but = find.find_image(direct +"/reset.png")
                if (reset_but == None):
                    reset_but = find.find_image(direct +"/reset_lost.png")
                if (reset_but == None):
                    reset_but = find.find_image(direct +"/reset_won.png")     
                if (reset_but != None):
                    auto.click((reset_but[0]+reset_but[2]/2),(reset_but[1]+reset_but[3]/2)) 
                    #auto.click((reset_but[0]+reset_but[2]/2),(reset_but[1]+reset_but[3]/2))    
                    for key in std_boards:
                        Lboard_dem = find.find_image(direct +"/"+std_boards[key].fullBoardImage)
                        if(Lboard_dem != None):
                            this_game = std_boards[key]
                            board_dem = find.find_image(direct +"/"+std_boards[key].boardImage)
                            currentGameState = auto.screenshot(region=board_dem)
                            raise found
                if(direct == "Mines"):
                    for key in std_boards:
                        Lboard_dem = find.find_image(direct +"/"+std_boards[key].fullBoardImage)
                        if(Lboard_dem != None):
                            this_game = std_boards[key]
                            board_dem = find.find_image(direct +"/"+std_boards[key].boardImage)
                            currentGameState = auto.screenshot(region=board_dem)
                            raise found
                    
        except found:            
            print("Game board found: " + str(this_game.difficulty))
    
        gameBoard = [[minesweeper.cell(this_game.width,this_game.height,x,y,this_game.mines,board_dem) for y in range(this_game.height)] for x in range(this_game.width)]
        mines = this_game.mines
        stdProb = mines/(this_game.width*this_game.height)                                          #records the probability that a random cell is a mine 
        unkList = [(a,b)for a in range(this_game.width) for b in range(this_game.height)]         #makes a list of unknown cells for the random click function
        #Pick a starting point
        find.randClick(gameBoard, this_game, stdProb, unkList)
        find.read_board(board_dem, gameBoard, this_game, direct)
        gameOver = False                                #used to determine a finished game
        hung = 0
        randClicks = 0
        hung_flag = False
        ts = time.time()
        while(not gameOver):
            print("Thinking...")
            changed = []
            t0 = time.time()
            mines = 0 
            unk = 0
            unkList = []
            for row in reversed(gameBoard):
                for cell in reversed(row):
                    changed = changed + (cell.eval(gameBoard))                       #runs logic on cells    
            for row in gameBoard:
                for cell in row:
                    changed = changed + (cell.eval(gameBoard))                       #runs logic on cells    
                    if(cell.currentValue == 9):
                        mines = mines + 1
                    elif(cell.currentValue == 10):
                        unkList.append((cell.x,cell.y))
                        unk = unk + 1
            try:            
                stdProb = (this_game.mines-mines)/unk
                #print("StdProb: %5.3F" %stdProb)
            except Exception:
                 pass
            t1 = time.time()       
            if(changed != []):
                hung= 0
                hung_flag = False
            
            th0,th1,th2,th3,th4 = (0,)*5    
            if (hung >= 1):
                th0 = time.time()
                for row in gameBoard:
                    for cell in row:
                        find.click(cell, .1)                                        # verifies that no clicks have been missed 
                hung = 0
                th1 = time.time()
                gameState = find.gameEnd(Lboard_dem,direct)        
                if(gameState != None):
                    runs = runs + 1
#                     if(gameState == "Won"):
#                         restart = True
                    if(mines <= (this_game.mines*.25)):
                        restart = True                                              # tell program to restart if program failed early
                    else:
                        runs += 1
                    if(runs <= 500):
                         restart = True
                    gameOver = True
                    tf = time.time() - ts 
                    break
                th2 = time.time()
                if(hung_flag):
                    if(not find.findEdge(gameBoard, this_game)):
                        th3 = time.time()
                        try:
                            find.randClick(gameBoard, this_game, stdProb, unkList)
                            randClicks = randClicks + 1
                        except:
                            gameOver = True
                            gameState = "won"
                            tf = time.time() - ts
                        th4 = time.time()-th3
                        th3 = th3-th2
                        
                hung_flag = True
                
                print("Re-Click: %(re-click)5.3f, Screen Read: %(findstate)5.3f, Edge Find: %(edge)5.3f, Rand Clicking: %(final)5.3f" \
                   %{"re-click":th1-th0,"findstate":th2-th1,"edge":th3, "final":th4})
            t2 = time.time()         
            for item in changed:
                cell = gameBoard[item[0]][item[1]]  
                find.click(cell, .1)
            t3 = time.time()
                    
            find.read_board(board_dem, gameBoard, this_game, direct)
            hung += 1
            t4 = time.time()
            
            ##   timing data  ##
            evalT += t1-t0
            hungT += (th1-th0) + (th3)
            ClickingT += t3-t2
            ScreenReadT += (t4-t3)+(th2-th1)
            RandClickT += th4
            print("Eval: %(eval)5.3f, Hung Logic: %(hung)5.3f, Clicking: %(click)5.3f, Screen Read: %(read)5.3f" \
                   %{"eval":t1-t0,"hung":th3,"click":t3-t2,"read":t4-t3})
            
            
            
        #find.testMode(gameBoard)        
        out = str("Done!! I " + gameState + " (Difficulty: %s, Mines Left: %i, Time: %5.3fS, Random Clicks: %i)" %(this_game.difficulty, this_game.mines-mines, tf, randClicks) )
        print(out)
        f = open(direct +"/minesweeper_log.txt", "a")
        out = str(gameState + ",%s,%i,%5.3f,%i" %(this_game.difficulty, this_game.mines-mines, tf, randClicks))
        out2 = str("%s,%s,%s,%s,%s" %(evalT,hungT,ClickingT,ScreenReadT,RandClickT))
        f.write(out+out2+"\n")
        print("Eval: %(eval)5.3f, Hung Logic: %(hung)5.3f, Clicking: %(click)5.3f, Screen Read: %(read)5.3f, RandClick: %(rand)5.3f" \
                      %{"eval":evalT,"hung":hungT,"click":ClickingT,"read":ScreenReadT, "rand":RandClickT})
   
