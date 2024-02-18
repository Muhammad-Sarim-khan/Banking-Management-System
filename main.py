""" BEFORE STARTING THE PROGRAM, CLOSE ALL CSV FILES OPENED IN EXCEL.
    INSTALL pandas MODULE TO RUN THIS PROGRAM. AND ADD csv EXTENSION FOR PYCHARM."""


import random
import pandas as pd
import datetime
import time
from abc import ABC, abstractmethod

df = pd.read_csv("Client_Information.csv")
s_df = pd.read_csv("Saving_Account_Info.csv")
loan_df = pd.read_csv("Loan_Account_Info.csv")
t_df = pd.read_csv("Transaction_History.csv")


class LoanError(Exception):
    pass


class CNICError(Exception):
    pass


class AccountError(Exception):
    pass


class PasswordError(Exception):
    pass


class PhoneNumberError(Exception):
    pass


class Interface:
    """ Interface <>----- (Composition) Customer Class and Admin Class.
    Class Interface has no specific functionality of its own. It doesn't own any attributes. Its main purpose is to
    be the main interface of the program and start it as such. It possesses two static methods: admin_interface and
    customer_interface, which are self-explanatory.
    Interface owns class Customer and Admin, which are accessed through its two static methods.
    """

    def __init__(self):
        while True:
            print("Welcome to FS banking application!")
            print("Administrator Options --- A")
            print("Customer Options -------- B")
            print("Exit -------------------- C")
            interface_choice = input("Enter here: ").upper()
            print()
            if interface_choice == "A":
                Interface.admin_interface()
                break
            elif interface_choice == "B":
                Interface.customer_interface()
                break
            elif interface_choice == "C":
                Interface.slow_ltrs("Exited!")
                break
            else:
                print("Please enter a valid option.")

    @staticmethod
    def admin_interface():
        """admin_interface instantiates the Admin class upon correct input of password. """

        while True:
            print("This is the Administrator Side. Only authorized people are allowed to access.")
            print("If would you like to exit, enter 0 for name or password or just restart the program.")
            name = input("Enter your name: ")
            password = input("Enter your password: ")  # 12345678 is the default pswrd. First line of Password file.
            if name == "0" or password == "0":
                Interface.slow_ltrs("Exited!")
                break
            with open("Password+BlockedAccounts.txt") as f:
                file_pswrd = f.readline(8)  # The password can only be 8 characters. Hence, f.readline(8)
                if password == file_pswrd:   # Comparison
                    time.sleep(0.3)
                    Interface.slow_ltrs("LOGIN SUCCESSFUL!")
                    a = Admin(name, password)   # OBJECT INSTANTIATION
                    break
                else:
                    print("Incorrect Password! Please try again!")

    @staticmethod
    def customer_interface():
        """customer_interface provides two options, excluding exit, Login and Create Account.

        For Login, there are three things that happen before going to the user options.
        First, the cnic entered is checked that whether or not, it is blocked.
        If it isn't blocked, then after login, loans of the customer are checked. If not paid for more than a month,
        access is restricted. For more than 6 months, cnic of the user is blocked.
        Lastly, if there is a savings account, savings are increased on a monthly basis due to interest.
        For Create Account, once again, the cnic is checked whether or not it is blocked. Then, after checking various
        conditions, a basic account is created. Creating Loan Account and Savings Accounts options are also available.
        If not availed, user will be provided the options to create these accounts."""

        while True:
            print("Login ------------ Press 0")
            print("Create Account --- Press 1")
            print("Press any other key to exit.")
            choice = input("Enter here: ")
            if choice == "0":
                while True:
                    try:
                        print("-------------------------------------- LOGIN -------------------------------------------")
                        print("In order to login to your account, please enter the correct and proper information.")
                        print("If you would like to exit, enter 0 in place of name or cnic or pin.")
                        ask_name = input("Enter your full name: ")
                        ask_cnic = int(input("Enter your CNIC (without dashes): "))
                        ask_pin = int(input("Enter your pin: "))

                        if ask_name == "0" or ask_cnic == "0" or ask_pin == "0":
                            Interface.slow_ltrs("Exited!")
                            break

                    except ValueError:
                        print("Invalid Input!")

                    else:
                        # If account is blocked
                        if Customer.check_account_is_blocked(ask_cnic) is True:
                            print("Your account has been blocked!")
                            print("Your account may have been blocked by the administrator or as a result of "
                                  "unpaid loans!")
                            print("---------------------------------------------------------------------------------\n")
                            time.sleep(0.3)
                            break

                        row_no = Account.login_account(ask_pin, ask_cnic)
                        # This will return row number as a list or False. If a list is returned, then it will only
                        # contain a single number representing the row number, which will be accessed at various points
                        # through the program via indexing at 0. Hence, row_no[0] is accessing the row number stored in
                        # the list at index 0 (only one element). It does NOT mean row number zero. 0 however can alse
                        # be present in the list.

                        if row_no is not False:
                            Interface.slow_ltrs("", 0.1)
                            print("LOGIN SUCCESSFUL!")
                            login_customer = Customer(df.at[row_no[0], "FirstName"], df.at[row_no[0], "LastName"],
                                                      ask_pin, df.at[row_no[0], "AccountID"], ask_cnic,
                                                      df.at[row_no[0], "Address"], df.at[row_no[0], "PhoneNumber"])
                            # pandas .at[] methods takes row and column as arguments. Returns value at those indices.
                            print(f"Hello ", end="")
                            Interface.slow_ltrs({login_customer.first_name.capitalize() + " " +
                                                 login_customer.last_name.capitalize() + "!"}, 0.01)
                            time.sleep(0.1)

                            TransactionHistory.store_customer_history(ask_cnic, "Logged in to Account")
                            # Storing time of logging in to account.

                            ask_again = True   # Setting a variable (flag).
                            while True:
                                savings_index = s_df.index[s_df["CNIC"] == ask_cnic].tolist()
                                loan_index = loan_df.index[loan_df["CNIC"] == ask_cnic].tolist()
                                # This is the same concept as the row no. This will return a list containing a single
                                # row number, that says that this customer logging in has an account or not. savings_
                                # index for Savings Account and loan_index for Loan Account. An empty list means that
                                # the account does not exist. This was done here in order to prevent checking multiple
                                # times throughout the code. Hence, they will passed as args to many methods.

                                if len(loan_index) != 0:  # If true, user has a loan account.
                                    loan_choice = LoanAccount.loan_check_message(loan_index)

                                    if loan_choice == 3:
                                        Admin.block_account(ask_cnic)
                                        print("Your account has now been blocked!")
                                        print("----------------------------------\n")
                                        time.sleep(0.2)
                                        break

                                    if ask_again is True and loan_choice is not None:
                                        pay_now = input("Pay now (Y/N): ").upper()

                                        if pay_now == "Y":
                                            login_customer.deposit(row_no, savings_index, loan_index, only_loan=True)

                                        elif pay_now == "N" and loan_choice == 1:
                                            print("Make sure to pay this month's payment soon!")
                                            print(f"Now, {login_customer.first_name}")

                                        elif pay_now == "N" and loan_choice == 2:
                                            print("Account access has been restricted!")
                                            print("Pay your due loans in order to access your account!")
                                            print("----------------------------------------------------\n")
                                            time.sleep(0.2)
                                            break

                                ask_again = False  # So, it doesn't keep asking again if the user has taken loan
                                # and it is same month  as taking the loan or a month after.
                                # Statement will not be reached for unpaid greater than one month, hence, it will keep
                                # asking for payment and restrict access or block if loan is not paid for more than
                                # six months.

                                if len(savings_index) != 0:
                                    Customer.interest_on_savings(savings_index)  # For incrementing savings monthly.

                                print("What would you like to do?")
                                print("Deposit Money --------------- A\n"
                                      "Withdraw Money -------------- B\n"
                                      "Balance/Loan Enquiry -------- C\n"
                                      "See Account Information ----- D\n"
                                      "Transfer Money -------------- E\n"
                                      "Delete Account -------------- F")
                                if len(loan_index) != 0:
                                    print("Renew Loan Account ------ G")
                                if len(loan_index) == 0:
                                    print("Create Loan Account -- H")
                                if len(savings_index) == 0:  # Only when user doesn't have a savings account.
                                    print("Create Savings Account ------ I")
                                print("Enter any other key to exit.\n")
                                time.sleep(0.1)

                                customer_choice = input("Enter your preferred option here: (Enter only letter "
                                                        "for e.g: a, b etc.)").lower()

                                if customer_choice == "a":
                                    login_customer.deposit(row_no, savings_index, loan_index)
                                    # No break here b/c it will break the loop and ask for login again.

                                elif customer_choice == "b":
                                    login_customer.withdraw(row_no, savings_index)

                                elif customer_choice == "c":
                                    login_customer.balance_inquiry(row_no, savings_index, loan_index)

                                elif customer_choice == "d":
                                    login_customer.display_account_info(row_no, savings_index, loan_index)

                                elif customer_choice == "e":
                                    login_customer.transfer_money(row_no)

                                elif customer_choice == "f":
                                    login_customer.delete_account(row_no, savings_index, loan_index)
                                    break

                                elif customer_choice == "g" and len(loan_index) != 0:
                                    login_customer.renew_loan_account(row_no, loan_index)

                                elif customer_choice == "h" and len(loan_index) == 0:
                                    login_customer.create_loan_account()

                                # Both conditions, otherwise user might press f and go to this method by no choice.
                                elif customer_choice == "i" and len(savings_index) == 0:
                                    login_customer.create_savings_account()

                                else:
                                    Interface.slow_ltrs("Exited account!")
                                    print("--------------------------\n")
                                    break
                        else:
                            time.sleep(0.1)
                            print("-----------------------------------\n")
                            # If it is false. It just loops again.

            elif choice == "1":
                while True:
                    try:
                        print(
                            "------------------------------------ CREATE ACCOUNT ------------------------------------")
                        first_name = input("Enter your first name: ")
                        last_name = input("Enter your last name: ")
                        cnic = int(input("Enter your CNIC (Without dashes and having 13 digits): "))
                        pin = int(input("Enter a four digit pin. Use only numbers: "))
                        address = input("Enter your address: ")
                        phone_number = input("Enter your phone number (Without dashes): ")
                        if len(phone_number) != 11:
                            raise PhoneNumberError
                        if Customer.check_account_is_blocked(cnic) is True:
                            print("This CNIC no. has been banned from the bank!")
                            print("Please try using a different CNIC to create account!.")
                            print("-----------------------------------------------------\n")
                            break
                        assert len(str(pin)) == 4
                        if len(str(cnic)) != 13:
                            raise CNICError
                        check_account = df.index[df["CNIC"] == cnic].tolist()
                        print(check_account)
                        # same as row number before. Returns [] or [n] where n is a row number.
                        if len(check_account) != 0:
                            raise AccountError
                    except ValueError:
                        print("Invalid Input!")
                    except AssertionError:
                        print("Please enter valid information!")
                    except CNICError:
                        print("Please enter the correct CNIC number having 13 digits. Enter without dashes.")
                    except AccountError:
                        print("There is already an account under this cnic! Please try using a different cnic number!")
                    except PhoneNumberError:
                        print("Please enter the correct phone number having eleven digits.")
                    else:
                        accountID = random.randint(10000000, 100000000)
                        print(f"You have been assigned the account ID: {accountID}")
                        customer = Customer(first_name, last_name, pin, accountID, cnic, address, phone_number)
                        # OBJECT INSTANTIATION
                        customer.create_account()
                        TransactionHistory.store_customer_history(cnic, "Created Current Account")
                        print("Your basic account has been successfully created and your information has been stored!")
                        print("You can also create a ")
                        print("Savings Account --------------- A\n"
                              "Loan Account ------------------ B\n"
                              "Press any other key to exit.")
                        print("Please enter correct details to create your own account.")
                        time.sleep(0.1)

                        # If user does not create savings or loan or both accounts here,then there will be an option
                        # when you can login.
                        account_choice = input("What type of account would you like to create?").lower()
                        if account_choice == "a":  # Savings Account
                            customer.create_savings_account()
                            break

                        elif account_choice == "b":  # Loan Account
                            customer.create_loan_account()
                            break

                        else:
                            Interface.slow_ltrs("Exited!")
                            break
            else:
                Interface.slow_ltrs("Exited!")
                break

    @staticmethod
    def slow_ltrs(string, slp_time=0.1):
        """ This method was created to print characters in a dramatic way. It takes a single string argument and sleep
            seconds between printing of each letter. Sleep time is optional and set to 0.1 by default.
            """
        for i in string:
            print(i, end="")
            time.sleep(slp_time)
        print()
    # In this whole program, this method is called in many main classes by reference of Interface


