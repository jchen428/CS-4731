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
from moba import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states.extend([Move, Defend, FollowEnemy, AttackEnemy, MoveToEnemyTower, MoveToEnemyBase, AttackTower, AttackBase, Done])
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)

############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.
class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		self.agent.changeState(Move)
		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)
class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:
class Move(State):

	def execute(self, delta = 0):
		#if self.agent.world.getBaseForTeam(self.agent.team).numSpawned < 4:
			#self.agent.changeState(Defend)
		if len(self.agent.world.getEnemyTowers(self.agent.team)) > 0:
			self.agent.changeState(MoveToEnemyTower)
		elif len(self.agent.world.getEnemyBases(self.agent.team)) > 0:
			self.agent.changeState(MoveToEnemyBase)
		else:
			self.agent.changeState(Done)

id = 1
class Defend(State):

	def enter(self, oldstate):
		global id
		if id > 3:
			id = 1
		self.id = id
		id += 1

		self.baseLoc = self.agent.world.getBaseForTeam(self.agent.team).getLocation()
		# Top left
		if self.baseLoc[0] < self.agent.world.dimensions[0] / 2 and self.baseLoc[1] < self.agent.world.dimensions[1] / 2:
			top = (self.baseLoc[0] + 200, self.baseLoc[1])
			mid = (self.baseLoc[0] + 150, self.baseLoc[1] + 150)
			bot = (self.baseLoc[0], self.baseLoc[1] + 200)
		# Top right
		elif self.baseLoc[0] > self.agent.world.dimensions[0] / 2 and self.baseLoc[1] < self.agent.world.dimensions[1] / 2:
			top = (self.baseLoc[0] - 200, self.baseLoc[1])
			mid = (self.baseLoc[0] - 150, self.baseLoc[1] + 150)
			bot = (self.baseLoc[0], self.baseLoc[1] + 200)
		# Bot left
		elif self.baseLoc[0] < self.agent.world.dimensions[0] / 2 and self.baseLoc[1] > self.agent.world.dimensions[1] / 2:
			top = (self.baseLoc[0], self.baseLoc[1] - 200)
			mid = (self.baseLoc[0] + 150, self.baseLoc[1] - 150)
			bot = (self.baseLoc[0] + 200, self.baseLoc[1])
		# Bot right
		else:
			top = (self.baseLoc[0], self.baseLoc[1] - 200)
			mid = (self.baseLoc[0] - 150, self.baseLoc[1] - 150)
			bot = (self.baseLoc[0] - 200, self.baseLoc[1])

		if self.id == 1:
			self.agent.navigateTo(top)
		elif self.id == 2:
			self.agent.navigateTo(mid)
		elif self.id == 3:
			self.agent.navigateTo(bot)

	def execute(self, delta = 0):
		enemies = self.agent.world.getEnemyNPCs(self.agent.team)
		if len(enemies) > 0:
			dists = []
			for enemy in enemies:
				dists.append((distance(self.baseLoc, enemy.getLocation()), enemy))
			nearestEnemy = min(dists)
			if nearestEnemy[0] < 500:
				self.agent.changeState(FollowEnemy, nearestEnemy[1])

	def exit(self):
		self.agent.stopMoving()

class FollowEnemy(State):

	def parseArgs(self, args):
		self.target = args[0]

	def enter(self, oldstate):
		self.agent.navigateTo(self.target.getLocation())

	def execute(self, delta = 0):
		if self.agent.moveTarget is None:
			self.agent.navigateTo(self.target.getLocation())
		elif distance(self.agent.getLocation(), self.target.getLocation()) <= BIGBULLETRANGE:
			self.agent.changeState(AttackEnemy, self.target)

	def exit(self):
		self.agent.stopMoving()

class AttackEnemy(State):

	def parseArgs(self, args):
		self.target = args[0]

	def execute(self, delta = 0):
		if distance(self.agent.getLocation(), self.target.getLocation()) <= BIGBULLETRANGE and self.target.alive:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()
		elif self.target.alive:
			self.agent.changeState(FollowEnemy, self.target)
		else:
			self.agent.changeState(Defend)

