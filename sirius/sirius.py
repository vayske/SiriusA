import glob
import os
from creart import create
from graia.saya import Saya
from graia.ariadne.connection.config import config
from graia.ariadne.app import Ariadne
from loguru import logger
from utils.credentials import get_credential

# setup logger
logger.add("../logs/sirius-{time:YYYY-MM-DD}.log", rotation="00:00", encoding="utf-8")
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# get mirai config
account = int(get_credential("QQ_ACCOUNT"))
verify_key = get_credential("MIRAI_KEY")

# setup Ariadne
saya = create(Saya)
app = Ariadne(
    connection=config(
        account=account,
        verify_key=verify_key,
    ),
)

# load modules
with saya.module_context():
    modules = glob.glob("modules/*", recursive=True)
    for module in modules:
        module = module.split('.', 1)[0].replace('/', '.')
        saya.require(f'{module}')

# run Ariadne
app.launch_blocking()