class Admin:
    """ Attributes
    ---------------
    name : str
    password : str

    Methods
    -------------
    change_password(self)
    show_customer_account_details(cnic)
    show_transaction_history(cnic)
    delete_account(cnic, row_no)
    block_account(cnic)
    get_blocked_accounts(cnic)
    print_all_accounts()
    """

    def __init__(self, name, password):
        self.name = name
        self.password = password
        print(f"Welcome {self.name.capitalize()}!")
        while True:
            print("What would you like to do?")
            print("See Customer Details ---- A\n"
                  "See Transaction History - B\n"
                  "Delete Account ---------- C\n"
                  "Block Account ----------- D\n"
                  "See Blocked Accounts ---- E\n"
                  "Change Password --------- F\n"
                  "Exit -------------------- G")
            time.sleep(0.1)
            admin_choice = input("Enter here: ").upper()

            if admin_choice == "A" or admin_choice == "B" or admin_choice == "C" or admin_choice == "D":
                # Specific print statements for specific options. For the above options, the administrator will be shown
                # all accounts before deciding on his specific customer.
                if admin_choice == "A":
                    Admin.print_all_accounts()
                    print("Enter the CNIC (without dashes) of the person whose account information you would like "
                          "to see!")

                elif admin_choice == "B":
                    Admin.print_all_accounts()
                    print("These are all the available accounts!")
                    print("Enter the cnic of the account would you like to see the transaction history!")

                elif admin_choice == "C":
                    Admin.print_all_accounts()
                    print("These are all the available accounts!")
                    print("Enter the CNIC (without dashes) of the person whose account you would like to delete!")

                elif admin_choice == "D":
                    Admin.print_all_accounts()
                    print("These are all the available accounts!")
                    print("Enter the CNIC (without dashes) of the person whose account you would like to block!")
                print("Press 0 to exit.")

                try:
                    cnic = int(input("Enter here: "))
                    if cnic == 0:
                        Interface.slow_ltrs("Exited!")
                        break

                    row_no = df.index[df["CNIC"] == cnic].tolist()  # Same as before in customer interface.
                    if len(row_no) == 0:
                        raise CNICError
                except ValueError:
                    print("Invalid Input!")
                except CNICError:
                    print("The account you are looking for does not exist! Please try again!")
                else:
                    if admin_choice == "A":
                        Admin.show_customer_account_details(cnic, row_no)

                    elif admin_choice == "B":
                        Admin.show_transaction_history(cnic)

                    elif admin_choice == "C":
                        Admin.delete_account(cnic, row_no)

                    elif admin_choice == "D":
                        Admin.block_account(cnic)

            elif admin_choice == "E":
                Admin.get_blocked_accounts()

            elif admin_choice == "F":
                self.change_password()

            elif admin_choice == "G":
                Interface.slow_ltrs("Exiting from administrator options...", 0.01)
                time.sleep(0.1)
                print("Exited!")
                print("-------------------------------------\n")
                break

            else:
                print("Invalid Input!")

    def change_password(self):
        """ Changes Password stored in file. Must know old password. No arguments."""

        cur_pswrd = input("Enter your current password: ")
        while True:
            try:
                if cur_pswrd == self.password:
                    print("Your new password must be 8 letters long!")
                    new_pswrd = input("Enter your new password here: ")
                    reenter = input("Re-enter your new password here: ")
                    if len(new_pswrd) != 8:
                        raise PasswordError
                    assert new_pswrd == reenter
                else:
                    raise ValueError
            except ValueError:
                print("The entered password does not match with your current password.")
                print("Please try again!")
                break
            except AssertionError:
                print("Your entered passwords don't match! Please type the same new password when asked!")
            except PasswordError:
                print("Password must have 8 letters!")
            else:
                with open("Password+BlockedAccounts.txt") as f:
                    file_contents = f.readlines()
                if "\n" in file_contents[0]:  # Accounting for where \n is.
                    file_contents[0] = new_pswrd + "\n"
                else:
                    file_contents[0] = new_pswrd
                with open("Password+BlockedAccounts.txt", "w") as f:  # Erasing the file to and rewriting edited data.
                    for line in file_contents:
                        f.write(line)
                print("Password changed successfully!")
                print("------------------------------\n")
                break

    @staticmethod
    def show_customer_account_details(cnic, row_no):
        """ Prints accounts details using pandas .at[row_number, col_number] method.
        Parameters
        ------------
        cnic : int
        row_no : lst (Will contain single element.)
        """

        while True:
            savings_index = s_df.index[s_df["CNIC"] == cnic].tolist()
            loan_index = loan_df.index[loan_df["CNIC"] == cnic].tolist()
            print("-------------------- Current Account Info -----------------------")
            print("FirstName: ", df.at[row_no[0], "FirstName"])
            print("LastName: ", df.at[row_no[0], "LastName"])
            print("Pin: ****")
            print("AccountID: ", df.at[row_no[0], "AccountID"])
            print("CNIC: ", df.at[row_no[0], "CNIC"])
            print("Balance: ", df.at[row_no[0], "CurrentBalance"])
            print("CreditLimit: ", df.at[row_no[0], "CreditLimit"])
            print("Address: ", df.at[row_no[0], "Address"])
            print("PhoneNumber: ", df.at[row_no[0], "PhoneNumber"])
            print("-----------------------------------------------------------------\n")
            time.sleep(0.2)
            if len(savings_index) != 0:
                print("----------------- Saving Account Details -------------------")
                print("SavingsBalance: ", s_df.at[savings_index[0], "PrincipalAmount"])
                print("------------------------------------------------------------\n")
                time.sleep(0.2)
            if len(loan_index) != 0:
                print("----------------- Loan Account Details ---------------------")
                print("LoanDue: ", loan_df.at[loan_index[0], "LoanDue"])
                print("LoanDuration: ", loan_df.at[loan_index[0], "LoanDuration"])
                print("------------------------------------------------------------\n")
            time.sleep(0.2)
            break

    @staticmethod
    def show_transaction_history(cnic):
        """ Transaction history is stored out of order, hence this method parses the file for one given user's
        transaction history.
        Parameters
        ----------
        cnic : int (user's cnic)
        """

        for i in range(len(t_df)):
            if t_df.at[i, "CNIC"] == cnic:
                print("Operation: ", t_df.at[i, "Operation"])
                print("DateofOperation: ", t_df.at[i, "DateofOperation"])
                print("TimeofOperation: ", t_df.at[i, "TimeofOperation"])
                print("------------------------------------------------\n")

    @staticmethod
    def delete_account(cnic, row_no):
        """ Deletes account of user.
        Parameters
        --------------
        cnic : int
        row_no : lst (Will contain single element)
        """

        s_index = s_df.index[s_df["CNIC"] == cnic].tolist()
        loan_index = loan_df.index[loan_df["CNIC"] == cnic].tolist()
        transaction_index = t_df.index[t_df["CNIC"] == cnic].tolist()

        if len(s_index) == 0 and len(loan_index) == 0:
            print("The mentioned user only has a single current account!")
            print("Delete his account? Confirm?")
        if len(s_index) != 0 or len(loan_index) != 0:
            print("The mentioned user has more than one account!")
            print("Delete both accounts? Confirm?")
        choice = input("(Y/N)?").upper()  # Confirmation
        if choice == "Y":
            CheckingAccount.delete_account(row_no)
            if len(s_index) != 0:
                SavingsAccount.delete_account(s_index)
            if len(loan_index) != 0:
                LoanAccount.delete_account(loan_index)
            if len(transaction_index) != 0:
                TransactionHistory.delete_transaction_history(transaction_index)
            print("-------------------------------------\n")
        elif choice == "N":
            print("Account has not been deleted!")
            print("-------------------------------------\n")
        else:
            print("Invalid Input!")

    @staticmethod
    def block_account(cnic):
        """ Puts account cnic in blocked accounts file. Any cnic in the file will not be able to access their acc.
        Parameters
        -----------
        cnic : int
        """
        with open("Password+BlockedAccounts.txt") as f:
            lst = f.readlines()

        if "\n" not in lst[len(lst) - 1]:  # len(lst) -  1 to prevent IndexError
            lst.append("\n"+str(cnic))
        else:
            lst.append(str(cnic))
        with open("Password+BlockedAccounts.txt", "w") as f:
            for line in lst:
                f.write(line)
        print("The mentioned account has been successfully blocked!")
        print("The account can no longer be accessed!")

    @staticmethod
    def get_blocked_accounts():
        """ Prints list of all blocked accounts. If there are no blocked accounts, then it informs as such."""

        with open("Password+BlockedAccounts.txt") as f:
            lst = f.readlines()

        if len(lst) > 1:
            print("The following are the CNICs of the blocked accounts: ")
            for i in lst[1:]:   # First line is the password
                if "\n" in i:
                    print(i[:len(i)-2])
                else:
                    print(i)
            print("------------------------------------------------------\n")
        else:
            print("There are no blocked accounts currently.")
            print("-----------------------------------------\n")
        # len gives total length not starting from zero. While indexing starts from zero.
        # So, if I minus 1 from the len() that will give me the last element in indexing
        # Since, I don't want the last element to be printed which would be \n in the if statement, hence, I minus
        # 2 to prevent this.
        # The else statement prints as is, ofc, since, it won't have \n.

    @staticmethod
    def print_all_accounts():
        """ Prints all accounts information.  Parameters = None"""

        for i in range(len(df)):
            print("FirstName: ", df.at[i, "FirstName"], ", Last Name: ", df.at[i, "LastName"], ", CNIC: ",
                  str(df.at[i, "CNIC"]), ", AccountID: ", df.at[i, "AccountID"], end="")
            for j in range(len(s_df)):
                if df.at[i, "CNIC"] == s_df.at[j, "CNIC"]:
                    print(", Savings Account: Exists", end=" ")
            for k in range(len(loan_df)):
                if df.at[i, "CNIC"] == loan_df.at[k, "CNIC"]:
                    print(", Loan Account: Exists", end=" ")
            print()
            time.sleep(0.1)


