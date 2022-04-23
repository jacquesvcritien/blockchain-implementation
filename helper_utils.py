import hashlib

#function to return needed string in hash
def get_needed_hash_substring(num_of_consecutive_zeros):
    needed_str = ""

    for i in range(num_of_consecutive_zeros):
        needed_str += "0"

    return needed_str

#function to calculate hash
def get_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()