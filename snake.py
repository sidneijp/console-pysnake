# encoding: utf-8
import os
import time
import sys
import termios
import tty
import select

def getInput():
    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
        return sys.stdin.read(3)
    return None

class Field(object):
    def __init__(self, fname):
        self.data = self._loadField(fname)
        self.heigth = self._getHeigth()
        self._formatField()

    def _loadField(self, fname):
        fname = 'stages/%s/field' % (fname,)
        f = file(fname, 'r')
        stage = f.readlines()
        f.close()
        return stage

    def _getHeigth(self):
        heigth = 0
        for line in self.data:
            length = len(line)
            if length > heigth:
                heigth = length
        return heigth

    def _formatField(self):
        stage = '/' + ((self.heigth-1) * '-') + '\\\n'
        for i, line in enumerate(self.data):
            spaces = (self.heigth - len(line))
            line = line.rstrip('\n')
            stage += '|' + line + (spaces * ' ') + '|\n'
        stage += '\\' + ((self.heigth-1) * '-') + '/\n'
        self.data = list(stage)

class Apple(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = '$'

class Stage(object):
    def __init__(self, stage, snake):
        self.field = Field(stage)
        self.apples = self._loadApples(stage)
        self.snake = snake
        self.screen = list(self.field.data)
        self.t1 = time.time()
        self.t2 = self.t1

    def _loadApples(self, fname):
        fname = 'stages/%s/apples' % (fname,)
        f = file(fname, 'r')
        apples = []
        for line in f.readlines():
            line = line.split(',')
            for i, value in enumerate(line):
                line[i] = int(value)
            apple = Apple(*line)
            print apple.x, apple.y
            apples.append(apple)
        f.close()
        return apples

    def _screenPosition(self, element):
        return element.x + element.y * (self.field.heigth+2)

    def _outOfField(self, position):
        if self.screen[position] == '|' or self.screen[position] == '-':
            return True
        return False

    def render(self):
        self.screen = list(self.field.data)
        if len(self.apples) > 0 and self.apples[0] is not None:
            apple_position = self._screenPosition(self.apples[0])
            self.screen[apple_position] = self.apples[0].char
        for bodyPart in self.snake.body:
            bodyPart_position = self._screenPosition(bodyPart)
            self.screen[bodyPart_position] = bodyPart.char
        head_position = self._screenPosition(self.snake.head)
        self.screen[head_position] = self.snake.head.char

    def paint(self):
        for unit in self.screen:
            print unit,

    def graphicsUpdate(self):
        os.system("clear")
        self.render()
        self.paint()

    def update(self):
        self.graphicsUpdate()
        if self.t2 - self.t1 >= 0.25:
            self.snake.moveForward()
            self.t1 = time.time()
        self.t2 = time.time()
        return self.process()

    def process(self):
        position = self._screenPosition(self.snake.head)
        if self.screen[position] == '#' or self.screen[position] == 'o' or self._outOfField(position):
            self.snake.head.char = 'X'
            self.graphicsUpdate()
            return False
        elif self.screen[position] == '$':
            self.apples.pop(0)
            self.snake.addBodyPart()
            if len(self.apples) == 0:
                self.graphicsUpdate()
                return False
        data_in = getInput()
        if data_in == '\x1b[C': # TURN RIGHT
            self.snake.turnRight()
        elif data_in == '\x1b[D': # TURN LEFT
            self.snake.turnLeft()
        elif data_in == '\x1b[A': # TURN UP
            self.snake.turnUp()
        elif data_in == '\x1b[B': # TURN DOWN
            self.snake.turnDown()
        return True

class Head(object):
    CHARS = {2: '>', 4: 'A', 6: '<', 8: 'V', 0: 'X'}

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.old_x = None
        self.old_y = None
        self.direction = direction
        self.char = Head.CHARS[self.direction]

    def moveForward(self):
        self.old_x = self.x
        self.old_y = self.y
        if self.direction == 2:
            self.x += 1
        elif self.direction == 4:
            self.y -= 1
        elif self.direction == 6:
            self.x -= 1
        elif self.direction == 8:
            self.y += 1

class BodyPart(object):
    def __init__(self, parent):
        self.x = parent.old_x
        self.y = parent.old_y
        self.old_x = None
        self.old_y = None
        self.parent = parent
        self.char = 'o'

    def moveForward(self):
        self.old_x = self.x
        self.old_y = self.y
        self.x = self.parent.old_x
        self.y = self.parent.old_y

class Snake(object):
    def __init__(self, x, y, direction):
        self.head = Head(x, y, direction)
        self.body = []

    def addBodyPart(self):
        tail = self._getTail()
        bodyPart = BodyPart(tail)
        self.body.append(bodyPart)

    def _getTail(self):
        if len(self.body) == 0:
            return self.head
        return self.body[-1]

    def turnRight(self):
        if self.head.old_x == self.head.x + 1:
            return
        self.head.direction = 2
        self.head.char = Head.CHARS[self.head.direction]

    def turnUp(self):
        if self.head.old_y == self.head.y - 1:
            return
        self.head.direction = 4
        self.head.char = Head.CHARS[self.head.direction]

    def turnLeft(self):
        if self.head.old_x == self.head.x - 1:
            return
        self.head.direction = 6
        self.head.char = Head.CHARS[self.head.direction]

    def turnDown(self):
        if self.head.old_y == self.head.y + 1:
            return
        self.head.direction = 8
        self.head.char = Head.CHARS[self.head.direction]

    def moveForward(self):
        self.head.moveForward()
        for bodyPart in self.body:
            bodyPart.moveForward()

if __name__ == "__main__":
    snake = Snake(2, 2, 2)

    stage = Stage(sys.argv[1], snake)

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while stage.update():
            pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

