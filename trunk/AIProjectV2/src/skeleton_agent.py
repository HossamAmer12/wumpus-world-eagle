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
from rlglue.types import Observation
from  math import sqrt,ceil



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
		
		self.agenda = self.AGENT
		self.successoStates = []
		self.partialStateNodes = []
		self.q = []
		#self.actions = ['f', 'l', 'r', 'c', 'g', 'a']
		self.strategies = ['BFS', 'DFS']
		self.strategyIndex = -1
		self.pathToGoal = []
		self.pathToGoalIndex = -1
		self.visited = np.ndarray(shape=(self.WIDTH, self.HEIGHT, 4, 2, 2), dtype=np.bool)
		
		self.heapQueue = []
		#print self.visited
		
	def agent_start(self, observation):
		#Generate random action, 0 or 1
		#print 'Start the method start'
		#global strategyIndex, partialStateNodes, q, agenda, pathToGoalIndex, EAGLE
		action = Action()
		action.charArray.append('q')
		#action.intArray=[9,0,0,0,1,0,2,1,0,1,1,1,2,2,0,2,1,2,2]
		action.intArray = [1, 0, 0]
	
		
		initPartialNode = Node()
		self.strategyIndex += 1
		self.partialStateNodes = [initPartialNode]
		self.q = []
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
			
			
			#print 'Successor states: '
			#print  map(str,self.successorStates)
			
			self.q = self.enqueue(self.q, self.successorStates)
			#print map(str,self.q)
			if self.q == []:
				print 'fail'
				lastAction.intArray = []
				lastAction.charArray.append('x')
				lastAction.intArray = []
				return lastAction
			
			first = self.q.pop(0)
			#print first
			#print first
			orient = ['N', 'E', 'S', 'W']
			OrienTindex = orient.index(first.state.orintation)
			holdingGold = 1 if first.state.holdingGold else 0
			wumposKilled = 1 if first.state.killedWampus else 0
			self.visited[first.state.position[0], first.state.position[1], OrienTindex, holdingGold, wumposKilled] = True
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

		validPosition, newPosition = self.newPosition(node.state.position, node.state.orintation)
		action = Action()
		action.intArray = [1, newPosition[0], newPosition[1]]
		action.charArray.append('q')
		return action


	def getSuccessorStates(self, parentNode):

		oldState = parentNode.state
		tempNodes = []
		'''
		# validating Action c
		if oldState.position == (0, 0) and oldState.holdingGold:
			newState = State( oldState.orintation, oldState.position, oldState.holdingGold, oldState.killedWampus, oldState.path)
			newNode = Node('c', newState, parentNode.pathCost + self.actionCost('c'), parentNode.actionPath,parentNode.observation)
			newNode.actionPath.append('x')
			tempNodes.append(newNode)
			return tempNodes
		'''
		# validating Action g
		if parentNode.observation[0] == 1 and not oldState.holdingGold:
			newState = State(oldState.orintation, oldState.position, True, oldState.killedWampus, oldState.path)
			newNode = Node('g', newState, parentNode.pathCost + self.actionCost('g'), parentNode.actionPath, parentNode.observation)
			tempNodes.append(newNode)
			return tempNodes
		
		
			
		# validating Action f
		validPosition, newPosition = self.newPosition(parentNode.state.position, parentNode.state.orintation)
		if validPosition:
			newState = State(oldState.orintation, newPosition, oldState.holdingGold, oldState.killedWampus, oldState.path)
			newNode = Node('f', newState, parentNode.pathCost + self.actionCost('f'), parentNode.actionPath)
			tempNodes.append(newNode)


		# validating Action r
		newOrientation = self.newOrintation(oldState.orintation, 'r')
		newState = State(newOrientation, oldState.position, oldState.holdingGold, oldState.killedWampus, oldState.path)
		newNode = Node('r', newState, parentNode.pathCost + self.actionCost('r'), parentNode.actionPath, parentNode.observation)
		tempNodes.append(newNode)
	
		# validating Action l
		newOrientation = self.newOrintation(oldState.orintation, 'l')
		newState = State(newOrientation, oldState.position, oldState.holdingGold, oldState.killedWampus, oldState.path)
		newNode = Node('l', newState, parentNode.pathCost + self.actionCost('l'), parentNode.actionPath, parentNode.observation)
		tempNodes.append(newNode)
		
		# validating Action a
		if not oldState.killedWampus:
			#print '* create'
			newState = State(oldState.orintation, oldState.position, oldState.holdingGold, True, oldState.path)
			newNode = Node('a', newState, parentNode.pathCost + self.actionCost('a'), parentNode.actionPath, parentNode.observation)
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
			holdingGold = 1 if node.state.holdingGold else 0
			orient = ['N', 'E', 'S', 'W']
			OrienTindex = orient.index(node.state.orintation)
			holdingGold = 1 if node.state.holdingGold else 0
			wumposKilled = 1 if node.state.killedWampus else 0
			#print self.visited[node.state.position[0],node.state.position[1],OrienTindex,holdingGold]
			if self.visited[node.state.position[0], node.state.position[1], OrienTindex, holdingGold, wumposKilled ]:
				invalidNodes.append(node)
				#print 'invalidated'
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
				
			
			
		#print 'invalid'
		#print map(str, invalidNodes)	
		map(partialNodes.remove, invalidNodes)
		#print len(partialNodes)		
		
		return partialNodes
	
	def add_node(self, node, priority=0):
		
		entry = [priority, node]
		hp.heappush(self.heapQueue, entry)
	
	def list_reconstruct(self):
		que=[]
		for i  in range( len(self.heapQueue)):
			num, x = hp.heappop(self.heapQueue)
			que.append(x)
		return que
			
	
	def enqueue(self, que, listOfNodes):
		# insert according to the strategy
		if self.strategyIndex == 0: #BFS
			que.extend(listOfNodes)
		elif self.strategyIndex == 1: #DFS
			map(lambda x: que.insert(0, x), listOfNodes)
			#print que
			#print len(que)
			#print que
		elif self.strategyIndex == 2: #UCS
			map(lambda x: self.add_node(x, x.pathCost), que)
			map(lambda x: self.add_node(x, x.pathCost), listOfNodes)	
			que = self.list_reconstruct()
		
		elif self.strategyIndex == 3:# A*
			map(lambda x: self.add_node(x, x.pathCost+x.heuristic), que)
			map(lambda x: self.add_node(x, x.pathCost+x.heuristic) , listOfNodes)
			que = self.list_reconstruct()
#          	for y in que:
#          		print 'UCS: ', y
		return que
	
	
		
		
	def goal(self, node):
		if node.state.position == (0, 0) and node.state.holdingGold :
			return True
		else:
			return False


if __name__ == "__main__":
	AgentLoader.loadAgent(skeleton_agent())
