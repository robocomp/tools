PYTHON_TYPES = {'bool', 'float', 'int', 'long', 'str', 'double', 'byte'}

def full_type_string(type, module):
    if type in PYTHON_TYPES: return type
    elif type == 'byte':     return 'bytes'
    elif type == 'string':   return 'str'
    else:                    return f'{module}.{type}'

def number_duplicates(list, matcher=lambda x: x):
    indices = {}

    for element in list:
        key = matcher(element)
        index = indices.get(key, 0)
        indices[key] = index+1
        yield element, str(index) if index else ''
