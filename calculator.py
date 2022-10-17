import sys


class CalculatorError(Exception):
    """Base class for Calculator exceptions"""

    pass


class EmptyInputError(CalculatorError):
    """Raised when on empty input"""

    def __init__(self):
        self.message = "Empty input was provided."
        super().__init__(self.message)


class ParenthesesError(CalculatorError):
    """
    Parentheses are used incorrectly
    """

    def __init__(self):
        self.message = "Not matching parentheses were found in math expression."
        super().__init__(self.message)


class UnexpectedInput(CalculatorError):
    """
    Raised when get invalid symbol
    """
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.message = f"Got invalid symbol: '{self.symbol}'"
        super().__init__(self.message)


class NothingToDoError(CalculatorError):
    """
    Raised if there are no operators in expression
    """
    def __init__(self):
        self.message = f"There are no any arithmetic operators like '-' or '*'"
        super().__init__(self.message)


class CustomCalc:
    def __init__(self):
        self.operators_priors = {
            '(': 1,
            ')': None,
            '+': 2,
            '-': 2,
            '*': 3,
            '/': 3,
            ':': 3,
            '~': 4,
        }

    def get_number(self, math_str: str, start: int):
        """
        Collects number (int or fractional with decimal separators) from string expression
        starting at specified position
        """
        num_str = ""
        dots = 0
        for s in math_str[start:]:
            if s.isdigit():
                num_str += s
            elif s == '.' and dots < 2:
                dots += 1
                num_str += s
            else:
                return num_str
        return num_str

    def cast_number(self, number: str):
        """
        Casts a number to optimal format (int or float)
        """

        if '.' in number:
            return float(number)
        else:
            return int(number)


    def split_to_tokens(self, math_str: str):
        """
        Splits str mathematical expression to list of tokens
        """
        math_str = math_str.replace(' ', '')
        cur_pos = 0
        token_list = []
        operators = 0
        while cur_pos < len(math_str):
            if math_str[cur_pos].isdigit():
                num = self.get_number(math_str, cur_pos)
                token_list.append(num)
                cur_pos += len(num)
            elif math_str[cur_pos] in self.operators_priors.keys():
                if math_str[cur_pos] == '-' \
                        and (cur_pos == 0 or (cur_pos > 0 and math_str[cur_pos - 1] == '(')):
                    token_list.append('~')
                else:
                    token_list.append(math_str[cur_pos])
                    if not math_str[cur_pos] in ('(', ')'):
                        operators += 1
                cur_pos += 1
            else:
                raise UnexpectedInput(math_str[cur_pos])
        if operators == 0:
            raise NothingToDoError
        return token_list

    def check_parentheses(self, token_list: list):
        """
        Validates infix math expression in terms of parentheses using.
        """
        opened_parentheses = int(token_list[0] == '(')
        closed_parentheses = int(token_list[0] == ')')
        opened_parentheses += int(token_list[1] == '(')
        closed_parentheses += int(token_list[1] == ')')
        for token in token_list[2:]:
            if opened_parentheses < closed_parentheses:
                raise ParenthesesError()
            opened_parentheses += int(token == '(')
            closed_parentheses += int(token == ')')
        if opened_parentheses != closed_parentheses:
            raise ParenthesesError()

    def infix_to_postfix(self, tokens: list):
        """
        Transforms expression to postfix notation.
        """
        stack = []
        output_list = []

        for token in tokens:
            if token[0].isdigit():
                output_list.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                top = stack.pop()
                while top != '(':
                    output_list.append(top)
                    top = stack.pop()
            else:
                while len(stack) > 0 \
                        and self.operators_priors[stack[-1]] >= self.operators_priors[token]:
                    output_list.append(stack.pop())
                stack.append(token)

        while len(stack) > 0:
            output_list.append(stack.pop())

        return output_list

    def math_operation(self, arg1, arg2, operator: str):
        """
        Provides arithmetical operations
        """
        if operator == '+':
            return arg1 + arg2
        elif operator == '-' or operator == '~':
            return arg1 - arg2
        elif operator == ':' or operator == '/':
            try:
                res = arg1 / arg2
            except ZeroDivisionError as ex:
                sys.exit("You cannot divide by zero, check if math expression is correct")
            return res
        else:
            return arg1 * arg2

    def postfix_calc(self, postfix_list: list):
        """
        Evaluates expression written in postfix notation
        """
        stack = []

        for token in postfix_list:
            if token[0].isdigit():
                stack.append(self.cast_number(token))
            else:
                if token == '~':
                    arg2 = stack.pop()
                    arg1 = 0
                    res = self.math_operation(arg1, arg2, token)
                else:
                    arg2 = stack.pop()
                    arg1 = stack.pop()
                    res = self.math_operation(arg1, arg2, token)
                stack.append(res)
        return stack.pop()

    def eval_math_expr(self, math_expr: str):
        """
        Executes the whole calculation process
        """
        tokens = self.split_to_tokens(math_expr)
        self.check_parentheses(tokens)
        postfix_expr = self.infix_to_postfix(tokens)
        res = self.postfix_calc(postfix_expr)
        print('=', res)


cal = CustomCalc()
print("Running calculator. Press ctrl + C or input 'q' to quit")
while True:
    try:
        s = input("Enter your expression: ")
        if s != 'q':
            try:
                cal.eval_math_expr(s)
            except (EmptyInputError, ParenthesesError, UnexpectedInput, NothingToDoError) as ex:
                print(f"Error occurred: {ex}\nLet's correct your expression and try again\n")
            except Exception as un_ex:
                print("Unexpected error occurred :( \nLet's try another input.")
        else:
            print("Have a nice day!\n")
            break
    except KeyboardInterrupt as ex:
        print("\nHave a nice day!\n")
        break
