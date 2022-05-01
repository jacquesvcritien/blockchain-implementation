import json
from protocol import Protocol
from state import State
from chain import Chain
from importlib import import_module
from helper_utils import get_module_fn
import config as config

port = 3012
chain = Chain()
state = State(port, chain)
protocol = Protocol(state)

msg=protocol.get_block_count()
print(msg)
print(config.PAYLOAD_ENCODING)


Database = get_module_fn("models.account.db_model2", "Database")

db = Database()
print(db.get_balance("0"))

db.increase_balance("0x1")
db.increase_balance("0x1")
print(db.get_balance("0x1"))
db.increase_balance("0x2")
db.increase_balance("0x1")
print(db.get_balance("0x1"))
db.decrease_balance("0x1")
print(db.get_balance("0x1"))
# db.increase_balance("0x1")
# db.increase_balance("0x2")
# db.increase_balance("0x2")
# db.increase_balance("0x3")
# db.decrease_balance("0x2")
# db.decrease_balance("0x3")

# print(db.database)