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

### This function optimizes the given path and returns a new path
### source: the current position of the agent
### dest: the desired destination of the agent
### path: the path previously computed by the Floyd-Warshall algorithm
### world: pointer to the world
def shortcutPath(source, dest, path, world, agent):
	### YOUR CODE GOES BELOW HERE ###
	# Skip current node if agent already has a clear shot to the next node
	remove = []
	i = 0
	while i < len(path) - 1 and clearShot(source, path[i + 1], world.getLinesWithoutBorders(), agent):
		remove.append(path[i])
		i += 1
	path = [node for node in path if node not in remove]

	# Same thing but going backwards from destination
	remove = []
	i = len(path) - 1
	while i > 0 and clearShot(dest, path[i - 1], world.getLinesWithoutBorders(), agent):
		remove.append(path[i])
		i -= 1
	path = [node for node in path if node not in remove]
	### YOUR CODE GOES BELOW HERE ###
	return path

### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
	### YOUR CODE GOES BELOW HERE ###
	path = nav.getPath()	# Already popped current move target
	if path is None:
		return False

	path.append(nav.getDestination())

	# Starting from the destination, work backwards to find the latest node you have a clear shot to
	i = len(path) - 1
	while i > 0 and not clearShot(nav.agent.getLocation(), path[i], nav.world.getLinesWithoutBorders(), nav.agent):
		i -= 1

	if i > 0:
		nav.agent.moveToTarget(path[i])
		path = path[i + 1:]
		nav.setPath(path)
		return True
	### YOUR CODE GOES ABOVE HERE ###
	return False

### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### agent: the Agent object
def clearShot(p1, p2, worldLines, agent):
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
	for obstacle in worldLines:
		if rayTrace(p1, p2, obstacle) is not None or rayTrace(leftPoint1, leftPoint2, obstacle) is not None or rayTrace(rightPoint1, rightPoint2, obstacle) is not None:
			clear = False
			break

	if clear:
		return True
	### YOUR CODE GOES ABOVE HERE ###
	return False
