'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from mycreatepathnetwork import *
from mynavigatorhelpers import *
import heapq

###############################
### AStarNavigator
###
### Creates a path node network and implements the FloydWarshall all-pairs shortest-path algorithm to create a path to the given destination.
			
class AStarNavigator(NavMeshNavigator):

	def __init__(self):
		NavMeshNavigator.__init__(self)

	### Create the pathnode network and pre-compute all shortest paths along the network.
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
		return None
		
	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., it's current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		### Make sure the next and dist matricies exist
		if self.agent != None and self.world != None:
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			###   Tell the agent to move to dest
			### Step 2: If there is an obstacle, create the path that will move around the obstacles.
			###   Find the pathnodes closest to source and destination.
			###   Create the path by traversing the self.next matrix until the pathnode closes to the destination is reached
			###   Store the path by calling self.setPath()
			###   Tell the agent to move to the first node in the path (and pop the first node off the path)
			if clearShot(source, dest, self.world.getLines(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
				end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
				if start != None and end != None:
					#print len(self.pathnetwork)
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
					#print len(newnetwork)
					closedlist = []
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						path = shortcutPath(source, dest, path, self.world, self.agent)
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None
		
	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcutes can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)

def unobstructedNetwork(network, worldLines):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			newnetwork.append(l)
	return newnetwork

def astar(init, goal, network):
	path = []
	open = []
	closed = []
	### YOUR CODE GOES BELOW HERE ###
	openSet = set()
	closedSet = set()
	origin = {}
	gScore = {}
	fScore = {}

	heapq.heappush(open, (0, init))
	openSet.add(init)
	gScore[init] = 0
	fScore[init] = distance(init, goal)

	while len(open) > 0:
		curr = heapq.heappop(open)

		if curr[1] is goal:
			currNode = curr[1]
			path.append(currNode)
			while currNode in origin.keys():
				currNode = origin[currNode]
				path.append(currNode)
			path.reverse()
			closed = list(closedSet)
			return path, closed

		openSet.remove(curr[1])
		closedSet.add(curr[1])

		for edge in network:
			if curr[1] in edge:
				neighbor = edge[0]
				if curr[1] is edge[0]:
					neighbor = edge[1]

				if neighbor not in closedSet:
					cost = gScore[curr[1]] + distance(neighbor, goal)
					if neighbor not in openSet:
						openSet.add(neighbor)
						heapq.heappush(open, (cost, neighbor))
					elif cost >= gScore[neighbor]:
						continue

					origin[neighbor] = curr[1]
					gScore[neighbor] = cost
					fScore[neighbor] = gScore[neighbor] + distance(neighbor, goal)
	### YOUR CODE GOES ABOVE HERE ###
	return path, closed

def myUpdate(nav, delta):
	### YOUR CODE GOES BELOW HERE ###
	# If the agent is trapped, stop it from moving to force it to replan
	if not clearShot(nav.agent.getLocation(), nav.agent.getMoveTarget(), nav.world.getGates(), None, nav.agent):
		nav.agent.stopMoving()
	### YOUR CODE GOES ABOVE HERE ###
	return None

def myCheckpoint(nav):
	### YOUR CODE GOES BELOW HERE ###
	nav.agent.stopMoving()
	### YOUR CODE GOES ABOVE HERE ###
	return None

### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
	### YOUR CODE GOES BELOW HERE ###
	threshold = agent.getMaxRadius()

	# Calculate angle of the line
	dy = p1[1] - p2[1]
	dx = p1[0] - p2[0]
	theta = math.atan2(dy, dx)

	# Calculate perpendicular angles
	left = theta + math.pi / 2
	right = theta - math.pi / 2

	# Calculate points to draw parallel rays
	leftPoint1 = (p1[0] + threshold * math.cos(left), p1[1] + threshold * math.sin(left))
	leftPoint2 = (p2[0] + threshold * math.cos(left), p2[1] + threshold * math.sin(left))
	rightPoint1 = (p1[0] + threshold * math.cos(right), p1[1] + threshold * math.sin(right))
	rightPoint2 = (p2[0] + threshold * math.cos(right), p2[1] + threshold * math.sin(right))

	# Check for obstacle collisions against three parallel lines
	clear = True
	#for obstacle in worldLines:
	if rayTraceWorld(p1, p2, worldLines) is not None or rayTraceWorld(leftPoint1, leftPoint2, worldLines) is not None or rayTraceWorld(rightPoint1, rightPoint2, worldLines) is not None:
		clear = False
		#break

	if clear:
		return True
	### YOUR CODE GOES ABOVE HERE ###
	return False
