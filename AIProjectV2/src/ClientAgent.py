

import Node
import State

EGALE = 1
AGENT = 0




agenda = AGENT
successoStates = []
partialStateNodes = []
q = []
actions = ['f', 'l', 'r', 'c', 'g', 'a']
strategies = ['BFS', 'DFS']
strategyIndex = 1
pathToGoal = []
pathToGoalIndex = 0

def agent_start(observation):
    global strategyIndex, partialStateNodes, q, agenda, pathToGoalIndex
    
  
    initPartialNode = Node()
     
    strategyIndex = -1 
    partialStateNodes = []
    q = []
    agenda = EGALE
    pathToGoalIndex = -1
    return (['.', []])


def agent_step(observation):
    global successorStates, agenda, q, pathToGoal, partialStateNodes, pathToGoalIndex
    if agenda == EGALE:
        successorStates = updateWorkingNodeSet(partialStateNodes, observation)
        q = enqueue(q, successoStates)
        if q == []:
            return (['x'], [])
        first = q.pop(0)
        if goal(first):
            pathToGoal = createPathToGoal(first)
            agenda = AGENT
            return (['.'], [])
        
        
        partialStateNodes = getSuccessorStates(first)
        return getCellsNeededForDiscovery(partialStateNodes) 
    
    if agenda == AGENT:
        pathToGoalIndex += 1
        return ([pathToGoal[pathToGoalIndex]], [])
         
         
        
        

def getCellsNeededForDiscovery(nodes):
    #to Do but return should be like that
   return 
        
        
def getSuccessorStates(parentNode):
    
    oldState=parentNode.state

    tempNodes=[]
    
    # validating Action c
    if oldState.position == (0,0) and oldState.holdingGold:
        newState=State(oldState.hasArrow,oldState.orintation, oldState.position,oldState.holdingGold, oldState.killedWampus, oldState.path)
        newNode=Node('c',newState,parentNode.pathCost+actionCost('c'),parentNode.actionPath)
        newNode.actionPath.append('x')
        tempNodes.append(newNode)
        return tempNodes
    
    # validating Action g
    if parentNode.observation[0] == 1:
        newState=State(oldState.hasArrow,oldState.orintation, oldState.position,True, oldState.killedWampus, oldState.path)
        newNode=Node('g',newState,parentNode.pathCost+actionCost('g'),parentNode.actionPath)
        tempNodes.append(newNode)
        return tempNodes
    
    # validating Action f
    validPosition,newPosition = newPosition(parentNode.state.position, parentNode.state.orintation, 'f')
    if validPosition:
        newState=State(oldState.hasArrow,oldState.orintation, newPosition,oldState.holdingGold, oldState.killedWampus, oldState.path)
        newNode=Node('f',newState,parentNode.pathCost+actionCost('f'),parentNode.actionPath)
        tempNodes.append(newNode)
        
    
    
    # validating Action r
    newOrientation = newOrintation(oldState.orintation, 'r')
    newState=State(oldState.hasArrow,newOrientation, oldState.position,oldState.holdingGold, oldState.killedWampus, oldState.path)
    newNode=Node('r',newState,parentNode.pathCost+actionCost('r'),parentNode.actionPath)
    tempNodes.append(newNode)

    # validating Action l
    newOrientation = newOrintation(oldState.orintation, 'l')
    newState=State(oldState.hasArrow,newOrientation, oldState.position,oldState.holdingGold, oldState.killedWampus, oldState.path)
    newNode=Node('l',newState,parentNode.pathCost+actionCost('l'),parentNode.actionPath)
    tempNodes.append(newNode)

    # validating Action a
    if oldState.hasArrow:
        newState=State(False,oldState.orintation, oldState.position,oldState.holdingGold, True, oldState.path)
        newNode=Node('a',newState,parentNode.pathCost+actionCost('a'),parentNode.actionPath)
        tempNodes.append(newNode)
    
    return tempNodes

def newPosition(position, orintation, action):
    orient = ['N', 'E', 'S', 'W']
    index = orient.index(orintation)
    shifts = [0, 1, 1, 0, 0, -1, -1, 0]
    
    if action == 'f':
        if -1 < position[0] + shifts[index * 2] < 12 and -1 < position[1] + shifts[index * 2 + 1] < 12:
            
            position = (position[0] + shifts[index * 2], position[1] + shifts[index * 2 + 1])
            return True, position
        else:
            return False, position
   
    return True, position
         
    
def newOrintation(orintation, action):
    orint = ['N', 'E', 'S', 'W']
    index = orint.index(orintation)
    if action == 'l':
        index = (index - 1) % 4
    elif action == 'r':
        index = (index + 1) % 4
    
    return orint[index]
        
def actionCost(action):
    return 1

def createPathToGoal(node):
    #ToDO
    return []


def updateWorkingNodeSet(partialNodes, observation):
    #TO DO  
    return []


def enqueue(que, listOfNodes):
    # insert according to the strategy
    if strategyIndex == 0: #BFS
        que.extend(listOfNodes)
    elif strategyIndex == 1: #DFS
        map(lambda x: que.insert(0, x), listOfNodes)
    return que

def goal(node):
    if node.state.position == (0,0) and node.state.holdingGold :
        return True
    else:
        return False
    
s = [1]
d = [2, 34, 455]
s = enqueue(s, d)
print ([2], [3])
print agenda
agent_start(None)
print agenda




        