class Customer:
    """      Customer <> --- (Composition)  Sub-classes of Accounts

    The Customer class handles all customer operations. Hence, Customer has composition with Account
    class and it's subclasses that is Customer owns Account and its subclasses. This has been done so that only
    Customer and Admin class have composition with Interface.
    row_no, savings_index, loan_index and transaction_index(in delete_account) attribute are passed as parameter in
    various methods. Each of these variables define a list of the specific row where the user's account is in its
    specific file that is Current Account file, Saving Account file, Loan Account file or Transaction History file.
    The list only has one element and is therefore accessed as <variable>[0] to pass in the actual row
    number in methods to access the any value of that row.


     Parameters
     ---------
     first_name : str
     last_name : str
     pin : int
     accountid : int
     cnic : int
     address : str
     phone_num : str

     Methods
     ---------
     create_account(self)
     create_savings_account(self)
     create_loan_account(self, loan_index)
     check_account_is_blocked(cnic)
     deposit(self, row_no, savings_index, loan_index, only_loan=False)
     withdraw(self, row_no, savings_index)
     balance_inquiry(row_no, savings_index, loan_index)
     display_account_info(self, row_no, savings_index, loan_index)
     interest_on_savings(savings_index)
     delete_account(self, row_no, savings_index, loan_index)
     renew_loan_account(self, row_no, loan_index)
     """

    def __init__(self, first_name, last_name, pin: int, accountid: int, cnic: int, address, phone_num):
        self.first_name = first_name
        self.last_name = last_name
        self.pin = pin
        self.accountID = accountid
        self.cnic = cnic
        self.address = address
        self.phone_num = phone_num

    def create_account(self):
        """ Instatiantes Checking Account and calls its create account method. Args passed through self in method."""

        c = CheckingAccount(self.cnic)
        c.create_account(self.first_name, self.last_name, self.pin, self.accountID, self.address, self.phone_num)

    def create_savings_account(self):
        """ This method creates Savings Account.

        Savings are inputted and inputted value is verified and checked. If correct, SavingsAccount is instantiated and
        savings parameter is passed in as an argument. Its method create_savings_account is called.
        """

        while True:
            try:
                print("---------------------------------- Create Savings Account ------------------------------------")
                savings = int(input("Enter the amount of money to be stored in your savings account (In numbers only): "))
                reenter = int(input("Reenter your CNIC: "))
                if savings == 0:
                    print("Savings account was not created!")
                    break
                assert savings > 0
                if reenter != self.cnic:
                    raise CNICError
            except ValueError:
                print("Please enter the correct information.")
            except CNICError:
                print("The CNIC you have entered does not match with our records. Please try again!")
            else:
                savings_acc = SavingsAccount(self.cnic, savings)    # OBJECT INSTANTIATION
                savings_acc.create_savings_account()
                break

    def create_loan_account(self):
        """  This method creates Loan Account.

        If user already has a loan account, they can renew their loan account to borrow more loans if he/she has paid
        their previous loans.
        loan and loan_duration are inputted and are verified and checked. If correct, LoanAccount is instantiated and
        loan and loan_duration parameters are passed in as an arguments. Its method create_loan_account is called.

        Parameters
        ----------
        self
        """
        while True:
            try:
                print("-------------------------------- Create Loan Account --------------------------------")
                print("To create a loan account, please specify the amount of loan that"
                      "you want.")
                print("You can loan up to Rs. 1,000,000. ")
                print("Maximum loan duration is 3 years or 36 months.")
                print("Minimum loan duration is 6 months.")
                loan = int(input("Enter the money to be borrowed here: "))
                assert loan < 1000000 or loan > 0
                loan_duration = int(input("Enter the duration of your loan (in months only): "))
                assert 6 <= loan_duration <= 36
                reenter = int(input("Reenter your cnic: "))
                if reenter != self.cnic:
                    raise CNICError
                if loan / loan_duration < 1000:
                    raise LoanError
            except AssertionError:
                print("Please enter money within the specified limit.")
            except ValueError:
                print("Please enter only numbers in place of loan money and loan duration.")
            except LoanError:
                print("The loan entered is too small as compared to the loan duration")
                print("The loan return per month should be at least Rs.1000")
                print(f"Your current loan payment per month only amounts to Rs.{loan/loan_duration}")
            except CNICError:
                print("The CNIC you have entered does not match with our records. Please try again!")
            else:
                row_no = df.index[df["CNIC"] == self.cnic].tolist()
                loan_acc = LoanAccount(self.cnic, loan_duration, loan)  # OBJECT INSTANTIATION
                loan_acc.create_loan_account(row_no)
                break

    def deposit(self, row_no, savings_index, loan_index, only_loan=False):
        """ Deposit method for depositing money in current balance, savings or for paying loans.

        This method, based on the user's account, gives options asking user in which account to deposit money.
        If there is only Checking/ Current Account, deposit method of Checking account is run after instantiation.
        If there is more than one account, than options are provided accordingly.
        CheckingAccount, SavingsAccount and LoanAccount are all instantiated inside the class and their respective
        deposit method accessed w.r.t their objects.
        only_loan parameter is there for depositing loans when user is supposed to get direct access to deposit loan
        such as when he/she hasn't paid their loans (it is then set to True).

        Parameters
        -------------
        row_no : lst
        savings_index : lst
        loan_index : lst
        only_loan : False (Default parameter, set to True when to only deposit loans)

        """

        if only_loan is False:
            if len(savings_index) != 0 or len(loan_index) != 0:
                print("Where would you like to deposit your money?")
                print("You can enter c to deposit money in your current account.")
                if len(savings_index) != 0:
                    print("Or enter s to deposit money in your savings account.")
                if len(loan_index) != 0:
                    print("Or enter the letter l to pay your loans.")
                print("Press any other key to exit.")
                time.sleep(0.1)
                dep_choice = input("Enter here: ")
                if dep_choice == "c":
                    c = CheckingAccount(self.cnic)
                    c.deposit(row_no)
                elif dep_choice == "s" and len(savings_index) != 0:
                    cur_savings = s_df.at[savings_index[0], "PrincipalAmount"]
                    s = SavingsAccount(self.cnic, cur_savings)
                    s.deposit(savings_index)
                elif dep_choice == "l" and len(loan_index) != 0:
                    loan_duration = loan_df.at[loan_index[0], "LoanDuration"]
                    loan_due = loan_df.at[loan_index[0], "LoanDue"]
                    l = LoanAccount(self.cnic, loan_duration, loan_due)
                    l.deposit(loan_index)
                else:
                    Interface.slow_ltrs("Exited!")
            else:
                acc = CheckingAccount(self.cnic)
                acc.deposit(row_no)
        else:
            loan_duration = loan_df.at[loan_index[0], "LoanDuration"]
            loan_due = loan_df.at[loan_index[0], "LoanDue"]
            l = LoanAccount(self.cnic, loan_duration, loan_due)
            l.deposit(loan_index)

    def withdraw(self, row_no, savings_index):
        """ This method is for withdrawal of money from Checking and SavingAccount.

        If user only has Checking/ Current Account, then money is withdrawn using its withdraw method.
        If user has both Checking and Savings Account, then options are provided for withdrawal.
        Both of these Account sub-classes are instantiated and withdraw method is called w.r.t their objects.

        Parameters
        ---------
        row_no : lst
        savings_index : lst

        """

        if len(savings_index) != 0:
            print("You have two accounts to withdraw money from.")
            print("Enter c to withdraw money from your current account.")
            print("Enter s to withdraw money from savings account.")
            print("Press any other key to exit.")
            time.sleep(0.1)
            wd_choice = input("Enter here: ")
            c = CheckingAccount(self.cnic)  # OBJECT INSTANTIATION
            if wd_choice == "c":
                c.withdraw(row_no)
            elif wd_choice == "s" and len(savings_index) != 0:
                cur_savings = s_df.at[savings_index[0], "PrincipalAmount"]
                s = SavingsAccount(self.cnic, cur_savings)  # OBJECT INSTANTIATION
                s.withdraw(row_no)
            else:
                Interface.slow_ltrs("Exited!")
        else:
            acc = CheckingAccount(self.cnic)  # OBJECT INSTANTIATION
            acc.withdraw(row_no)

    def balance_inquiry(self, row_no, savings_index, loan_index):
        """ Balance Inquiry method for current, savings and loan balances.

        If user only has Checking/ Current Account, only its balance information is provided.
        If user has more than one accounts, then options are provided for balance inquiry.
        Both of these Account sub-classes are instantiated and withdraw method is called w.r.t their objects.

        Parameters
        -----------

        row_no : lst  # All explained in customer_interface
        savings_index : lst
        loan_index : lst

        """

        if len(savings_index) or len(loan_index) != 0:
            print("Which account would you like to know the balance of ?")
            print("Enter a to know the balance for all your accounts.")
            print("Enter c to know the balance of your current account.")
            if len(savings_index) != 0:
                print("Enter s to know the balance of your savings account. ")
            if len(loan_index) != 0:
                print("Enter l to know the balance of your loan account")
            print("Enter any other key to exit!")
            time.sleep(0.1)
            choice = input("Enter your option here: ").lower()
            c = CheckingAccount(self.cnic)
            s = SavingsAccount(self.cnic)
            l = LoanAccount(self.cnic)
            if choice == "a":
                c.balance_inquiry(row_no)
                if len(savings_index) != 0:
                    s.balance_inquiry(savings_index)
                if len(loan_index) != 0:
                    l.balance_inquiry(loan_index)
            elif choice == "c":
                c.balance_inquiry(row_no)
            elif choice == "s":
                s.balance_inquiry(savings_index)
            elif choice == "l":
                l.balance_inquiry(loan_index)
            else:
                Interface.slow_ltrs("Exited!")
                print("-----------------\n")
        else:  # Will run when there is no savings or loan account.
            c = CheckingAccount(self.cnic)
            c.balance_inquiry(row_no)

    def transfer_money(self, row_no):
        """ Transfer money from one user to another. Only Instantiates Checking Account then, calls its method.

        Parameters
        ---------
        row_no : lst

        """

        c = CheckingAccount(self.cnic)
        c.transfer_money(row_no)

    def renew_loan_account(self, row_no, loan_index):
        loan_due = loan_df.at[loan_index[0], "LoanDue"]
        while True:
            if loan_due == 0:
                print("You are eligible for a loan!")
                try:
                    print("-------------------------------- Renew Loan Account --------------------------------")
                    print("To renew your loan account, please specify the amount of loan that"
                          "you want.")
                    print("You can loan up to Rs. 1,000,000 ")
                    print("Maximum loan duration is 3 years.")
                    print("Minimum loan duration is 6 months.")
                    loan = int(input("Enter the money to be borrowed here: "))
                    loan_duration = int(input("Enter the duration of your loan (in months only): "))
                    reenter = int(input("Reenter your cnic: "))
                    if reenter != self.cnic:
                        raise CNICError
                    assert loan < 1000000 or loan > 0
                    assert 6 <= loan_duration <= 36
                    if loan / loan_duration < 1000:
                        raise LoanError
                except AssertionError:
                    print("Please enter money within the specified limit.")
                except ValueError:
                    print("Please enter only numbers in place of loan money and loan duration.")
                except LoanError:
                    print("The loan entered is too small as compared to the loan duration")
                    print("The loan return per month should be at least Rs.1000")
                    print(f"Your current loan payment per month only amounts to Rs.{loan/loan_duration}")
                except CNICError:
                    print("The CNIC you have entered does not match with our records. Please try again!")
                else:
                    loan_acc = LoanAccount(self.cnic, loan_duration, loan)  # OBJECT INSTANTIATION
                    loan_acc.create_loan_account(row_no, renewal=True)
                    break

            else:
                print("\nYou already possess a loan account and are ineligible for its renewal!")
                print("Please pay your current loans before renewal of your loan account!")
                print("----------------------------------------------------------------------\n")
                time.sleep(0.2)
                break

    @staticmethod
    def check_account_is_blocked(cnic):
        """ Checks account is blocked or not.

        Parameters
        ----------
        cnic : int

        Returns
        ---------
        True  # If Account CNIC is blocked (i.e. present in blocked account file)
        False  # If Account CNIC is not blocked (i.e. not present in blocked account file)

        """
        with open("Password+BlockedAccounts.txt", "r") as f:
            for line in f:
                if line[0:-1] == str(cnic):
                    return True
            return False


    @staticmethod
    def interest_on_savings(savings_index):
        """ Calls Savings Account's static method of incrementing savings.

        Parameters
        ---------
        savings_index : lst  # As has been explained in customer_interface
        """

        s = SavingsAccount(savings_index)
        s.interest_on_savings(savings_index)

    def display_account_info(self, row_no, savings_index, loan_index):
        """ Displays customer account information.

        If customer has a single Checking/ Current Account, then only it's information is displayed.
        If more than one account, then, all account are printed accordingly

        Parameters
        ---------
        self
        row_no : lst
        savings_index : lst
        loan_index : lst
        """

        print(f"Your account is under the CNIC {self.cnic}")
        print("----------------------------------- Current Account Info ----------------------------")
        print(df.iloc[row_no[0]])  # iloc[row, column] Since, col is not provided, it will give all columns.
        print("-------------------------------------------------------------------------------------\n")
        if len(savings_index) != 0:
            time.sleep(0.1)
            print("------------------------------ Savings Account Info --------------------------------")
            print(s_df.iloc[savings_index[0]])  # Same here
            print("------------------------------------------------------------------------------------\n")
        if len(loan_index) != 0:
            time.sleep(0.1)
            print("--------------------------------- Loan Account Info --------------------------------")
            print(loan_df.iloc[loan_index[0]])  # Same here
            print("------------------------------------------------------------------------------------\n")

    def delete_account(self, row_no, savings_index, loan_index):
        """ Method for deleting account and transaction history. Calls methods of Account sub-classes and Transaction
        History.

        Parameters
        ----------
        row_no: lst
        savings_index: lst
        loan_index: lst
        """
        transaction_index = t_df.index[t_df["CNIC"] == self.cnic].tolist()

        if len(savings_index) != 0 or len(loan_index) != 0:
            print("You have multiple accounts. Which account would you like to delete? ")
            print("Delete All Accounts --------------- A")
            if len(savings_index) != 0:
                print("Delete Savings Account ------------ S")
            if len(loan_index) != 0:
                print("Delete Loan Account --------------- L")
                print("Press any other key to exit!")
            choice = input("Enter your choice here: ").upper()
            if choice == "A":
                CheckingAccount.delete_account(row_no)
                if len(savings_index) != 0:
                    SavingsAccount.delete_account(savings_index)
                if len(loan_index) != 0:
                    LoanAccount.delete_account(loan_index)
                if len(transaction_index) != 0:
                    TransactionHistory.delete_transaction_history(transaction_index)
            elif choice == "S":
                SavingsAccount.delete_account(savings_index)
            elif choice == "L":
                LoanAccount.delete_account(loan_index)
            else:
                Interface.slow_ltrs("Exited!")
                print("--------------------------------------------\n")
                time.sleep(0.2)
        elif len(savings_index) == 0 and len(loan_index) == 0:
            print("You have a single current account!")
            print("Confirm deletion of account? ")
            print("Enter y to delete. Press any other key to exit.")
            choice = input("Enter here: ").upper()
            if choice == "Y":
                CheckingAccount.delete_account(row_no)
                if len(transaction_index) != 0:
                    TransactionHistory.delete_transaction_history(transaction_index)
                print("Account deleted successfully!")
                print("-----------------------------\n")
                time.sleep(0.2)
            else:
                print("Account was not deleted!")
                print("-----------------------------\n")
                time.sleep(0.2)


