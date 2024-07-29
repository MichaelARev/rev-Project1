from pymongo import MongoClient
import json
import logging
from bson.json_util import dumps
import os

class LoginMenu:
    def __init__(self, db):
        logging.basicConfig(filename="store.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')
        logging.info("Initializing Login Menu...")
        self.db = db
    
    def login(self):
        logging.info("User Login accessed...")
        while(True):
            os.system('cls')
            print("LOGIN")
            uname = input("Please enter username: ")
            uname = uname.lower()
            passw = input("Please enter password: ")
            try:
                auth = self.db.users.find_one({'username' : uname, 'password' : passw})
            except Exception as e:
                print("User Lookup Operation Failed")
                logging.error("Failed to query user for login...")
                logging.error(e)
                return -1
            if(auth): break
            else: 
                selection = input("Invalid login! Try again? [Y/N]: ")
                if(selection.upper() == 'N'): return -1
        return auth

    def signup(self):
        logging.info("User Sign-up Menu Accessed...")
        while(True):
            os.system('cls')
            print("SIGN-UP")
            uname = input("Please enter desired username: ")
            uname = uname.lower()
            try:
                exists = list(self.db.users.find({'username' : uname}))
            except Exception as e:
                logging.error("Failed to query user for sign-up...")
                logging.error(e)
                print("Username check failed!")
                continue
            if(exists): print('Username already exists!')
            else: break
        
        while(True):
            passw = input("Please enter password: ")
            pass2 = input("Please re-enter password: ")
            if(passw == pass2): break
            else: print("Passwords do not match!")
        
        fname = input("Please enter first name: ")
        lname = input("Please enter last name: ")

        admin = input("Is this user admin? [Y/N]: ")
        while(admin.upper() not in ['Y', 'N']):
            admin = input("Invalid input! Is user admin? [Y/N]: ")
        if(admin.upper() == 'Y'): admin = True
        else: admin = False

        logging.info("Inserting new user...")
        try:
            self.db.users.insert_one({"username" : uname, "password" : passw, "first_name" : fname, "last_name" : lname, 'admin' : admin})
        except Exception as e:
            logging.error("Failed to insert new user...")
            logging.error(e)
            print("Failed to add user")
            


    def welcome(self):
        os.system('cls')
        logging.info("Login Welcome menu accessed...")
        print("Welcome to Joe's Hardware Store!")
        choice = input("Login, sign-up, or exit? [L/S/E]: ")
        while (choice.lower() != 'l' and choice.lower() != 's' and choice.lower() != 'e'):
            choice = input("Invalid choice! L for login or S for sign-up (E to exit): ")
        if(choice.lower() == 'e'): return -1
        if(choice.lower() == 's'): self.signup()
        ID = self.login()
        return ID