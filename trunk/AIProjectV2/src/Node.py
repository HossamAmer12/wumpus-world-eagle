'''
Created on Nov 21, 2011

@author: taher
'''
from State import State

class Node:
    pass
   
    def __init__(self,  action = '.',state=None , pathCost = 0, actionPath = [],observation=None):
        self.state = State() if state==None else state 
        self.pathCost = 0
        self.action= action
        self.actionPath = []
        self.actionPath.extend(actionPath)
        self.actionPath.append(action)
        self.observation = observation
        
      
    def __str__(self):
        return  'State: ' + str(self.state)+ ', PathCost: ' + str(self.pathCost)+ ', Action: '+ str(self.action)+ ', ActionPath: ' + str(self.actionPath)+ ', Observation: '+ str(self.observation)
  
      
        


