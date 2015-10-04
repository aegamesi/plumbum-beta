# Plumbum Beta
EXPRESSION_CONSTANT = 'const' # A number - num
EXPRESSION_NAME = 'name' # A name - 'name'
EXPRESSION_GROUP = 'group' # A group of expressions added together. Highest precendence - [expressions]
EXPRESSION_FUNC = 'func' # A function call - (name, [args])
EXPRESSION_POWER = 'power' # Raising an expression to an exponent - (base, exponent)
EXPRESSION_MUL = 'mul' # a list of expressions multiplied together - [expressions]
EXPRESSION_DIV = 'div' # one expression divided by another - (num, div)

def parse(string):
	"""Parses a string, returns an expression"""

	# Tokenize
	TOKEN_NONE = 0
	TOKEN_NUMBER = 1
	TOKEN_OPERATOR = 2
	TOKEN_NAME = 3
	TOKEN_GROUP = 4
	operators = ['+', '-', '*', '/', '^']
	whitespace = [' ', ""]

	tokens = []
	i = 0
	while i < len(string):
		char = string[i]

		if char.isspace():
			i += 1
			continue

		# Grouping Symbols
		if char == '(':
			tokens.append((TOKEN_GROUP, 0))
			i += 1
			continue
		if char == ')':
			tokens.append((TOKEN_GROUP, 1))
			i += 1
			continue

		# Operators
		if char in operators:
			tokens.append((TOKEN_OPERATOR, char))
			i += 1
			continue

		# Name
		if char.isalpha():
			name = char
			i += 1
			while i < len(string):
				char = string[i]
				if not char.isalnum():
					break
				name += char
				i += 1

			tokens.append((TOKEN_NAME, name))
			continue

		# Number
		# TODO support all floats, not just ints
		if char.isdigit():
			num = int(char)
			i += 1
			while i < len(string):
				char = string[i]
				if not char.isdigit():
					break
				num *= 10
				num += int(char)
				
				i += 1

			tokens.append((TOKEN_NUMBER, num))
			continue
	# Tokenization complete
	
	# Build tokens into a tree of expressions
	# P/E/MD/AS
	def pop():
		return tokens.pop()
	def peek():
		return tokens[-1]

	def read_unit():
		"""
		Reads a single unit... a constant, or a name, or a group
		"""
		peeked = peek()
		if peeked[0] == TOKEN_GROUP:
			return read_chunk()
		if peeked[0] == TOKEN_NUMBER:
			return (EXPRESSION_CONSTANT, pop()[1])
		if peeked[0] == TOKEN_NAME:
			return (EXPRESSION_NAME, pop()[1])

		raise Exception("Invalid unit")

	def read_chunk():
		"""
		If the token list begins with an open group, read a group...
		otherwise, read a term.

		Reads a single 'group' -- if it starts with an open group, go until the last closed group
		A "term" is a set of expressions multiplied (or divided, or exponented) together
		A "group" is a set of terms added (or subtracted...) together
		"""
		peeked = peek()
		is_group = peeked[0] == TOKEN_GROUP
		if is_group:
			assert peeked[1] == 0, "Unexpected close paren while parsing group"

			pop() # get rid of the opening paren

			# keep reading more chunks until we get a close paren
			group = []
			while len(tokens):
				token = peek()
				if token[0] == TOKEN_GROUP and token[1] == 1:
					pop()
					break
				if token[0] == TOKEN_OPERATOR and (token[1] == '+' or token[1] == '-'):
					pop()
					chunk = read_chunk()
					# TODO if it's '-', multiply the chunk by -1
					if token[1] == '-':
						chunk = (EXPRESSION_MUL, [(EXPRESSION_CONSTANT, -1), chunk])
					group.append(chunk)
					continue

				group.append(read_chunk())

			if len(group) == 1:
				return group[0]
			return (EXPRESSION_GROUP, group)

		else:
			chunk = [] # a set of things multiplied together
			negative = False
			if peeked[0] == TOKEN_OPERATOR and peeked[0] == '-':
				negative = True
				pop()
			
			while len(tokens):
				peeked = peek()

				if peeked[0] == TOKEN_GROUP:
					if peeked[1] == 0:
						chunk.append(read_chunk())
						continue
					if peeked[1] == 1:
						break

				if peeked[0] == TOKEN_OPERATOR:
					# stop if it's an addition or subtraction operator
					if peeked[1] == '+' or peeked[1] == '-':
						break

					if peeked[1] == '^':
						pop()
						assert len(chunk) > 0, "Unexpected '^' when parsing expression"
						assert len(tokens) > 0, "Unexpected '^' when parsing expression"
						base = chunk.pop()
						exp = read_unit()
						chunk.append((EXPRESSION_POWER, (base, exp)))
						continue

					if peeked[1] == '/':
						pop()
						assert len(chunk) > 0, "Unexpected '/' when parsing expression"
						assert len(tokens) > 0, "Unexpected '/' when parsing expression"
						numerator = chunk.pop()
						denomenator = read_unit()
						chunk.append((EXPRESSION_DIV, (numerator, denomenator)))
						continue

					if peeked[1] == '*':
						pop()
						assert len(chunk) > 0, "Unexpected '*' when parsing expression"
						assert len(tokens) > 0, "Unexpected '*' when parsing expression"
						chunk.append(read_unit())
						continue

					# TODO function call

				unit = read_unit()
				if unit[0] == EXPRESSION_NAME:
					# see if it's actually a function call
					if len(tokens):
						peeked = peek()
						if peeked[0] == TOKEN_GROUP and peeked[1] == 0:
							# it is.
							argument = read_chunk()
							chunk.append((EXPRESSION_FUNC, (unit, argument)))
							continue

				chunk.append(unit)

			if len(chunk) == 1:
				return chunk[0]
			return (EXPRESSION_MUL, chunk)
		

	# add an opening and closing paren, and reverse tokens
	tokens.insert(0, (TOKEN_GROUP, 0))
	tokens.append((TOKEN_GROUP, 1))
	tokens.reverse() # so that we can .pop() off tokens
	expressions = []
	return read_chunk()