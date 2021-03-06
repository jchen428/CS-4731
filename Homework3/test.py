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
from apspnavigator import *
from nearestgatherer import *

def getLocation(mover):
	return mover.getLocation()


def cloneAPSPNavigator(nav):
	newnav = APSPNavigator()
	newnav.world = nav.world
	newnav.pathnodes = nav.pathnodes
	newnav.pathnetwork = nav.pathnetwork
	newnav.next = nav.next
	newnav.dist = nav.dist
	return newnav

nav = APSPNavigator()


world = GameWorld(None, (1224, 900), (1224, 900))
agent = Agent(AGENT, (SCREEN[0]/2, SCREEN[1]/2), 0, SPEED, world)
world.initializeTerrain([[(100, 100), (200, 100), (300, 300)]])
world.setPlayerAgent(agent)
nav.setWorld(world)
agent.setNavigator(nav)
world.initializeResources([(220, 575), (550, 700), (700, 500), (900, 300)], RESOURCE)
world.debugging = True

g = NearestGatherer(NPC, (50, 50), 0.0, SPEED, world)
nav2 = cloneAPSPNavigator(nav)
g.setNavigator(nav2)
g.setTargets(map(getLocation, list(world.resources)))
world.addNPC(g)
g.start()

world.run()
