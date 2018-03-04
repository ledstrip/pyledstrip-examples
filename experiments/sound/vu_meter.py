#!/usr/bin/python3
import argparse
import random

import pyaudio

from amplitude import Amplitude
from pyledstrip import LedStrip
from vu_constants import RATE, INPUT_FRAMES_PER_BLOCK

# !/usr/bin/env python
# coding: utf-8

PERIOD = 0.05



class Debris:
    def __init__(self, pos, v, ch, cs, cv):
        self.pos = pos
        self.v = v
        self.ch = ch
        self.cs = cs
        self.cv = cv
        self.age = 0

    def move(self, t):
        self.age += t
        self.cv *= 0.9
        self.pos += self.v * t

        if self.age > 3:
            return []
        else:
            return [self]

    def paint(self, strip: LedStrip):
        strip.add_hsv(self.pos,
                      random.uniform(0,1), #0.33,  # self.ch,
                      self.cs,
                      self.cv / 100
                      )


class Rocket:
    def __init__(self, pos, v, ch, cs, cv):
        self.pos = pos
        self.v = v
        self.ch = ch
        self.cs = cs
        self.cv = cv
        self.age = 0

    def move(self, t):
        self.age += t
        self.pos += self.v * t

        if g_amp > 120: # self.age > 3:
            debris = []
            for i in range(3):
                item = Debris(self.pos, 10 * random.uniform(-1, 1), random.uniform(0, 1), 1, 1)
                debris.append(item)
            return debris
        else:
            return [self]

    def paint(self, strip: LedStrip):
        strip.add_hsv(self.pos,
                      0.16,  # self.ch,
                      self.cs, self.cv)


class Launcher:
    def __init__(self, pos, ch, cs, cv):
        self.pos = pos
        self.ch = ch
        self.cs = cs
        self.cv = cv
        self.age = 0
        self.freq = 0.5 * random.uniform(0.0, 1)

    def move(self, t):
        self.age += t

        if self.age > self.freq:
            self.age -= self.freq
            rocket = Rocket(
                self.pos,
                10 * random.uniform(0.5, 1) * random.choice([1,-1]),
                random.uniform(0, 1),
                1,
                1
            )
            return [self, rocket]
        else:
            return [self]

    def paint(self, strip: LedStrip):
        strip.add_hsv(self.pos,
                      0.00,  # self.ch,
                      self.cs, self.cv)


class World:

    def __init__(self, strip: LedStrip):
        worldsize = strip.led_count

        self.lauchners = []
        for i in range(3):
            self.lauchners.append(
                Launcher(
                    random.uniform(0, worldsize),
                    0,
                    1,
                    1
                )
            )

    def update(self, strip: LedStrip):
        strip.clear()

        newStuff = []
        for rocket in self.lauchners:
            results = rocket.move(PERIOD)  # tickrate is perfect
            newStuff += results

        self.lauchners = newStuff

        for rocket in self.lauchners:
            rocket.paint(strip)

        strip.transmit()


def main(args):
    strip = LedStrip(args=args, loop=True, flip=True)
    w = World(strip)
    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(format=pyaudio.paInt16,
                            channels=2,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=INPUT_FRAMES_PER_BLOCK
                            )

        maximal = Amplitude()
        while True:
            data = stream.read(INPUT_FRAMES_PER_BLOCK)
            amp = Amplitude.from_data(data)
            if amp > maximal:
                maximal = amp
            #amp.display(scale=600, mark=maximal)
            update(None, strip, amp.to_int(scale=300), w)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

g_amp = 0


def update(self, strip: LedStrip, amp, w):
    #  strip.clear()
    #
    # print("amp is %s" % amp)
    #
    #  for i in range(amp):
    #      strip.set_pixel_rgb(i, 1, 0,0 )
    #
#  strip.transmit()
    global g_amp
    g_amp = amp
    w.update(strip)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
