'''

Hossam Amer
Taher Galal
Mohamed Gad
'''


from rlglue.agent.Agent import Agent
from rlglue.agent import AgentLoader as AgentLoader
from rlglue.types import Action
from Node import Node
from State import State
import numpy as np
import Queue
import time


class skeleton_agent(Agent):
	
	def agent_init(self, taskSpec):
		'''
		initialize the agent
		'''
		#See the sample_sarsa_agent in the mines-sarsa-example project for how to parse the task spec
		self.WIDTH = 12
		self.HEIGHT = 12
		self.EAGLE = 1
		self.AGENT = 0
		self.MAX_DEPTH=self.WIDTH*self.HEIGHT*10 # for ID
		self.STRATRGIES = ['BFS', 'DFS','ID','UCS','A*']
		
		self.agenda = self.AGENT
		self.successoStates = []
		self.partialStateNodes = []		
		self.strategyIndex = -1
		self.pathToGoal = []
		self.pathToGoalIndex = -1
		# visited array
		self.visited = np.ndarray(shape=(self.WIDTH, self.HEIGHT, 4, 2, 2), dtype=np.bool)
		#iteration number for ID
		self.iteration=0
		# for debug
		self.depthq=[]
		
		
	def agent_start(self, observation):
		'''
		initialize the episode strategy
		'''
		#Generate action, query 0,0
		action = Action()
		action.charArray.append('q')
		action.intArray = [1, 0, 0]
		# increment strategy
		self.strategyIndex += 1
		#add 1st node (0,0) and North with arrow to the partial nodes
		initPartialNode = Node()
		self.partialStateNodes = [initPartialNode]
		#initialize new queue according to strategy
		self.newQueu()
		#set the agenda
		self.agenda = self.EAGLE
		#reset the pointer to the action path
		self.pathToGoalIndex = -1 
		self.visited.fill(False)
		self.depthq=[]
		# to measure performance
		self.numExpandedNodes=0
		self.startTime=time.time()
		#print 'End the method start'
		return action
		
		
	def newQueu(self):
		'''
		initialize the search queue 
		'''
		if self.strategyIndex ==0: #BFS
			self.heapQueue = Queue.Queue()
		elif self.strategyIndex == 1 or self.strategyIndex == 2: #DFS , ID
			self.heapQueue = Queue.LifoQueue()
		elif self.strategyIndex == 3 or self.strategyIndex == 4: #UCS, A* 
			self.heapQueue = Queue.PriorityQueue()

		
	def agent_step(self, reward, observation):
		'''
		called by the rl-glue 
		'''
		action = Action()
		
		#eagle mode 
		if self.agenda == self.EAGLE:
			# combine observation with partial nodes and enqueue
			self.successorStates = self.updateWorkingNodeSet(self.partialStateNodes, observation)			
			self.enqueue(self.successorStates)
			
			
			if self.heapQueue.empty():
				# In case Iterative Deepening it should check if it exceeded number of iterations or not
				if self.strategyIndex==2 and self.iteration <= self.MAX_DEPTH: # if ID
					self.iteration+=1
					action.charArray.append('q')
					action.intArray = [1, 0, 0]
					initPartialNode = Node()
					self.partialStateNodes = [initPartialNode]
					self.heapQueue = Queue.LifoQueue()
					self.visited.fill(False)
					return action
				# if not ID 
				print 'fail'
				print 'ellapsed time:', time.time()-self.startTime,'s'
				action.intArray = []
				action.charArray.append('x')
				action.intArray = []
				return action
		
			#Get first element from list
			first=self.heapQueue.get()[1]
			self.numExpandedNodes+=1
			#for debug
			self.depthq.append(first.depth)
			self.setVisited(first)
			# if reaching goal just send dummy action and change the mode	
			if self.goal(first):
				self.pathToGoal = self.createPathToGoal(first)
				self.agenda = self.AGENT
				print self.pathToGoal,'number of steps',len(self.pathToGoal)
				print 'number of expanded nodes:',self.numExpandedNodes
				print 'ellapsed time:', time.time()-self.startTime,'s'
				#print max(self.depthq)
				action.charArray.append('.')
				action.intArray = []
				return action
			
			self.partialStateNodes = self.getSuccessorStates(first)
			return self.getCellsNeededForDiscovery(first) 

		# Agent mode just send actions
		if self.agenda == self.AGENT:
			self.pathToGoalIndex = self.pathToGoalIndex + 1
			action.charArray.append(self.pathToGoal[self.pathToGoalIndex])
			action.intArray = []
			return action

		
	
	
	
	def getCellsNeededForDiscovery(self, node):
		'''
		Generate list I contains locations to discover and send action with them
		'''
		newPosition = self.newPosition(node.state.position, node.state.orintation)[1]
		action = Action()
		action.intArray = [1, newPosition[0], newPosition[1]]
		action.charArray.append('q')
		return action


	def getSuccessorStates(self, parentNode):
		'''
		expand the current node by valid actions f,l,r,a and g in case of observation indicates gold
		'''
		# for iterative deepening don't expand more nodes if depth reaches limit
		if self.strategyIndex==2 and parentNode.depth==self.iteration :
			return []
		
		oldState = parentNode.state
		tempNodes = []
		
		# validating Action g
		if parentNode.observation[0] == 1 and not oldState.holdingGold:
			newState = State(oldState.orintation, oldState.position, True, oldState.killedWampus)
			newCost  =  parentNode.pathCost + self.actionCost('g')
			newNode = Node('g', newState, newCost, parentNode.actionPath, parentNode.observation)
			tempNodes.append(newNode)
			return tempNodes #no need to continue other states
				
		# validating Action f
		validPosition, newPosition = self.newPosition(parentNode.state.position, parentNode.state.orintation)
		if validPosition:
			newState = State(oldState.orintation, newPosition, oldState.holdingGold, oldState.killedWampus)
			newCost  =  parentNode.pathCost + self.actionCost('f')
			newNode = Node('f', newState, newCost, parentNode.actionPath)
			tempNodes.append(newNode)

		# validating Action r
		newOrientation = self.newOrintation(oldState.orintation, 'r')
		newState = State(newOrientation, oldState.position, oldState.holdingGold, oldState.killedWampus)
		newCost  =  parentNode.pathCost + self.actionCost('r')
		newNode = Node('r', newState, newCost, parentNode.actionPath, parentNode.observation)
		tempNodes.append(newNode)
	
		# validating Action l
		newOrientation = self.newOrintation(oldState.orintation, 'l')
		newState = State(newOrientation, oldState.position, oldState.holdingGold, oldState.killedWampus)
		newCost  =  parentNode.pathCost + self.actionCost('l')
		newNode = Node('l', newState, newCost, parentNode.actionPath, parentNode.observation)
		tempNodes.append(newNode)
		
		# validating Action a
		if not oldState.killedWampus:
			newState = State(oldState.orintation, oldState.position, oldState.holdingGold, True)
			newCost  =  parentNode.pathCost + self.actionCost('a')
			newNode = Node('a', newState, newCost, parentNode.actionPath, parentNode.observation)	
			tempNodes.append(newNode)
					
		return tempNodes
	
	
	def newPosition(self, position, orintation):
		'''
		generating next location called in case of forward
		'''
		orient = ['N', 'E', 'S', 'W']
		index = orient.index(orintation)
		shifts = [ 0, 1, 1, 0, 0, -1, -1, 0]
				
		if -1 < position[0] + shifts[index * 2] < self.WIDTH and -1 < position[1] + shifts[index * 2 + 1] < self.HEIGHT:
			position = (position[0] + shifts[index * 2], position[1] + shifts[index * 2 + 1])
			return True, position
		else:
			return False, position


	def newOrintation(self, orintation, action):
		'''
		generate next orientation   
		'''
		orint = ['N', 'E', 'S', 'W']
		index = orint.index(orintation)
		if action == 'l':
			index = (index - 1) % 4
		elif action == 'r':
			index = (index + 1) % 4
		return orint[index]


	def actionCost(self, action):
		'''
		cost of actions 
		'''
		if action == 'a':
			return 10
		else:
			return 1

	
	def createPathToGoal(self, node):
		'''
		fix the actions list after success by adding the climb action and remove the unused. 
		'''
		node.actionPath.pop(0)
		node.actionPath.append('c')
		return node.actionPath
	
	
	def updateWorkingNodeSet(self, partialNodes, observations):
		'''
		updating the partial nodes with the observation. 
		'''	
		invalidNodes = [] # nodes to be removed observation invalidated them
		observation = observations.intArray
		#loop on partial nodes to validate them
		for node in partialNodes:
			# if the node is visited before invalidate it
			if self.isVisted(node):
				invalidNodes.append(node)
				continue
			# if the node is curring action forward checks if the next node is empty.
			if node.action == 'f':
				if observation[1] == 1 or (observation[2] == 1 and not (node.state.killedWampus)):
					invalidNodes.append(node)
				else:
					node.observation = observation
			#validating action shoot arrow if the facing cell is containing Wumpus or not  
			if node.action == 'a':
				if observation[2] == 0 or observation[1] == 1:
						invalidNodes.append(node)
						
			#special case for the first node
			if node.action == '.':
				node.observation = observation
		# removes the invalid node from partial nodes
		map(partialNodes.remove, invalidNodes)		
		return partialNodes
	
	
	def setVisited(self,node):
		'''
		set the node as visited in the table 
		'''
		orient = ['N', 'E', 'S', 'W']
		OrienTindex = orient.index(node.state.orintation)
		holdingGold = 1 if node.state.holdingGold else 0
		wampusKilled = 1 if node.state.killedWampus else 0
		self.visited[node.state.position[0], node.state.position[1], OrienTindex, holdingGold, wampusKilled ]=True
		
		
	def isVisted(self,node):
		'''
		check if state is visited or not according to visited table
		'''
		orient = ['N', 'E', 'S', 'W']
		OrienTindex = orient.index(node.state.orintation)
		holdingGold = 1 if node.state.holdingGold else 0
		wampusKilled = 1 if node.state.killedWampus else 0
		return self.visited[node.state.position[0], node.state.position[1], OrienTindex, holdingGold, wampusKilled ]

	
	def add_node(self, node, priority=0):
		'''
		inserting the given node and its priority as tuple in search queue
		'''
		entry = (priority, node)
		self.heapQueue.put(entry)
	
	
	def enqueue(self, listOfNodes):
		'''
		inserting the nodes in the main search queue
		'''
		if self.strategyIndex == 0: #BFS
			# mark nodes as visited
			map(self.setVisited,listOfNodes)
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
		elif self.strategyIndex == 1: #DFS
			# mark nodes as visited
			map(self.setVisited,listOfNodes)
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
		elif self.strategyIndex == 2: #ID
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
		elif self.strategyIndex == 3: #UCS
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
		elif self.strategyIndex == 4:# A*
			map(lambda x: self.add_node(x, x.pathCost+x.heuristic), listOfNodes)
			
		
	def goal(self, node):
		'''
		Checks if the current mode is the goal node here is to be in (0,0) and with gold so the agent 
		'''
		if node.state.position == (0, 0) and node.state.holdingGold :
			return True
		else:
			return False
		
	#For Debuging printing the queue
	def printQue(self):
		if self.strategyIndex ==0: #BFS
			h = Queue.Queue()
		elif self.strategyIndex == 1 or self.strategyIndex == 2: #DFS , ID
			h = Queue.LifoQueue()
		elif self.strategyIndex == 3 or self.strategyIndex == 4: #UCS, A* 
			h = Queue.PriorityQueue()
		
		while not self.heapQueue.empty():
			temp= self.heapQueue.get()
			h.put(temp)
			print temp[1],
		print 

	
	def agent_end(self, reward):
		print reward
	
	def agent_cleanup(self):
		pass
	
	def agent_message(self, inMessage):
		if inMessage == "what is your name?":
			return "my name is skeleton_agent, Python edition!";
		else:
			return "I don't know how to respond to your message";
	
if __name__ == "__main__":
	AgentLoader.loadAgent(skeleton_agent())

