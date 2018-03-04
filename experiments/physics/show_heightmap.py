#!/usr/bin/env python3
import argparse

import numpy as np

from ledworld import LedWorld
from pyledstrip import LedStrip


class Game:
    def __init__(self, strip: LedStrip):
        self.strip = strip
        self.things = []
        self.age = 0

    def loop(self):
        self.strip.clear()

        y_min = np.min(world.to_np()[2,:])
        y_max = np.max(world.to_np()[2,:])

        for led in world.leds.values():
            # print(led)
            self.strip.set_hsv(led.id, (led.y - y_min) / (y_max - y_min), 1.0, 1.0)

        self.strip.transmit()


def main(args):
    strip = LedStrip(args=args)
    global world
    world = LedWorld.from_json_file("data/heightmap.default.json")
    world.plot()

    game = Game(strip)
    game.loop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gravity-based LED particle simulation')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
