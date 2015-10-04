# Plumbum Beta

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