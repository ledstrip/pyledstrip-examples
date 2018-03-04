#!/usr/bin/env python3
import argparse
import fcntl
import math
import os
import random
import sys
import collections
import time


import matplotlib.pyplot as plt
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

    def __init__(self, pos, v, hue, ttl=DEFAULT_TTL, radius=1.0):
        self.pos = pos
        self.v = v
        self.hue = hue
        self.ttl = ttl
        self.radius = radius
        self.mass = 2 * radius

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
        # velocity_based_hue = min(math.pow(abs(self.v) / 2, 2), 0.9)
        velocity_based_brightness = max(math.pow(abs(self.v) / 2, 2), 0.1) * min(self.ttl / 3, 1)
        # strip.add_hsv(self.pos - self.radius, self.hue, 1, velocity_based_brightness)
        strip.add_hsv(self.pos, self.hue, 1, velocity_based_brightness)
        # strip.add_hsv(self.pos + self.radius, self.hue, 1, velocity_based_brightness)

        for i, hpos in enumerate(self.hist):
            strip.add_hsv(hpos, self.hue, 1, 1) # 1/len(self.hist) * i)


class Particle(Paintable):
    def __init__(self, pos, v, hue, radius=1.0):
        super().__init__(pos, v, hue=hue, radius=radius)
        self.ttl2 = 8

    def tick(self, t, world2=None):
        super().tick(t, world2)
        self.ttl2 -= t

    def is_alive(self, strip):
        return super().is_alive(strip) and self.ttl2 > 0

    def paint(self, strip: LedStrip):
        # velocity_based_hue = min(math.pow(abs(self.v) / 2, 2), 0.9)
        br = math.pow(self.ttl2 / 2, 3)  # max(math.pow(abs(self.v) / 2, 2), 0.1) * min(self.ttl / 3, 1)
        # strip.add_hsv(self.pos - self.radius, self.hue, 1, velocity_based_brightness)
        strip.add_hsv(self.pos, self.hue, 1, br)
        # strip.add_hsv(self.pos + self.radius, self.hue, 1, velocity_based_brightness)

        for i, hpos in enumerate(self.hist):
            if i % 5 == 0:
                strip.add_hsv(hpos, self.hue, 1, 0.05/len(self.hist) * i)

    def spawn_things(self, strip):
        # if self.is_alive(strip):
        #     return []
        # else:
        #     s = 2
        #     return [
        #         Debris(pos=self.pos, v=random.uniform(-s, +s), hue=random.random(), radius=random.uniform(0.5, 2)),
        #         Debris(pos=self.pos, v=random.uniform(-s, +s), hue=random.random(), radius=random.uniform(0.5, 2)),
        #         Debris(pos=self.pos, v=random.uniform(-s, +s), hue=random.random(), radius=random.uniform(0.5, 2)),
        #         Debris(pos=self.pos, v=random.uniform(-s, +s), hue=random.random(), radius=random.uniform(0.5, 2)),
        #         Debris(pos=self.pos, v=random.uniform(-s, +s), hue=random.random(), radius=random.uniform(0.5, 2)),
        #     ]
        return []


class Debris(Paintable):
    def __init__(self, pos, v, hue, radius=1):
        super().__init__(pos, v, hue=hue, radius=radius)
        self.ttl2 = 1
        print("Debris born")

    def tick(self, t, world2=None):
        super().tick(t, world2)
        self.ttl2 -= t

    def is_alive(self, strip):
        return super().is_alive(strip) and self.ttl2 > 0

    def spawn_things(self, strip):
        return []


class Launcher(Paintable):
    def __init__(self, pos: float, hue: float, radius=1.0):
        super().__init__(pos, 0, hue, radius=radius)
        self.firerate = 1.5
        self.cooldown = self.firerate

    def tick(self, t, world2=None):
        self.cooldown -= t

    def spawn_things(self, strip):
        if self.cooldown < 0:
            self.cooldown = self.firerate * random.uniform(0.5, 1)
            s = 0.15 * 4
            s = random.uniform(-s, s)
            return [
                Particle(pos=self.pos, v=+s, hue=self.hue, radius=self.radius),
                Particle(pos=self.pos, v=-s, hue=self.hue, radius=self.radius),
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

        plt.plot(ys)
        plt.plot(ys2)
        plt.show()
        (minima,) = argrelextrema(ys2, np.greater)
        (maxima,) = argrelextrema(ys2, np.less)

        fig = my_world.plot()
        a = fig.gca()
        # a.annotate("foo", (100,100))

        for extr in minima:
            self.things.append(
                Launcher(pos=extr, hue=2 / 3, radius=-0.003) #blue
            )

            ixys = my_world.to_np()

            a.annotate("min", (ixys[1, extr], ixys[2, extr]))
            print(extr, (ixys[1, extr], ixys[2, extr]))

        for extr in maxima:
            self.things.append(
                Launcher(pos=extr, hue=0, radius=0.01)
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
                        Particle(pos=self.strip.led_count,
                                 v=random.uniform(1, 3),
                                 hue=random.random(),
                                 radius=random.uniform(0.5, 2)
                                 )
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
        if RANDOM_SPAWNS:
            spawn = random.random()
            if spawn < 0.005:
                self.things.append(
                    Particle(pos=0, v=-random.uniform(1, 3), hue=random.random(), radius=random.uniform(0.5, 2))
                )
            elif spawn >= 0.995:
                self.things.append(
                    Particle(pos=self.strip.led_count, v=random.uniform(1, 3), hue=random.random(),
                             radius=random.uniform(0.5, 2))
                )

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
