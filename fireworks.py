#!/usr/bin/env python
# coding: utf-8

import argparse
import random
import time

from periodicx import periodicx
from pyledstrip import LedStrip

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

    def draw(self, strip):
        brightness = 1.0
        if self.lastbright:
            brightness = 0.0

        self.lastbright = not self.lastbright
        strip.add_rgb(self.pos, brightness, brightness, brightness)


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

    def draw(self, strip):
        strip.add_hsv(self.pos, self.hue, 1.0, self.brightness)


def maprange(value, frommin, frommax, tomin, tomax):
    return tomin + (tomax - tomin) * (value - frommin) / (frommax - frommin)


class Fireworks:
    PERIOD = 1 / 60

    rockets = []
    particles = []
    next_rocket = 0

    def launchrocket(self):
        self.rockets.append(Rocket(
            ROCKET_LAUNCH_POS,
            random.choice(ROCKET_LAUNCH_DIRECTIONS) * random.uniform(ROCKET_SPEED_MIN, ROCKET_SPEED_MAX)
        ))

    def explosion(self, center):
        color_center = random.random()
        size = random.randrange(EXPLOSION_SIZE_MIN, EXPLOSION_SIZE_MAX)
        for i in range(0, size):
            self.particles.append(Particle(
                pos=center,
                speed=random.choice([-1.0, 1.0]) * random.uniform(0.0, maprange(
                    size,
                    EXPLOSION_SIZE_MIN, EXPLOSION_SIZE_MAX,
                    EXPLOSION_SPEED_MIN, EXPLOSION_SPEED_MAX
                )),
                hue=(color_center + random.choice([-0.25, 0.25])) % 1.0,
                brightness=random.uniform(0.6, 1.0)
            ))

    def trail(self, pos):
        self.particles.append(Particle(
            pos=pos,
            speed=0,
            hue=random.uniform(0.0, 0.2) % 1.0,
            brightness=random.uniform(0.1, 0.2),
            decay=0.8)
        )

    def update(self, strip):
        if time.time() >= self.next_rocket:
            self.launchrocket()
            self.next_rocket = time.time() + random.uniform(0.9, 3.0)

        strip.clear()

        for particle in self.particles:
            particle.update()
            particle.draw(strip)

        self.particles = list(filter(lambda item: item.brightness > 0.01, self.particles))

        for rocket in self.rockets:
            self.trail(rocket.pos)
            rocket.update()
            rocket.draw(strip)
            if abs(rocket.speed) <= EXPLOSION_SPEED:
                self.explosion(rocket.pos)

        self.rockets = list(filter(lambda rocket: abs(rocket.speed) > EXPLOSION_SPEED, self.rockets))

        strip.transmit()


def main(args):
    strip = LedStrip(args=args)
    periodicx(Fireworks().update, Fireworks.PERIOD, strip)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
