from itertools import chain
from symengine.printing import ccode
from .strings import count_up

def codelines(expressions):
	for expression in expressions:
		try:
			codeline = ccode(expression)
		except RuntimeError as error:
			if "Not supported" not in str(error):
				raise
			else:
				raise NotImplementedError(
						"Cannot convert the following expression to C Code:\n"
						+ str(expression)
						)
		yield codeline + ";\n"

def render_declarator(name, _type, size=0):
	return _type + " " + name + ("[%i]"%size if size else "")

def write_in_chunks(lines, mainfile, deffile, name, chunk_size, arguments):
	funcname = "definitions_" + name
	
	first_chunk = []
	try:
		for _ in range(chunk_size+1):
			first_chunk.append(next(lines))
	except StopIteration:
		for line in first_chunk:
			mainfile.write(line)
	else:
		lines = chain(first_chunk, lines)
		
		while True:
			mainfile.write(funcname + "(")
			deffile.write("void " + funcname + "(")
			if arguments:
				mainfile.write(", ".join(argument[0] for argument in arguments))
				deffile.write(", ".join(render_declarator(*argument) for argument in arguments))
			else:
				deffile.write("void")
			mainfile.write(");\n")
			deffile.write("){\n")
			
			try:
				for _ in range(chunk_size):
					deffile.write(next(lines))
			except StopIteration:
				break
			finally:
				deffile.write("}\n")
			
			funcname = count_up(funcname)

