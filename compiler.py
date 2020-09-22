import getopt
import json
import sys

coding = 'utf-8'


# Function that checks command line parameters
def check_args(argv):
    try:
        opts, args = getopt.getopt(argv, "i:o", ["input="])
    except getopt.GetoptError:
        print('compiler.py -i <input_file>')

    for opt, arg in opts:
        if opt in ('-i', '--input'):
            return arg

    return 'program.py'


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
        delimiters = [' ', '\n', ':', ';', '(', ')']
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
        yield string[start_pos:current_pos], {'symbol': start_pos + 1, 'line': line_counter}

    string = string.replace(b'\r', b'')
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
            else:
                print("Lexem \"{}\" is not recognizable.".format(i.decode(coding)))
        elif i[0].decode(coding).startswith(
                ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            if i[0].decode(coding).count('.') == 1:
                if i[0].decode(coding).replace('.', '').isnumeric() and not i[0].decode(coding).endswith('.'):
                    tokens.append((i, 'float_constant'))
                else:
                    print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
            else:
                print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
        else:
            start_sym = tuple([chr(k) for k in range(65, 91)] + [chr(k) for k in range(97, 123)])
            if i[0].decode(coding).startswith(start_sym):
                if i[0].decode(coding).isalnum():
                    tokens.append((i, 'identifier'))
                else:
                    print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
            else:
                print("Lexem \"{}\" is not recognizable.".format(i[0].decode(coding)))
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

    # Recursive parser
    def parse_statement(tokens, index=0):
        statement = {}

        tokenIterator = TokensIter(tokens, index)
        token = tokenIterator.next_item()
        if not token:
            print("Unexpected EOF")
            exit()

        if token[1] != 'white_space':
            print("\nError function body must be in white spaces\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                                  token[0][1][
                                                                                                      'symbol']))
            exit()

        token = skip_white_spaces(token, tokenIterator)
        if not token:
            print("Unexpected EOF")
            exit()

        if token[1] != 'return_keyword':
            print("Statement must start from return\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                     token[0][1]['symbol']))
            exit()

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("Unexpected EOF")
            exit()

        if token[1] not in ['float_constant', 'octal_constant', 'decimal_constant']:
            print("Wrong return type\nLine: {}, Character: {}".format(token[0][1]['line'], token[0][1]['symbol']))

        if token[1] == 'octal_constant':
            value = int(token[0][0].decode(coding), 8)
            if not -2147483648 < value < 2147483647:
                print("Value out of int32_t range\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                   token[0][1]['symbol']))
                exit()
            type = 'int'
        elif token[1] == 'float_constant':
            value = int(float(token[0][0].decode(coding)))
            if not -2147483648 < value < 2147483647:
                print("Value out of int32_t range\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                   token[0][1]['symbol']))
                exit()
            type = 'float'
        else:
            value = int(token[0][0].decode(coding))
            if not -2147483648 < value < 2147483647:
                print("Value out of int32_t range\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                   token[0][1]['symbol']))
                exit()
            type = 'int'

        exp = {'kind': 'Expression',
               'type': type,
               'value': value}

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if token:
            print("Expected end of file after return statement")
            exit()

        statement['kind'] = 'Statement'
        statement['name'] = 'return'
        statement['exp'] = exp
        return statement

    def parse_function(tokens, index=0):
        func = {}
        tokenIterator = TokensIter(tokens, index - 1)
        token = tokenIterator.next_item()
        if not token:
            print("Blank file")
            exit()

        if token[1] != 'function_declaration':
            print("\nError func must be declared\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                  token[0][1]['symbol']))
            exit()

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)
        if not token:
            print("Unexpected EOF")
            exit()

        if token[1] != 'identifier':
            print("\nError in function declaration, function must have name\nLine: {}, Character: {}".format(
                token[0][1]['line'], token[0][1]['symbol']))
            exit()
        name = token[0][0].decode(coding)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("Unexpected EOF")
            exit()

        if token[1] != 'open_parentheses':
            print(
                "\nError after func name must be open parentheses\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                                   token[0][1][
                                                                                                       'symbol']))
            exit()

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("Unexpected EOF")
            exit()

        if token[1] != 'closed_parentheses':
            print("\nError after open parentheses must be closed parentheses\nLine: {}, Character: {}".format(
                token[0][1]['line'], token[0][1]['symbol']))
            exit()

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("Unexpected EOF")
            exit()

        if token[1] != 'colon':
            print("\nError after closed parentheses must be colon\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                                   token[0][1][
                                                                                                       'symbol']))
            exit()

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)

        if not token:
            print("Unexpected EOF")
            exit()

        if token[1] != 'new_line':
            print("Must be new line after func declaration\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                            token[0][1]['symbol']))
            exit()

        statement = parse_statement(tokens, tokenIterator.get_current_id())
        func['kind'] = 'Function Declaration'
        func['name'] = name
        func['statement'] = statement
        return func

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
                return program
            else:
                print("\nError more than 1 function given")
                exit()
        else:
            print("\nError program must start from function\nLine: 1, Character: 1")
            exit()

    AST = parse_program(tokens)
    return AST


# CODE GENERATION

def codegen(AST):
    code = ''
    for k1 in AST:
        if k1.startswith('function'):
            for k2 in AST[k1]:
                if k2.startswith('statement'):
                    if AST[k1][k2]['name'] == "return":
                        if AST[k1][k2]['exp']['type'] == 'int':
                            code = 'mov eax, {}\nret'.format(AST[k1][k2]['exp']['value'])
                        elif AST[k1][k2]['exp']['type'] == 'float':
                            code = 'mov eax, {}\nret'.format(AST[k1][k2]['exp']['value'])
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


if __name__ == "__main__":
    main(sys.argv[1:])