class MoveToEnemyTower(State):

	def enter(self, oldstate):
		enemyTowers = self.agent.world.getEnemyTowers(self.agent.team)
		dists = []
		for tower in enemyTowers:
			dists.append((distance(self.agent.getLocation(), tower.getLocation()), tower))
		self.nearestTower = min(dists)[1]

	def execute(self, delta = 0):
		if self.agent.moveTarget is None:
			self.agent.navigateTo(self.nearestTower.getLocation())
		elif distance(self.agent.getLocation(), self.nearestTower.getLocation()) <= BIGBULLETRANGE:
			self.agent.changeState(AttackTower, self.nearestTower)

	def exit(self):
		self.agent.stopMoving()

class MoveToEnemyBase(State):

	def enter(self, oldstate):
		enemyBases = self.agent.world.getEnemyBases(self.agent.team)
		dists = []
		for base in enemyBases:
			dists.append((distance(self.agent.getLocation(), base.getLocation()), base))
		self.nearestBase = min(dists)[1]

	def execute(self, delta = 0):
		if self.agent.moveTarget is None:
			self.agent.navigateTo(self.nearestBase.getLocation())
		elif distance(self.agent.getLocation(), self.nearestBase.getLocation()) <= BIGBULLETRANGE:
			self.agent.changeState(AttackBase, self.nearestBase)

	def exit(self):
		self.agent.stopMoving()

class AttackTower(State):

	def parseArgs(self, args):
		self.target = args[0]

	def enter(self, oldstate):
		self.originalLoc = self.agent.getLocation()
		self.targetLoc = self.target.getLocation()

		dy = self.originalLoc[1] - self.targetLoc[1]
		dx = self.originalLoc[0] - self.targetLoc[0]
		theta = math.atan2(dy, dx)
		offsetAngle1 = theta - math.pi / 8
		offsetAngle2 = theta + math.pi / 8
		self.offset1 = (self.targetLoc[0] + 0.75 * BIGBULLETRANGE * math.cos(offsetAngle1), self.targetLoc[1] + 0.75 * BIGBULLETRANGE * math.sin(offsetAngle1))
		self.offset2 = (self.targetLoc[0] + 0.75 * BIGBULLETRANGE * math.cos(offsetAngle2), self.targetLoc[1] + 0.75 * BIGBULLETRANGE * math.sin(offsetAngle2))
		self.agent.navigateTo(self.offset1)

	def execute(self, delta = 0):
		enemyTowers = self.agent.world.getEnemyTowers(self.agent.team)
		if self.target in enemyTowers:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()

			if self.agent.moveTarget is None:
				if distance(self.agent.getLocation(), self.offset1) < 25:
					self.agent.navigateTo(self.offset2)
				elif distance(self.agent.getLocation(), self.offset2) < 25:
					self.agent.navigateTo(self.offset1)
		else:
			self.agent.changeState(Move)

class AttackBase(State):

	def parseArgs(self, args):
		self.target = args[0]

	def enter(self, oldstate):
		self.originalLoc = self.agent.getLocation()
		self.targetLoc = self.target.getLocation()

		dy = self.originalLoc[1] - self.targetLoc[1]
		dx = self.originalLoc[0] - self.targetLoc[0]
		theta = math.atan2(dy, dx)
		offsetAngle1 = theta - math.pi / 8
		offsetAngle2 = theta + math.pi / 8
		self.offset1 = (self.targetLoc[0] + BIGBULLETRANGE * math.cos(offsetAngle1), self.targetLoc[1] + BIGBULLETRANGE * math.sin(offsetAngle1))
		self.offset2 = (self.targetLoc[0] + BIGBULLETRANGE * math.cos(offsetAngle2), self.targetLoc[1] + BIGBULLETRANGE * math.sin(offsetAngle2))
		self.agent.navigateTo(self.offset1)

	def execute(self, delta = 0):
		enemyBases = self.agent.world.getEnemyBases(self.agent.team)
		if self.target in enemyBases:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()

			if self.agent.moveTarget is None:
				if distance(self.agent.getLocation(), self.offset1) < 25:
					self.agent.navigateTo(self.offset2)
				elif distance(self.agent.getLocation(), self.offset2) < 25:
					self.agent.navigateTo(self.offset1)
		else:
			self.agent.changeState(Move)

class Done(State):
	def enter(self, args):
		self.agent.stopMoving()
		print "Total minions spawned: ", self.agent.world.getBaseForTeam(self.agent.team).numSpawned
