import re

from django.forms import ValidationError

TYPES = {
    "integer": "int",
    "double": "float",
    "float": "float",
    "boolean": "bool",
    "character": "str",
    "string": "str",
}

CONVERTIBLES = [
    ("\t", ""),
    ("”", '"'),
    ("MOD", "%"),
    ("CASE", "case"),
    ("FALSE", "False"),
    ("TRUE", "True"),
    ("false", "False"),
    ("true", "True"),
    ("ELSE IF", "ELIF"),
    ("ELSEIF", "ELIF"),
    ("ELSIF", "ELIF"),
    ("END WHILE", "ENDWHILE"),
    ("END IF", "ENDIF"),
    ("THEN", ""),
    ("RANDOM", "random"),
    ("AND", "and"),
    ("OR", "or"),
    ("NOT", "not"),
]


re_flags = re.VERBOSE
re_remainder = re.compile(""" \s* ( \w+ )(?: \s* \[ \s* \] )? \s* """, re_flags)
re_first_construct = re.compile(
    """
	    DECLARE                    # Start of DECLARE statement
	\s* ( \w+ )                             # Type
	\s+ ( \w+ )(?: \s* \[ \s* \] )?         # Variable name
	\s* """,
    re_flags,
)


def preprocess(user_input: str) -> list:  # sourcery skip: raise-specific-error
    pseudo_no_empty_strings = list(filter(None, user_input.splitlines()))
    var_types: dict = {}
    preprocessed_pseudocode = []

    for codeline, line in enumerate(pseudo_no_empty_strings, start=1):

        line = re.sub("\s*[;:]\s*$", "", line)

        if line.startswith("DECLARE"):
            first_word, *args = line.split(",")
            var_type, first_var = re_first_construct.match(first_word).groups()
            extra_vars = list(map(lambda x: re_remainder.match(x).groups()[0], args))

            for var_name in [first_var] + extra_vars:
                if var_type.lower() not in TYPES.keys():
                    raise ValidationError(
                        f"Line {codeline}: Unknown variable type '{var_type}'",
                        f"Expected variable type in: {list(TYPES.keys())}"
                    )
                var_types[var_name] = TYPES[var_type.lower()]

        for old, new in CONVERTIBLES:
            line = line.replace(old, new)

        preprocessed_pseudocode.append(line)

    return preprocessed_pseudocode


def converted(preprocessed_pseudo:list) -> list:

    output = ""
    while_level = 0
    if_level = 0
    converted_psuedocode = []

    for codeline, line in enumerate(preprocessed_pseudo, start=1):
        indent_level = while_level + if_level

        if (
            line.startswith("DECLARE")
            or line.startswith("PROGRAM")
            or line.startswith("START")
            or line.startswith("BEGIN")
        ):
            output = ""
        elif line.startswith("DISPLAY"):

            line = re.sub("DISPLAY ?", "print(", line).strip() + ")"
            line = re.sub('("[^"]*?")\s*\+\s*', "\\1, ", line)  # removes "+"
            output = re.sub('\s*\+\s*("[^"]*?")', ", \\1", line)
        elif line.startswith("SET"):
            output = line.replace("SET", "").strip()
        elif line.startswith("WHILE"):
            while_level += 1
            output = line.replace("WHILE", "while").strip() + ":"
        elif line.startswith("IF"):
            if_level += 1
            output = line.replace("IF", "if").strip() + ":"
        elif line.startswith("ENDIF"):
            if if_level == 0:
                raise IndentationError(f"line {codeline}: no IF block for ENDIF.")
            if_level -= 1
            output = ""
        elif line.startswith("ENDWHILE"):
            if while_level == 0:
                raise IndentationError(f"line {codeline}: no WHILE block for ENDWHILE.")
            output = ""
            while_level -= 1
        elif line.startswith("ELSE"):
            if if_level == 0:
                raise IndentationError(f"line {codeline}: no IF block for ELSE.")
            output = "else:"
            indent_level -= 1
        elif line.startswith("ELIF"):
            if if_level == 0:
                raise IndentationError(f"line {codeline}: no IF block for ELSEIF.")
            output = line.replace("ELIF", "elif").strip() + ":"
            indent_level -= 1
        else:
            raise ValidationError(f'Error: line {codeline}: Cannot figure out: "{line.strip()}"')

        indentation = indent_level * "    "

        if not isinstance(output, list):
            output = [output]

        converted_psuedocode.extend(
            indentation + python_line for python_line in output if python_line != ""
        )
    return converted_psuedocode


def pseudocode_converter(user_input: str) -> list:

    """Return a list of converted Pseudocode in Python"""
    preprocessed = preprocess(user_input)
    return converted(preprocessed)
