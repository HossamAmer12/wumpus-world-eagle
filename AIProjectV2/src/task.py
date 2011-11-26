import heapq as hp
import itertools

from Node import Node
from State import State
#
#
#pq = []                         # list of entries arranged in a heap
#entry_finder = {}               # mapping of tasks to entries
#REMOVED = '<removed-task>'      # placeholder for a removed task
#counter = itertools.count()     # unique sequence count
#
#def add_task(task, priority=0):
#    
#    print 'Adding task'
#    
#    'Add a new task or update the priority of an existing task'
#   # if task in entry_finder:
#    #    remove_task(task)
#     #   print 'Hello from remove!', task, priority
#     
#    count = next(counter)
#    entry = [priority, count, task]
#    #entry_finder[task] = entry
#    hp.heappush(pq, entry)
#
#def remove_task(task):
#    'Mark an existing task as REMOVED.  Raise KeyError if not found.'
#    entry = entry_finder.pop(task)
#    entry[-1] = REMOVED
#
#def pop_task():
#    'Remove and return the lowest priority task. Raise KeyError if empty.'
#    while pq:
#        priority, count, task = hp.heappop(pq)
#        if task is not REMOVED:
#          #  del entry_finder[task]
#            return task
#    raise KeyError('pop from an empty priority queue')

import Queue



q=Queue.Queue()


node1 = Node()
node2 = Node()
node3 = Node()
node4 = Node()
node5 = Node()
node6 = Node()

node1.pathCost = -12
node2.pathCost = 13
node3.pathCost = -12
node4.pathCost = 12
node5.pathCost = 13

q.put((node1.pathCost,node1))
q.put((node2.pathCost,node2))
q.put((node3.pathCost,node3))
q.put((node4.pathCost,node4))
q.put((node5.pathCost,node5))

print q.get()[1]
print q.get()[1]
print q.get()[1]
print q.get()[1]
print q.get()[1]
print q.get()[1]


#add_task(node1, -12)
#add_task(node2, -13)
#add_task(node2, -12)

#add_task(node1, 12)
#add_task(node2, 13)
#add_task(node2, 12)
#
#size = len(pq)
#
#print size
#
##for i in range(size):
#
#print 'Queue', pop_task()
#print 'Queue', pop_task()
#print 'Queue', pop_task()