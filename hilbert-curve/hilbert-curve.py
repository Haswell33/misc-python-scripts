#!/usr/bin/env python3
import sys
from turtle import *
import matplotlib
matplotlib.use('Agg')


def hilbert(level, angle, step):
    if level == 0:
        return
    right(angle)
    hilbert(level - 1, -angle, step)
    forward(step)
    left(angle)
    hilbert(level - 1, angle, step)
    forward(step)
    hilbert(level - 1, angle, step)
    left(angle)
    forward(step)
    hilbert(level - 1, -angle, step)
    right(angle)


if __name__ == '__main__':  # input params: {scriptname}.py {number}
    level = int(sys.argv[1])
    size = 200
    penup()
    goto(-size / 2.0, size / 2.0)
    pendown()
    hilbert(level, 90, size / (2 ** level - 1))  # For positioning turtle
    done()
