import getopt
import json
import sys

coding = 'utf-8'


# Function that checks command line parameters
def check_args(argv):
    try:
        opts, args = getopt.getopt(argv, "i:o", ["input="])
    except getopt.GetoptError:
        print('2-14-Python-ІВ-81-Зубець-compiler.py -i <input_file>')
        input()
        exit(1)

    for opt, arg in opts:
        if opt in ('-i', '--input'):
            return arg

    return '2-14-Python-ІВ-81-Зубець-program.txt'


# LEXER

def lexer(file_name):
    file = open(str(file_name), 'rb')
    characters = file.read().rstrip()
    tokens = tokenizer(string_scanner(characters))
    file.close()
    return tokens


# Function that splits input string into lexems
def string_scanner(string: bytes, pos=0):
    def next_item(start_pos):
        delimiters = [' ', '\n', ':', ';', '(', ')', '-', '+', '~']
        current_pos = start_pos
        line_counter = 1
        while current_pos < str_len:
            if chr(string[current_pos - 1]) == '\n':
                line_counter += 1
            if chr(string[start_pos]) in delimiters:
                yield string[start_pos:start_pos + 1], {'symbol': start_pos + 1, 'line': line_counter}
                start_pos += 1
                current_pos += 1
            else:
                if chr(string[current_pos]) in delimiters:
                    yield string[start_pos:current_pos], {'symbol': start_pos + 1, 'line': line_counter}
                    start_pos = current_pos
                else:
                    current_pos += 1
        if string[start_pos:current_pos] != b'':
            yield string[start_pos:current_pos], {'symbol': start_pos + 1, 'line': line_counter}

    string = string.replace(b'\r', b'').lstrip(b'\n')
    str_len = len(string)
    if str_len == pos:
        return

    items = [i for i in next_item(pos)]
    return items


