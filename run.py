

class Window:
    def __init__(self, width=40, height=20):
        self.os = __import__("os")

        self.height = height
        self.width = width
        self.os.system("mode con: cols={} lines={}".format(self.width, self.height))
        self.clear()

    def clear(self):
        self.pixels = [[" "]*self.width]*self.height

    def flip(self):
        self.os.system("cls")
        batch = ""
        for line in self.pixels:
            batch += "".join(line)
        print(batch)
def rgb()
window = Window(width=120, height=40)

while True:
    window.flip()



#print("░▒▓█")

