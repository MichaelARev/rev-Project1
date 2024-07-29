import json
import logging
from datetime import date
import os
from tabulate import tabulate

class StoreMenu:
    def __init__(self, user, db):
        logging.basicConfig(filename="storeMenu.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')
        logging.info("Initializing Store Menu...")
        self.user = user
        self.db = db
    
    def open(self):
        print("Welcome {}!".format(self.user['first_name']))
        self.menu()
    
    def menu(self):
        while(True):
            os.system('cls')
            print("CUSTOMER MENU")
            print("Please select an option: ")
            print('[V]iew my orders')
            print('[C]reate order')
            print('[E]xit')
            selection = input('Selection: ')
            while(selection.upper() not in ['V', 'C', 'E']): 
                selection = input("Invalid selection! Try again: ")
            match selection.upper():
                case 'V': self.view()
                case 'C': self.order()
                case 'E': break
    
    def view(self):
        logging.info("Loading customer orders...")
        try:
            orders = self.db.orders.find({'customer_id' : self.user['_id']})
            orders = list(orders)
        except Exception as e:
            print("Failed to load orders!")
            
            logging.error('Failed to load orders...')
            logging.error(e)
            return
        #orders = json.loads(orders)
        try:
            os.system('cls')
            table = []
            for i, order in enumerate(orders): table.append([i, order['date'], order['item_name'], order['quantity'], order['total']])
            print(tabulate(table, headers=['Order #', 'Date', 'Item', 'Quantity', 'Total']))
            input('Any key to continue...')

        except Exception as e:
            print("Failed to display orders!")
            logging.error("Failed to display orders...")
            logging.error(e)
            return

    def order(self):
        logging.info("Loading inventory for Order menu...")
        try:
            inventory = list(self.db.inventory.find())
        except Exception as e:
            print("Failed to load inventory")
            logging.error("Failed to load inventory...")
            logging.error(e)
            return

        while(True):
            try:
                os.system('cls')
                table = []
                for i, item in enumerate(inventory):
                    if(item['quantity'] > 0):
                        table.append([i, item['item_name'], '$'+str(item['price']), str(item['quantity'])])
                print(tabulate(table, headers=['Item #', 'Item', 'Price', 'Quantity Avaiable']))
                choice = input("Please enter the number of the item to order or -1 to exit: ")
                while(True):
                    try:
                        choice = int(choice)
                        if(choice == -1): return
                        if ((int(choice) < 0) or (int(choice) > len(inventory)-1)): choice = input("Invalid item! Try again or -1 to exit: ")
                        else: break
                    except:
                        choice = input("Invalid item! Try again or -1 to exit: ")

                item = inventory[int(choice)]
                break
            except ValueError as e:
                print("Invalid input! Try again")
                logging.error("Invalid input on item selection...")
            except Exception as e:
                print("Error!")
                logging.error("Error selecting item...")
                logging.error(e)
                break
        
        
        
        while(True):
            try:
                quant = input("Please enter the quantity of item to order: ")
                assert quant.isdigit()
                quant = int(quant)
                assert (quant <= item['quantity']) and (quant > 0)
                break
            except ValueError as e:
                logging.error("User entered invalid quantity...")
                print("Invalid quantity! Try again")
            except AssertionError as e:
                logging.error("User entered invalid quantity...")
                print("Invalid quantity! Try again")
                

        
        
        logging.info("Inserting new order...")
        try:
            today = str(date.today())
            
            order = {'customer_id':self.user['_id'], 'date' : today, 'item_name':(inventory[int(choice)])['item_name'], 'quantity':quant, 'total':float(quant*item['price'])}
            self.db.orders.insert_one(order)
        except Exception as e:
            print("Failed to insert new order!")
            logging.error("Failed to insert new order...")
            logging.error(e)
            return
        logging.info("Updating Quantity...")
        try:
            newQuantity = item['quantity'] - quant
            self.db.inventory.update_one( {'_id' : item['_id']}, {'$set': {'quantity' : newQuantity}})
        except Exception as e:
            print("Failed to update quantity!")
            logging.error("Failed to update order quantity...")
            logging.error(e)
            return

        
