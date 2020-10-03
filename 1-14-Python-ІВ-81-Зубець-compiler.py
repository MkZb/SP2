import getopt
import json
import sys

coding = 'utf-8'


# Function that checks command line parameters
def check_args(argv):
    try:
        opts, args = getopt.getopt(argv, "i:o", ["input="])
    except getopt.GetoptError:
        print('1-14-Python-ІВ-81-Зубець-compiler.py -i <input_file>')
        input()
        exit(1)

    for opt, arg in opts:
        if opt in ('-i', '--input'):
            return arg

    return '1-14-Python-ІВ-81-Зубець-program.py'


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
        delimiters = [' ', '\n', ':', ';', '(', ')', '-', '+']
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
        b'\n': 'new_line'
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
    def parse_statement(tokens, index=0):
        statement = {}

        tokenIterator = TokensIter(tokens, index-1)
        token = tokenIterator.next_item()

        print(token)
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

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

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

        exp = {'kind': 'Expression',
               'type': type,
               'value': value}

        statement['kind'] = 'Statement'
        statement['name'] = 'return'
        statement['exp'] = exp

        token = tokenIterator.next_item()
        token = skip_white_spaces_new_line(token, tokenIterator)

        if not token:
            pass
        elif token[1] == 'identifier':
            next_token = tokenIterator.next_item()
            next_token = skip_white_spaces(next_token, tokenIterator)

            if not next_token:
                print("\nUnexpected token\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                           token[0][1]['symbol']))
                input()
                exit(1)

            if next_token[1] != 'open_parentheses':
                print("\nUnexpected token\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                           token[0][1]['symbol']))
                input()
                exit(1)

            next_token = tokenIterator.next_item()
            next_token = skip_white_spaces(next_token, tokenIterator)

            if not next_token:
                print("\nUnexpected token\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                           token[0][1]['symbol']))
                input()
                exit(1)

            if next_token[1] != 'closed_parentheses':
                print("\nUnexpected token\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                           token[0][1]['symbol']))
                input()
                exit(1)
        elif token[1] == 'function_declaration':
            pass
        else:
            print("\nUnexpected token\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                       token[0][1]['symbol']))
            input()
            exit(1)

        return statement

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
        statement = parse_statement(tokens, tokenIterator.get_current_id())
        func['kind'] = 'Function Declaration'
        func['name'] = name
        func['statement'] = statement
        return func

    def parse_func_call(tokens, index=0):
        func_call = {}

        tokenIterator = TokensIter(tokens, index)
        token = tokenIterator.next_item()

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

        token = tokenIterator.next_item()
        token = skip_white_spaces_new_line(token, tokenIterator)

        if token != False:
            print("\nUnexpected token\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                     token[0][1]['symbol']))
            exit(1)

        return func_call

    def parse_program(tokens, index=0):
        program = {}
        if tokens[0][1] == 'function_declaration':
            functions_amount = 0
            for i in tokens:
                if i[1] == 'function_declaration':
                    functions_amount += 1
            if functions_amount == 1:
                function = parse_function(tokens)
                program['kind'] = 'Program'
                program['function'] = function
                c = 0
                for i in range(len(tokens)):
                    if tokens[i][0][0].decode(coding) == function['name']:
                        c += 1
                    if c == 2:
                        func_call = parse_func_call(tokens, index=i - 1)
                        program['function_call'] = func_call
                        break

                if c == 1:
                    print("\nWarning: function call not found. Code will not be generated.")
                    return program
                if c == 2:
                    return program
                else:
                    print("\nMore than 1 identifier given.")
                    input()
                    exit(1)
            else:
                print("\nMore than 1 function given.")
                input()
                exit(1)
        else:
            print("\nError program must start from function declaration\nLine: 1, Character: 1")
            input()
            exit(1)

    AST = parse_program(tokens)
    return AST


# CODE GENERATION

def codegen(AST):
    code = ''
    for func_call_search in AST:
        if func_call_search.startswith('function_call'):
            func = 0
            for k1 in AST:
                if k1 == 'function' and AST[k1]['name'] == AST[k1]['name']:
                    func += 1
                    for k2 in AST[k1]:
                        if k2.startswith('statement'):
                            if AST[k1][k2]['name'] == "return":
                                if AST[k1][k2]['exp']['type'] == 'int':
                                    code = '{}:\n   mov eax, {}\n   ret'.format(AST[k1]['name'],
                                                                                AST[k1][k2]['exp']['value'])
                                elif AST[k1][k2]['exp']['type'] == 'float':
                                    code = '{}:\n   mov eax, {}\n   ret'.format(AST[k1]['name'],
                                                                                AST[k1][k2]['exp']['value'])
            if func != 1:
                print('\n Function declaration not found')
                input()
                exit(1)
    return code


# Main program
def main(argv):
    file_name = check_args(argv)
    if not file_name.endswith('.py'):
        print("Wrong file format, expected .py")
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

    with open('1-14-Python-ІВ-81-Зубець-output.asm', 'w') as f:
        f.write(code)

    print("\nEnter anything to exit")
    input()


if __name__ == "__main__":
    main(sys.argv[1:])
