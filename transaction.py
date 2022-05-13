import hashlib
import json
import ecdsa
import config as config
import base64
from txHashedContent import TxHashedContent 

class Transaction:
    def __init__(self, from_user, to_user):
        self.hashed_content = TxHashedContent(from_user, to_user)
        self.hash = ""

    @classmethod
    def load(cls, hashed_content, hash):
        #init tx
        new_tx = cls(hashed_content.signed_content.from_ac, hashed_content.signed_content.to_ac)
        #fill hashed content signature
        new_tx.hashed_content.signature = hashed_content.signature
        #fill hash
        new_tx.hash = hash

        return new_tx

    #function to calculate hash
    def calculate_hash_sign(self, wallet):

        #stringify signed content of tx
        payload = json.dumps(self.hashed_content.signed_content.get_signed_content())

        # #hash the payload
        # content_hash = hashlib.sha256(payload.encode(config.BYTE_ENCODING_TYPE)).hexdigest()
        
        #get signing key
        priv_key = bytes.fromhex(wallet.private_key)
        sk = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1)

        #add signature to content
        self.hashed_content.signature = sk.sign(payload.encode(config.BYTE_ENCODING_TYPE)).hex()
        #get hashed content
        tx = self.hashed_content.get_hashed_content()
        
        #set to json string
        payload = json.dumps(tx)
        #hash the payload
        self.hash = hashlib.sha256(payload.encode(config.BYTE_ENCODING_TYPE)).hexdigest()
        # print("TX hash", self.hash)
        
    def verify(self):

        #verify tx hash to make sure signature did not change
        tx_hash = self.hash

        #get hashed content
        tx = self.hashed_content.get_hashed_content()

        #calculate hash
        tx_payload = json.dumps(tx)
        hash_to_verify = hashlib.sha256(tx_payload.encode(config.BYTE_ENCODING_TYPE)).hexdigest()
        
        #ensure hash matches content
        if(tx_hash != hash_to_verify):
            print("TX Hash does not match with content")
            return

        #load verifying key
        #if sender is 0, load private key of receiver, otherwise of sender
        sender = self.hashed_content.signed_content.from_ac
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(sender), curve=ecdsa.SECP256k1) if sender != "0" else ecdsa.VerifyingKey.from_string(bytes.fromhex(self.hashed_content.signed_content.to_ac), curve=ecdsa.SECP256k1)
       
        try: 
            #get signed content as json string
            content_json = json.dumps(self.hashed_content.signed_content.get_signed_content())

            #verify with signature       
            vk.verify(bytes.fromhex(self.hashed_content.signature), content_json.encode("utf-8"))
        except:
            #ensure signature is verified
            print("TX's signature cannot be verified")
            return False
        
        # print("Block verified successful") 
        return True

    #returns a json representation
    def to_json(self):
        return {
            "hash": self.hash,
            "hashedContent": self.hashed_content.get_hashed_content()
        }

