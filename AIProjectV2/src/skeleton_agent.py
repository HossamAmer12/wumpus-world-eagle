# 
# Copyright (C) 2008, Brian Tanner
# 
#http://rl-glue-ext.googlecode.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from rlglue.agent.Agent import Agent
from rlglue.agent import AgentLoader as AgentLoader
from rlglue.types import Action





from Node import Node
from State import State
import numpy as np


import Queue





class skeleton_agent(Agent):
	
	
	
	def agent_init(self, taskSpec):
		#See the sample_sarsa_agent in the mines-sarsa-example project for how to parse the task spec
		self.WIDTH = 12
		self.HEIGHT = 12
		self.EAGLE = 1
		self.AGENT = 0
		self.MAX_DEPTH=self.WIDTH*self.HEIGHT*10
		self.agenda = self.AGENT
		self.successoStates = []
		self.partialStateNodes = []
		
		#self.actions = ['f', 'l', 'r', 'c', 'g', 'a']
		self.strategies = ['BFS', 'DFS','ID','UCS','A*']
		self.strategyIndex = -1
		self.pathToGoal = []
		self.pathToGoalIndex = -1
		self.visited = np.ndarray(shape=(self.WIDTH, self.HEIGHT, 4, 2, 2), dtype=np.bool)
		
		self.iteration=0
		
		self.depthq=[]
		
		
	def agent_start(self, observation):
		#Generate random action, 0 or 1
	
		action = Action()
		action.charArray.append('q')
		action.intArray = [1, 0, 0]
		
		self.strategyIndex += 1
		
		initPartialNode = Node()
		self.partialStateNodes = [initPartialNode]
		
		#Initialize data structure
		if self.strategyIndex ==0: #BFS
			self.heapQueue = Queue.Queue()
		elif self.strategyIndex == 1 or self.strategyIndex == 2: #DFS , ID
			self.heapQueue = Queue.LifoQueue()
		elif self.strategyIndex == 3 or self.strategyIndex == 4: #UCS, A* 
			self.heapQueue = Queue.PriorityQueue()
			
		
		self.agenda = self.EAGLE
		self.pathToGoalIndex = -1 
		self.visited.fill(False)
		self.depthq=[]
		return action
		


	
	def agent_step(self, reward, observation):
		action = Action()
			
		if self.agenda == self.EAGLE:
			self.successorStates = self.updateWorkingNodeSet(self.partialStateNodes, observation)
			
			self.enqueue(self.successorStates)
		
			if self.heapQueue.empty():
				if self.strategyIndex==2 and self.iteration <= self.MAX_DEPTH:
					self.iteration+=1
					action.charArray.append('q')
					action.intArray = [1, 0, 0]
					initPartialNode = Node()
					self.partialStateNodes = [initPartialNode]
					self.heapQueue = Queue.LifoQueue()
					self.visited.fill(False)
					return action
				
				
				print 'fail'
				action.intArray = []
				action.charArray.append('x')
				action.intArray = []
				return action
		

			#hashas
			#first = hp.heappop(self.heapQueue)[1]
			first=self.heapQueue.get()[1]
			
			self.depthq.append(first.depth)
		
			
			self.setVisited(first)
			#print 'current', first
			if self.goal(first):
				self.pathToGoal = self.createPathToGoal(first)
				self.agenda = self.AGENT
				print 'len',len(self.pathToGoal),self.pathToGoal
				
				print max(self.depthq)
				action.charArray.append('.')
				action.intArray = []
				return action
			
			
			self.partialStateNodes = self.getSuccessorStates(first)
			
			#print 'Partial state nodes: '
			#print map(str,self.partialStateNodes)
			
			return self.getCellsNeededForDiscovery(first) 
			
		if self.agenda == self.AGENT:
			self.pathToGoalIndex = self.pathToGoalIndex + 1
			#print self.pathToGoal[self.pathToGoalIndex]
			action.charArray.append(self.pathToGoal[self.pathToGoalIndex])
			action.intArray = []
			return action

		
	
	def agent_end(self, reward):
		pass
	
	def agent_cleanup(self):
		pass
	
	def agent_message(self, inMessage):
		if inMessage == "what is your name?":
			return "my name is skeleton_agent, Python edition!";
		else:
			return "I don't know how to respond to your message";
		
	
	def getCellsNeededForDiscovery(self, node):

		newPosition = self.newPosition(node.state.position, node.state.orintation)[1]
		action = Action()
		action.intArray = [1, newPosition[0], newPosition[1]]
		action.charArray.append('q')
		return action


	def getSuccessorStates(self, parentNode):
		#print 'parentNode', parentNode.depth
		if self.strategyIndex==2 and parentNode.depth==self.iteration :
			return []
		
		oldState = parentNode.state
		tempNodes = []
		
		# validating Action g
		if parentNode.observation[0] == 1 and not oldState.holdingGold:
			newState = State(oldState.orintation, oldState.position, True, oldState.killedWampus)
			
			#hashas
			newCost  =  parentNode.pathCost + self.actionCost('g')
			newNode = Node('g', newState, newCost, parentNode.actionPath, parentNode.observation,parentNode.depth)
			
			tempNodes.append(newNode)
			return tempNodes
		
			
		# validating Action f
		validPosition, newPosition = self.newPosition(parentNode.state.position, parentNode.state.orintation)
		if validPosition:
			newState = State(oldState.orintation, newPosition, oldState.holdingGold, oldState.killedWampus)
			#hashas
			newCost  =  parentNode.pathCost + self.actionCost('f')
			newNode = Node('f', newState, newCost, parentNode.actionPath, parentNode.depth)
			
