'''
Created on Nov 19, 2011

@author: taher
'''
class State(object):
    
    def __init__(self,hasArrow = True , orintation = 'N', position = (0,0), holding_gold = False, killedWampus = False, path = []):
        self.orintation = orintation
        self.position = position
        self.holding_gold = holding_gold
        self.path = path.append(position)
        self.killedWampus = killedWampus
        self.hasArrow = hasArrow





