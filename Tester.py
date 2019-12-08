#!/usr/bin/env python
#title           :Tester
#description     :This is used to find an image on the current screen
#author          :William Burdick-Crow
#date            :Sep 28, 2016
#usage           :
#notes           :Support for multiple monitors is limited
#python_version  :3.5
#=============================================================================

import find
import minesweeper
import pyautogui as auto
def edgeSimTest ():
    """tests edge sim by forcing in a defined eval 
    Input:none    
    Output:none
    """
    eval = [2,2,1,1]
    mines = []
    results = []
    find.simIter(eval, mines, results)
    
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
    print("Results: ")
    for result in results:
        print(result)
    print("Passed: ")
    for item in passed:
        print(item)            
    print("Final: \n"+str(final))

def testPrint():
    print("I ran")
    return False
    
if(__name__ == "__main__"):
#     exit = False
#     while(not exit):
#         edgeSimTest()
#         if(input("Run Again? :") != "y"):
#             exit = True
    if(True and testPrint()):
        pass