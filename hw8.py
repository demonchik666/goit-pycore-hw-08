from collections import UserDict
from datetime import datetime as dt
from datetime import timedelta as td
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # реалізація класу
	pass

class Phone(Field):
    #додавання валідації для номера телефону
    def __init__(self, value):
        if not (value.isdigit() and len(value)==10):
            raise ValueError(f"Phone number {value} must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = dt.strptime(value, '%d.%m.%Y')
            if birthday_date > dt.today():
                raise ValueError("Birthday cannot be in the future.")
            birthday_date_str = birthday_date.strftime('%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.value = birthday_date_str
        
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    #Додавання номера телефону до запису
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        return None

    #Зміна номера телефону з валідацією
    def edit_phone(self, old_phone, new_phone):
        new_phone = Phone(new_phone)  # Перевірка валідності нового номера
        self.remove_phone(old_phone)  # Знаходимо та видаляємо старий номер
        self.phones.append(new_phone) # Додаємо новий валідний номер
        return None

    #Пошук номера телефону в записі
    def find_phone(self, phone):
        for given_phone in self.phones:
            if given_phone.value == phone:
                return given_phone
        return None
    
    #Видалення номера телефону з запису
    def remove_phone(self, phone):
        if self.find_phone(phone) is None:
            raise ValueError(f"Phone number {phone} not found in record.")
        else: self.phones.remove(self.find_phone(phone))
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    # реалізація класу адресної книги
    def add_record(self, record):
        self.data[record.name.value] = record

    # Додавання запису до адресної книги
    def find(self, name) -> Record:
        return self.data.get(name, None)
    
    # Пошук запису за ім'ям
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    # Повертає найближчі дні народження записів з адресної книги
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = dt.today()
        for record in self.values():
            if record.birthday is None:
                continue
        # Беремо саме дату (string) з об'єкта Birthday
            birthday_date = dt.strptime(record.birthday.value, ('%d.%m.%Y'))
        # Створюємо дату дня народження на цей рік
            birthday_this_year = birthday_date.replace(year=today.year)
        # Якщо день народження вже минув цього року — переносимо на наступний рік
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            days_until_birthday = (birthday_this_year - today).days
            if 0 <= days_until_birthday <= days:
            # Перевірка на вихідні — переносимо привітання на понеділок
                if birthday_this_year.weekday() >= 5:
                    days_ahead = 7 - birthday_this_year.weekday()
                    birthday_this_year += td(days=days_ahead)
                congratulation_date_str = birthday_this_year.strftime("%d.%m.%Y")
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date_str
                })
        return upcoming_birthdays

    def __str__(self):
        records = [str(record) for record in self.data.values()]
        return "\n".join(records) if records else "Address book is empty."
    
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def input_error(func): # Decorator to handle input errors
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Wrong parameters."
        except IndexError:
            return "Wrong parameters."
        except KeyError:
            return "Contact not found."
    return inner

@input_error
def parse_input(user_input): # Function to parse user input
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook): # Function to change a contact's phone number
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None: # Check if the contact exists
        return "Contact not found."
    else:
        record.edit_phone(old_phone, new_phone) # Change the first phone number
        return "Contact changed." 
    
@input_error
def phone_number(args, book: AddressBook): # Function to get a contact's phone number
    name = args[0]
    record = book.find(name)
    if record is None: # Check if the contact exists
        return "Contact not found."
    else:
        result = ""
        for phone in record.phones:
            result += f"{phone.value}\n"
        return result
    
@input_error
def add_birthday(args, book: AddressBook): # Function to add a birthday to a contact
    name, birthday, *_ = args
    record = book.find(name)
    if record is None: # Check if the contact exists
        return "Contact not found."
    else:
        record.add_birthday(birthday)
        return "Birthday added."
    
@input_error
def show_birthday(args, book: AddressBook): # Function to show a contact's birthday
    name, *_ = args
    record = book.find(name)
    if record is None: # Check if the contact exists
        return "Contact not found."
    elif record.birthday is None: # Check if the contact has a birthday
        return "Birthday not found."
    else:
        return f"{record.name.value}'s birthday is on {record.birthday.value}."
    
@input_error
def birthdays(book: AddressBook): # Function to show all contacts with birthdays
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:  # Check if there are any upcoming birthdays
        return "No upcoming birthdays in the next 7 days."
    result = "Contacts with upcoming birthdays:\n"
    for record in upcoming_birthdays:
        result += f"{record['name']}: {record['congratulation_date']}\n"
    return result

def print_all(book: AddressBook): # Function to print all contacts
    if len(book) == 0: # Check if there are any contacts
        return "No contacts found."
    else:
        result = "Contacts: \n"
        for record in book.values(): # Print all contacts
            result += f"{record.name.value}: "
            if record.phones:
                result += ", ".join(phone.value for phone in record.phones)
            if record.birthday:
                result += f" | Birthday: {record.birthday.value}"
            result += "\n"
        return result
    

def main():
    book = load_data("addressbook.pkl")  # Load the address book from file
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(phone_number(args, book))

        elif command == "all":
            print(print_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")
    save_data(book)

if __name__ == "__main__":
    main()