import hashlib
import json
import ecdsa
import config as config
import base64
from txHashedContent import TxHashedContent 

class Transaction:
    def __init__(self, from_user, to_user, spent_tx=None):
        """
        Class initialiser

        :param from_user: the transaction's sender
        :param to_user: the transaction's receiver
        :param spent_tx: if a spent transaction for PoT
        """
        self.hashed_content = TxHashedContent(from_user, to_user, spent_tx)
        self.hash = ""

    @classmethod
    def load(cls, hashed_content, hash):
        """
        Function to load a transaction

        :param hashed_content: hashed content to add
        :param hash: hashed block hash
        """
        #init tx
        spent_tx = None if config.DB_MODEL == "account" else hashed_content.signed_content.spent_tx
        new_tx = cls(hashed_content.signed_content.from_ac, hashed_content.signed_content.to_ac, spent_tx)
        #fill hashed content signature
        new_tx.hashed_content.signature = hashed_content.signature
        #fill hash
        new_tx.hash = hash

        return new_tx

    def calculate_hash_sign(self, wallet):
        """
        Function to calculate the hash of a payload

        :param wallet: wallet to sign with
        """

        #stringify signed content of tx
        payload = json.dumps(self.hashed_content.signed_content.get_signed_content())

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
        
    def verify(self):
        """
        Function to verify a transaction

        :return: if successful
        """

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
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(sender), curve=ecdsa.SECP256k1) if sender != config.MINING_SENDER else ecdsa.VerifyingKey.from_string(bytes.fromhex(self.hashed_content.signed_content.to_ac), curve=ecdsa.SECP256k1)
       
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

    def to_json(self):
        """
        Function to convert transaction to json

        :return: json representation of transaction
        """

        return {
            "hash": self.hash,
            "hashedContent": self.hashed_content.get_hashed_content()
        }

