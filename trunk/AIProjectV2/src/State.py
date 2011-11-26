'''
Created on Nov 19, 2011

@author: taher
'''
class State:
    pass
    
    def __init__(self, orintation = 'N', position = (0,0), holdingGold = False, killedWampus = False):
        self.orintation = orintation
        self.position = position
        self.holdingGold = holdingGold
        self.killedWampus = killedWampus

    def __str__(self):
        return  '' + str(self.orintation)+ ', ' + str(self.position)+ ', '+ str(self.holdingGold)+ ', ' + str(self.path)+ ', '+ str(self.killedWampus)





