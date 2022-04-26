class TuringMachine:
    def __init__(self) -> None:
        self.tape = {}
        self.head = 0

    def moveHead(self, dir: str) -> int:
        if (dir == "R"): self.head += 1
        elif (dir == "L"): self.head -= 1
        elif (dir != "S"): raise ValueError("Wrong head direction")
        return self.head
    
    def ifEq(self, value: str):
        try:
            return self.tape[self.head] == value
        except KeyError:
            return "" == value

    def setIfEq(self, checkValue: str, setValue: str, direction: str) -> None:
        if (self.ifEq(checkValue)):
            self.tape[self.head] = setValue
            self.moveHead(direction)
            return True
        return False

    def set(self, value: str) -> None:
        self.tape[self.head] = value

    def getTape(self):
        if self.tape == {}: return []
        j = 0
        tape = [None for _ in range(abs(max(self.tape)) + abs(min(self.tape)) + 1)]
        for i in range(min(self.tape), max(self.tape) + 1):
            try:
                tape[j] = self.tape[i]
            except KeyError:
                tape[j] = ""
            j += 1
        return tape
    
    def getValue(self):
        try:
            return self.tape[self.head]
        except KeyError:
            return ""