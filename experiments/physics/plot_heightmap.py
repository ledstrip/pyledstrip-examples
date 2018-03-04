#!/usr/bin/env python3
import argparse

import math

from ledworld import LedWorld
from particles2 import angle_between
from pyledstrip import LedStrip
import numpy as np


if __name__ == '__main__':
    world = LedWorld.from_json_file("data/heightmap.default.json")
    fig = world.plot()
    a = fig.gca()
    for i in range(110, 140):

        sp_old = world.leds[i].get_xy()
        sp_new = world.leds[i +1].get_xy()

        # inclined plane
        ang = angle_between(sp_old, sp_new)

        # a.annotate("%s %.1f %.1f" % (i, np.rad2deg(ang), math.sin(ang)), (world.leds[i].x, world.leds[i].y))
        a.annotate("%.1f" % (math.sin(ang)), (world.leds[i].x, world.leds[i].y))
        a.plot([world.leds[i].x], [world.leds[i].y], "rx")



    fig.show()