class Account(ABC):
    """ Account class serves as a template for its subclasses by being an abstract class.

    Attributes
    -----------
    cnic : int
    balance : int

    Methods
    ---------
    deposit(row_no)  -- Abstract
    withdraw(row_no)
    balance_inquiry(row_no)  -- Abstract
    login_account(ask_cnic, ask_pin)
    delete_account(index)
    """
    def __init__(self, cnic, balance=0):
        self.balance = balance
        self.cnic = cnic

    @abstractmethod
    def deposit(self, row_no):
        """ Abstract Method of Account Class, deposit. To be defined in sub-classes

        Parameters
        ---------
        self
        row_no : lst

        """
        pass

    def withdraw(self, row_no):
        """ Method of Account Class, deposit.To be defined in sub - classes. This method was not made abstract because
        LoanAccount should not have withdraw method.

        Parameters
        ---------
        self
        row_no : lst
        """
        pass

    @abstractmethod
    def balance_inquiry(self, row_no):
        """ Abstract Method of Account Class, balance_inquiry. To be defined in sub-classes

        Parameters
        ---------
        self
        row_no : lst
        """
        pass

    @staticmethod
    def login_account(ask_pin, ask_cnic):
        """ Checks cnic and pin provided, whether they exist in file or not.

        Parameters
        ----------
        ask_pin : int
        ask_cnic : int

        Returns
        -------
        check_cnic : False # If account doesn't exist
        check_cnic : lst # If account exists. Variable's value will be a lst containing a single row number.
        """
        try:
            check_cnic = df.index[df["CNIC"] == ask_cnic].tolist()
            check_pin = df.index[df["Pin"] == ask_pin].tolist()
            assert len(check_cnic) != 0 and len(check_pin) != 0
        except AssertionError:
            print("Your account can't be found! Please try entering the correct information or making a new account "
                  "if you don't have one.")
            return False
        else:
            return check_cnic

    @staticmethod
    @abstractmethod
    def delete_account(row_no):
        """ Abstract method of Account class, delete_account to be defined in sub-classes.

        Parameters
        ---------
        row_no : lst
        """
        pass


