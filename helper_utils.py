import hashlib
from importlib import import_module

#function to return needed string in hash
def get_needed_hash_substring(num_of_consecutive_zeros):
    needed_str = ""

    for i in range(num_of_consecutive_zeros):
        needed_str += "0"

    return needed_str

#function to calculate hash
def get_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

#function to write to file
def write_to_file(content, file):
    print(content, file=file)
    file.flush()

#function to get module function
def get_module_fn(module, function):
    mod = import_module(module)
    return getattr(mod, function)