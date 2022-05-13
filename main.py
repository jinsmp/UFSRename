import os

from bot import Bot

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

if __name__ == "__main__":
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)

    Bot().run()
