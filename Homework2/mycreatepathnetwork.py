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

# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
	nodes = []
	edges = []
	polys = []
	### YOUR CODE GOES BELOW HERE ###
	points = world.getPoints()
	lines = world.getLines()
	obstacles = [obstacle.getPoints() for obstacle in world.getObstacles()]
	triangleLines = []

	# Find triangles
	for point0 in points:
		for point1 in points:
			if point1 is not point0: # and point0 not in currTriangle and point1 not in currTriangle:
				if rayTraceWorldNoEndPoints(point0, point1, lines + triangleLines) is not None:
					if (point0, point1) not in lines + triangleLines and (point1, point0) not in lines + triangleLines:
						continue

				for point2 in points:
					if point2 is not point0 and point2 is not point1: # and point2 not in currTriangle:
						if rayTraceWorldNoEndPoints(point1, point2, lines + triangleLines) is not None:
							if (point1, point2) not in lines + triangleLines and (point2, point1) not in lines + triangleLines:
								continue

						if rayTraceWorldNoEndPoints(point2, point0, lines + triangleLines) is not None:
							if (point2, point0) not in lines + triangleLines and (point0, point2) not in lines + triangleLines:
								continue

						triangleLines.append((point0, point1))
						triangleLines.append((point1, point2))
						triangleLines.append((point2, point0))
						newTriangle = [point0, point1, point2]
						polys.append(newTriangle)

	remove = []
	for i in range(len(polys)):
		if polys[i] not in remove:
			triPermutations = [[polys[i][0], polys[i][1], polys[i][2]],
							[polys[i][0], polys[i][2], polys[i][1]],
							[polys[i][1], polys[i][0], polys[i][2]],
							[polys[i][1], polys[i][2], polys[i][0]],
							[polys[i][2], polys[i][0], polys[i][1]],
							[polys[i][2], polys[i][1], polys[i][0]]]

			# Remove triangles that are also obstacles
			broken = False
			for obstacle in obstacles:
				if obstacle in triPermutations:
					remove.append(polys[i])
					broken = True
					break
			if broken:
				continue

			# Remove duplicate permutations of triangles
			for j in range(i + 1, len(polys)):
				if polys[j] in triPermutations:
					remove.append(polys[j])
	polys = [poly for poly in polys if poly not in remove]

	remove = []
	for poly in polys:
		for obstacle in obstacles:
			# Remove triangles that encompass obstacles
			for point in obstacle:
				if pointInsidePolygonPoints(point, poly) and (not pointOnPolygon(point, poly) and point not in poly):
					remove.append(poly)
					break

			# Remove triangles that cut through obstacles
			for i in range(len(poly)):
				point0 = poly[i]
				if i == len(poly) - 1:
					point1 = poly[0]
				else:
					point1 = poly[i + 1]
				midpoint = ((point0[0] + point1[0]) / 2, (point0[1] + point1[1]) / 2)
				if pointInsidePolygonPoints(midpoint, obstacle) and pointOnPolygon(midpoint, obstacle) is False:
					remove.append(poly)
					break
	polys = [poly for poly in polys if poly not in remove]

	# Merge triangles
	i = 0
	polysLength = len(polys)
	while i < polysLength:
		j = 0
		while j < polysLength:
			if polys[j] is not polys[i]:
				sharedPoints = polygonsAdjacent(polys[i], polys[j])
				if sharedPoints is not False:
					newPoly = polys[i] + polys[j]

					# Remove duplicate points
					for point in sharedPoints:
						newPoly.remove(point)

					# Find a crude "center" of merged polygon (midpoint of common edge)
					center = ((sharedPoints[0][0] + sharedPoints[1][0]) / 2, (sharedPoints[0][1] + sharedPoints[1][1]) / 2)

					# Sort newPoly's points in clockwise order
					sorting = []
					for point in newPoly:
						val = math.atan2(point[1] - center[1], point[0] - center[0])
						sorting.append((val, point))
					sorting.sort(key = lambda p:p[0])
					newPoly = []
					for entry in sorting:
						newPoly.append(entry[1])

					# Check if newPoly is convex
					if isConvex(newPoly):
						polys.append(newPoly)
						remove0 = polys[i]
						remove1 = polys[j]
						polys.remove(remove0)
						polys.remove(remove1)
						i = -1
						polysLength -= 1
						break
			j += 1
		i += 1

	# Place path nodes at center of polygons and midpoints of polygon edges
	radius = world.getAgent().getMaxRadius()
	centers = []
	for poly0 in polys:
		center = (sum(map(lambda p: p[0], poly0))/float(len(poly0)), sum(map(lambda p: p[1], poly0))/float(len(poly0)))
		nodes.append(center)
		centers.append(center)

		for poly1 in polys:
			if poly1 is not poly0:
				sharedPoints = polygonsAdjacent(poly0, poly1)
				if sharedPoints is not False:
					midpoint = ((sharedPoints[0][0] + sharedPoints[1][0]) / 2, (sharedPoints[0][1] + sharedPoints[1][1]) / 2)
					if midpoint not in nodes:
						nodes.append(midpoint)

	# Create path edges by connecting unobstructed pathnodes within each polygon
	connectedNodes = []
	for poly in polys:
		for node0 in nodes:
			for node1 in nodes:
				if node1 is not node0 and \
						(pointOnPolygon(node0, poly) or pointInsidePolygonPoints(node0, poly)) and \
						(pointOnPolygon(node1, poly) or pointInsidePolygonPoints(node1, poly)) and \
						(node0, node1) not in edges and (node1, node0) not in edges:
					# Calculate angle of the line
					dy = node0[1] - node1[1]
					dx = node0[0] - node1[0]
					theta = math.atan2(dy, dx)

					# Calculate perpendicular angles
					left = theta + math.pi / 2
					right = theta - math.pi / 2

					# Calculate points to draw parallel rays
					leftPoint0 = (node0[0] + radius * math.cos(left), node0[1] + radius * math.sin(left))
					leftPoint2 = (node1[0] + radius * math.cos(left), node1[1] + radius * math.sin(left))
					rightPoint0 = (node0[0] + radius * math.cos(right), node0[1] + radius * math.sin(right))
					rightPoint1 = (node1[0] + radius * math.cos(right), node1[1] + radius * math.sin(right))

					# Check for obstacle collisions against three parallel lines and connect pathnodes if no collisions are found
					if rayTraceWorld(node0, node1, lines) is None and rayTraceWorld(leftPoint0, leftPoint2, lines) is None and rayTraceWorld(rightPoint0, rightPoint1, lines) is None:
						edges.append((node0, node1))
						if node0 not in connectedNodes:
							connectedNodes.append(node0)
						if node1 not in connectedNodes:
							connectedNodes.append(node1)

	# Remove disconnected nodes
	nodes = [node for node in nodes if node in connectedNodes]

	"""
	for poly in polys:
		drawPolygon(poly, world.debug, (0, 255, 0), 6)
	#for edge in edges:
		#pygame.draw.line(world.debug, (0, 0, 255), edge[0], edge[1], 3)
	for node in nodes:
		drawCross(world.debug, node, (255, 0, 0), 5, 5)
	print "points: ", points
	print "obstacles: ", obstacles
	print len(polys), "polys: ", polys
	print len(nodes), "nodes: ", nodes
	"""
	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys
