import random
import sqlite3


def luhn_digit(string):
    temp = [int(i) for i in string]
    for i, num in enumerate(temp):
        if i % 2 == 0:
            if num * 2 > 9:
                temp[i] = num * 2 - 9
            else:
                temp[i] = num * 2
    last_digit = (10 - sum(temp)) % 10
    return last_digit


class Account:

    def __init__(self, **args):
        if len(args) == 0:
            self.card_number = self.generate_card_number()
            self.pin = self.generate_pin()
            self.balance = 0
            # store the card account into the database
            cur.execute(f"""INSERT INTO card(number, pin, balance) VALUES ('{self.card_number}','{self.pin}',0)""")
            conn.commit()
        else:
            self.card_number = args.get('card_number')
            self.pin = args.get('pin')
            self.balance = args.get('balance')

    def generate_card_number(self):
        chars = "0123456789"
        string = ''.join([random.choice(chars) for _ in range(9)])
        string = "400000" + string
        # generate last digit according to Luhn's algorithm
        string += str(luhn_digit(string))
        return string

    def generate_pin(self):
        chars = "0123456789"
        string = ''.join([random.choice(chars) for _ in range(4)])
        return string

    def check_balance(self):
        return self.balance

    def change_balance(self, money):
        self.balance += money
        cur.execute(f"UPDATE card SET balance={self.balance} WHERE number='{self.card_number}'")
        conn.commit()


class Menu:
    possible_states = ["main", "wallet"]

    def __init__(self):
        self.state = "main"

    def main(self):
        print("1. Create an account\n2. Log into account\n0. Exit")
        response = input()
        if response == '1':
            acc = Account()
            print(f"Your card has been created\nYour card number: \n{acc.card_number}\nYour card PIN: \n{acc.pin}""")
            self.main()
        elif response == '2':
            self.log_in()
        else:
            self.exit()

    def log_in(self):
        card_number = input("Enter your card number: \n")
        pin = input("Enter your PIN\n")
        # check if there is such combination in the database
        cur.execute(f"SELECT * FROM card WHERE number='{card_number}' AND pin='{pin}'")
        conn.commit()
        temp = cur.fetchone()
        conn.commit()
        if temp is not None:
            acc = Account(card_number=temp[1], pin=temp[2], balance=int(temp[3]))
            print("You have successfully logged in!")
            self.state = 'wallet'
            self.wallet(acc)
        else:
            print("Wrong card number of PIN!")
            self.main()

    def wallet(self, acc):
        print("""
1. Balance 
2. Add income 
3. Do transfer 
4. Close account 
5. Log out 
0. Exit
            """)
        response = input()
        if response == '1':
            print(f"Balance: {acc.check_balance()}")
            self.wallet(acc)
        elif response == '2':
            income_to_add = int(input("Enter income:\n"))
            acc.change_balance(income_to_add)
            print("Income was added!")
            self.wallet(acc)
        elif response == '3':
            recipient_card = input("Enter card number:\n")
            if str(luhn_digit(recipient_card[:-1])) == recipient_card[-1]:
                cur.execute(f"SELECT * FROM card WHERE number='{recipient_card}'")
                conn.commit()
                temp = cur.fetchone()
                conn.commit()
                if temp is not None:
                    money_to_transfer = int(input("Enter how much money you want to transfer:\n"))
                    if acc.check_balance() >= money_to_transfer:
                        acc.change_balance(-money_to_transfer)
                        cur.execute(
                            f"UPDATE card SET balance=balance+{money_to_transfer} WHERE number='{recipient_card}'")
                        conn.commit()
                        print("Success!")
                        self.wallet(acc)
                    else:
                        print("Not enough money!")
                        self.wallet(acc)
                else:
                    print("Such a card does not exist.")
                    self.wallet(acc)
            else:
                print("Probably you made a mistake in the card number. \nPlease try again!")
                self.wallet(acc)
        elif response == '4':
            cur.execute(f"DELETE FROM card WHERE number='{acc.card_number}'")
            conn.commit()
            print("The account has been closed!")
            self.main()
        elif response == '5':
            print("You have successfully logged out!")
            self.state = 'main'
            self.main()
        else:
            self.exit()

    def exit(self):
        print("Bye!")
        exit()


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card (
id INTEGER PRIMARY KEY,
'number' TEXT,
pin TEXT,
balance INTEGER DEFAULT 0
)""")
conn.commit()

start = Menu()
start.main()