class TransactionHistory:
    """ This class stores and deletes the transaction history of customer. It has no attributes.

    Methods
    ----------
    store_customer_history(cnic, operation: str)
    delete_transaction_history(cnic)
    """
    @staticmethod
    def store_customer_history(cnic, operation: str):
        """ Store's customer history when called.  CNIC, the operation performed, date and the time are all stored
        in the file.

        Parameters
        ----------
        cnic : int
        operation : str
        """

        cur_datetime = datetime.datetime.now()
        current_date = datetime.date.today()
        str_time = cur_datetime.strftime("%H:%M:%S")
        lst = [cnic, operation, str_time, current_date]
        t_df.loc[len(t_df)] = lst
        t_df.to_csv("Transaction_History.csv", index=False)

    @staticmethod
    def delete_transaction_history(transaction_index):
        """  This method deletes the transaction history of a user.

        The file is read and changes are made to the dataframe. The index passed as argument contains a list of row
        numbers where the customer's transaction history is stored. The for loop iterates over the list and drops each
        row according to the row number. The changed dataframe is then stored back into the file.

        Parameters
        ----------
        transaction_index: lst
        """

        transaction_df = pd.read_csv("Transaction_History.csv")
        if len(transaction_index) != 0:
            for i in transaction_index:  # As there will be one more than one row of the person's transactions
                transaction_df = transaction_df.drop(labels=i, axis=0)
            transaction_df.to_csv("Transaction_History.csv", index=False)


