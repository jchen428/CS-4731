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

###############################
### APSPNavigator
###
### Creates a path node network and implements the FloydWarshall all-pairs shortest-path algorithm to create a path to the given destination.
class APSPNavigator(NavMeshNavigator):

	### next: indicates which node to traverse to next to get to a given destination. A dictionary of dictionaries such that next[p1][p2] tells you where to go if you are at p1 and want to go to p2
	### dist: the distance matrix. A dictionary of dictionaries such that dist[p1][p2] tells you how far from p1 to p2.
	def __init__(self):
		NavMeshNavigator.__init__(self)
		self.next = None
		self.dist = None

	### Create the pathnode network and pre-compute all shortest paths along the network.
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
		self.next, self.dist = APSP(self.pathnodes, self.pathnetwork)
		return None
		
	### Finds the shortest path from the source to the destination.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., it's current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		### Make sure the next and dist matricies exist
		if self.agent != None and self.world != None and self.next != None and self.dist != None: 
			self.source = source
			self.destination = dest
			if clearShot(source, dest, self.world.getLinesWithoutBorders(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				start = findClosestUnobstructed(source, self.pathnodes, self.world.getLines())
				end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLines())
				if start != None and end != None and start in self.dist and end in self.dist[start] and self.dist[start][end] < INFINITY:
					path = findPath(start, end, self.next)
					path = shortcutPath(source, dest, path, self.world, self.agent)
					self.setPath(path)
					if len(self.path) > 0:
						first = self.path.pop(0)
						self.agent.moveToTarget(first)
		return None

	### This function gets called by the agent to figure out if some shortcutes can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

### Returns a path as a list of points in the form (x, y)
### start: the start node, one of the nodes in the path network
### end: the end node, one of the nodes in the path network
### next: the matrix of next nodes such that next[p1][p2] tells where to go next
def findPath(start, end, next):
	path = []
	### YOUR CODE GOES BELOW HERE ###
	# Just keep appending nearest nodes onto the path
	if next[start][end] is not None:
		path.append(start)
		while start is not end:
			start = next[start][end]
			path.append(start)
	### YOUR CODE GOES ABOVE HERE ###
	return path
	
def APSP(nodes, edges):
	next = {} # a dictionary of dictionaries. next[p1][p2] will give you the next node to go to, or None
	dist = {} # a dictionary of dictionaries. dist[p1][p2] will give you the distance.
	for n in nodes:
		next[n] = {}
		dist[n] = {}
	### YOUR CODE GOES BELOW HERE ###
		# Initialize next and dist matrices
		for m in nodes:
			next[n][m] = None
			dist[n][m] = INFINITY

	# Assign edge weights to dist and neighbors in next
	for e in edges:
		d = distance(e[0], e[1])
		dist[e[0]][e[1]] = d
		dist[e[1]][e[0]] = d
		next[e[0]][e[1]] = e[1]
		next[e[1]][e[0]] = e[0]

	# Floyd-Warshall
	for w in nodes:
		for u in nodes:
			for v in nodes:
				if dist[u][v] > dist[u][w] + dist[w][v]:
					next[u][v] = next[u][w]
					dist[u][v] = dist[u][w] + dist[w][v]

	"""
	for k, v in dist.items():
		print k
		print v
		val = v.items()
		for thing in val:
			print thing[1]
		print ""
	"""
	### YOUR CODE GOES ABOVE HERE ###
	return next, dist

### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
	### YOUR CODE GOES BELOW HERE ###
	threshold = 1.5 * agent.getRadius()

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
	for obstacle in worldLines:
		if rayTrace(p1, p2, obstacle) is not None or rayTrace(leftPoint1, leftPoint2, obstacle) is not None or rayTrace(rightPoint1, rightPoint2, obstacle) is not None:
			clear = False
			break

	if clear:
		return True
	### YOUR CODE GOES ABOVE HERE ###
	return False
