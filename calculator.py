# Smart calculator implementation with variable memory.
from typing import Dict
from operator import pow, truediv, mul, add, sub
import re

# support for recognition of variables and valid numerical input
valid_variable = re.compile('[a-zA-z]+$')
#valid_number = re.compile('[0-9]+')

# storage of calculator variables
var_dict = dict() # type: Dict[str,int]

def smart_calculator():
    while True:
        expression = input()
        if expression.startswith('/'):  # identify if a command was issued
            command(expression)

        # do nothing, continue
        elif expression == '':
            pass

        else:
            try:
                result = analyze_expression(expression)
                if result is not None and '=' not in expression:
                    print(result)
            except Exception as e:
                print(e.args[0])

    # end main program loop

def analyze_expression(expression, first=True):
    # first, determine if '=' is even in play at all:
    if '=' not in expression:
        return solve_expr(expression)
    else:
        # get the variable name from the left side
        left_side = expression[:expression.index('=')]
        left_side = left_side.strip() # remove any remaining leading and trailing whitespace

        # ensure the left side is actually valid
        global valid_variable
        if not valid_variable.match(left_side):  # if the variable is actually valid (i.e. latin characters only with nothing else at end)
            if first:
                raise KeyError('Invalid identifier')  # at this point the function will be abandoned ('Invalid Identifier')
            else:
                raise ValueError('Invalid assignment')

        # evaluate what is on the right side.  Now, we know the left hand side variable is valid
        right_side = expression[expression.index('=')+1:]
        right_side_result = analyze_expression(right_side, False)

        # assign to the dictionary the variable name and the result produced from right_side
        global var_dict
        var_dict[left_side] = right_side_result

        # return the ultimate result
        return var_dict[left_side]


def solve_expr(expression):

    pattern_split = r'(\++|(?!^)\-+(?!\d+)|\(|\)|\*|\/)|\s+'    # split on +, -, *, \, (, ), and whitespace.  Allow one or more + or - expressions.
    operator_pattern = re.compile('[()*/]|\++|\-+|\*\*$')   # includes exponentiation as potential future operator
    # items = list(filter(None, re.split('(\++|\-+)|\s+', expression)))
    items = list(filter(None, re.split(pattern_split, expression))) # the infix stack

    # convert the expression to raw postfix (with variables resolved) result using stack
    stack = []
    postfix = []

    for item in items:
        item = resolve_item(item, operator_pattern) # item will now either be a digit or an operator
        if isinstance(item, int): #if it was resolved as an integer
            postfix.append(item)
        elif item == '(':
            stack.append(item)
        elif item == ')':
            while len(stack) >= 0: # pop operators from stack until '(' is popped.  note if '(' is not popped, then we're in trouble
                if len(stack) == 0: # if we have not broken yet, there is an unbalanced parenthesis problem.
                    raise ValueError('Invalid expression')
                if len(stack) > 0 and stack[-1] == '(':
                    stack.pop()
                    break
                else:
                    postfix.append(stack.pop())
        else:  # it's an operator! (+, -, /, *)
            if item in '*/':
                while len(stack) > 0 and stack[-1] in '*/':
                    postfix.append(stack.pop())
                stack.append(item)
            elif item in '+-':
                while len(stack) > 0 and stack[-1] in '*/+-':
                    postfix.append(stack.pop())
                stack.append(item)

    # finish up - pop all operators from the stack and append to the postfix
    while stack:
        postfix.append(stack.pop())

    operators = {
        '+' : add,
        '-' : sub,
        '*' : mul,
        '/' : truediv,
        '**': pow   # not officially implemented
    }

    # compute result
    for item in postfix:
        if isinstance(item,str) and item in '**/+-':
            try:
                second_item = stack.pop()
                first_item = stack.pop()
            except:
                raise ValueError('Invalid expression')
            int_calc = operators[item](first_item,second_item)
            stack.append(int_calc)
        else:
            stack.append(item)

    if len(stack) > 1:
        raise ValueError('Invalid expression')

    return int(stack[0])

# Used to return the value of the given item; either the same value int he case of integer or the variable value
def resolve_item(item, operator_pattern):
    try:
        return int(item)
    except ValueError:  # if the item is not an int

        # see if the item is a valid operator, if so, return it
        if operator_pattern.match(item):
            if item.startswith('+'):
                item = '+'
            if item.startswith('-'):
                if item.count('-') % 2 == 1:
                    item = '-'
                else:
                    item = '+'
            return item

        # not an operator, see if the item is even a valid identifier
        global valid_variable
        if not valid_variable.match(item):
            raise KeyError('Invalid identifier')
        try:
            global var_dict
            return_val = var_dict[item]
        except LookupError as e:
            raise Exception('Unknown variable') from e
        else:  # successful variable resolution
            return return_val


def command(expression):
    if expression == '/help':
        print('This program is a smart calculator.  You may calculate expressions and assign values to variables.')
        print('A variable consists of latin characters only, e.g. A-Z and a-z.')
        print('If you try to create an invalid variable using an invalid name, the program will inform you.')
        print('Valid examples include:')
        print('   1 + 2 + 3')
        print('   a = b = 5')
        print('   a + b - 7')
        print('   5 * (a + 7)')
        print('Once you type the expression, hit ENTER to calculate.')
        print('You may also look up the value of a valid identifier by typing its name and hitting ENTER.')
        print('Examples include:')
        print('a = 5')
        print('a')
        print('# the program will display the value of \'a\' which in this case is 5.')
        print('Type /exit to leave the program.')
        print('Happy calculating!\n')
    elif expression == '/exit':
        print('Bye!')
        exit()
    else:
        print('Unknown command')

# Boilerplate for program entry
if __name__ == '__main__':
    smart_calculator()
