import getopt
import json
import sys

coding = 'utf-8'


# Function that checks command line parameters
def check_args(argv):
    try:
        opts, args = getopt.getopt(argv, "i:o", ["input="])
    except getopt.GetoptError:
        print('6-14-Python-ІВ-81-Зубець.py -i <input_file>')
        input()
        exit(1)

    for opt, arg in opts:
        if opt in ('-i', '--input'):
            return arg

    return '6-14-Python-ІВ-81-Зубець.txt'


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
        delimiters = [' ', '\n', ':', ';', '(', ')', '-', '+', '~', '=', ',', '>', '<', '%', '#']
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
        b'>>': 'r_shift',
        b'if': 'if',
        b'else': 'else',
        b'elif': 'elif',
        b',': 'coma',
        b'>>=': 'r_shift_equals',
        b'while': 'while',
        b'break': 'break',
        b'continue': 'continue',
        b'and': 'and',
        b'>': 'greater',
        b'<': 'less',
        b'==': 'equal_check',
        b'%': 'remainder'
    }
    comment = 0
    for i in items:
        if comment:
            if i[0] == b'\n':
                comment = 0
            else:
                continue
        if i[0] == b'#':
            comment = 1
            continue
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
    for i in range(len(tokens)):
        if i < (len(tokens) - 1):
            if tokens[i][1] == 'r_shift':
                if tokens[i + 1][1] == 'equal':
                    tokens[i] = ((b'>>=', tokens[i][0][1]), templates[b'>>='])
                    tokens.pop(i + 1)
            if tokens[i][1] == 'equal':
                if tokens[i + 1][1] == 'equal':
                    tokens[i] = ((b'>>=', tokens[i][0][1]), templates[b'=='])
                    tokens.pop(i + 1)

    return tokens


# PARSER

