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
from gridnavigator import *




nav = GreedyGridNavigator()

#This is the tall one with sparse obstacles
world = GameWorld(SEED, (768,1024), (768,1024))
agent = Agent(AGENT, (384,SCREEN[1]/2), 0, SPEED, world)

polygons = [[(20, 0), (20, 38), (38, 37), (37, 0)],
            [(210, 5), (200, 15), (220, 15)]]


world.initializeTerrain(polygons, (255, 0, 0), 1)
world.setPlayerAgent(agent)
agent.setNavigator(nav)
nav.setWorld(world)
world.initializeRandomResources(NUMRESOURCES)
world.debugging = True
world.run()
