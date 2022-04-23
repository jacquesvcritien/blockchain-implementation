import hashlib
import json
import ecdsa
import base64

class Transaction:
    def __init__(self, from_user, to_user):
        self.content = {
            "from" : from_user,
            "to" : to_user
        }
        self.hash = ""
        self.signature = ""

    #function to calculate hash
    def calculate_hash_sign(self, wallet):

        #set to json string
        payload = json.dumps(self.content)

        # #hash the payload
        # content_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        #get signing key
        priv_key = bytes.fromhex(wallet.private_key)
        sk = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1)

        #add sender
        self.sender = wallet.public_key

        #add signature to content
        self.signature = sk.sign(payload.encode('utf-8')).hex()
        tx = {
            "signature": self.signature,
            "content":  payload,
            "sender": self.sender
        }
        
        #set to json string
        payload = json.dumps(tx)
        #hash the payload
        self.hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        print("TX hash", self.hash)
        
    def verify_tx(self):

        #verify tx hash to make sure signature did not change
        tx_hash = self.hash

        tx = {
            "signature": self.signature,
            "content":  json.dumps(self.content),
            "sender": self.sender
        }

        #calculate hash
        tx_payload = json.dumps(tx)
        hash_to_verify = hashlib.sha256(tx_payload.encode('utf-8')).hexdigest()
        
        #ensure hash matches content
        if(tx_hash != hash_to_verify):
            print("TX Hash does not match with content")
            return

        #load verifying key
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.sender), curve=ecdsa.SECP256k1)
       
        try: 
            #get content as json string
            content_json = json.dumps(self.content)

            #verify with signature       
            vk.verify(bytes.fromhex(self.signature), content_json.encode("utf-8"))
        except:
            #ensure signature is verified
            print("TX's signature cannot be verified")
            return
        
        print("TX verified successful")

    #returns a json representation
    def to_json(self):
        return {
            "signature": self.signature,
            "content":  self.content,
            "sender": self.sender,
            "hash": self.hash
        }

