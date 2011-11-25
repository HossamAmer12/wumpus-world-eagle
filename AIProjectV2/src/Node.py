'''
Created on Nov 21, 2011

@author: taher
'''
from State import State

class Node:
    pass
   
    def __init__(self, action='.', state=None , pathCost=0, actionPath=[], observation=None):
        self.state = State() if state == None else state 
        self.pathCost = 0
        self.action = action
        self.actionPath = []
        self.actionPath.extend(actionPath)
        self.actionPath.append(action)
        self.observation = observation
        
      
    def __str__(self):
        return  'State: ' + str(self.state) + ', PathCost: ' + str(self.pathCost) + ', Action: ' + str(self.action) + ', ActionPath: ' + str(self.actionPath) + ', Observation: ' + str(self.observation)

  
#    def  __cmp__(self, other):
#        if self.pathCost < other.pathCost:
#            return -1
#        elif self.pathCost == other.pathCost:
#            return 0; 
#        else:
#            return 1;   
'''
small Node I think this to work 100% correct like in java it simply can be
return self.pathCost - other.pathCost; and that is set

'''
#http://brandon.sternefamily.net/files/astar.txt
#http://brandon.sternefamily.net/posts/2005/02/a-star-algorithm-in-python/

