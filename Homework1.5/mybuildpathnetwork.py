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

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates the pathnetwork as a list of lines between all pathnodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):
	lines = []
	### YOUR CODE GOES BELOW HERE ###
	obstacles = world.getLines()
	threshold = 1.5 * agent.getRadius()

	# Iterate through every possible pair of pathnodes, excluding identical nodes and duplicate pairs
	for node1 in pathnodes:
		for node2 in pathnodes:
			if node1 is not node2 and (node1, node2) not in lines and (node2, node1) not in lines:
				obstructed = False

				# Calculate angle of the line
				dy = node1[1] - node2[1]
				dx = node1[0] - node2[0]
				theta = math.atan2(dy, dx)

				# Calculate perpendicular angles
				left = theta + math.pi / 2
				right = theta - math.pi / 2

				# Calculate points to draw parallel rays
				leftPoint1 = (node1[0] + threshold * math.cos(left), node1[1] + threshold * math.sin(left))
				leftPoint2 = (node2[0] + threshold * math.cos(left), node2[1] + threshold * math.sin(left))
				rightPoint1 = (node1[0] + threshold * math.cos(right), node1[1] + threshold * math.sin(right))
				rightPoint2 = (node2[0] + threshold * math.cos(right), node2[1] + threshold * math.sin(right))

				#print theta * 180 / math.pi
				#print node1, ", ", node2
				#print leftPoint1, ", ", leftPoint2
				#print rightPoint1, ", ", rightPoint2, "\n"

				# Check for obstacle collisions against three parallel lines
				for obstacle in obstacles:
					if rayTrace(node1, node2, obstacle) is not None or rayTrace(leftPoint1, leftPoint2, obstacle) is not None or rayTrace(rightPoint1, rightPoint2, obstacle) is not None:
						obstructed = True
						break

				# If none of the lines are obstructed, then connect the pathnodes
				if obstructed is False:
					lines.append((node1, node2))
	### YOUR CODE GOES ABOVE HERE ###
	return lines