class CheckingAccount(Account):
    """ Checking Account is a sub-class of Account, dealing with current balance and operations performed on it.

    row_no attribute is passed as parameter in various methods. It is list of the specific row where the user's account
    is. The list only has one element and is therefore accessed as row_no[0] to pass in the actual row number in methods
    to access the any value of that row.

    Attributes
    ---------
    credit_limit = 100000
    overdraft_fee = 3000

    Methods
    -------
    create_account(self, cnic, balance = 0)
    deposit(self, row_no)
    withdraw(self, row_no)
    balance_inquiry(self, row_no)
    login_account(ask_pin, ask_cnic)
    """

    def __init__(self, cnic):
        """
        Parameters
        ---------
        self.credit_limit : 100000
        self.overdraft_fee : 3000
        """
        super().__init__(cnic)
        self.credit_limit = 100000
        self.overdraft_fee = 3000

    def create_account(self, f_name, l_name, acc_pin, acc_id, address, phone_num):
        """ Creates account by storing information provided in a file.

        Parameters
        ----------
        self
        f_name : str
        l_name : str
        acc_pin : int
        acc_id : int
        address : str
        phone_num :str
        """

        lst = [f_name, l_name, acc_pin, acc_id, self.cnic, 0, self.credit_limit, address, phone_num]
        df.loc[len(df)] = lst  # .loc[row, col] Last row and all cols (since, not specified). "Assigning" value
        df.to_csv("Client_Information.csv", index=False)
        # Saving the data to the appropriate file. And setting index to False to not store indices.

    def deposit(self, row_no):
        """ For depositing money in current account. Overdraft option is available having credit limit upto Rs. 100000.
        Balance is updated in the file.

        Parameters
        ----------
        self
        row_no : lst

        """
        while True:
            try:
                deposit = int(input("Enter the money to be deposited: "))  # 20000 or 2000
                cur_balance = df.at[row_no[0], "CurrentBalance"]  # -13000 for example
                if deposit == 0:
                    print("Balance was not updated!")
                    Interface.slow_ltrs("Exited!")
                    print("------------------------\n")
                    break
            except ValueError:
                print("Please enter the money only in numbers.")
            else:
                new_bal = cur_balance + deposit  # 20000 - 13000 = 7000 or 2000 - 13000 = -11000
                if cur_balance < 0:    # -ve balance Condition
                    print("Overdraft loan and fee due on you have been deducted from your deposit.")
                    if new_bal >= 0:   # Then all overdraft must have been deducted
                        print("All overdraft loan and fee have been deducted.")
                        print("Credit limit has been renewed to Rs.100000")
                        df.at[row_no[0], "CreditLimit"] = 100000
                        df.to_csv("Client_Information.csv", index=False)  # Saving
                    df.at[row_no[0], "CurrentBalance"] = new_bal   # Storing at the proper index
                    print(f"Your new balance is Rs.", df.at[row_no[0], "CurrentBalance"])
                    time.sleep(0.1)
                    print("--------------------------------------------------------\n")
                    df.to_csv("Client_Information.csv", index=False)  # Saving
                    TransactionHistory.store_customer_history(self.cnic, f"Deposited Rs. {deposit}")
                else:   # No overdraft due
                    df.at[row_no[0], "CurrentBalance"] = new_bal  # Storing at the proper index
                    df.to_csv("Client_Information.csv", index=False)  # Saving
                    print("Your balance has been updated!")
                    print(f"Your new balance is Rs.{new_bal}")
                    time.sleep(0.1)
                    print("------------------------------\n")
                    TransactionHistory.store_customer_history(self.cnic, f"Deposited Rs. {deposit}")
                    break

    def withdraw(self, row_no):
        """ Withdraw money with credit limit (100000) from Checking Account balance. Balance is updated in the file.

        Parameters
        ----------
        row_no: lst
        """

        while True:
            try:
                cur_balance = df.at[row_no[0], "CurrentBalance"]
                print(f"Your current balance is {cur_balance}.")  # For example, 10000
                withdraw = int(input("Enter money to be withdrawn: "))  # 20000
                credit_limit = df.at[row_no[0], "CreditLimit"]  # Customer's credit limit. Subject to change.
                print(f"Option of overdraft is available upto {credit_limit}. ")
                assert abs(cur_balance-withdraw) < credit_limit  # Not going above credit limit
            except ValueError:
                print("Please enter the money only in numbers.")
            except AssertionError:
                print("You have insufficient balance for this withdrawal.")
                print(f"Your credit limit is Rs. {credit_limit} and the entered amount exceeds it.")
            else:
                if withdraw > cur_balance:
                    print("You have insufficient funds. Would you like to overdraft?")
                    print(f"A fee of Rs.{self.overdraft_fee} will be charged. ")  # 3000
                    confirm = input("Confirm (Y/N) : ").upper()
                    if confirm == "Y":
                        new_bal = cur_balance - withdraw  # -10000
                        new_credit_limit = credit_limit + new_bal  # Because balance is negative. # 100000+(-10000)
                        df.at[row_no[0], "CreditLimit"] = new_credit_limit  # 90000
                        new_bal = new_bal - self.overdraft_fee  # -10000 - 3000 = -13000
                        df.at[row_no[0], "CurrentBalance"] = new_bal   # -13000
                        df.to_csv("Client_Information.csv", index=False)  # Storing data to file
                        print(f"Your new balance is {new_bal}.")
                        print("Overdraft fee has been added to it.")
                        print("Any money deposited will automatically deduct the overdraft loan and fee.")
                        time.sleep(0.1)
                        print("-----------------------------------------------------------------------\n")
                        TransactionHistory.store_customer_history(self.cnic, f"Withdrew Rs. {withdraw} having overdraft of"
                                                               f" Rs.{withdraw-cur_balance}. Overdraft Fee: Rs. 3000")
                        break
                    else:
                        print("No money was withdrawn!")
                        Interface.slow_ltrs("Exited!")
                        print("------------------------------\n")
                        break

                else:
                    new_bal = cur_balance - withdraw
                    df.at[row_no[0], "CurrentBalance"] = new_bal  # Storing at proper index
                    df.to_csv("Client_Information.csv", index=False)  # Saving to proper file without indices
                    print(f"You have successfully withdrawn Rs.{withdraw}")
                    print(f"Your new balance is Rs.{new_bal}")
                    time.sleep(0.1)
                    print("------------------------------\n")
                    TransactionHistory.store_customer_history(self.cnic, f"Withdrew Rs. {withdraw}")

    def balance_inquiry(self, row_no):
        """ Inquire Balance of Current/Checking Account.

        Parameters
        ---------
        self
        row_no : lst
        """

        balance = df.at[row_no[0], "CurrentBalance"]
        print(f"Your current balance is Rs. {balance}.")
        time.sleep(0.1)
        print("--------------------------------------\n")
        TransactionHistory.store_customer_history(self.cnic, f"Balance Inquired: Rs. {balance}")

    def transfer_money(self, row_no):
        """ Transfer of money from one user to another. Cannot transfer money to blocked users. Balance is updated in
        the file.

        Parameters
        ---------
        self
        row_no : lst
        """

        while True:
            try:
                sender_balance = df.at[row_no[0], "CurrentBalance"]
                if sender_balance <= 0:
                    print("You have insufficient funds for this transaction!")
                    print(f"Your current balance is Rs.{sender_balance}")
                    print("-----------------------------------------\n")
                    break
                print("In order to transfer money to someone, enter their CNIC. If you want to exit, simply enter 0.")
                reciever_cnic = int(input("Enter here: "))
                if reciever_cnic == 0:
                    break
                with open("Password+BlockedAccounts.txt", "r") as f:  # Checking if reciever cnic is blocked
                    for line in f:
                        if line == str(reciever_cnic):
                            print("This account has been blocked!")
                            print("You cannot transfer money to it!")
                            print("----------------------------------\n")
                            time.sleep(0.2)
                            break
                check_cnic = df.index[df["CNIC"] == reciever_cnic].tolist()
                if len(check_cnic) == 0 or reciever_cnic == self.cnic:
                    raise CNICError
                dep_money = int(input("Enter the money to be deposited: "))
                assert dep_money < sender_balance
            except ValueError:
                print("Invalid input!")
            except AssertionError:
                print(f"Current Balance: {sender_balance}")
                print("Insufficient Balance! Cannot Transfer Money!")
            except CNICError:
                print("Invalid CNIC!")
            else:
                sender_name = df.at[row_no[0], "FirstName"] + " " + df.at[row_no[0], "LastName"]
                receiver_name = df.at[check_cnic[0], "FirstName"] + " " + df.at[check_cnic[0], "LastName"]
                print(f"Transfer Rs. {dep_money} to {receiver_name}...")
                confirmation = input("Confirm (Y/N):").upper()
                if confirmation == "Y":
                    receiver_balance = df.at[check_cnic[0], "CurrentBalance"]
                    new_sender_balance = sender_balance - dep_money
                    new_receiver_balance = receiver_balance + dep_money
                    df.at[row_no[0], "CurrentBalance"] = new_sender_balance  # Storing at proper index
                    df.at[check_cnic[0], "CurrentBalance"] = new_receiver_balance  # Storing at proper index
                    df.to_csv("Client_Information.csv", index=False)  # Storing data in file
                    TransactionHistory.store_customer_history(self.cnic, f"Transferred Rs.{dep_money} to {receiver_name}")
                    TransactionHistory.store_customer_history(reciever_cnic, f"Received Rs. {dep_money} from {sender_name}")
                    print("Transaction Successful!")
                    break
                elif confirmation == "N":
                    print("Transaction Cancelled! Did Not Transfer Money!")
                    time.sleep(0.1)
                    print("--------------------------------------------\n")
                    break
                else:
                    print("Invalid Input!")

    @staticmethod
    def delete_account(row_no):
        """ Deletes checking/ current account by removing row from file.

        Parameters
        ----------
        row_no: lst
        """
        pd_df = pd.read_csv("Client_Information.csv")
        pd_df = pd_df.drop(labels=row_no[0],
                           axis=0)  # Label is the specfic row no to drop. Axis=0 for rows & 1 for cols.
        pd_df.to_csv("Client_Information.csv", index=False)
        print("Current Account deleted successfully!")
        print("-------------------------------------\n")
        time.sleep(0.2)