#			newNode = Node('f', newState, parentNode.pathCost + self.actionCost('f'), parentNode.actionPath)
			tempNodes.append(newNode)

		# validating Action r
		newOrientation = self.newOrintation(oldState.orintation, 'r')
		newState = State(newOrientation, oldState.position, oldState.holdingGold, oldState.killedWampus)
		
		#hashas
		newCost  =  parentNode.pathCost + self.actionCost('r')
		newNode = Node('r', newState, newCost, parentNode.actionPath, parentNode.observation,parentNode.depth)
		
#		newNode = Node('r', newState, parentNode.pathCost + self.actionCost('r'), parentNode.actionPath, parentNode.observation)
		tempNodes.append(newNode)
	
		# validating Action l
		newOrientation = self.newOrintation(oldState.orintation, 'l')
		newState = State(newOrientation, oldState.position, oldState.holdingGold, oldState.killedWampus)
		
		#hashas
		newCost  =  parentNode.pathCost + self.actionCost('l')
		newNode = Node('l', newState, newCost, parentNode.actionPath, parentNode.observation,parentNode.depth)
		
#		newNode = Node('l', newState, parentNode.pathCost + self.actionCost('l'), parentNode.actionPath, parentNode.observation)
		tempNodes.append(newNode)
		
		# validating Action a
		if not oldState.killedWampus:
			#print '* create'
			newState = State(oldState.orintation, oldState.position, oldState.holdingGold, True)
			
			#hashas
			newCost  =  parentNode.pathCost + self.actionCost('a')
			newNode = Node('a', newState, newCost, parentNode.actionPath, parentNode.observation, parentNode.depth)
			
			#newNode = Node('a', newState, parentNode.pathCost + self.actionCost('a'), parentNode.actionPath, parentNode.observation)
			tempNodes.append(newNode)
					
		return tempNodes
	
	def newPosition(self, position, orintation):
		orient = ['N', 'E', 'S', 'W']
		index = orient.index(orintation)
		shifts = [ 0, 1, 1, 0, 0, -1, -1, 0]
				
		if -1 < position[0] + shifts[index * 2] < self.WIDTH and -1 < position[1] + shifts[index * 2 + 1] < self.HEIGHT:
			position = (position[0] + shifts[index * 2], position[1] + shifts[index * 2 + 1])
			return True, position
		else:
			return False, position


	def newOrintation(self, orintation, action):
		orint = ['N', 'E', 'S', 'W']
		index = orint.index(orintation)
		if action == 'l':
			index = (index - 1) % 4
		elif action == 'r':
			index = (index + 1) % 4
		return orint[index]

	def actionCost(self, action):
		return 1
	
	def createPathToGoal(self, node):
		#ToDO
		node.actionPath.pop(0)
		node.actionPath.append('c')
		return node.actionPath
	
	
	def updateWorkingNodeSet(self, partialNodes, observations):
		#print len(partialNodes),	
		
			
		invalidNodes = []
		observation = observations.intArray
		for node in partialNodes:
			if self.isVisted(node):
				invalidNodes.append(node)
				continue
			if node.action == 'f':
				if observation[1] == 1 or (observation[2] == 1 and not (node.state.killedWampus)):
					invalidNodes.append(node)
				else:
					node.observation = observation
				
			if node.action == 'a':
				if observation[2] == 0 or observation[1] == 1:
						invalidNodes.append(node)
						#print '* Invalid'
						
			if node.action == '.':
				node.observation = observation
	
		map(partialNodes.remove, invalidNodes)		
		return partialNodes
	
	
	def setVisited(self,node):
		orient = ['N', 'E', 'S', 'W']
		OrienTindex = orient.index(node.state.orintation)
		holdingGold = 1 if node.state.holdingGold else 0
		wampusKilled = 1 if node.state.killedWampus else 0
		self.visited[node.state.position[0], node.state.position[1], OrienTindex, holdingGold, wampusKilled ]=True
		
	def isVisted(self,node):
		orient = ['N', 'E', 'S', 'W']
		OrienTindex = orient.index(node.state.orintation)
		holdingGold = 1 if node.state.holdingGold else 0
		wampusKilled = 1 if node.state.killedWampus else 0
		return self.visited[node.state.position[0], node.state.position[1], OrienTindex, holdingGold, wampusKilled ]

	def add_node(self, node, priority=0):
#		print 'Node: ', node
		entry = (priority, node)
		#hp.heappush(self.heapQueue, entry)
		self.heapQueue.put(entry)
	

			
	def enqueue(self, listOfNodes):
			
		# insert according to the strategy
		if self.strategyIndex == 0: #BFS
			# mark nodes as visited
			map(self.setVisited,listOfNodes)
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
			
		elif self.strategyIndex == 1: #DFS
			# mark nodes as visited
			map(self.setVisited,listOfNodes)
			map(lambda x: self.add_node(x, x.pathCost*-1), listOfNodes)
		
		elif self.strategyIndex == 2: #ID
			# mark nodes as visited
			map(self.setVisited,listOfNodes)
			map(lambda x: self.add_node(x, x.pathCost*-1), listOfNodes)
			
		elif self.strategyIndex == 3: #UCS
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
		
		elif self.strategyIndex == 4:# A*
			map(lambda x: self.add_node(x, x.pathCost+x.heuristic), listOfNodes)
		
		
		
	def goal(self, node):
		if node.state.position == (0, 0) and node.state.holdingGold :
			return True
		else:
			return False


if __name__ == "__main__":
	AgentLoader.loadAgent(skeleton_agent())
