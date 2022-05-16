
from pymongo import MongoClient
from sample_config import Config


class Database:
    def __init__(self, uri, database_name):
        self._client = MongoClient(Config.DB_URI)
        self.db = self._client[database_name]
        self.rename = self.db.Rename

    def new_user(self, id, name, fileid, document, update):
        return dict(
            id=id,
            name=name,
            file_id=fileid,
            doc=document,
            update=update,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    async def add_user(self, id, name):
        if self.rename.find_one({'id': int(id)}):
            self.rename.delete_one({'id': int(id)})

        user = self.new_user(id, name, None, True, True)
        self.rename.insert_one(user)

    async def is_user_exist(self, id):
        user = self.rename.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = self.rename.count_documents({})
        return count

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        self.rename.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        self.rename.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = self.rename.find_one({'id': int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_user_by_id(self, id):
        try:
            user = self.rename.find_one({'id': int(id)})

            if not user:
                return True, True
            else:
                return user['doc'], user['update']
        except:
            return True, True

    async def get_all_users(self):
        try:
            users = list(self.rename.find({}))
            return users
        finally:
            pass

    async def delete_user(self, user_id):
        self.rename.delete_many({'id': int(user_id)})

    async def get_banned(self):
        b_users = []
        users = self.rename.find_one({'ban_status.is_banned': True})
        if users:
            b_users = [user['id'] async for user in users]
        return b_users

    async def update_thumb(self, user_id, name, file_id) -> bool:
        try:
            user = self.rename.find_one({'id': int(user_id)})

            if not user:
                user = self.new_user(int(user_id), name, '', True, True)
                self.rename.insert_one(user)

            self.rename.update_one({'id': user_id}, {'$set': {'file_id': file_id}})
            return True
        except:
            return False

    async def get_thumb(self, user_id):
        try:
            user = self.rename.find_one({'id': int(user_id)})

            if not user:
                return None
            else:
                return user['file_id']
        except:
            return None

    async def update_all(self, new_field, value):
        try:
            self.rename.update_many({}, {'$set': {f'{new_field}': value}}, upsert=False, array_filters=None)
            return True
        except Exception as e:
            return False

    async def update_by_id(self, user_id, new_field, value):
        try:
            self.rename.update_one({'id': int(user_id)}, {'$set': {f'{new_field}': value}})
            return True
        except Exception as e:
            return False


rename_db = Database(Config.DB_URI, 'UFSBOTZ')