# Function that tokenize lexems
def tokenizer(items: list):
    tokens = []
    templates = {
        b'def': 'function_declaration',
        b'(': 'open_parentheses',
        b')': 'closed_parentheses',
        b'return': 'return_keyword',
        b';': 'semicolon',
        b':': 'colon',
        b' ': 'white_space',
        b'\n': 'new_line',
        b'~': 'bitwise_complement',
        b'+': 'addition'
    }
    for i in items:
        if i[0] in templates.keys():
            tokens.append((i, templates[i[0]]))
        elif i[0].decode(coding).isnumeric():
            tokens.append((i, 'decimal_constant'))
        elif i[0].decode(coding).startswith('0o'):
            if i[0].decode(coding).replace('0o', '').isnumeric():
                if i[0].decode(coding).replace('0o', '').count('8') + i[0].decode(coding).replace('0o', '').count(
                        '9') == 0:
                    tokens.append((i, 'octal_constant'))
                else:
                    print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
                    input()
                    exit(1)
            else:
                print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
                input()
                exit(1)
        elif i[0].decode(coding).startswith(
                ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            if i[0].decode(coding).count('.') == 1:
                if i[0].decode(coding).replace('.', '').isnumeric() and not i[0].decode(coding).endswith('.'):
                    tokens.append((i, 'float_constant'))
                else:
                    print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
                    input()
                    exit(1)
            else:
                print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
                input()
                exit(1)
        else:
            start_sym = tuple([chr(k) for k in range(65, 91)] + [chr(k) for k in range(97, 123)])
            if i[0].decode(coding).startswith(start_sym):
                if i[0].decode(coding).isalnum():
                    tokens.append((i, 'identifier'))
                else:
                    print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
                    input()
                    exit(1)
            else:
                print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
                input()
                exit(1)
    return tokens


# PARSER

def parser(tokens: list):
    # Class that allows us to iterate through tokens list
    class TokensIter:
        def __init__(self, tokens: list, start_item=-1):
            self.tokens = tokens
            self.start_item = start_item
            self.current_item = start_item

        def has_next(self, tokens):
            try:
                item = tokens[self.current_item + 1]
                return True
            except:
                return False

        def next_item(self):
            if self.has_next(self.tokens):
                self.current_item += 1
                return self.tokens[self.current_item]
            else:
                return False

        def set_id(self, id):
            self.current_item = id

        def get_current_id(self):
            return self.current_item

    # Function that allows to skip white spaces that doesn't matter
    def skip_white_spaces(token, tokenIterator: TokensIter):
        if not token:
            return token
        while token[1] == 'white_space':
            if not token:
                return token
            token = tokenIterator.next_item()
        return token

    def skip_new_line(token, tokenIterator: TokensIter):
        if not token:
            return token
        while token[1] == 'new_line':
            if not token:
                return token
            token = tokenIterator.next_item()
        return token

    def skip_white_spaces_new_line(token, tokenIterator: TokensIter):
        if not token:
            return token
        while token[1] in ['white_space', 'new_line']:
            if not token:
                return token
            token = tokenIterator.next_item()
        return token

    # Recursive parser
    def parse_factor(tokens, index=0):
        factor = {}
        factor['kind'] = 'Factor'

        tokenIterator = TokensIter(tokens, index)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)
        id = tokenIterator.get_current_id()

        if token[1] == 'open_parentheses':
            factor['kind'] = 'Exp in brackets'
            exp, id = parse_exp(tokens, tokenIterator.get_current_id())
            factor['exp'] = exp
            tokenIterator.set_id(id - 1)
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)
            if token[1] != 'closed_parentheses':
                print("\nExpected closing parentheses\nLine: {}, Character: {}".format(token[0][1]['line'], token[0][1]['symbol']))
                exit()

            return factor, tokenIterator.get_current_id()
        elif token[1] == 'bitwise_complement':
            factor['kind'] = 'Expression'
            factor['type'] = 'Unary'
            factor['operator'] = token[0][0].decode(coding)
            new_factor, id = parse_factor(tokens, tokenIterator.get_current_id())
            factor['factor'] = new_factor
            return factor, id

        else:
            factor['kind'] = 'Constant'
            if not token:
                print("\nUnexpected EOF")
                input()
                exit(1)

            if token[1] not in ['float_constant', 'octal_constant', 'decimal_constant']:
                print("\nWrong return type\nLine: {}, Character: {}".format(token[0][1]['line'], token[0][1]['symbol']))
                input()
                exit(1)

            if token[1] == 'octal_constant':
                value = int(token[0][0].decode(coding), 8)
                if not -2147483648 < value < 2147483647:
                    print("\nValue out of int32_t range\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                         token[0][1]['symbol']))
                    input()
                    exit(1)
                type = 'int'
            elif token[1] == 'float_constant':
                value = int(float(token[0][0].decode(coding)))
                if not -2147483648 < value < 2147483647:
                    print("\nValue out of int32_t range\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                         token[0][1]['symbol']))
                    input()
                    exit(1)
                type = 'float'
            else:
                value = int(token[0][0].decode(coding))
                if not -2147483648 < value < 2147483647:
                    print("\nValue out of int32_t range\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                         token[0][1]['symbol']))
                    input()
                    exit(1)
                type = 'int'
            factor['type'] = type
            factor['value'] = value
            return factor, id

    def parse_exp(tokens, index=0):
        exp = {}
        exp['kind'] = 'Expression'
        exp['type'] = 'Non Binary'
        tokenIterator = TokensIter(tokens, index)

        factor, id = parse_factor(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        next_item = token[1]
        if next_item != 'addition':
            exp['factor'] = factor

        counter = 1
        while next_item == 'addition':
            print(next_item)
            exp['type'] = 'Binary'
            exp['operator'] = '+'
            exp['addition'+str(counter)] = factor
            counter += 1
            factor, id = parse_factor(tokens, tokenIterator.get_current_id())
            exp['addition'+str(counter)] = factor
            tokenIterator.set_id(id)
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)
            next_item = token[1]
            exp['add_count'] = counter

        return exp, tokenIterator.get_current_id()

    def parse_statement(tokens, index=0):
        statement = {}

        tokenIterator = TokensIter(tokens, index - 1)
        token = tokenIterator.next_item()

        if not token:
            print("Unexpected EOF")
            input()
            exit(1)

        if token[1] != 'white_space':
            print("\nError function body must be in white spaces\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                                  token[0][1][
                                                                                                      'symbol']))
            input()
            exit(1)

        token = skip_white_spaces(token, tokenIterator)
        if not token:
            print("\nUnexpected EOF")
            input()
            exit(1)

        if token[1] != 'return_keyword':
            print("\nStatement must start from return\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                       token[0][1]['symbol']))
            input()
            exit(1)

        exp, id = parse_exp(tokens, tokenIterator.get_current_id())

        statement['kind'] = 'Statement'
        statement['name'] = 'return'
        statement['exp'] = exp

        return statement, id

    def parse_function(tokens, index=0):
        func = {}
        tokenIterator = TokensIter(tokens, index - 1)
        token = tokenIterator.next_item()
        if not token:
            print("Blank file")
            input()
            exit(1)

        if token[1] != 'function_declaration':
            print("\nError func must be declared\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                  token[0][1]['symbol']))
            input()
            exit(1)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)
        if not token:
            print("\nUnexpected EOF")
            input()
            exit(1)

        if token[1] != 'identifier':
            print("\nError in function declaration, function must have name\nLine: {}, Character: {}".format(
                token[0][1]['line'], token[0][1]['symbol']))
            input()
            exit(1)
        name = token[0][0].decode(coding)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("\nUnexpected EOF")
            input()
            exit(1)

        if token[1] != 'open_parentheses':
            print(
                "\nError after func name must be open parentheses\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                                   token[0][1][
                                                                                                       'symbol']))
            input()
            exit(1)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("\nUnexpected EOF")
            input()
            exit(1)

        if token[1] != 'closed_parentheses':
            print("\nError after open parentheses must be closed parentheses\nLine: {}, Character: {}".format(
                token[0][1]['line'], token[0][1]['symbol']))
            input()
            exit(1)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("\nUnexpected EOF")
            input()
            exit(1)

        if token[1] != 'colon':
            print("\nError after closed parentheses must be colon\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                                   token[0][1][
                                                                                                       'symbol']))
            input()
            exit(1)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("\nUnexpected EOF")
            input()
            exit(1)

        if token[1] != 'new_line':
            print("\nMust be new line after func declaration\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                              token[0][1]['symbol']))
            input()
            exit(1)

        token = skip_new_line(token, tokenIterator)
        statement, id = parse_statement(tokens, tokenIterator.get_current_id())
        func['kind'] = 'Function Declaration'
        func['name'] = name
        func['statement'] = statement
        return func, id

    def parse_func_call(tokens, index=0):
        func_call = {}

        tokenIterator = TokensIter(tokens, index)
        token = tokenIterator.next_item()
        token = skip_white_spaces_new_line(token, tokenIterator)
        if token[1] != 'identifier':
            print("\nIdentifier expected \nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                           token[0][1]['symbol']))
            input()
            exit(1)

        name = token[0][0]
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if token[1] != 'open_parentheses':
            print("\nExpected open parentheses at function call after identifier\nLine: {}, Character: {}".format(
                token[0][1]['line'],
                token[0][1]['symbol']))
            exit(1)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if token[1] != 'closed_parentheses':
            print(
                "\nExpected closing parentheses at function call after open parentheses\nLine: {}, Character: {}".format(
                    token[0][1]['line'],
                    token[0][1]['symbol']))
            exit(1)

        func_call['type'] = 'Function Call'
        func_call['name'] = name.decode(coding)

        return func_call, tokenIterator.get_current_id()

    def parse_program(tokens, index=0):
        program = {}
        func, id = parse_function(tokens)
        program['kind'] = 'Program'
        program['function'] = func

        tokenIterator = TokensIter(tokens, id)
        token = tokenIterator.next_item()
        token = skip_white_spaces_new_line(token, tokenIterator)

        if token[1] != 'identifier':
            print("Not id")
            exit(1)

        func_call, id = parse_func_call(tokens, id)
        program['function_call'] = func_call

        tokenIterator.set_id(id)
        token = tokenIterator.next_item()
        token = skip_white_spaces_new_line(token, tokenIterator)

        if token != False:
            print("\nUnexpected token\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                       token[0][1]['symbol']))
            exit(1)

        return program

    AST = parse_program(tokens)
    return AST


# CODE GENERATION
global code
code = ''


def codegen(AST):
    global code

    def code_from_ast(exp: dict):
        global code
        if exp['kind'] == 'Constant':
            code = code + "   mov eax, {}\n   push eax\n".format(exp['value'])
        if exp['kind'] == 'Expression':
            if exp['type'] == 'Unary':
                code_from_ast(exp['factor'])
                code = code + '   pop eax\n   not eax\n   push eax\n'
            if exp['type'] == 'Non Binary':
                code_from_ast(exp['factor'])
            if exp['type'] == 'Binary':
                for i in range(1, exp['add_count']+1):
                    code_from_ast(exp['addition'+str(i)])
                for i in range(1, exp['add_count']):
                    code = code + '   pop eax\n   pop ebx\n   add eax, ebx\n   push eax\n'
        if exp['kind'] == 'Exp in brackets':
            code_from_ast(exp['exp'])

    for func_call_search in AST:
        if func_call_search.startswith('function_call'):
            func = 0
            for k1 in AST:
                if k1 == 'function' and AST[func_call_search]['name'] == AST[k1]['name']:
                    func += 1
                    for k2 in AST[k1]:
                        if k2.startswith('statement'):
                            if AST[k1][k2]['name'] == "return":
                                exp = AST[k1][k2]['exp']
                                code = code + AST[k1]['name'] + ":\n"
                                code_from_ast(exp)
                                code = code + '   pop eax\n   ret'
                                code = code.replace('\n   push eax\n   pop eax', '')
            if func != 1:
                print('\n Function declaration not found')
                input()
                exit(1)
    return code


# Main program
def main(argv):
    file_name = check_args(argv)
    if not file_name.endswith('.txt'):
        print("Wrong file format, expected .txt")
        return
    tokens = lexer(file_name)

    print("Tokens list:")
    for token in tokens:
        print(token)

    AST = parser(tokens)

    print()
    print()
    print("AST:")
    AST_readable = json.dumps(AST, indent=4)
    print(AST_readable)

    code = codegen(AST)
    print()
    print()
    print("Generated Code:")
    print(code)

    with open('2-14-Python-ІВ-81-Зубець-output.asm', 'w') as f:
        f.write(code)

    print("\nEnter anything to exit")
    input()


if __name__ == "__main__":
    main(sys.argv[1:])
