class Node:
    def __init__(self, x=0, y=0, color=(0,0,0)):
        self.x = x
        self.y = y
        self.color = color
    
    def nodeToList(self):
        return [self.x, self.y, self.color]