def parser(tokens: list):
    spacing = []

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
        white_space_counter = 0
        if not token:
            return token, white_space_counter
        while token[1] == 'white_space':
            if not token:
                return token, white_space_counter
            token = tokenIterator.next_item()
            white_space_counter += 1
        return token, white_space_counter

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
        token = skip_white_spaces(token, tokenIterator)[0]
        id = tokenIterator.get_current_id()
        name = token[0][0].decode(coding)
        if token[1] == 'identifier':
            save_id = id
            token = tokenIterator.next_item()
            token, id = skip_white_spaces(token, tokenIterator)
            if token[1] != 'open_parentheses':
                id = save_id - 1
                tokenIterator.set_id(id)
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]
            else:
                factor['kind'] = "Function call"
                factor['name'] = name
                token = tokenIterator.next_item()
                token, id = skip_white_spaces(token, tokenIterator)
                args = 0
                next_item = token[1]
                while next_item != 'closed_parentheses':
                    args += 1
                    factor['arg' + str(args)], id = parse_conditional_exp(tokens, tokenIterator.get_current_id() - 1)
                    tokenIterator.set_id(id)
                    token = tokenIterator.next_item()
                    token, save_id = skip_white_spaces(token, tokenIterator)
                    if token[1] == 'closed_parentheses':
                        break
                    elif token[1] == 'coma':
                        token = tokenIterator.next_item()
                        token, id = skip_white_spaces(token, tokenIterator)
                    else:
                        print("\nUnexpected token in function call arguments\nLine: {}, Character: {}".format(
                            token[0][1]['line'],
                            token[0][1]['symbol']))
                        print()
                        exit(1)

                if token[1] != 'closed_parentheses':
                    print("\nExpected closing parentheses\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                           token[0][1]['symbol']))
                    input()
                    exit(1)
                return factor, tokenIterator.get_current_id()

        if token[1] == 'open_parentheses':
            factor['kind'] = 'Exp in brackets'
            exp, id = parse_conditional_exp(tokens, tokenIterator.get_current_id())
            print(exp)
            factor['exp'] = exp
            tokenIterator.set_id(id)
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            if token[1] != 'closed_parentheses':
                print("\nExpected closing parentheses\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                       token[0][1]['symbol']))
                input()
                exit(1)

            return factor, tokenIterator.get_current_id()
        elif token[1] == 'bitwise_complement':
            factor['kind'] = 'Expression'
            factor['type'] = 'Unary'
            factor['operator'] = token[0][0].decode(coding)
            new_factor, id = parse_factor(tokens, tokenIterator.get_current_id())
            factor['factor'] = new_factor
            return factor, id

        elif token[1] == 'r_shift_equals':
            new_factor, id = parse_factor(tokens, tokenIterator.get_current_id())
            factor['factor'] = new_factor
            return factor, id

        elif token[1] == 'identifier':
            factor['kind'] = 'Variable'
            factor['name'] = token[0][0].decode(coding)
            return factor, tokenIterator.get_current_id()

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
            return factor, tokenIterator.get_current_id()

    def parse_term(tokens, index=0):
        exp = {}
        tokenIterator = TokensIter(tokens, index)

        exp['kind'] = 'Expression'
        exp['type'] = 'Remainder'

        term, id = parse_factor(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)
        save_id = id
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

        next_item = token[1]

        if next_item not in ['remainder']:
            exp = term
            return exp, save_id

        counter = 1
        exp['remainder1'] = term

        while next_item == 'remainder':
            counter += 1
            term, id = parse_factor(tokens, tokenIterator.get_current_id())
            exp['remainder' + str(counter)] = term
            tokenIterator.set_id(id)
            save_id = id
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            next_item = token[1]
            exp['remainder_counter'] = counter

        return exp, save_id

    def parse_add(tokens, index=0):
        exp = {}
        tokenIterator = TokensIter(tokens, index)
        exp['kind'] = 'Expression'
        exp['type'] = 'Non Binary'
        factor, id = parse_term(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)

        save_id = id
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]
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
                factor, id = parse_term(tokens, tokenIterator.get_current_id())
                exp['addition' + str(add_counter)] = factor
                tokenIterator.set_id(id)
                save_id = id
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]
                next_item = token[1]
                exp['add_count'] = add_counter
            else:
                sub_counter += 1
                factor, id = parse_term(tokens, tokenIterator.get_current_id())
                exp['substraction' + str(sub_counter)] = factor
                tokenIterator.set_id(id)
                save_id = id
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]
                next_item = token[1]
                exp['sub_count'] = sub_counter

        return exp, save_id

    def parse_shift(tokens, index=0):
        exp = {}
        tokenIterator = TokensIter(tokens, index)

        exp['kind'] = 'Expression'
        exp['type'] = 'Non Binary'
        term, id = parse_add(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)
        save_id = id
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

        next_item = token[1]

        if next_item != 'r_shift':
            exp = term
            return exp, save_id

        counter = 1
        exp['type'] = 'Shifting'
        exp['r_shift' + str(counter)] = term

        while next_item == 'r_shift':
            counter += 1
            term, id = parse_add(tokens, tokenIterator.get_current_id())
            exp['r_shift' + str(counter)] = term
            tokenIterator.set_id(id)
            save_id = id
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            next_item = token[1]
            exp['shift_counter'] = counter

        return exp, save_id

    def parse_comparison(tokens, index=0):
        exp = {}
        tokenIterator = TokensIter(tokens, index)

        exp['kind'] = 'Expression'
        exp['type'] = 'Comparison'

        term, id = parse_shift(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)
        save_id = id
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

        next_item = token[1]

        if next_item not in ['greater', 'less', 'equal_check']:
            exp = term
            return exp, save_id

        counter = 1
        exp['comparison1'] = term

        while next_item in ['greater', 'less', 'equal_check']:
            counter += 1
            term, id = parse_shift(tokens, tokenIterator.get_current_id())
            exp['comparison' + str(counter)] = term
            exp['comparison' + str(counter) + '_sign'] = next_item
            tokenIterator.set_id(id)
            save_id = id
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            next_item = token[1]
            exp['comparison_counter'] = counter

        return exp, save_id

    def parse_log_and(tokens, index=0):
        exp = {}
        tokenIterator = TokensIter(tokens, index)

        exp['kind'] = 'Expression'
        exp['type'] = 'Non Binary'

        term, id = parse_comparison(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)
        save_id = id
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

        next_item = token[1]

        if next_item != 'and':
            exp = term
            return exp, save_id

        counter = 1
        exp['type'] = 'And'
        exp['and' + str(counter)] = term

        while next_item == 'and':
            counter += 1
            term, id = parse_comparison(tokens, tokenIterator.get_current_id())
            exp['and' + str(counter)] = term
            tokenIterator.set_id(id)
            save_id = id
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            next_item = token[1]
            exp['and_counter'] = counter

        return exp, save_id

    def parse_conditional_exp(tokens, index=0):
        exp = {}
        tokenIterator = TokensIter(tokens, index)

        exp['kind'] = 'Expression'
        exp['type'] = 'Conditional'

        term, id = parse_log_and(tokens, tokenIterator.get_current_id())
        tokenIterator.set_id(id)
        save_id = id
        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]
        next_item = token[1]

        if next_item != 'if':
            exp = term
            return exp, save_id

        exp['true_condition'] = term

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

        term, id = parse_log_and(tokens, tokenIterator.get_current_id() - 1)
        exp['condition'] = term

        tokenIterator.set_id(id)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

        if token[1] != 'else':
            print("\nExpected 'else' keyword\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                              token[0][1][
                                                                                  'symbol']))
            input()
            exit(1)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

        term, id = parse_conditional_exp(tokens, tokenIterator.get_current_id() - 1)
        exp['false_condition'] = term

        return exp, id

    def parse_statement(tokens, index=0):
        def check_nesting(space_info: list, spaces: int, type: str):
            while True:
                last_item = space_info.pop()
                if last_item[1] == 'statement':
                    continue
                elif (last_item[0] == spaces) and (last_item[1] == 'if'):
                    space_info.append(last_item)
                    return True
                elif (last_item[0] > spaces) and (last_item[1] == 'if'):
                    return False
                else:
                    continue

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

        token, spaces = skip_white_spaces(token, tokenIterator)

        if not token:
            print("\nUnexpected EOF")
            input()
            exit(1)

        if token[1] == 'return_keyword':
            spacing.append((spaces, 'statement'))
            exp, id = parse_conditional_exp(tokens, tokenIterator.get_current_id())

            statement['kind'] = 'Statement'
            statement['type'] = 'Return'
            statement['exp'] = exp

            tokenIterator.set_id(id)
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            if token[1] not in ['new_line']:
                print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                            token[0][1]['symbol']))
                input()
                exit(1)
            return statement, tokenIterator.get_current_id()
        elif token[1] == 'break':
            statement['kind'] = 'Statement'
            statement['type'] = 'Break'

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            if token[1] not in ['new_line']:
                print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                            token[0][1]['symbol']))
                input()
                exit(1)
            return statement, tokenIterator.get_current_id()

        elif token[1] == 'continue':
            statement['kind'] = 'Statement'
            statement['type'] = 'Continue'

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            if token[1] not in ['new_line']:
                print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                            token[0][1]['symbol']))
                input()
                exit(1)
            return statement, tokenIterator.get_current_id()

        elif token[1] == 'identifier':
            spacing.append((spaces, 'statement'))
            statement['kind'] = 'Statement'
            statement['type'] = 'Assignment'
            statement['var'] = token[0][0].decode(coding)

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            if token[1] not in ['equal', 'r_shift_equals']:
                print("\nExpected '='\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                       token[0][1]['symbol']))
                input()
                exit(1)

            if token[1] == 'r_shift_equals':
                statement['type'] = 'R_shift + Assignment'
                statement['value'], id = parse_factor(tokens, tokenIterator.get_current_id() - 1)
            else:
                statement['value'], id = parse_conditional_exp(tokens, tokenIterator.get_current_id())

            tokenIterator.set_id(id)
            token = tokenIterator.next_item()
            if token[1] not in ['new_line']:
                print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                            token[0][1]['symbol']))
                input()
                exit(1)

            token = skip_new_line(token, tokenIterator)
            return statement, tokenIterator.get_current_id() - 1

        elif token[1] == 'if':
            spacing.append((spaces, 'if'))
            statement['kind'] = 'Statement'
            statement['type'] = 'Conditional'

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]

            statement['condition'], id = parse_conditional_exp(tokens, tokenIterator.get_current_id() - 1)

            tokenIterator.set_id(id)

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]

            if token[1] not in ['colon']:
                print("\nExpected ':'\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                       token[0][1]['symbol']))
                input()
                exit(1)

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]

            if token[1] not in ['new_line']:
                print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                            token[0][1]['symbol']))
                input()
                exit(1)

            token = tokenIterator.next_item()
            token, current_spaces = skip_white_spaces(token, tokenIterator)
            last_item = spacing.pop()
            if current_spaces <= last_item[0]:
                print("\nUnidentified nesting\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                               token[0][1]['symbol']))
                input()
                exit(1)
            else:
                spacing.append(last_item)
            statement_counter = 1
            statement['statement' + str(statement_counter)], id = parse_statement(tokens,
                                                                                  tokenIterator.get_current_id() - current_spaces - 1)
            tokenIterator.set_id(id)
            token = tokenIterator.next_item()

            token, new_spaces = skip_white_spaces(token, tokenIterator)
            save_id = id
            while new_spaces == current_spaces:
                statement_counter += 1
                statement['statement' + str(statement_counter)], id = parse_statement(tokens,
                                                                                      tokenIterator.get_current_id() - current_spaces - 1)
                tokenIterator.set_id(id)
                save_id = id
                token = tokenIterator.next_item()
                token, new_spaces = skip_white_spaces(token, tokenIterator)

            tokenIterator.set_id(save_id - 1)
            token = tokenIterator.next_item()
            if token[1] not in ['new_line']:
                print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                            token[0][1]['symbol']))
                input()
                exit(1)

            save_id = tokenIterator.get_current_id()
            token = skip_new_line(token, tokenIterator)
            token, new_spaces = skip_white_spaces(token, tokenIterator)
            elif_check = token[1]
            if elif_check == 'elif':
                if check_nesting(spacing, new_spaces, 'elif'):
                    elif_count = 0
                else:
                    return statement, tokenIterator.get_current_id() - new_spaces - 1

            while elif_check == 'elif':
                spacing.append((new_spaces, 'elif'))
                elif_count += 1
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]

                statement['elif' + str(elif_count)] = {}
                statement['elif' + str(elif_count)]['condition'], id = parse_conditional_exp(tokens,
                                                                                             tokenIterator.get_current_id() - 1)
                tokenIterator.set_id(id)
                token = tokenIterator.next_item()
                if token[1] not in ['colon']:
                    print("\nExpected ':'\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                           token[0][1]['symbol']))
                    input()
                    exit(1)

                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]

                if token[1] not in ['new_line']:
                    print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                token[0][1]['symbol']))
                    input()
                    exit(1)

                token = tokenIterator.next_item()
                token, current_spaces = skip_white_spaces(token, tokenIterator)
                statement_counter = 1
                statement['elif' + str(elif_count)]['statement' + str(statement_counter)], id = parse_statement(
                    tokens,
                    tokenIterator.get_current_id() - current_spaces - 1)
                tokenIterator.set_id(id)
                save_id = id
                token = tokenIterator.next_item()
                token, new_spaces = skip_white_spaces(token, tokenIterator)

                while new_spaces == current_spaces:
                    statement_counter += 1
                    statement['elif' + str(elif_count)]['statement' + str(statement_counter)], id = parse_statement(
                        tokens,
                        tokenIterator.get_current_id() - current_spaces - 1)
                    tokenIterator.set_id(id)
                    save_id = id
                    token = tokenIterator.next_item()
                    token, new_spaces = skip_white_spaces(token, tokenIterator)

                tokenIterator.set_id(save_id - 1)
                token = tokenIterator.next_item()
                if token[1] not in ['new_line']:
                    print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                token[0][1]['symbol']))
                    input()
                    exit(1)

                token = tokenIterator.next_item()
                save_id = tokenIterator.get_current_id()
                token = skip_white_spaces(token, tokenIterator)[0]
                elif_check = token[1]

            tokenIterator.set_id(save_id - 1)
            token = tokenIterator.next_item()
            save_id = tokenIterator.get_current_id()
            token = skip_new_line(token, tokenIterator)
            token, new_spaces = skip_white_spaces(token, tokenIterator)
            else_check = token[1]

            if else_check == 'else':
                if not check_nesting(spacing, new_spaces, 'else'):
                    return statement, tokenIterator.get_current_id() - new_spaces - 1

            if token[1] == 'else':
                spacing.append((new_spaces, 'else'))
                statement['else'] = {}
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]

                if token[1] not in ['colon']:
                    print("\nExpected ':'\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                           token[0][1]['symbol']))
                    input()
                    exit(1)

                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]

                if token[1] not in ['new_line']:
                    print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                token[0][1]['symbol']))
                    input()
                    exit(1)

                token = tokenIterator.next_item()
                token, current_spaces = skip_white_spaces(token, tokenIterator)
                statement_counter = 1
                statement['else']['statement' + str(statement_counter)], id = parse_statement(
                    tokens,
                    tokenIterator.get_current_id() - current_spaces - 1)
                tokenIterator.set_id(id)
                token = tokenIterator.next_item()
                token, new_spaces = skip_white_spaces(token, tokenIterator)
                save_id = id
                while new_spaces == current_spaces:
                    statement_counter += 1
                    statement['else']['statement' + str(statement_counter)], id = parse_statement(
                        tokens,
                        tokenIterator.get_current_id() - current_spaces - 1)
                    tokenIterator.set_id(id)
                    save_id = id
                    token = tokenIterator.next_item()
                    token, new_spaces = skip_white_spaces(token, tokenIterator)

                tokenIterator.set_id(save_id - 1)
                token = tokenIterator.next_item()
                if token[1] not in ['new_line']:
                    print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                                token[0][1]['symbol']))
                    input()
                    exit(1)

                token = skip_new_line(token, tokenIterator)
            else:
                tokenIterator.set_id(save_id)
            while True:
                last_item = spacing.pop()
                if last_item[1] == 'if':
                    break
            return statement, tokenIterator.get_current_id()
        elif token[1] == 'while':
            spacing.append((spaces, 'while'))
            statement['kind'] = 'Statement'
            statement['type'] = 'While loop'

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]

            statement['condition'], id = parse_conditional_exp(tokens, tokenIterator.get_current_id() - 1)

            tokenIterator.set_id(id)

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]

            if token[1] not in ['colon']:
                print("\nExpected ':'\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                       token[0][1]['symbol']))
                input()
                exit(1)

            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]

            if token[1] not in ['new_line']:
                print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                            token[0][1]['symbol']))
                input()
                exit(1)

            token = tokenIterator.next_item()
            token, current_spaces = skip_white_spaces(token, tokenIterator)
            last_item = spacing.pop()

            if current_spaces <= last_item[0]:
                print("\nUnidentified nesting\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                               token[0][1]['symbol']))
                input()
                exit(1)
            else:
                spacing.append(last_item)
            statement_counter = 1
            statement['statement' + str(statement_counter)], id = parse_statement(tokens,
                                                                                  tokenIterator.get_current_id() - current_spaces - 1)
            tokenIterator.set_id(id)
            token = tokenIterator.next_item()

            token, new_spaces = skip_white_spaces(token, tokenIterator)
            save_id = id

            while new_spaces == current_spaces:
                statement_counter += 1
                statement['statement' + str(statement_counter)], id = parse_statement(tokens,
                                                                                      tokenIterator.get_current_id() - current_spaces - 1)
                tokenIterator.set_id(id)
                save_id = id
                token = tokenIterator.next_item()
                token, new_spaces = skip_white_spaces(token, tokenIterator)

            tokenIterator.set_id(save_id - 1)
            token = tokenIterator.next_item()
            if token[1] not in ['new_line']:
                print("\nExpected new line\nLine: {}, Character: {}".format(token[0][1]['line'],
                                                                            token[0][1]['symbol']))
                input()
                exit(1)

            token = skip_new_line(token, tokenIterator)
            save_id = tokenIterator.get_current_id()

            while True:
                last_item = spacing.pop()
                if last_item[1] == 'while':
                    break

            return statement, tokenIterator.get_current_id() - 1

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
        token = skip_white_spaces(token, tokenIterator)[0]
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
        token = skip_white_spaces(token, tokenIterator)[0]

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
        token, save_id = skip_white_spaces(token, tokenIterator)

        next_item = token[1]
        args = 0
        while next_item != 'closed_parentheses':
            args += 1
            if next_item == 'identifier':
                func['arg' + str(args)] = token[0][0].decode(coding)
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            next_item = token[1]
            if next_item == 'coma':
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]
                next_item = token[1]
            elif next_item == 'closed_parentheses':
                break
            else:
                print(
                    "\nError after open parentheses must be closed parentheses and arguments must be separeted by coma\nLine: {}, Character: {}".format(
                        token[0][1]['line'], token[0][1]['symbol']))
                input()
                exit(1)

        if not token:
            print("\nUnexpected EOF")
            input()
            exit(1)

        if token[1] != 'closed_parentheses':
            print(
                "\nError after open parentheses must be closed parentheses and arguments must be separeted by coma\nLine: {}, Character: {}".format(
                    token[0][1]['line'], token[0][1]['symbol']))
            input()
            exit(1)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

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
        token = skip_white_spaces(token, tokenIterator)[0]

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
        statement, id = parse_statement(tokens, tokenIterator.get_current_id() - 1)
        func['kind'] = 'Function Declaration'
        func['name'] = name
        func['statement' + str(statement_counter)] = statement

        tokenIterator.set_id(id - 1)
        token = tokenIterator.next_item()
        token = skip_new_line(token, tokenIterator)
        save_id = tokenIterator.get_current_id()
        token = skip_white_spaces_new_line(token, tokenIterator)
        next_item = token[1]
        while next_item in ['identifier', 'return_keyword', 'if', 'while']:
            if next_item == 'identifier':
                token = tokenIterator.next_item()
                token = skip_white_spaces(token, tokenIterator)[0]
                if token[1] == 'open_parentheses':
                    return func, save_id - 1
                else:
                    tokenIterator.set_id(save_id)

            statement_counter += 1
            token = tokenIterator.next_item()
            token = skip_white_spaces(token, tokenIterator)[0]
            tokenIterator.set_id(save_id - 1)
            token = tokenIterator.next_item()
            token = skip_new_line(token, tokenIterator)
            statement, id = parse_statement(tokens, tokenIterator.get_current_id() - 1)
            func['statement' + str(statement_counter)] = statement
            tokenIterator.set_id(id)
            token = skip_new_line(token, tokenIterator)
            save_id = tokenIterator.get_current_id()
            token = skip_white_spaces_new_line(token, tokenIterator)
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
        token = skip_white_spaces(token, tokenIterator)[0]

        if token[1] != 'open_parentheses':
            print("\nExpected open parentheses at function call after identifier\nLine: {}, Character: {}".format(
                token[0][1]['line'],
                token[0][1]['symbol']))
            exit(1)

        token = tokenIterator.next_item()
        token = skip_white_spaces(token, tokenIterator)[0]

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
        func_num = 1
        program['function' + str(func_num)] = func
        tokenIterator = TokensIter(tokens, id)
        token = tokenIterator.next_item()
        token = skip_white_spaces_new_line(token, tokenIterator)
        next_item = token[1]
        while next_item == 'function_declaration':
            func_num += 1
            program['function' + str(func_num)], id = parse_function(tokens, tokenIterator.get_current_id() - 1)
            tokenIterator.set_id(id)
            token = tokenIterator.next_item()
            token = skip_white_spaces_new_line(token, tokenIterator)
            next_item = token[1]

        if token[1] != 'identifier':
            print("Expected function call\n \nLine: {}, Character: {}".format(
                token[0][1]['line'],
                token[0][1]['symbol']))
            exit(1)

        func_call, id = parse_func_call(tokens, id)
        program['call_function'] = func_call

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
code = r'''.586
.model flat, stdcall
option casemap:none

include     \masm32\include\windows.inc
include     \masm32\include\kernel32.inc
include     \masm32\include\masm32.inc
include     \masm32\include\user32.inc

includelib  \masm32\lib\kernel32.lib
includelib  \masm32\lib\masm32.lib
includelib  \masm32\lib\user32.lib

NumbToStr   PROTO :DWORD,:DWORD
{function_decl}

.data
buff        db 11 dup(?)

.code
start:
    invoke  {main_func}
    invoke  NumbToStr, eax, ADDR buff
    invoke  StdOut, eax
    invoke  ExitProcess, 0

'''

