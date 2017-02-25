class Display(object):

    def __init__(self):

        self.width = 240
        self.height = 320

        self.fb = open("/dev/fb0")
        self.frame = [[(0, 0, 0) for x in range(0, self.width)] for y in range(0, self.height)]

    def fill(self, r, g, b):
        self.frame = [[(r, g, b) for x in range(0, self.width)] for y in range(0, self.height)]

    def flip(self):
        self.fb.seek(0)
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.fb.write("%c%c%c\n" % self.frame[y][x])

if __name__ == "__main__":
    import time

    display = Display()
    display.fill(255, 0, 255)
    display.flip()

    time.sleep(10)