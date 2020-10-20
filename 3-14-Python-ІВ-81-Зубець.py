import getopt
import json
import sys

coding = 'utf-8'


# Function that checks command line parameters
def check_args(argv):
    try:
        opts, args = getopt.getopt(argv, "i:o", ["input="])
    except getopt.GetoptError:
        print('3-14-Python-ІВ-81-Зубець.py -i <input_file>')
        input()
        exit(1)

    for opt, arg in opts:
        if opt in ('-i', '--input'):
            return arg

    return '3-14-Python-ІВ-81-Зубець.txt'


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
        delimiters = [' ', '\n', ':', ';', '(', ')', '-', '+', '~', '=', '>>']
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
        b'+': 'addition',
        b'-': 'substraction',
        b'=': 'equal',
        b'>>': 'r_shift'
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
            tokenIterator.set_id(id)
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)
            if token[1] != 'closed_parentheses':
                print("\nExpected closing parentheses\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                       token[0][1]['symbol']))
                exit(1)

            return factor, tokenIterator.get_current_id()
        elif token[1] == 'bitwise_complement':
            factor['kind'] = 'Expression'
            factor['type'] = 'Unary'
            factor['operator'] = token[0][0].decode(coding)
            new_factor, id = parse_factor(tokens, tokenIterator.get_current_id())
            factor['factor'] = new_factor
            return factor, id

        elif token[1] == 'identifier':
            factor['kind'] = 'Variable'
            factor['name'] = token[0][0].decode(coding)
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

    def parse_term(tokens, index=0):
        exp = {}
        tokenIterator = TokensIter(tokens, index)
        exp['kind'] = 'Expression'
        exp['type'] = 'Non Binary'

        factor, id = parse_factor(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)

        save_id = id
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        next_item = token[1]
        if (next_item != 'addition') and (next_item != 'substraction'):
            exp['factor'] = factor
            return exp, save_id

        exp['type'] = 'Addition'
        add_counter = 1
        sub_counter = 1

        exp['addition1'] = factor

        while next_item in ['addition', 'substraction']:
            if next_item == 'addition':
                add_counter += 1
                factor, id = parse_factor(tokens, tokenIterator.get_current_id())
                exp['addition' + str(add_counter)] = factor
                tokenIterator.set_id(id)
                save_id = id
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)
                next_item = token[1]
                exp['add_count'] = add_counter
            else:
                sub_counter += 1
                factor, id = parse_factor(tokens, tokenIterator.get_current_id())
                exp['substraction' + str(sub_counter)] = factor
                tokenIterator.set_id(id)
                save_id = id
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)
                next_item = token[1]
                exp['sub_count'] = sub_counter

        return exp, save_id

    def parse_exp(tokens, index=0):
        exp = {}
        tokenIterator = TokensIter(tokens, index)

        exp['kind'] = 'Expression'
        exp['type'] = 'Non Binary'

        term, id = parse_term(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)

        save_id = id
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        next_item = token[1]

        if next_item != 'r_shift':
            exp = term
            return exp, save_id

        counter = 1
        exp['type'] = 'Shifting'
        exp['r_shift' + str(counter)] = term

        while next_item == 'r_shift':
            counter += 1
            print('111', token)
            term, id = parse_factor(tokens, tokenIterator.get_current_id())
            exp['r_shift' + str(counter)] = term
            tokenIterator.set_id(id)
            save_id = id
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)
            next_item = token[1]
            exp['shift_counter'] = counter

        return exp, save_id

    def parse_statement(tokens, index=0):
        statement = {}

        tokenIterator = TokensIter(tokens, index)
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

        if token[1] == 'return_keyword':
            print('222', tokens[tokenIterator.get_current_id()])
            exp, id = parse_exp(tokens, tokenIterator.get_current_id())

            statement['kind'] = 'Statement'
            statement['type'] = 'Return'
            statement['exp'] = exp

            tokenIterator.set_id(id)
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)
            if token[1] not in ['new_line']:
                print("\nExpected '='\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                       token[0][1]['symbol']))
                input()
                exit(1)
            return statement, tokenIterator.get_current_id()

        elif token[1] == 'identifier':
            statement['kind'] = 'Statement'
            statement['type'] = 'Assignment'
            statement['var'] = token[0][0].decode(coding)

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)

            if token[1] != 'equal':
                print("\nExpected '='\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                       token[0][1]['symbol']))
                input()
                exit(1)

            statement['value'], id = parse_exp(tokens, tokenIterator.get_current_id())

            tokenIterator.set_id(id)
            token = tokenIterator.next_item()
            if token[1] not in ['new_line']:
                print("\nExpected '='\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                       token[0][1]['symbol']))
                input()
                exit(1)

            token = skip_new_line(token, tokenIterator)

            return statement, tokenIterator.get_current_id()

        else:
            print("\nStatement must be either return or assignment\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                                    token[0][1][
                                                                                                        'symbol']))
            input()
            exit(1)

    def parse_function(tokens, index=0):
        func = {}
        tokenIterator = TokensIter(tokens, index)
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

        statement_counter = 1
        token = skip_new_line(token, tokenIterator)
        statement, id = parse_statement(tokens, tokenIterator.get_current_id())
        func['kind'] = 'Function Declaration'
        func['name'] = name
        func['statement' + str(statement_counter)] = statement

        tokenIterator.set_id(id - 1)

        token = tokenIterator.next_item()

        token = skip_new_line(token, tokenIterator)

        save_id = tokenIterator.get_current_id()

        token = skip_white_spaces(token, tokenIterator)
        next_item = token[1]

        while (next_item == 'identifier') or (next_item == 'return_keyword'):
            statement_counter += 1
            tokenIterator.set_id(save_id)
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)

            if token[1] == 'open_parentheses':
                break
            tokenIterator.set_id(save_id)
            token = tokenIterator.next_item()

            statement, id = parse_statement(tokens, tokenIterator.get_current_id())
            func['statement' + str(statement_counter)] = statement
            tokenIterator.set_id(id)
            token = skip_new_line(token, tokenIterator)
            save_id = tokenIterator.get_current_id()
            token = skip_white_spaces(token, tokenIterator)
            next_item = token[1]

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
        func, id = parse_function(tokens, -1)
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
var_map = {}
counter = 0


