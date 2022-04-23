import time
import json
from helper_utils import get_needed_hash_substring
from helper_utils import get_hash
from hashedContent import HashedContent 
from datetime import datetime

NEEDED_ZEROS = 5

class Block:
    def __init__(self, prev_hash):
        self.hashed_content = HashedContent(prev_hash)
        self.hash = {}

    #function to increase nonce
    def increase_nonce(self):
        self.hashed_content.nonce += 1

    #function to calculate hash of block
    def calculate_hash(self):

        #set date
        self.hashed_content.timestamp = datetime.now()

        #get content
        content = self.hashed_content.get_content()
        payload = json.dumps(content)

        #hash the payload
        content_hash = get_hash(payload)

        #start timer
        start_time = time.time()

        #needed hash substring not in content hash
        while(not content_hash.startswith(get_needed_hash_substring(NEEDED_ZEROS))):
            #increase nonce
            self.increase_nonce()

            #get content again
            payload = json.dumps(content)
            content = self.hashed_content.get_content()

            #rehash and test again
            content_hash = get_hash(payload)
            # print("Nonce", self.hashed_content.nonce)
            # print("Generated hash", content_hash)

        print("Found hash", content_hash)
        print("--- %s seconds ---" % (time.time() - start_time))
        self.hash = content_hash