class SavingsAccount(Account):
    """ SavingAccount is a sub-class of Account class dealing with the user's savings and related operations.

    savings_index attribute is passed as parameter in various methods. It is list of the specific row where the user's
    account is. The list only has one element and is therefore accessed as savings_index[0] to pass in the actual row
    number in methods to access the any value of that row.

    Attributes
    -----------
    savings : int
    interest_rate = 0.1

    Methods
    -----------
    create_savings_account(self)
    deposit(self, savings_index)
    withdraw(self, savings_index)
    balance_inquiry(self, savings_index)
    interest_on_savings(self, savings_index)
    """

    def __init__(self, cnic, savings=0):
        """
        Parameters
        ----------
        self.savings
        self.interest_rate = 0.1
        """
        super().__init__(cnic)
        self.savings = savings
        self.interest_rate = 0.083

    def create_savings_account(self):
        """ Creates Savings Account by storing information in the file.

        CNIC, date, savings and last_date_paid (set to 0 initially) are saved in the Savings Account file.

        Parameters
        ---------
        self
        """
        today = datetime.date.today()
        lst = [self.cnic, today, self.savings, 0]
        s_df.loc[len(s_df)] = lst
        s_df.to_csv("Saving_Account_Info.csv", index=False)
        print("Your Savings Account has been successfully created!")
        print(f"Your current savings are: {self.savings} which will be incremented annually on the interest rate of 10%"
              f"and monthly on the rate of 0.83%")
    # Since, we are creating the savings account, there obviously no need to read and add as there will be no savings.

        TransactionHistory.store_customer_history(self.cnic, "Created Savings Account")

    def deposit(self, savings_index):
        """ Deposits money in savings balance. Balance is updated in the file.

        Parameters
        ----------
        self
        savings_index : lst
        """

        while True:
            try:
                print(f"Your current savings are {self.savings}.")
                s_deposit = int(input("Enter money to be deposited in your savings: "))
                assert s_deposit > 0
            except ValueError:
                print("Please enter the money only in numbers.")
            except AssertionError:
                print("Deposited money can't be negative!")
            else:
                new_savings = self.savings + s_deposit
                s_df.at[savings_index[0], "PrincipalAmount"] = new_savings
                s_df.to_csv("Saving_Account_Info.csv", index=False)
                print("Your savings balance has been updated!")
                print(f"Your new balance is Rs.{new_savings}.")
                print("---------------------------------\n")
                TransactionHistory.store_customer_history(self.cnic, f"Deposited Rs. {s_deposit}")
                break

    def withdraw(self, savings_index):
        """ Withdraws money from savings balance. Balance is updated in the file
        Parameters
        ----------
        self
        savings_index : lst
        """
        while True:
            try:
                print(f"Your current savings are {self.savings}.")
                s_withdraw = int(input("Enter money to be withdrawn: "))
                assert s_withdraw < self.savings
            except ValueError:
                print("Please enter the money only in numbers.")
            except AssertionError:
                print("You have insufficient funds for this operation. Please try again!")
            else:
                new_savings = self.savings - s_withdraw
                s_df.at[savings_index[0], "PrincipalAmount"] = new_savings
                s_df.to_csv("Saving_Account_Info.csv", index=False)
                print("Your savings balance has been updated!")
                print(f"Your new balance is Rs.{new_savings}.")
                time.sleep(0.1)
                print("---------------------------------\n")
                TransactionHistory.store_customer_history(self.cnic, f"Withdrew Rs. {s_withdraw}")
                break

    def balance_inquiry(self, savings_index):
        """ Balance inquiry of savings balance.

        Parameters
        ---------
        self
        savings_index : lst
        """

        bal_inquiry = s_df.at[savings_index[0], "PrincipalAmount"]
        print("Your current savings are Rs.", bal_inquiry, ".")
        time.sleep(0.1)
        print("--------------------------------------\n")
        TransactionHistory.store_customer_history(self.cnic, f"Balance Inquired: (Rs.{bal_inquiry})")

    def interest_on_savings(self, savings_index):
        """ This methods increments a customer's savings on a monthly basis.

        Method is run when the customer logs in. However many months have passed is multiplied with monthly
        incrementation and added to the balance.

        Parameters
        ---------
        self
        savings_index : lst
        """
        cur_date = datetime.date.today()
        last_date_inc = s_df.at[savings_index[0], "LastDateIncrement"]
        date_of_acc_creation = s_df.at[savings_index[0], "InitialDate"]
        date_of_acc_creation = datetime.datetime.strptime(date_of_acc_creation, "%Y-%m-%d")
        acc_creation_diff_months = (cur_date.year - date_of_acc_creation.year) * 12 + (cur_date.month - date_of_acc_creation.month)
        if last_date_inc == 0 and acc_creation_diff_months == 0:   # Since, it is intially set to 0.
            pass  # Pass as in don't do anything
        elif acc_creation_diff_months != 0 and last_date_inc == 0:  # Same month condition
            principal_amount = s_df.at[savings_index[0], "PrincipalAmount"]
            principal_amount += (principal_amount*self.interest_rate)*acc_creation_diff_months
            s_df.at[savings_index[0], "LastDateIncrement"] = cur_date
            s_df.at[savings_index[0], "PrincipalAmount"] = principal_amount
            s_df.to_csv("Saving_Account_Info.csv", index=False)
            # Incremented when customer logs in. Hence, the incrementation is multiplied with month difference
        elif last_date_inc != 0:
            last_date_inc = datetime.datetime.strptime(last_date_inc, "%Y-%m-%d")
            months = (cur_date.year - last_date_inc.year) * 12 + (cur_date.month - last_date_inc.month)
            if months > 0:
                principal_amount = s_df.at[savings_index[0], "PrincipalAmount"]
                principal_amount += (principal_amount * self.interest_rate) * acc_creation_diff_months
                s_df.at[savings_index[0], "LastDatePaid"] = cur_date
                s_df.at[savings_index[0], "PrincipalAmount"] = principal_amount
                s_df.to_csv("Saving_Account_Info.csv", index=False)
                # Incremented when customer logs in. Hence, the incrementation is multiplied with month difference

    @staticmethod
    def delete_account(index):
        """ Deletes savings account by removing row from Saving Accounts file.

        Parameters
        ----------
        index: lst
        """
        savings_df = pd.read_csv("Saving_Account_Info.csv")
        savings_df = savings_df.drop(labels=index[0], axis=0)
        # Label is the specific row no to drop. Axis=0 for rows & 1 for cols.

        savings_df.to_csv("Saving_Account_Info.csv", index=False)
        print("Savings Account deleted successfully!")
        print("-------------------------------------\n")
        time.sleep(0.2)


