#!/usr/bin/env python3
import argparse
import collections
import fcntl
import math
import os
import random
import sys
import time

import numpy as np
from scipy.signal import argrelextrema

from ledworld import LedWorld, savitzky_golay
from pyledstrip import LedStrip

LED_PER_METER = 60
LED_DIST = 1 / LED_PER_METER
DEFAULT_TTL = 2
RANDOM_SPAWNS = False


class nonblocking(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()

    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)

    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)


class Thing:
    def tick(self, t):
        pass

    def is_alive(self, strip):  # TODO get rid of strip
        return False

    def paint(self, strip: LedStrip):
        pass

    def spawn_things(self, strip):
        return []


def angle_between(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    res = np.arctan2(dy, dx)
    # print(p1, p2, dx, dy, np.rad2deg(res))
    return res


class Paintable(Thing):
    pos = None
    v = None
    hue = None
    ttl = None
    mass = None
    width = None

    def __init__(self, pos, v, hue, mass, radius, ttl=DEFAULT_TTL):
        self.pos = pos
        self.v = v
        self.hue = hue
        self.ttl = ttl
        self.mass = mass
        self.radius = radius
        self.hist = collections.deque(maxlen=30)

    def __str__(self):
        return "P: pos=%.2f v=%.2f h=%.2f" % (self.pos, self.v, self.hue)

    def tick(self, t, world2=None):
        # TODO check this
        if self.pos < 0:
            self.pos = 298
        if self.pos >= 299:
            self.pos = 1

        # TODO dirty state-not-available-hack
        if world2 is None:
            world2 = world  # world better be something globally defined

        # supporting points
        sp_old = world2.leds[math.floor(self.pos) + 0].get_xy()
        sp_new = world2.leds[math.floor(self.pos) + 1].get_xy()

        # inclined plane
        ang = angle_between(sp_old, sp_new)
        if self.v < 0:
            pass
        g = 9.81 * self.mass
        a_clean = g * math.sin(ang)

        # self-invented friction
        air_resistance = 0.6
        mass = 1  # self.mass
        a_resistance = air_resistance / mass * self.v
        a_final = a_clean - a_resistance
        # a_fake = a

        # semi implicit euler
        self.v += a_final * t
        self.pos += self.v * t * 20

        if abs(self.v) < 0.2:
            self.ttl = self.ttl - t
        else:
            self.ttl = DEFAULT_TTL

        self.hist.append(self.pos)

    def is_alive(self, strip):
        return strip.led_count >= self.pos >= 0 and self.ttl >= 0

    def paint(self, strip: LedStrip):
        pass


class Particle(Paintable):
    def __init__(self, pos, v, hue, mass, radius, ttl=DEFAULT_TTL):
        super().__init__(pos, v, hue=hue, mass=mass, radius=radius)
        self.ttl2 = ttl

    def tick(self, dt, world2=None):
        super().tick(dt, world2)
        self.ttl2 -= dt

    def is_alive(self, strip):
        return super().is_alive(strip) and self.ttl2 > 0

    def paint(self, strip: LedStrip):
        strip.add_hsv(self.pos, self.hue, 1, 1)
        for i, hpos in enumerate(self.hist):
            if i % 5 == 0:
                strip.add_hsv(hpos, self.hue, 1, 0.05 / len(self.hist) * i)

    def spawn_things(self, strip):
        return []


class Launcher(Paintable):
    def __init__(self, pos: float, hue: float, mass: float, radius: float):
        super().__init__(pos, 0, hue, 1.0, radius=radius)
        self.firerate = 1.2
        self.mass = mass
        self.cooldown = self.firerate

    def tick(self, dt, world2=None):
        self.cooldown -= dt

    def spawn_things(self, strip):
        if self.cooldown < 0:
            self.cooldown = self.firerate * random.uniform(0.5, 1)
            s = 2
            s = random.uniform(s / 2, s)
            return [
                Particle(pos=self.pos, v=+s, hue=self.hue, mass=self.mass, radius=self.radius, ttl=1),
                Particle(pos=self.pos, v=-s, hue=self.hue, mass=self.mass, radius=self.radius, ttl=1),
            ]
        else:
            return []


class Game:
    def __init__(self, strip, my_world: LedWorld):
        self.strip = strip
        self.things = []
        self.age = 0

        ys = my_world.to_np()[2, :]
        ys2 = savitzky_golay(ys, 51, 3)

        # plt.plot(ys)
        # plt.plot(ys2)
        # plt.show()
        (minima,) = argrelextrema(ys2, np.greater)
        (maxima,) = argrelextrema(ys2, np.less)

        fig = my_world.plot()
        a = fig.gca()
        # a.annotate("foo", (100,100))

        for extr in minima:
            self.things.append(
                Launcher(pos=extr, hue=2 / 3, mass=-0.1, radius=-0.003)  #blue
            )

            ixys = my_world.to_np()

            a.annotate("min", (ixys[1, extr], ixys[2, extr]))
            print(extr, (ixys[1, extr], ixys[2, extr]))

        for extr in maxima:
            self.things.append(
                Launcher(pos=extr, hue=0, mass=0.5, radius=0.01)
            )

            ixys = my_world.to_np()

            a.annotate("max", (ixys[1, extr], ixys[2, extr]))
            print(extr, (ixys[1, extr], ixys[2, extr]))

        fig.show()

    def handle_input(self):
        # spawn on ENTER key
        with nonblocking(sys.stdin):
            try:
                c = sys.stdin.read(1)
                if ' ' in c:
                    print(".%s." % c)
                    self.things.append(
                        Particle(pos=81, v=random.uniform(-3, 3), hue=random.random(), mass=1.0, radius=1.0, ttl=80)
                    )
                elif len(c) > 0:
                    for particle in self.things:
                        print(particle)
            except IOError:
                pass  # no input

    def loop(self):
        last_time = time.perf_counter()
        while True:
            self.handle_input()
            now = time.perf_counter()
            t = now - last_time
            self.strip.clear()
            # print("%d" % len(self.things))
            self.simulate(t)
            # print("%d" % len(self.things))
            self.paint()
            self.strip.transmit()
            last_time = now
            time.sleep(0.01)

    def simulate(self, t):
        self.age += t
        self.spawn()
        self.things = sorted(self.things, key=lambda p: p.pos)
        next_generation = []
        for i, particle in enumerate(self.things[:]):  # iterate over copy so original can be modified
            particle.tick(t)

            if particle.is_alive(self.strip):
                next_generation.append(particle)

            things = particle.spawn_things(self.strip)
            if things:
                next_generation.extend(things)
        self.things = next_generation

    def spawn(self):
        pass

    def paint(self):
        for particle in self.things:
            particle.paint(self.strip)


def main(args):
    strip = LedStrip(args=args)
    global world
    world = LedWorld.from_json_file("data/heightmap.default.json")
    world.plot()

    game = Game(strip, world)
    game.loop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gravity-based LED particle simulation')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
