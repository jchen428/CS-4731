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

# Creates a grid as a 2D array of True/False values (True =  traversable). Also returns the dimensions of the grid as a (columns, rows) list.
def myCreateGrid(world, cellsize):
    grid = None
    dimensions = (0, 0)
    ### YOUR CODE GOES BELOW HERE ###
    width = world.getDimensions()[0]
    height = world.getDimensions()[1]

    dimensions = (int(width / cellsize), int(height / cellsize))
    grid = [[True for x in range(height)] for x in range(width)]
    lines = world.getLinesWithoutBorders()

    # Check for grid intersections for each line
    for line in lines:
        point0 = line[0]
        point1 = line[1]

        dx = abs(point0[0] - point1[0])
        dy = abs(point0[1] - point1[1])
        x = int(point0[0])
        y = int(point0[1])
        n = 1

        # Determine which way to look starting from point0 with incX and incY
        # diff determines whether a horizontal or vertical gridline will be intersected next
        # A positive diff means a vertical gridline is closer, and a negative diff means horizontal gridline is closer
        # Note: The grid's coordinate system is actually flipped vertically, but the directional descriptions will
        # assume it's a normal cartesian plane.

        # Line is vertical
        if dx == 0:
            incX = 0
            diff = sys.float_info.max
        # Left to right
        elif  point0[0] < point1[0]:
            incX = 1
            n += int(point1[0]) - x
            diff = (int(point0[0]) + 1 - point0[0]) * dy
        # Right to left
        else:
            incX = -1
            n += x - int(point1[0])
            diff = (point0[0] - int(point0[0])) * dy

        # Line is horizontal
        if dy == 0:
            incY = 0
            diff -= sys.float_info.max
        # Bottom to top
        elif point0[1] < point1[1]:
            incY = 1
            n += int(point1[1]) - y
            diff -= (int(point0[1]) + 1 - point0[1]) * dx
        # Top to bottom
        else:
            incY = -1
            n += y - int(point1[1])
            diff -= (point0[1] - int(point0[1])) * dx

        for n in range(n, 0, -1):
            cellX = int(x / cellsize)
            cellY = int(y / cellsize)
            grid[cellX][cellY] = False

            if diff > 0:
                y += incY
                diff -= dx
            else:
                x += incX
                diff += dy

    # Check for unmarked cells inside obstacles
    obstacles = world.getObstacles()
    for x in range(0, width, int(cellsize)):
        for y in range(0, height, int(cellsize)):
            cellX = int(x / cellsize)
            cellY = int(y / cellsize)
            if grid[cellX][cellY] is True:
                for obstacle in obstacles:
                    if pointInsidePolygonLines((x, y), obstacle.getLines()):
                        grid[cellX][cellY] = False
    ### YOUR CODE GOES ABOVE HERE ###
    return grid, dimensions

