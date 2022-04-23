from os.path import exists
import ecdsa
import base64

class Wallet:
    def __init__(self, username):
        self.user_initials = username
        #check if wallet already exists for port
        filename = "wallets/"+username.lower()+"_wallet.txt"
        file_exists = exists(filename)

        #if file exists, read public and private key, otherwise create them
        if(file_exists):
            #open fike
            with open(filename) as f:
                lines = f.read().split('\n', 1)
                self.private_key = lines[0].split("Private key: ")[1]
                self.public_key = lines[1].split("Wallet address / Public key: ")[1]
        else:
            #generate private key
            sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
            self.private_key = sk.to_string().hex()

            #get public key
            self.public_key = sk.get_verifying_key().to_string().hex() #this is your verification key (public key)
            #encoding of public key
            # self.public_key = base64.b64encode(bytes.fromhex(self.public_key))

            with open(filename, "w") as f:
                # f.write("Private key: {0}\nWallet address / Public key: {1}".format(self.private_key, self.public_key.decode()))
                f.write("Private key: {0}\nWallet address / Public key: {1}".format(self.private_key, self.public_key))

        print("Logged in with", str(self.public_key))

    def get_public_key(self):
        return self.public_key