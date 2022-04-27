from decouple import config
from auth_utils import AuthJwt
from typing import Union
import motor.motor_asyncio
import asyncio

auth = AuthJwt()


async def mongo_init():
    MONGO_URI = config('MONGO_URI')
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    database = client.mail_auth
    collection_account = database.account
    collection_tmp_account = database.tmp_account
    return collection_account, collection_tmp_account


def account_serializer(data: dict) -> dict:
    data["id"] = str(data["_id"])
    del data["_id"]
    return data


async def db_get_account(username: str) -> Union[dict, None]:
    collection_account, _ = await mongo_init()
    print('start: db_get_account')
    data = await collection_account.find_one({'username': username})
    print('data :', data)
    print('end: db_get_account')
    if data:
        return account_serializer(data)
    else:
        return None


async def db_get_tmp_account(username: str) -> Union[dict, None]:
    _, collection_tmp_account = await mongo_init()
    data = await collection_tmp_account.find_one({'username': username})
    if data:
        return account_serializer(data)
    else:
        return None


async def db_create_account(data: dict) -> bool:
    collection_account, _ = await mongo_init()
    print('start: db_create_account')
    await collection_account.insert_one(data)
    print('end: db_create_account')


async def db_create_tmp_account(data: dict) -> bool:
    _, collection_tmp_account = await mongo_init()
    await collection_tmp_account.insert_one(data)


async def db_delete_tmp_account(username: str) -> bool:
    _, collection_tmp_account = await mongo_init()
    account = await collection_tmp_account.find_one({'username': username})
    if account:
        delete_account = await collection_tmp_account.delete_one({'username': username})

        # 削除したアカウントの個数が格納されているのでそれを使って削除したかどうかをboolで返却
        if delete_account.deleted_count > 0:
            return True

    return False