class LoanAccount(Account):
    def __init__(self, cnic, loan_duration=1, loan_due=1):
        """ Loan Account is a sub-class of Account class dealing with customer loans and related operations.

        Customer can be banned from the application if he/she does not pay his/her loans. This will happen by adding the
        customer's cnic to the blocked accounts file.
        loan_index attribute is passed as parameter in various methods. It is list of the specific row where the user's
        account is. The list only has one element and is therefore accessed as loan_index[0] to pass in the actual row
        number in methods to access the any value of that row.
        Loan payment starts one month after creation of account.
        Interest rate is o.1 (10%) annually and 0.00833(0.8%) monthly. Its multiplied with total loan and added to the
        loan per month.

        Attributes
        ----------
        cnic: int
        self.loan_duration: int
        self.loan_due: int
        self.interest_rate = 0.1
        self.interest_rate_per_month : int
        self.loan_per_month : int

        Methods
        -------
        create_loan_account(self)
        deposit(loan_index)
        withdraw(loan_index)
        balance_inquiry(loan_index)
        """
        super().__init__(cnic)
        self.loan_duration = loan_duration  # 12 for example
        self.loan_due = loan_due  # 120000
        self.interest_rate = 0.1  # 10% or 10/100 or 0.1
        self.interest_per_month = self.interest_rate/self.loan_duration  # 0.1/12 = 0.0083
        self.loan_per_month = self.loan_due / self.loan_duration + self.loan_due*self.interest_per_month
        # 120000/12 + (120000*0.0083) = 10000 + 996 = 10996 will be the total amount per month

    def create_loan_account(self, row_no, renewal=False):
        """  This method creates Loan Account by storing information in the file.

        For renewal of account, an argument, renewal, is made True (False by default) which alters certain print statements
        and the transaction history to be more appropriate for the renewal of the customer's loan account.

        Parameters
        -----------
        row_no: lst
        renewal : False
        """
        cur_date = datetime.date.today()
        loan_df.loc[len(loan_df)] = [self.cnic, cur_date, self.loan_due, self.loan_duration, self.loan_per_month, 0]
        if renewal is False:
            print("Your Loan Account has been successfully created!")
        else:
            print("Your Loan Account has been successfully renewed!")
        print(f"Your current loan is Rs. {self.loan_due} and duration is {self.loan_duration} months on the interest "
              f"rate of 10%")
        current_acc_bal = df.at[row_no[0], "CurrentBalance"]
        new_balance = current_acc_bal + self.loan_due
        df.at[row_no[0], "CurrentBalance"] = new_balance
        print(f"Your current account balance has been updated to {new_balance}")
        df.to_csv("Client_Information.csv", index=False)
        print("Your loan payment will start from next month!")
        print("Missed payments will only be entertained up to 6 months of taking the loan after which you will be "
              "banned from the bank and reported to law enforcements of the city.")
        time.sleep(0.1)
        print("--------------------------------------------\n")
        loan_df.to_csv("Loan_Account_Info.csv", index=False)
        if renewal is False:
            TransactionHistory.store_customer_history(self.cnic, f"Created Loan Account with loan Rs.{self.loan_due} "
                                                                 f"and duration as Rs.{self.loan_duration} with "
                                                                 f"interest rate as 10% annually and 0.83% monthly")
        else:
            TransactionHistory.store_customer_history(self.cnic, f"Renewed Loan Account with loan Rs. {self.loan_due}"
                                                                 f"and duration as Rs.{self.loan_duration} with"
                                                                 f"interest rate as 10% annually and 0.83% monthly.")

    def deposit(self, loan_index):
            """  Deposit Method i.e. Method for paying loans of LoanAccount. Loan due is updated in the file.

            Extra interest is charged if customer hasn't paid for more than one month. Exact loan is to be paid every
            month with interest rate. Loan due in file represents loan without the interest.

            Parameters
            ----------
            self
            loan_index
            """
            last_date_paid = loan_df.at[loan_index[0], "LastDatePaid"]
            last_date_paid = datetime.datetime.strptime(last_date_paid, "%Y-%m-%d")
            date_of_loan = loan_df.at[loan_index[0], "InitialDate"]
            date_of_loan = datetime.datetime.strptime(date_of_loan, "%Y-%m-%d")
            cur_date = datetime.date.today()
            initial_date_diff = (cur_date.year - date_of_loan.year) * 12 + (cur_date.month - date_of_loan.month)
            # Meaning difference of months from account formation to cur_date, which should be zero.
            # And if it is and last_date_paid is also which is what it is set to initially then that means that the
            # account was just formed this month.
            while True:
                try:
                    if last_date_paid == 0 and initial_date_diff == 0:  # Meaning loan was just taken.
                        print("Your loan payment starts from next month!")
                        print("Please try later!")
                        time.sleep(0.1)
                        print("---------------\n")
                        break
                    months = (cur_date.year - last_date_paid.year) * 12 + (cur_date.month - last_date_paid.month)
                    dep_loan = 0  # Variable Initialization to not raise error in else block.
                    initial_loan = months * self.loan_per_month  # Same here
                    if last_date_paid.month == cur_date.month:
                        print("Your loan for this month has been paid!")
                        time.sleep(0.1)
                        print("-------------------------------------\n")
                        break
                    elif months == 1:
                        print(f"The amount you have to pay for this month's loan is {self.loan_per_month}")
                        dep_loan = int(input("Enter this month's payment here: "))
                        assert dep_loan == self.loan_per_month
                    elif 1 < months <= 6:
                        interest_addition = months*(self.loan_per_month*self.interest_rate)
                        total_loan = initial_loan + interest_addition
                        print(f"You have not paid your monthly loan for {months} months now!")
                        print("You will be charged an extra interest fee on each months loan.")
                        print(f"Your initial total loans were Rs. {initial_loan} but as a result of extra interest have"
                              f"been increased to Rs. {total_loan}")
                        loan_pay = int(input("Please duly enter the correct amount of money here: "))
                        assert loan_pay == total_loan
                except ValueError:
                    print("Please enter only numbers for the money for depositing loan!")
                except AssertionError:
                    print("Please enter the correct amount of money.")
                else:
                    if months == 1:
                        remaining_loan = self.loan_due - dep_loan  # B/c loan due doesn't account for interest.
                        loan_df.at[loan_index[0], "LoanDue"] = remaining_loan
                        TransactionHistory.store_customer_history(self.cnic, f"Deposited Loan: Rs.{dep_loan}")
                    elif 1 < months <= 6:
                        remaining_loan = self.loan_due - initial_loan  # B/c interest fee was extra for late payment.
                        loan_df.at[loan_index[0], "LoanDue"] = remaining_loan
                        TransactionHistory.store_customer_history(self.cnic, f"Deposited Loan: Rs.{total_loan}")
                    loan_df.at[loan_index[0], "LastDatePaid"] = cur_date
                    print("Transaction Successful!")
                    time.sleep(0.1)
                    print("--------------------------------------\n")
                    loan_df.to_csv("Loan_Account_Info.csv", index=False)

    def balance_inquiry(self, loan_index):
        """  Prints the loan due on the customer.

        Parameters
        ---------
        self
        loan_index
        """

        loan_inquiry = loan_df.at[loan_index[0], "LoanDue"]
        print(f"Your remaining loan is Rs. {loan_inquiry} with a monthly interest rate of 10%.")
        time.sleep(0.1)
        print("--------------------------------------\n")
        TransactionHistory.store_customer_history(self.cnic, f"Checked Loan: Rs.{loan_inquiry}")

    @staticmethod
    def loan_check_message(loan_index):
        """ This method is called to check a person's loan payment. It is called upon login.

        If loans haven't been paid for a month, the customer will be asked whether they want to pay now or not.
        If more than one month and less than six months, access will be restricted.
        If more than six months, account will be blocked!

        Parameters
        ---------
        loan_index : lst
        """

        loan_due = loan_df.at[loan_index[0], "LoanDue"]
        if loan_due != 0:
            cur_date = datetime.date.today()
            date_of_loan = loan_df.at[loan_index[0], "InitialDate"]
            date_of_loan = datetime.datetime.strptime(date_of_loan, "%Y-%m-%d")
            last_date_paid = loan_df.at[loan_index[0], "LastDatePaid"]
            acc_creation_months_diff = (cur_date.year - date_of_loan.year) * 12 + (cur_date.month - date_of_loan.month)
            if acc_creation_months_diff == 0 and last_date_paid == 0:
                pass
            # This is the condition where the customer hasn't paid from the start
            elif acc_creation_months_diff != 0 and last_date_paid == 0:

                if acc_creation_months_diff == 1:
                    print("Your loan for this month has not paid.")
                    return 1  # This will just remind the customer to pay and not restrict access or anything.

                elif 1 < acc_creation_months_diff <= 6:
                    print(f"You have not paid your loan for the past {acc_creation_months_diff} months!")
                    print("Access to your account is currently blocked!")
                    print("Pay the loan to access your account!")
                    print("Remember if payment is paid within 6 months from the last date of payment then, your account"
                          "will be banned and you will be reported to the police.")
                    return 2   # This will restrict access if payment is not paid

                elif acc_creation_months_diff > 6:
                    print("Your have not paid your loans for more than six months!")
                    return 3   # Account will be blocked

            # This is the condition where the customer has paid but stopped paying from a certain date
            elif last_date_paid != 0:
                last_date_paid = datetime.datetime.strptime(last_date_paid, "%Y-%m-%d")
                months = (cur_date.year - last_date_paid.year) * 12 + (cur_date.month - last_date_paid.month)

                if months == 1:
                    print("Your loan for this month has not paid.")
                    return 1  # This will just remind the customer to pay and not restrict access or anything.

                elif 1 < months <= 6:
                    print(f"You have not paid your loan for the past {months} months!")
                    print("Access to your account is currently blocked!")
                    print("Pay the loan to access your account!")
                    print("Remember if payment is paid within 6 months from the last date of payment then, your account"
                          "will be banned and you will be reported to the police.")
                    return 2   # This will restrict access if payment is not paid

                elif months > 6:
                    print("Your have not paid your loans for more than six months!")
                    return 3   # Account will be blocked

    @staticmethod
    def delete_account(index):
        """ Deletes loan account if loans have been paid. Deletes by removing row from Loan Accounts file.

        Parameters
        ----------
        index: lst
        """
        loan_pd_df = pd.read_csv("Loan_Account_Info.csv")
        loan_due = loan_pd_df.at[index[0], "LoanDue"]
        if loan_due == 0:
            loan_pd_df = loan_pd_df.drop(labels=index[0], axis=0)  # Deleting loan account if any.
            loan_pd_df.to_csv("Loan_Account_Info.csv", index=False)
            print("Loan Account deleted successfully!")
            print("----------------------------------\n")
            time.sleep(0.2)
        else:
            print("Cannot delete loan account!!")
            print("Loans have not yet been paid!")
            print("------------------------------\n")
            time.sleep(0.2)


obj = Interface()


