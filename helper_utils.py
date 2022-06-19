import hashlib
from importlib import import_module

#function 
def get_needed_hash_substring(num_of_consecutive_zeros):
    """
    Function to return needed substring of 0s in hash

    :param num_of_consecutive_zeros: the number of consecutive 0s needed in substring

    :return: a string made up of num_of_consecutive_zeros consective 0s
    """
    needed_str = ""

    for i in range(num_of_consecutive_zeros):
        needed_str += "0"

    return needed_str

def get_hash(content):
    """
    Function to calculate hash of content 

    :param content: the number content to caluclate its hash

    :return: the digest of the content's hash
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def write_to_file(content, file):
    """
    Function to write some content to file

    :param content: the content to write to file
    :param file: file object to write to
    """
    print(content, file=file)
    file.flush()

def get_module_fn(module, function):
    """
    Function to get module function. This is used to make it easier to switch between different consensus types and storage types

    :param module: the module to use
    :param function: the function to call

    :return: The function with the passed function name from the passed module
    """
    mod = import_module(module)
    return getattr(mod, function)