import os
import re
from collections import defaultdict

id_pattern = re.compile(r'^.\d+$')


class Config(object):

    # get a token from @BotFather
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "5387610840:AAGnG35LWjjfHjkR9SV6PWRgi3hESdM56SE")

    # The Telegram API things
    APP_ID = int(os.environ.get("APP_ID", 6452078))
    API_HASH = os.environ.get("API_HASH", 'a0dd41063f741506b67fe85704fcb81c')
    # Get these values from my.telegram.org

    # Array to store users who are authorized to use the bot
    # AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "").split())
    ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMINS', '631110062 1636552877 1535083157').split()]
    AUTH_USERS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('AUTH_USERS', '').split()]
    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    USER_LOG_CHANNEL = os.environ.get("LOG_CHANNEL", "-1001699085090")
    OWNER_ID = int(os.environ.get("OWNER_ID", "1636552877"))
    AUTH_USERS = (AUTH_USERS + ADMINS) if AUTH_USERS else []

    # Telegram maximum file upload size
    TG_MAX_FILE_SIZE = 2097152000

    # chunk size that should be used with requests
    CHUNK_SIZE = 128

    LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL', '-1001685776403'))

    # Database url
    DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://jmjsoft:jins2010@ufstest.nqmjo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    # Random Pictures
    PICS = (os.environ.get('PICS', 'https://telegra.ph/file/2692fbc4370a3c29c05ac.jpg https://telegra.ph/file/a9a30eda0e8d1b8b3796f.jpg https://telegra.ph/file/7007c29c4cf56b0e8602e.jpg https://telegra.ph/file/4992701e62e7e22df11cf.jpg')).split()

    # dict to control uploading and downloading
    gDict = defaultdict(lambda: [])

# temp db for banned
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT = int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    TEMP_USER = {}
    U_NAME = None
    B_NAME = None