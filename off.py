#!/usr/bin/env python
# coding: utf-8

import argparse

from pyledstrip import LedStrip


def main(args):
    strip = LedStrip(args=args)
    strip.off()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
    LedStrip.add_arguments(parser)
    main(parser.parse_args())
