from operator import mod
from statistics import mode
from tracemalloc import start
from node import Node
from turing import TuringMachine
import arcade

import tkinter
from tkinter import filedialog
tkinter.Tk().withdraw()


NODE_SIZE = 20
TAPE_SIZE = 30
ALLOWED_INPUT = {
    97: 'A', 98: 'B', 99: 'C', 100: 'D', 101: 'E', 102: 'F', 103: 'G', 104: 'H', 105: 'I', 106: 'J', 107: 'K', 108: 'L', 109: 'M', 110: 'N', 111: 'O', 112: 'P', 113: 'Q', 114: 'R', 115: 'S', 116: 'T', 117: 'U', 118: 'V', 119: 'W', 120: 'X', 121: 'Y', 122: 'Z',
    32: ' ', 46: '.', 48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8'
}

#the second one stores coordinates to visualise the graph
nodes = {}
Nodes = []

class MainWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True, update_rate=1/144)
        
        self.width = width
        self.height = height
        self.time = 0 
        self.mouse_x = None
        self.mouse_y = None
        self.selected = None
        self.typingWeight = False
        self.start = -1
        self.finish = -1
        self.weight = ["", "", ""]
        self.weightIndex = -1
        self.dragged = False
        self.shortPath = None
        self.current_node = None
        self.next_node = None
        self.higlighted_text = 0
        self.copybuffer = []

        self.turingMachine = TuringMachine()
        self.tapeCount = self.width // TAPE_SIZE
        self.headmin = -self.tapeCount // 2
        self.headmax = self.tapeCount // 2


        #nodes that we need to assign weight to
        self.ith_node = None
        self.jth_node = None
        
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()
        
        if (self.typingWeight):
            text = f'State transition: {"_" if len(self.weight[0]) == 0 and self.weightIndex == 0 else self.weight[0]}|{"_" if len(self.weight[1]) == 0 and self.weightIndex == 1 else self.weight[1]}|{"_" if len(self.weight[2]) == 0 and self.weightIndex == 2 else self.weight[2]}'
            arcade.draw_text(text, 0, self.height-NODE_SIZE, arcade.color.BLUE, NODE_SIZE, anchor_x="left", anchor_y="top")

        # arcade.draw_text(f'Start pos: {self.start}, end pos: {self.finish}', 0, self.height, arcade.color.BLUE, NODE_SIZE, anchor_x="left", anchor_y="top")

        #draw lines  
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if (j in nodes[i]):
                    node = Nodes[i]
                    c = Nodes[j]
                    arcade.draw_line(node.x, node.y, c.x, c.y, arcade.color.WHEAT, 2)
                    # arcade.draw_arc_outline(abs(node.x+c.x)//2, abs(node.y+c.y)//2, abs(node.x-c.x), 23, arcade.color.WHEAT, 90, 180, 3, 20) #abs(node.x-c.x), abs(node.y-c.y), arcade.color.WHEAT, 30, 40, 2)

                    #draw node text
                    for node_data in range(len(nodes[i][j])):
                        data = nodes[i][j][node_data]
                        text = f'{data[0]}|{data[1]}|{data[2]}'
                        del_y = NODE_SIZE if i > j else -NODE_SIZE
                        arcade.draw_text(text, abs(node.x+c.x)//2, abs(node.y+c.y)//2 + del_y + node_data * 4 + NODE_SIZE * node_data, arcade.color.BLUE, NODE_SIZE, anchor_x="center", anchor_y="center")

        #draw green lines
        if self.shortPath != None:
            for i in range(1, len(self.shortPath)):
                node = Nodes[self.shortPath[i]] 
                c = Nodes[self.shortPath[i-1]]  
                arcade.draw_line(node.x, node.y, c.x, c.y, arcade.color.GREEN, 2)

        #draw nodes
        for i in range(len(Nodes)):
            node = Nodes[i]
            if (self.start == i): 
                arcade.draw_triangle_filled(node.x, node.y, node.x - 30, node.y + 30, node.x - 30, node.y - 30, arcade.color.ALMOND)   
            
            color = node.color if i != self.next_node else arcade.color.RED
            arcade.draw_circle_filled(node.x, node.y, NODE_SIZE, color)
            arcade.draw_text(f'q{i}', node.x, node.y, arcade.color.BLUE, NODE_SIZE, anchor_x="center", anchor_y="center")

        tape = self.turingMachine.tape
        head_index = self.turingMachine.head
        # draw tape
        for i in range(-self.tapeCount//2, self.tapeCount//2):
            block_x_coord = self.width // 2 + TAPE_SIZE // 2 + TAPE_SIZE * i
            arcade.draw_rectangle_outline(block_x_coord, TAPE_SIZE // 2, TAPE_SIZE, TAPE_SIZE, arcade.color.AMARANTH)
        
        # draw tape data
        for i in range(self.headmin, self.headmax):
            text = tape[i] if i in tape else "□"
            text_x_coord = self.width // 2 + TAPE_SIZE // 2 + TAPE_SIZE * i - head_index * TAPE_SIZE
            arcade.draw_text(text, text_x_coord, TAPE_SIZE // 2, arcade.color.BLUE, TAPE_SIZE * 0.7, anchor_x="center", anchor_y="center")

        #draw tape head
        arcade.draw_rectangle_outline(self.width // 2 + TAPE_SIZE // 2, TAPE_SIZE // 2, TAPE_SIZE, TAPE_SIZE, arcade.color.BALL_BLUE, 4)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_update(self, dt):
        self.time += dt           

    def on_mouse_press(self, x, y, button, modifiers):
        for i in range(len(Nodes)):
            #if clicked on node
            if ((x > Nodes[i].x - NODE_SIZE and x < Nodes[i].x + NODE_SIZE) and (y > Nodes[i].y - NODE_SIZE and y < Nodes[i].y + NODE_SIZE)):
                if (self.selected == None):
                    #set selected node to i-th node
                    self.selected = i
                    Nodes[i].color = arcade.color.CAMEL
                else:
                    #if clicked on different node while selecting  
                    Nodes[self.selected].color = arcade.color.WHEAT

                    #get weight
                    self.typingWeight = True
                    self.weightIndex = 0

                    self.ith_node = i
                    self.jth_node = self.selected
                break
        else:
            if (self.selected):
                Nodes[self.selected].color = arcade.color.WHEAT
                self.selected = None


        for i in range(len(Nodes)):
            if ((x > Nodes[i].x - NODE_SIZE and x < Nodes[i].x + NODE_SIZE) and (y > Nodes[i].y - NODE_SIZE and y < Nodes[i].y + NODE_SIZE)) or (self.selected != None):
                break
        else:
            #create new node 
            Nodes.append(Node(self.mouse_x, self.mouse_y, arcade.color.WHEAT))
            node_id = len(Nodes)-1
            nodes[node_id] = {}
    
    def on_mouse_drag(self, x, y, *modifiers):
        self.dragged = True
        if self.selected != None:
            Nodes[self.selected].x = x
            Nodes[self.selected].y = y
    
    def on_mouse_release(self, x, y, *modifiers):
        if self.dragged and self.selected != None:
            Nodes[self.selected].color = arcade.color.WHEAT
            self.selected = None
            self.dragged = False
    
    def _reset(self):
        self.selected = None
        self.typingWeight = False
        self.weight = ["", "", ""]
        self.weightIndex = -1
        self.dragged = False
        self.next_node = None
        self.higlighted_text = 0
        self.copybuffer = []
        self.turingMachine = TuringMachine()
        self.tapeCount = self.width // TAPE_SIZE

    def _openfile(self):
        global nodes, Nodes
        folder_path = filedialog.askopenfile(filetypes=[["Turing Machine", "*.t"]]).name
        if (folder_path):
            savefile = open(folder_path, "r")
            data = savefile.readlines()
            nodes = eval(data[0])
            tempnodes = eval(data[1])
            Nodes = [Node(*i) for i in tempnodes]
            self.start = eval(data[2])
            self.current_node = self.start

            # reset all local data
            self._reset()

            print(f'Opened {folder_path}')
            savefile.close()

    def on_key_press(self, key, *modifiers):  
        # set start node
        if (not self.typingWeight and arcade.key.MOD_CTRL not in modifiers):
            if (key == arcade.key.S):
                #start node selection 
                if (self.selected != None):
                    self.start = self.selected
                    self.current_node = self.start
                else:
                    print('No node selected')
            if (key == arcade.key.F):
                #end node
                if (self.selected != None):
                    self.finish = self.selected
                else:
                    print('No node selected')

        if (key in ALLOWED_INPUT and self.typingWeight and self.weightIndex != 2):
            self.weight[self.weightIndex] += ALLOWED_INPUT[key]

        if (key == arcade.key.NUM_MULTIPLY): self.weight[self.weightIndex] += "_"
        
        if ((key == arcade.key.R or key == arcade.key.L or key == arcade.key.S) and self.weightIndex == 2):
            sym = ""
            if (key == arcade.key.R): sym = "R"
            if (key == arcade.key.L): sym = "L"
            if (key == arcade.key.S): sym = "S"
            self.weight[self.weightIndex] = sym

        if (key == arcade.key.TAB and self.typingWeight):
            self.weightIndex += 1
            if (self.weightIndex == 3): self.weightIndex = 0
        
        if (key == arcade.key.BACKSPACE):
            self.weight[self.weightIndex] = self.weight[self.weightIndex][:-1]


        if (key == arcade.key.ENTER):
            if (self.ith_node != None and self.jth_node != None):
                data_container = [self.weight[0], self.weight[1], self.weight[2]]
                try: nodes[self.jth_node][self.ith_node].append(data_container)
                except KeyError: nodes[self.jth_node][self.ith_node] = [data_container]
                    
                self.weight = ["", "", ""]
                self.weightIndex = -1
                self.typingWeight = False
                self.selected = None
                self.ith_node = None
                self.jth_node = None 
        
        if (key == arcade.key.DELETE):
            if self.selected != None:
                del Nodes[self.selected]
                del nodes[self.selected]

        if (key == arcade.key.ESCAPE):
            self.weight = ["", "", ""]
            self.weightIndex = -1
            self.typingWeight = False
            self.selected = None

        if (key == arcade.key.I):
            a = input()
            for i in range(len(a)):
                self.turingMachine.tape[i] = a[i]

        #debug
        if (key == arcade.key.UP):
            print(nodes)

        # reset turing machine
        if (key == arcade.key.R and arcade.key.MOD_CTRL in modifiers):
            self._reset()
            self.current_node = self.start

        # copy node with its self to self transitions
        if (key == arcade.key.C and arcade.key.MOD_CTRL in modifiers):
            n = nodes[self.selected]
            thisnode = self.selected
            print(n, thisnode)
            for i in n:
                if (i == thisnode):
                    self.copybuffer = n[i]
                    print(f'Copied {self.copybuffer}')

        # paste
        if (key == arcade.key.V and arcade.key.MOD_CTRL in modifiers):
            nodedata = '{'+str(len(nodes))+':'+str(self.copybuffer)+'}'
            nodes[len(nodes)] = eval(nodedata)
            Nodes.append(Node(self.mouse_x, self.mouse_y, arcade.color.WHEAT))

        # save file
        if (key == arcade.key.S and arcade.key.MOD_CTRL in modifiers):
            folder_path = filedialog.asksaveasfile(filetypes=[["Turing Machine", "*.t"]]).name
            if (folder_path):
                savefile = open(folder_path, "w")
                writenodes = [node.nodeToList() for node in Nodes]
                savefile.write(f'{nodes}\n{writenodes}\n{self.start}')
                savefile.close()

        # open file
        if (key == arcade.key.O and arcade.key.MOD_CTRL in modifiers):
            self._openfile()

        # step logic
        if (key == arcade.key.EQUAL):
            if (self.start != -1):
                # get data from current node
                data = nodes[self.current_node]
                # get current tape value
                tape_value = self.turingMachine.getValue()

                # go through all possible paths
                for i in list(data):
                    for j in range(len(data[i])):
                        if (tape_value == data[i][j][0]):
                            self.turingMachine.set(data[i][j][1])
                            self.turingMachine.moveHead(data[i][j][2])
                            self.headmin = min(self.turingMachine.head, self.headmin)
                            self.headmax = max(self.turingMachine.head, self.headmax)
                            self.next_node = i
                            self.current_node = i
                            break
                else: print("Failed to find any")
            else: print("No start node")
            
            # if at the end node
            if (self.current_node == self.finish):
                Nodes[self.current_node].color = arcade.color.GREEN