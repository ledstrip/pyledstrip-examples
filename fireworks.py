#!/usr/bin/python

import random
import time

from pyledstrip import pyledstrip

# todo time instead of frame based calculations
# todo do not sleep fixed amount of time

# one sided launcher
EXPLOSION_SPEED = 0.05
EXPLOSION_SIZE_MIN = 5
EXPLOSION_SIZE_MAX = 40
EXPLOSION_SPEED_MIN = 0.5
EXPLOSION_SPEED_MAX = 1.5
ROCKET_LAUNCH_POS = 0
ROCKET_LAUNCH_DIRECTIONS = [1.0]
ROCKET_SPEED_MIN = 0.5
ROCKET_SPEED_MAX = 8.5

# centered launcher
# EXPLOSION_SPEED = 0.05
# EXPLOSION_SIZE_MIN = 12
# EXPLOSION_SIZE_MAX = 40
# EXPLOSION_SPEED_MIN = 0.1
# EXPLOSION_SPEED_MAX = 1.0
# ROCKET_LAUNCH_POS = pyledstrip.LED_COUNT / 2
# ROCKET_LAUNCH_DIRECTIONS = [-1.0, 1.0]
# ROCKET_SPEED_MIN = 1.0
# ROCKET_SPEED_MAX = 4.0

rockets = []
particles = []


class Rocket:
	pos = 0
	speed = 0
	lastbright = False

	def __init__(self, pos, speed):
		self.pos = pos
		self.speed = speed

	def update(self):
		self.pos += self.speed
		self.speed *= 0.97

	def draw(self):
		brightness = 1.0
		if self.lastbright:
			brightness = 0.0

		self.lastbright = not self.lastbright
		pyledstrip.add_rgb(self.pos, brightness, brightness, brightness)


class Particle:
	pos = 0
	speed = 0
	hue = 0
	brightness = 0
	decay = 0

	def __init__(self, pos, speed, hue, brightness, decay=0.95):
		self.pos = pos
		self.speed = speed
		self.hue = hue
		self.brightness = brightness
		self.decay = decay

	def update(self):
		self.pos += self.speed
		self.speed *= 0.985
		self.brightness *= self.decay

	def draw(self):
		pyledstrip.add_hsv(self.pos, self.hue, 1.0, self.brightness)


def maprange(value, frommin, frommax, tomin, tomax):
	return tomin + (tomax - tomin) * (value - frommin) / (frommax - frommin)


def launchrocket():
	global rockets
	rockets.append(Rocket(
		ROCKET_LAUNCH_POS,
		random.choice(ROCKET_LAUNCH_DIRECTIONS) * random.uniform(ROCKET_SPEED_MIN, ROCKET_SPEED_MAX)
	))


def explosion(center):
	global particles
	color_center = random.random()
	size = random.randrange(EXPLOSION_SIZE_MIN, EXPLOSION_SIZE_MAX)
	for i in range(0, size):
		particles.append(Particle(
			center,
			random.choice([-1.0, 1.0]) * random.uniform(0.0, maprange(
				size,
				EXPLOSION_SIZE_MIN, EXPLOSION_SIZE_MAX,
				EXPLOSION_SPEED_MIN, EXPLOSION_SPEED_MAX
			)),
			(color_center + random.choice([-0.25, 0.25])) % 1.0,
			random.uniform(0.6, 1.0)
		))


def trail(pos):
	particles.append(Particle(pos, 0, random.uniform(0.0, 0.2) % 1.0, random.uniform(0.1, 0.2), 0.8))


if __name__ == "__main__":
	frame = 0
	next_rocket = 0
	while True:
		if frame == next_rocket:
			launchrocket()
			next_rocket = frame + random.randrange(30, 100)

		pyledstrip.clear()

		for particle in particles:
			particle.update()
			particle.draw()

		particles = list(filter(lambda item: item.brightness > 0.01, particles))

		for rocket in rockets:
			trail(rocket.pos)
			rocket.update()
			rocket.draw()
			if abs(rocket.speed) <= EXPLOSION_SPEED:
				explosion(rocket.pos)

		rockets = list(filter(lambda rocket: abs(rocket.speed) > EXPLOSION_SPEED, rockets))

		pyledstrip.transmit()
		frame += 1
		time.sleep(0.015)
