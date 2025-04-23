# Run only this file for cli system.

from database.model import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# import hashlib
import bcrypt
import getpass
from auth.mail import signup_mail, reset_mail

engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

button = input('Enter your button: login/signup: ')

def signup():
    username = input('Enter signup username: ')
    existing_user = session.query(User).filter_by(username = username).first()
    
    if existing_user:
        print('Username already exists.')
        raise ValueError('username already exists')
    
    # password = input('Enter signup password: ')
    password = getpass.getpass(prompt = 'Enter signup password: ')
    password_c = getpass.getpass(prompt = 'confirm signup password: ')
    
    # hash_object = hashlib.sha256()
    # hash_object.update(password.encode())
    # hashed_password = hash_object.hexdigest()
    
    if password.strip().lower() == password_c.strip().lower():
        password_bytes = password.encode()
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        user = User(username = username, password = hashed)
        session.add(user)
        session.commit()
        
        print('Signup successful.')    
        mail_login = input('do you want to recieve an email for signup : yes/no : ')
        
        if mail_login == 'yes':
            signup_mail()
            
    else:
        raise ValueError('password does not match try again')

def login():
    username = input('Enter your login username: ')
    
    # password = input('Enter your login password: ')
    password = getpass.getpass(prompt = 'Enter login password: ')
    
    ip_password = password.encode()
    user = session.query(User).filter_by(username = username).first()
    
    if user and bcrypt.checkpw(ip_password, user.password):
        print('Login successful')
        print('you will be logged out now! You can only change you password')
        
        reset_password_yn = input('do you want to change you current passowrd : yes/no : ')
        if reset_password_yn.strip().lower() == 'yes':
            reset_password()
            
            mail_reset = input('do you want to recieve an email for password reset : yes/no : ')
            if mail_reset.strip().lower() == 'yes':
                reset_mail()
            
        else:
            print('logged out')
        
    else:
        raise ValueError('Wrong credentials')

def quick_login(login_yn: str):
    if login_yn.lower() == 'yes':
        login()
        
    elif login_yn.lower() == 'no':
        exit()
        
    else:
        raise ValueError('No option identified')
    
def reset_password():
    username = input('enter you username : ')
    # current_password = input('enter you current password : ')
    
    current_password = getpass.getpass(prompt = 'Enter your current password: ')
    
    user = session.query(User).filter_by(username=username).first()
    ipc_password = current_password.encode()
    
    if user and bcrypt.checkpw(ipc_password, user.password):
        # new_password = input('enter you new password : ')
        
        new_password = getpass.getpass(prompt = 'Enter your new password: ')
        new_password_c = getpass.getpass(prompt = 'confirm your new password: ')
        
        if new_password == new_password_c:
            bytes_newpassword = new_password.encode()
            
            hashed_password = bcrypt.hashpw(bytes_newpassword, bcrypt.gensalt())
            user.password = hashed_password
            
            session.commit()
            
        else:
            raise ValueError('password does not match try again')
        
    else:
        raise ValueError('incorrect username or password')

if button.strip().lower() == 'signup':
    signup()
    
    login_yn = input('Do you want to login now : yes/no: ')
    quick_login(login_yn)

elif button.strip().lower() == 'login':
    login()

else:
    raise ValueError('No options identified')
