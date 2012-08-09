# encoding: utf-8
import os
import time
import sys
import termios
import tty
import select

t1 = time.time()
t2 = t1
SNAKE_HEAD_CHARS = (">", "<", "A", "V", 'X')

snake_head_direction = 0
snake_head_position = [1, 1]
snake_head_old_position = [1, 1]

keyboard_in = None

STAGE = \
"""\
##########
#        #
#        #
#        #
#     $  #
#        #
#        #
#        #
#        #
##########
"""
stage = list(STAGE)

def isData():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def render():
    global snake_head_direction
    old_position = snake_head_old_position[0] + snake_head_old_position[1] * 11
    position = snake_head_position[0] + snake_head_position[1] * 11
    stage[old_position] = 'o'
    stage[position] = SNAKE_HEAD_CHARS[snake_head_direction]
    
def paint():
    for unit in stage:
        print unit,

def process():
    global snake_head_direction, keyboard_in, snake_head_position
    #snake_head_position[0] = 1 + (snake_head_position[0] + 1)%4
    position = snake_head_position[0] + snake_head_position[1] * 11
    if stage[position] == '#' or stage[position] == 'o':
        snake_head_direction = 4
        os.system("clear")
        render()
        paint()
        return False
    elif stage[position] == '$':
        pass
    if isData():
        keyboard_in = sys.stdin.read(3)
        if keyboard_in == '\x1b[C' and snake_head_direction != 1: # TURN RIGHT
            snake_head_direction = 0
        elif keyboard_in == '\x1b[D' and snake_head_direction != 0: # TURN LEFT
            snake_head_direction = 1
        elif keyboard_in == '\x1b[A' and snake_head_direction != 3: # TURN UP
            snake_head_direction = 2
        elif keyboard_in == '\x1b[B' and snake_head_direction != 2: # TURN DOWN
            snake_head_direction = 3
    return True

def update():
    global t1, t2, snake_head_direction, snake_head_position, snake_head_old_position
    os.system("clear")
    render()
    paint()
    if t2 - t1 >= 1:
        snake_head_old_position = list(snake_head_position)
        if snake_head_direction == 0:
            snake_head_position[0] += 1
        elif snake_head_direction == 1:
            snake_head_position[0] -= 1
        elif snake_head_direction == 2:
            snake_head_position[1] -= 1
        elif snake_head_direction == 3:
            snake_head_position[1] += 1
        #
        t1 = time.time()
    t2 = time.time()
    return process() 

if __name__ == "__main__":
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        while update():
            pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
