from pymongo import MongoClient
from loginMenu import LoginMenu
from storeMenu import StoreMenu
from adminMenu import AdminMenu
import os

client = MongoClient()
db = client.get_database("store")
while(True):
    os.system('cls')
    login = LoginMenu(db)
    user = login.welcome()
    if(user == -1): exit()

    if(user['admin'] == True):
        admin = AdminMenu(user, db)
        admin.menu()
    else:
        store = StoreMenu(user, db)
        store.open()





