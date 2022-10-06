from semantic_cube import semantic_cube
from error_handler import raise_error


class stack_manager():
    def __init__(self) -> None:
        # Global addresses
        self.Gi = 0
        self.Gf = 2000
        # Local Addresses
        self.Li = 4000
        self.Lf = 5000
        # Temporal Addresses
        self.Ti = 6000
        self.Tf = 7000
        self.Tb = 8000
        # Constant Addresses
        self.Ci = 9000
        self.Cf = 10000
        # Pointer Address
        self.Tp = 11000

        self.temp_counter = 0
        self.instruction_counter = 0
        self.sc_instance = semantic_cube()
        self.operator_stack = []
        self.operand_stack = []
        self.type_stack = []
        self.jump_stack = []
        self.quadruples = []

    def push_operand(self, operand: str, type: str) -> None:
        self.operand_stack.append(operand)
        self.type_stack.append(type)

    def push_operator(self, operator: str) -> None:
        self.operator_stack.append(operator)

    def check_top_operator(self) -> str:
        return self.operator_stack[-1]

    def pop_operand(self) -> tuple:
        return self.operand_stack.pop(), self.type_stack.pop()

    def pop_operator(self) -> str:
        return self.operator_stack.pop()

    def push_jump(self, instruction_pointer: int) -> None:
        self.jump_stack.append(instruction_pointer)

    def pop_jump(self) -> int:
        return self.jump_stack.pop()

    def get_current_istruction_pointer(self) -> int:
        return self.instruction_counter

    def assign_quadruple_jump(self, quad: int, jump: int) -> None:
        self.quadruples[quad][3] = jump

    def dump_stacks(self) -> None:
        print("Operators stack:", self.operator_stack)
        print("Operands stack:", self.operand_stack)
        print("Types stack:", self.type_stack)
        print("Jumps stack:", self.jump_stack)
        print("Quadruples:")
        s = [["-" if e == None else str(e) for e in row]
             for row in self.quadruples]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        quads = dict(zip([str(i) + " ==> " for i in range(len(s))], s))
        table = [ip + fmt.format(*row) for ip, row in quads.items()]
        print('\n'.join(table))

    def finish_instructions(self) -> None:
        self.quadruples.append(["END", None, None, None])

    def produce_quadruple(self, level: str) -> None:
        if level == "while_goto":
            ops = ["while_goto"]
        elif level == "gotof":
            ops = ["gotof"]
        elif level == "goto":
            ops = ["goto"]
        elif level == "return":
            ops = ["return"]
        elif level == "read":
            ops = ["read"]
        elif level == "write":
            ops = ["write"]
        elif level == "simple_assignment":
            ops = ["="]
        elif level == "hyperexp":
            ops = ["and", "or"]
        elif level == "superexp":
            ops = [">", "<", "==", "<>"]
        elif level == "exp":
            ops = ["+", "-"]
        elif level == "term":
            ops = ["*", "/"]
        if self.check_top_operator() in ops:
            operator = self.pop_operator()
            if level == "while_goto":
                return_jump = self.pop_jump()
                self.quadruples.append([operator, return_jump, None, None])
            elif level == "goto":
                self.quadruples.append([operator, None, None, None])
            elif level == "gotof":
                operand1 = self.pop_operand()
                if operand1[1] == "bool":
                    self.quadruples.append([operator, operand1[0], None, None])
                else:
                    raise_error(None, "type_mismatch", args=("cond", operand1))
            elif level == "return":
                operand1 = self.pop_operand()
                self.quadruples.append([operator, None, None, operand1[0]])
            elif level == "simple_assignment":
                operand1 = self.pop_operand()
                operand2 = self.pop_operand()
                self.quadruples.append(
                    [operator, operand1[0], None, operand2[0]])
            elif level == "read":
                operand1 = self.pop_operand()
                self.quadruples.append([operator, None, None, operand1[0]])
            elif level == "write":
                operand1 = self.pop_operand()
                self.quadruples.append([operator, None, None, operand1[0]])
            else:
                operand1 = self.pop_operand()
                operand2 = self.pop_operand()
                res_type = self.sc_instance.type_match(
                    operator, operand1[1], operand2[1])
                if res_type != "ERR":
                    self.quadruples.append(
                        [operator, operand1[0], operand2[0], "t" + str(self.temp_counter)])
                    self.push_operand("t" + str(self.temp_counter), res_type)
                    self.temp_counter += 1
                else:
                    raise_error(None, "type_mismatch", args=(
                        operator, operand1, operand2))
            self.instruction_counter += 1