def codegen(AST):
    global code, var_map, counter

    def code_from_ast(exp: dict):
        global code, var_map

        if exp['kind'] == 'Constant':
            code = code + '    mov eax, {}\n    push eax\n'.format(exp['value'])

        if exp['kind'] == 'Variable':
            code = code + '    mov eax, [ebp + {}]\n    push eax\n'.format(var_map[exp['name']])

        if exp['kind'] == 'Expression':
            if exp['type'] == 'Unary':
                code_from_ast(exp['factor'])
                code = code + '    pop eax\n    not eax\n    push eax\n'
            if exp['type'] == 'Non Binary':
                code_from_ast(exp['factor'])
            if exp['type'] == 'Shifting':
                code_from_ast(exp['r_shift1'])
                for i in range(2, exp['shift_counter'] + 1):
                    code_from_ast(exp['r_shift'+str(i)])
                    code = code + '    pop ebx\n    pop eax\n    mov cl, bl\n    sar eax, cl\n    push eax\n'
            if exp['type'] == 'Addition':
                if 'add_count' in exp.keys():
                    for i in range(1, exp['add_count'] + 1):
                        code_from_ast(exp['addition' + str(i)])
                    for i in range(1, exp['add_count']):
                        code = code + '    pop eax\n    pop ebx\n    add eax, ebx\n    push eax\n'
                if 'sub_count' in exp.keys():
                    if 'add_count' not in exp.keys():
                        code_from_ast(exp['addition1'])
                    for i in range(2, exp['sub_count'] + 1):
                        code_from_ast(exp['substraction'+str(i)])
                        code = code + '    pop ebx\n    pop eax\n    sub eax, ebx\n    push eax\n'
        if exp['kind'] == 'Exp in brackets':
            code_from_ast(exp['exp'])

    for func_call_search in AST:
        if func_call_search.startswith('function_call'):
            func = 0
            for k1 in AST:
                if k1 == 'function' and AST[func_call_search]['name'] == AST[k1]['name']:
                    func += 1
                    code = code + AST[k1]['name'] + ":\n    push ebp\n    mov ebp, esp\n"
                    for k2 in AST[k1]:
                        if k2.startswith('statement'):
                            if AST[k1][k2]['type'] == "Return":
                                exp = AST[k1][k2]['exp']
                                code_from_ast(exp)
                                code = code + '    pop eax\n'
                            elif AST[k1][k2]['type'] == "Assignment":
                                exp = AST[k1][k2]
                                if exp['var'] not in var_map.keys():
                                    code_from_ast(exp['value'])
                                    counter += 4
                                    code = code + '    pop eax\n    mov [ebp + {}], eax\n'.format(counter)
                                    var_map[exp['var']] = counter
                                else:
                                    code_from_ast(exp['value'])
                                    code = code + '    pop eax\n    mov [ebp + {}], eax\n'.format(var_map[exp['var']])
                    code = code.replace('\n    push eax\n    pop eax', '')
                    code = code.replace('\n    push ebx\n    pop ebx', '')
                    code = code + "    mov esp, ebp\n    pop ebp\n    ret"
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

    with open('3-14-Python-ІВ-81-Зубець.asm', 'w') as f:
        f.write(code)

    print("\nEnter anything to exit")
    input()


if __name__ == "__main__":
    main(sys.argv[1:])
