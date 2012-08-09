#encoding: utf-8
import sys 
import select 
import tty 
import termios

def isData():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)
try:
        tty.setcbreak(sys.stdin.fileno())

        i = 0
        while 1:

                if isData():
                        c = sys.stdin.read(3)
                        print c
                        if c == '\x1b[B':         # x1b is ESC
                                print c
                                break

finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
