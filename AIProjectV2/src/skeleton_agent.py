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


import heapq as hp





class skeleton_agent(Agent):
	
	
	
	def agent_init(self, taskSpec):
		#See the sample_sarsa_agent in the mines-sarsa-example project for how to parse the task spec
		self.WIDTH = 12
		self.HEIGHT = 12
		self.EAGLE = 1
		self.AGENT = 0
		self.MAX_DEPTH=self.WIDTH*self.HEIGHT
		
		
		self.agenda = self.AGENT
		self.successoStates = []
		self.partialStateNodes = []
		
		#self.actions = ['f', 'l', 'r', 'c', 'g', 'a']
		self.strategies = ['BFS', 'DFS','ID','UCS','A*']
		self.strategyIndex = -1
		self.pathToGoal = []
		self.pathToGoalIndex = -1
		self.visited = np.ndarray(shape=(self.WIDTH, self.HEIGHT, 4, 2, 2), dtype=np.bool)
		
		self.heapQueue = []
		self.iteration=0
		#print self.visited
		
	def agent_start(self, observation):
		#Generate random action, 0 or 1
	
		action = Action()
		action.charArray.append('q')
		action.intArray = [1, 0, 0]
	
		self.strategyIndex += 1
		
		initPartialNode = Node()
		self.partialStateNodes = [initPartialNode]
		
		#hashas
		self.heapQueue = []
		
		self.agenda = self.EAGLE
		self.pathToGoalIndex = -1 
		self.visited.fill(False)
		#print 'End the method start'
		return action
		


	
	def agent_step(self, reward, observation):
		#Generate random action, 0 or 1
		#global successorStates, agenda, q, pathToGoal, partialStateNodes, pathToGoalIndex, AGENT, EAGLE
		#print str(observation.intArray)
		
		lastAction = Action()
		
		#print 'Start the method step'
		
		if self.agenda == self.EAGLE:
			self.successorStates = self.updateWorkingNodeSet(self.partialStateNodes, observation)
			
			
			#hashas	
			self.enqueue(self.successorStates)
			
#			print 'Heap Queue: ', len(self.heapQueue) 
			
			#hashas
			if len(self.heapQueue) == 0:
				if self.strategyIndex==2 and self.iteration <= self.MAX_DEPTH:
					self.iteration+=1
					print 'i',self.iteration
					action = Action()
					action.charArray.append('q')
					action.intArray = [1, 0, 0]
					initPartialNode = Node()
					self.partialStateNodes = [initPartialNode]
					self.heapQueue = []
					self.visited.fill(False)
					return action
				
				
				print 'fail'
				lastAction.intArray = []
				lastAction.charArray.append('x')
				lastAction.intArray = []
				return lastAction
		

			#hashas
			first = hp.heappop(self.heapQueue)[1]
			
			#print first
			self.setVisited(first)
			#print 'current', first
			if self.goal(first):
				self.pathToGoal = self.createPathToGoal(first)
				self.agenda = self.AGENT
				print self.pathToGoal
				
				lastAction.charArray.append('.')
				lastAction.intArray = []
				return lastAction
			
			
			self.partialStateNodes = self.getSuccessorStates(first)
			
			#print 'Partial state nodes: '
			#print map(str,self.partialStateNodes)
			
			return self.getCellsNeededForDiscovery(first) 
			
		if self.agenda == self.AGENT:
			self.pathToGoalIndex = self.pathToGoalIndex + 1
			#print self.pathToGoal[self.pathToGoalIndex]
			lastAction.charArray.append(self.pathToGoal[self.pathToGoalIndex])
			lastAction.intArray = []
			return lastAction

		
	
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
		print 'parentNode', parentNode.depth
		oldState = parentNode.state
		tempNodes = []

		# validating Action g
		if parentNode.observation[0] == 1 and not oldState.holdingGold:
			newState = State(oldState.orintation, oldState.position, True, oldState.killedWampus, oldState.path)
			
			#hashas
			newCost  =  parentNode.pathCost + self.actionCost('g')* (-1 if 1<=self.strategyIndex <= 2  else 1)
			newNode = Node('g', newState, newCost, parentNode.actionPath, parentNode.observation, parentNode.depth)
			
			tempNodes.append(newNode)
			return tempNodes
		
			
		# validating Action f
		validPosition, newPosition = self.newPosition(parentNode.state.position, parentNode.state.orintation)
		if validPosition:
			newState = State(oldState.orintation, newPosition, oldState.holdingGold, oldState.killedWampus, oldState.path)
			#hashas
			newCost  =  parentNode.pathCost + self.actionCost('f')* (-1 if 1<=self.strategyIndex <= 2  else 1)
			newNode = Node('f', newState, newCost, parentNode.actionPath, parentNode.depth)
			
#			newNode = Node('f', newState, parentNode.pathCost + self.actionCost('f'), parentNode.actionPath)
			tempNodes.append(newNode)

		# validating Action r
		newOrientation = self.newOrintation(oldState.orintation, 'r')
		newState = State(newOrientation, oldState.position, oldState.holdingGold, oldState.killedWampus, oldState.path)
		
		#hashas
		newCost  =  parentNode.pathCost + self.actionCost('r')* (-1 if 1<=self.strategyIndex <= 2  else 1)
		newNode = Node('r', newState, newCost, parentNode.actionPath, parentNode.observation, parentNode.depth)
		
#		newNode = Node('r', newState, parentNode.pathCost + self.actionCost('r'), parentNode.actionPath, parentNode.observation)
		tempNodes.append(newNode)
	
		# validating Action l
		newOrientation = self.newOrintation(oldState.orintation, 'l')
		newState = State(newOrientation, oldState.position, oldState.holdingGold, oldState.killedWampus, oldState.path)
		
		#hashas
		newCost  =  parentNode.pathCost + self.actionCost('l')* (-1 if 1<=self.strategyIndex <= 2  else 1)
		newNode = Node('l', newState, newCost, parentNode.actionPath, parentNode.observation, parentNode.depth)
		
#		newNode = Node('l', newState, parentNode.pathCost + self.actionCost('l'), parentNode.actionPath, parentNode.observation)
		tempNodes.append(newNode)
		
		# validating Action a
		if not oldState.killedWampus:
			#print '* create'
			newState = State(oldState.orintation, oldState.position, oldState.holdingGold, True, oldState.path)
			
			#hashas
			newCost  =  parentNode.pathCost + self.actionCost('a')* (-1 if 1<=self.strategyIndex <= 2 else 1)
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
		if self.strategyIndex==2 and len(partialNodes)>0  and partialNodes[0].depth>=self.iteration :
			return []
			
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
		entry = [priority, node]
		hp.heappush(self.heapQueue, entry)
	

			
	def enqueue(self, listOfNodes):
		
		# Marking the visited nodes
		map(self.setVisited,listOfNodes)
		
		
		# insert according to the strategy
		if self.strategyIndex == 0: #BFS

			#hashas
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
			
#			que.extend(listOfNodes)
			
		elif self.strategyIndex == 1: #DFS
			
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
		
		elif self.strategyIndex == 2: #ID
			
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
			
		elif self.strategyIndex == 3: #UCS
			
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)
		
		elif self.strategyIndex == 4:# A*
			
			map(lambda x: self.add_node(x, x.pathCost+x.heuristic), listOfNodes)
		
		
		
	def goal(self, node):
		if node.state.position == (0, 0) and node.state.holdingGold :
			print 'dep',node.depth,
			return True
		else:
			return False


if __name__ == "__main__":
	AgentLoader.loadAgent(skeleton_agent())
