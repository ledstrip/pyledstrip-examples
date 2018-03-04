#!/usr/bin/env python
# coding: utf-8

import argparse
import random

from periodicx import periodicx
from pyledstrip import LedStrip

random.seed()


class Snake:
	PERIOD = 1 / 60

	food = None
	snake = [0, 0, 0, 0]
	velocity = 0
	step = 0

	def update(self, strip):
		if self.food is None:
			self.food = random.randrange(strip.led_count)
			strip.set_pixel_rgb(self.food, 1, 0, 0)

		for i, part in enumerate(self.snake[::-1]):
			d = len(self.snake) - i + 1
			d = 4 if d < 4 else d
			d = max(1 / round(d / 4), 0.1)

			if 0 <= part < strip.led_count:
				if i % 4 < 2:
					strip.set_pixel_rgb(part, int(15 * d), int(40 * d), 0)
				else:
					strip.set_pixel_rgb(part, 0, int(40 * d), int(10 * d))
		if 0 <= self.snake[0] < strip.led_count:
			strip.set_pixel_rgb(self.snake[0], 170, 100, 0)
		strip.transmit()

		if self.food > self.snake[0]:
			self.velocity += 0.03
			self.velocity = 1 if self.velocity > 1 else self.velocity
		else:
			self.velocity -= 0.03
			self.velocity = -1 if self.velocity < -1 else self.velocity

		self.step += self.velocity

		if self.step >= 1 or self.step <= -1:
			if self.step >= 1:
				self.snake.insert(0, self.snake[0] + 1)
				self.step -= 1
			elif self.step <= -1:
				self.snake.insert(0, self.snake[0] - 1)
				self.step += 1
			if self.food not in self.snake:
				strip.set_pixel_rgb(self.snake.pop(), 0, 0, 0)
			else:
				while self.food in self.snake:
					self.food = random.randrange(strip.led_count)
				strip.set_pixel_rgb(self.food, 128, 0, 0)


def main(args):
	strip = LedStrip(args=args, led_count=600, power_limit=0.1)
	periodicx(Snake().update, Snake.PERIOD, strip)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Example code for pyledstrip.')
	LedStrip.add_arguments(parser)
	main(parser.parse_args())