var_map = {}
counter = -0
local_counter = 0
cond = 0
cond2 = 0
labels_list = []
labels_2 = []
and_counter = 0
while_counter = 0
cond_exp = 0


def codegen(AST):
    global code, var_map, counter, cond, local_counter
    functions = []

    def code_from_ast(exp: dict):
        global code, var_map, counter, cond, cond2, labels_list, and_counter, while_counter, cond_exp

        if exp['kind'] == 'Constant':
            code = code + '    mov eax, {}\n    push eax\n'.format(exp['value'])

        if exp['kind'] == 'Variable':
            if exp['name'] not in var_map.keys():
                print('Variable "{}" is not defined!'.format(exp['name']))
                input()
                exit(1)
            code = code + '    mov eax, [ebp {:+d}]\n    push eax\n'.format(var_map[exp['name']])

        if exp['kind'] == 'Statement':
            if exp['type'] == "Return":
                code_from_ast(exp['exp'])
                code = code + '    pop eax\n'
            elif exp['type'] == "Assignment":
                if exp['var'] not in var_map.keys():
                    code_from_ast(exp['value'])
                    if counter > 0:
                        counter += 4
                    else:
                        counter -= 4
                    code = code + '    pop eax\n    sub esp, 4\n    mov [ebp {:+d}], eax\n'.format(counter)
                    var_map[exp['var']] = counter
                else:
                    code_from_ast(exp['value'])
                    code = code + '    pop eax\n    mov [ebp {:+d}], eax\n'.format(var_map[exp['var']])
            elif exp['type'] == 'R_shift + Assignment':
                if exp['var'] not in var_map.keys():
                    print("Error variable {} is not defined before editing\n".format(exp['var']))
                    input()
                    exit(1)
                else:
                    code_from_ast(exp['value']['factor'])
                    code = code + '    pop ebx\n    mov eax, [ebp {:+d}]\n    mov cl, bl\n    sar eax, cl\n    mov [ebp {:+d}], eax\n'.format(
                        var_map[exp['var']], var_map[exp['var']])
            elif exp['type'] == 'Conditional':
                cond += 1
                cond2 += 1
                code_from_ast(exp['condition'])
                code = code + '    pop eax\n    cmp eax, 0\n    je @c{}\n'.format(cond)
                labels_list.append('c{}'.format(cond))
                labels_2.append('end{}'.format(cond2))

                for key in exp:
                    if key.startswith('statement'):
                        code_from_ast(exp[key])

                if len(labels_list) != 0:
                    end = labels_2.pop()
                    code = code + '    jmp @{}\n'.format(end)
                    labels_2.append(end)
                    code = code + '@{}:\n'.format(labels_list.pop())

                for key in exp:
                    if key.startswith('elif'):
                        cond += 1
                        code_from_ast(exp[key]['condition'])
                        code = code + '    pop eax\n    cmp eax, 0\n    je @c{}\n'.format(cond)
                        labels_list.append('c{}'.format(cond))
                        for elif_statement in exp[key]:
                            if elif_statement.startswith('statement'):
                                code_from_ast(exp[key][elif_statement])
                        end = labels_2.pop()
                        code = code + '    jmp @{}\n'.format(end)
                        labels_2.append(end)
                        code = code + '@{}:\n'.format(labels_list.pop())

                    if key == 'else':
                        for else_statement in exp[key]:
                            if else_statement.startswith('statement'):
                                code_from_ast(exp[key][else_statement])

                code = code + '@{}:\n'.format(labels_2.pop())
            elif exp['type'] == 'Break':
                code = code + '    jmp @{}\n'.format("while_end" + str(while_counter))
            elif exp['type'] == 'Continue':
                code = code + '    jmp @{}\n'.format("while_start" + str(while_counter))
            elif exp['type'] == "While loop":
                while_counter += 1
                local_while_count = while_counter
                code = code + '@{}:\n'.format("while_start" + str(local_while_count))
                code_from_ast(exp['condition'])
                code = code + '    pop eax\n    cmp eax, 0\n    je @{}\n'.format("while_end" + str(local_while_count))

                for st in exp:
                    if st.startswith('statement'):
                        code_from_ast(exp[st])
                code = code + '    jmp @{}\n'.format("while_start" + str(local_while_count))
                code = code + '@{}:\n'.format("while_end" + str(local_while_count))
        if exp['kind'] == 'Function call':
            arg_count = 0
            expected_args = 0
            for k in exp:
                if k.startswith('arg'):
                    arg_count += 1

            last = False
            for k in AST:
                if k.startswith('function'):
                    if AST[k]['name'] == exp['name']:
                        last = AST[k]

            if (not last):
                print("Error function {} is not defined\n".format(exp['name']))
                input()
                exit(1)

            for arg in last:
                if arg.startswith('arg'):
                    expected_args += 1

            if expected_args != arg_count:
                print("Unexpected args amount at function {}() call\n".format(exp['name']))
                input()
                exit(1)

            for i in range(arg_count, 0, -1):
                code_from_ast(exp['arg' + str(i)])
            code = code + '    call {}\n    push eax\n'.format(exp['name'], arg_count * 4)

        if exp['kind'] == 'Expression':
            if exp['type'] == 'Remainder':
                code_from_ast(exp['remainder1'])
                for i in range(2, exp['remainder_counter'] + 1):
                    code_from_ast(exp['remainder' + str(i)])
                    code = code + '    mov edx, 0\n    pop ebx\n    pop eax\n    div ebx\n    mov eax, edx\n    push eax\n'

            if exp['type'] == 'Comparison':
                code_from_ast(exp['comparison1'])
                for i in range(2, exp['comparison_counter'] + 1):
                    code_from_ast(exp['comparison' + str(i)])
                    code = code + '    pop ebx\n    pop eax\n    cmp eax, ebx\n'
                    if (exp['comparison' + str(i) + '_sign']) == 'equal_check':
                        code = code + '    mov eax, 0\n    sete al\n    push eax\n'
                    if (exp['comparison' + str(i) + '_sign']) == 'less':
                        code = code + '    mov eax, 0\n    setl al\n    push eax\n'
                    if (exp['comparison' + str(i) + '_sign']) == 'greater':
                        code = code + '    mov eax, 0\n    setg al\n    push eax\n'

            if exp['type'] == 'Conditional':
                cond += 1
                local_cond = cond
                code_from_ast(exp['condition'])
                code = code + '    pop eax\n    cmp eax, 0\n    je @{}\n'.format('cond_false' + str(local_cond))
                code_from_ast(exp['true_condition'])
                code = code + '    jmp @{}\n'.format('cond_end' + str(local_cond))
                code = code + '@{}:\n'.format('cond_false' + str(local_cond))
                code_from_ast(exp['false_condition'])
                code = code + '@{}:\n'.format('cond_end' + str(local_cond))
            if exp['type'] == 'Unary':
                code_from_ast(exp['factor'])
                code = code + '    pop eax\n    not eax\n    push eax\n'
            if exp['type'] == 'Non Binary':
                code_from_ast(exp['factor'])
            if exp['type'] == 'And':
                and_counter += 1
                local_and = and_counter
                for i in range(1, exp['and_counter'] + 1):
                    code_from_ast(exp['and' + str(i)])
                    code = code + '    pop eax\n    cmp eax, 0\n    je @{}\n'.format("end_and" + str(local_and))
                    if i == exp['and_counter']:
                        code = code + '    mov eax, 1\n'
                code = code + '@{}:\n    push eax\n'.format("end_and" + str(local_and))
            if exp['type'] == 'Shifting':
                code_from_ast(exp['r_shift1'])
                for i in range(2, exp['shift_counter'] + 1):
                    code_from_ast(exp['r_shift' + str(i)])
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
                        code_from_ast(exp['substraction' + str(i)])
                        code = code + '    pop ebx\n    pop eax\n    sub eax, ebx\n    push eax\n'
        if exp['kind'] == 'Exp in brackets':
            code_from_ast(exp['exp'])

    for func_call_search in AST:
        if func_call_search.startswith('call'):
            func = 0
            cond = 0
            for k1 in AST:
                if k1.startswith('function') and AST[func_call_search]['name'] == AST[k1]['name']:
                    func += 1
                    functions.append(AST[k1]['name'])
                    main_name = AST[k1]['name']
                    code = code + AST[k1]['name'] + " PROC\n    push ebp\n    mov ebp, esp\n"
                    for k2 in AST[k1]:
                        if k2.startswith('statement'):
                            code_from_ast(AST[k1][k2])
                    code = code + "    add esp, {}\n    pop ebp\n    ret\n{} ENDP\n\n".format(abs(counter),
                                                                                              AST[k1]['name'])
                elif k1.startswith('function'):
                    func_name = AST[k1]['name']
                    for check_if_last in AST:
                        if check_if_last.startswith('function') and AST[check_if_last]['name'] == func_name:
                            last = check_if_last.replace('function', '')
                    if k1.replace('function', '') == last:
                        arg_count = 0
                        for k in AST[k1]:
                            if k.startswith('arg'):
                                arg_count += 1
                        save_count = counter
                        save_vars = var_map
                        var_map = {}
                        counter = -0
                        functions.append(AST[k1]['name'])
                        code = code + AST[k1]['name'] + " PROC\n    push ebp\n    mov ebp, esp\n"
                        for k2 in AST[k1]:
                            if k2.startswith('statement'):
                                code_from_ast(AST[k1][k2])
                            if k2.startswith('arg'):
                                local_counter += 4
                                var_map[AST[k1][k2]] = local_counter + 4
                        code = code + "    add esp, {}\n    pop ebp\n    ret {}\n".format(abs(counter), local_counter)
                        code = code + "{} ENDP\n\n".format(AST[k1]['name'])
                        counter = save_count
                        var_map = save_vars
                        local_counter = 0
            if func != 1:
                print('\n Function declaration not found')
                input()
                exit(1)
    code = code + """NumbToStr PROC uses ebx x:DWORD,buffer:DWORD
    mov     ecx,buffer
    mov     eax,x
    mov     ebx,10
    add     ecx,ebx
@@:
    xor     edx,edx
    div     ebx
    add     edx,48
    mov     BYTE PTR [ecx],dl
    dec     ecx
    test    eax,eax
    jnz     @b
    inc     ecx
    mov     eax,ecx
    ret
NumbToStr ENDP

END start"""
    code = code.replace('\n    push eax\n    pop eax', '')
    code = code.replace('\n    push ebx\n    pop ebx', '')
    code = code.replace('{function_decl}', '\n'.join(list(map(lambda x: x + '   PROTO STDCALL', functions))))
    code = code.replace('{main_func}', main_name)
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

    with open('6-14-Python-ІВ-81-Зубець.asm', 'w') as f:
        f.write(code)

    print("\nEnter anything to exit")
    input()


if __name__ == "__main__":
    main(sys.argv[1:])
