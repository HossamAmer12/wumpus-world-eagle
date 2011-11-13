

EGALE=1
AGENT=0




agenda=AGENT
successoStates=[]
partialStateNodes=[]
q=[]
strategies=['BFS','DFS']
strategyIndex=1
pathToGoal=[]
pathToGoalIndex=0

def agent_start(observation):
    global strategyIndex,partialStateNodes,q,agenda,pathToGoalIndex
    strategyIndex=-1 
    partialStateNodes=[]
    q=[]
    agenda = EGALE
    pathToGoalIndex=-1
    return (['.',[]])


def agent_step(observation):
    global successorStates,agenda,q,pathToGoal,partialStateNodes,pathToGoalIndex
    if agenda == EGALE:
        successorStates=updateWorkingNodeSet(partialStateNodes,observation)
        q=enqueue(q,successoStates)
        if q==[]:
            return (['x'],[])
        first= q.pop(0)
        if goal(first):
            pathToGoal=createPathToGoal(first)
            agenda= AGENT
            return (['.'],[])
        
        
        partialStateNodes=getSuccessorStates(first)
        return getCellsNeededForDiscovery(partialStateNodes) 
    
    if agenda == AGENT:
        pathToGoalIndex+=1
        return ([pathToGoal[pathToGoalIndex]],[])
         
         
        
        

def getCellsNeededForDiscovery(nodes):
    #to Do but return should be like that
    
    I=[]
    return (['q'],I)
        
        
def getSuccessorStates(StateNode):
    #To Do
    return []
    
        

def createPathToGoal(node):
    #ToDO
    return []


def updateWorkingNodeSet(partialNodes,observation):
    #TO DO  
    return []


def enqueue(que,listOfNodes):
    # insert according to the strategy
    if strategyIndex==0: #BFS
        que.extend(listOfNodes)
    elif strategyIndex==1: #DFS
        map(lambda x: que.insert(0,x),listOfNodes)
    return que

def goal(node):
    #ToDO 
    return True
    
s=[1]
d=[2,34,455]
s=enqueue(s,d)
print ([2],[3])
print agenda
agent_start(None)
print agenda




        