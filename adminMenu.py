import logging
from bson import ObjectId
import bson
from tabulate import tabulate
import os

class AdminMenu:
    def __init__(self, user, db):
        logging.basicConfig(filename="adminMenu.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')
        logging.info("Initializing Admin Menu...")
        self.user = user
        self.db = db

    def menu(self):
        logging.info("Admin menu accessed...")
        print("Welcome {}!".format(self.user['first_name']))
        while(True):
            try:
                os.system('cls')
                print("ADMIN MENU")
                print("[1] View Orders")
                print("[2] View/Update Users")
                print("[3] View/Update Inventory")
                print("[4] Exit")
                choice = input("Enter Selection: ")
                assert choice.isdigit()
                assert int(choice) in range(1, 5)
            except AssertionError as e:
                print("Invalid Selection! Try again")
                logging.error("Invalid menu input...")
                logging.error(e)
                continue

            match choice:
                case '1': self.orders()
                case '2': self.users()
                case '3': self.inventory()
                case '4': break
    
    def orders(self):
        logging.info("Admin orders menu accessed...")
        orders = None
        while(True):
            choice = input("Enter user id or 0 to view all orders (E to exit): ")
            if(choice.upper() == 'E'): return
            logging.info("Loading orders...")
            try:
                if(choice == '0'):
                    orders = self.db.orders.find()
                else:
                    choice = ObjectId(choice)
                    orders = self.db.orders.find({'customer_id' : choice})
            except bson.errors.InvalidId as e:
                print("Invalid ID! No user found")
                logging.error("Invalid user ID entered...")
                continue
            except Exception as e:
                print("Failed to load user orders!")
                logging.error("Failed to load orders...")
                logging.error(e)
                continue
                
            try:
                os.system('cls')
                table = []
                for order in orders:
                    table.append([order['_id'], order['customer_id'], order['item_name'], order['quantity'], '$' + str(order['total'])])
                print(tabulate(table, headers = ['Order ID', 'Customer ID', 'Item', 'Quantity', 'Total']))
                input('Any key to continue...')
            except Exception as e:
                print("Failed to display orders!")
                logging.error("Failed to display orders...")
                logging.error(e)
                continue

    def users(self):
        logging.info("Admin users menu accessed...")
        users = None
        while(True):
            os.system('cls')
            choice = input("Enter user id or 0 to view all users (E to exit): ")
            if(choice.upper() == 'E'): return
            logging.info("Loading user(s)...")
            try:
                if(choice == '0'):
                    users = self.db.users.find().sort({'admin' : 1})
                else:
                    choice = ObjectId(choice)
                    users = self.db.users.find({'_id' : choice})
            except bson.errors.InvalidId as e:
                print("Invalid ID! No user found")
                logging.error("Invalid user ID entered...")
                continue
            except Exception as e:
                print("Failed to load users!")
                logging.error("Failed to load users...")
                logging.error(e)
                continue
                
            try:
                
                table = []
                userList = list(users)
                
                for i, user in enumerate(userList):
                    if (user['admin']):
                        table.append([i, user['_id'], user['first_name'], user['last_name'], user['username'], 'ADMIN', 'ADMIN'])
                        continue
                    pipeline = [
                        {'$match' : {'customer_id' : user['_id']}},
                        {'$group' : {'_id':'null', 'total_orders':{'$count':{}}, 'total_spent':{'$sum':'$total'}}}
                    ]
                    orderInfo = self.db.orders.aggregate(pipeline)
                    orderInfo = list(orderInfo)
                    if(len(orderInfo) > 0): 
                        orderInfo = orderInfo[0]
                        table.append([i, str(user['_id']), user['first_name'], user['last_name'], user['username'], orderInfo['total_orders'], orderInfo['total_spent']])
                    else:
                        table.append([i, str(user['_id']), user['first_name'], user['last_name'], user['username'], 0, 0])
                print(tabulate(table, headers = ["#", "User ID", "First Name", "Last Name", "Username", "Total Orders", "Total Spent"]))
            except Exception as e:
                print("Failed to display users!")
                logging.error("Failed to display users... User list length: " )
                logging.error(e)
                continue

            try:
                while(True):
                    choice = input('Enter # to edit or E to continue: ')
                    if(choice.upper() == 'E'): return
                    if(not choice.isdigit()): print("Invalid input!")
                    elif(int(choice) < 0 or int(choice) > len(list(userList))-1): print("Invalid input!")
                    else: break
                user = userList[int(choice)]
                print("[F]irst Name")
                print("[L]ast Name")
                print("[U]sername")
                print("[C]ancel")
                while(True):
                    change = input('Enter field to update: ')
                    match change.upper():
                        case 'F':
                            newName = input("Please Enter New First Name: ")
                            self.db.users.update_one( {'_id' : user['_id']}, {'$set': {'first_name' : newName}})
                            break
                        case 'L':
                            newName = input("Please Enter New Last Name: ")
                            self.db.users.update_one( {'_id' : user['_id']}, {'$set': {'last_name' : newName}})
                            break
                        case 'U':
                            newName = input("Please Enter New Username: ")
                            self.db.users.update_one( {'_id' : user['_id']}, {'$set': {'username' : newName}})
                            break
                        case 'C':
                            break
                        case _:
                            print("Invalid input! Try again")
            except Exception as e:
                print("Failed to update user")
                logging.error("Failed to update user...")
                logging.error(e)

    def inventory(self):
        logging.info("Admin inventory menu accessed...")
        while(True):
            items = None
            try:
                os.system('cls')
                items = self.db.inventory.find()
                items = list(items)
                table = []
                for i, item in enumerate(items):
                    table.append([i, item['item_name'], '$' + str(item['price']), str(item['quantity'])])
                print(tabulate(table, headers = ['#', 'Item', 'Price', 'Quantity Available']))
            except Exception as e:
                print("Failed to load inventory!")
                logging.error("Failed to load inventory...")
                logging.error(e)
            
            try:
                print("[C]reate Item")
                print("[U]pdate Item")
                print("[D]elete Item")
                print("[E]xit")
                choice = input("Enter Selection: ")
                match choice.upper():
                    case 'C':
                        name = input("Enter item name: ")
                        price = input("Enter item price: ")
                        while(True):
                            try:
                                float(price)
                                break
                            except:
                                price = input("Invalid price! Try again: ")
                        quantity = input("Enter item quantity: ")
                        while (not quantity.isdigit()):
                            quantity = input("Invalid quantity! Try again: ")
                        item = {'item_name':name, 'quantity':int(quantity), 'price':float(price)}
                        self.db.inventory.insert_one(item)
                    case 'U':
                        while(True):
                            selection = input("Enter # to update: ")
                            if(not selection.isdigit()): print("Invalid input!")
                            elif(int(selection) < 0 or (int(selection) > len(items))): print("Invalid input!")
                            else: break
                        selection = int(selection)
                        item = items[selection]
                        print('[N]ame')
                        print('[Q]uantity')
                        print('[P]rice')
                        update = input('Enter attribute to update: ')
                        while(update.upper() not in ['N', 'Q', 'P']): update = input("Invalid Selection! Try again: ")
                        if(update.upper() == 'N'):
                            name = input("Enter new name: ")
                            self.db.inventory.update_one( {'_id' : item['_id']}, {'$set': {'item_name' : name}})
                        elif (update.upper() == 'Q'):
                            newQuantity = input("Enter new quantity: ")
                            while (not newQuantity.isdigit()):
                                newQuantity = input("Invalid quantity! Try again: ")
                            newQuantity = int(newQuantity)
                            self.db.inventory.update_one( {'_id' : item['_id']}, {'$set': {'quantity' : newQuantity}})
                        elif (update.upper() == 'P'):
                            price = input("Enter new price: ")
                            while(True):
                                try:
                                    float(price)
                                    break
                                except:
                                    price = input("Invalid price! Try again: ")
                            price = float(price)
                            self.db.inventory.update_one( {'_id' : item['_id']}, {'$set': {'price' : price}})
                    case 'D':
                        selection = input("Enter # to delete: ")
                        while(not selection.isdigit() or int(selection) < 0 or int(selection) > len(list(items))-1):
                            selection = input("Invalid choice! Try again: ")
                        selection = int(selection)
                        item = items[selection]
                        self.db.inventory.delete_one({'_id':item['_id']})
                    case 'E':
                        break
                    case _:
                        print("Invalid input!")
            except Exception as e:
                print("Inventory operation failed!")
                logging.error('Inventory operation failed...')
                logging.error(e)
                    
