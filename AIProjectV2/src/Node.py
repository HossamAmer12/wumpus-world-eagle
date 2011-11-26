'''
Created on Nov 21, 2011

@author: taher
'''
from State import State

class Node:
    pass
    count=0 #static counter 
    '''
       class Node
           state 
           pathCost 
           actionPath
           observation
           heuristic
           depth
    '''     
   
    def heuristicValue(self):
        '''
        the heuristic fuction
        '''
        if self.state.holdingGold:
            x = self.state.position[0]
            y = self.state.position[1]
            return  x + y
        else:
            return 1
        
   
    def __init__(self,action='.', state=None , pathCost=0, actionPath=[], observation=None,parentNodeIn=None):
        self.state = State() if state == None else state 
        self.pathCost = pathCost
        self.action = action
        self.actionPath = []
        self.actionPath.extend(actionPath)
        self.actionPath.append(action)
        self.observation = observation
        self.heuristic = self.heuristicValue()
        self.depth=len(self.actionPath)-1
        self.id=Node.count
        Node.count+=1 
        self.parentNode=parentNodeIn
        
      
    def __str__(self):
        return  'id ' +str(self.id)+', state '+str(self.state)+ ', PathCost: ' + str(self.pathCost) + ', Action: ' + str(self.action) #+ ', ActionPath: ' + str(self.actionPath) + ', Observation: ' + str(self.observation)

