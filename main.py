from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
from database.model import User, Base
import sys

if 'auth.mail' in sys.modules:
    del sys.modules['auth.mail']

from auth.mail_ui import signup_mail, reset_mail

engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Authentication API")
templates = Jinja2Templates(directory="templates")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    
    if user and bcrypt.checkpw(password.encode(), user.password):
        return templates.TemplateResponse(
            "password_reset.html", 
            {"request": request, "username": username}
        )
    else:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Incorrect username or password"}
        )

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirmation: str = Form(...),
    send_email: bool = Form(False),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse(
            "signup.html", 
            {"request": request, "error": "Username already exists"}
        )
    
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        return templates.TemplateResponse(
            "signup.html", 
            {"request": request, "error": "Email address already in use"}
        )
    
    if password != password_confirmation:
        return templates.TemplateResponse(
            "signup.html", 
            {"request": request, "error": "Passwords do not match"}
        )
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    new_user = User(username=username, password=hashed_password, email=email)
    db.add(new_user)
    db.commit()
    
    if send_email:
        try:
            signup_mail(email)
        except Exception as e:
            print(f"Email sending failed: {e}")
    
    return templates.TemplateResponse(
        "signup_success.html", 
        {"request": request, "send_email": send_email}
    )

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset.html", {"request": request})

@app.post("/reset-password", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    username: str = Form(...),
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirmation: str = Form(...),
    send_email: bool = Form(False),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return templates.TemplateResponse(
            "reset.html", 
            {"request": request, "error": "User not found"}
        )
    
    if not bcrypt.checkpw(current_password.encode(), user.password):
        return templates.TemplateResponse(
            "reset.html", 
            {"request": request, "error": "Incorrect current password"}
        )
    
    if new_password != new_password_confirmation:
        return templates.TemplateResponse(
            "reset.html", 
            {"request": request, "error": "New passwords do not match"}
        )
    
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    user.password = hashed_password
    db.commit()
    
    if send_email and user.email:
        try:
            reset_mail(user.email)
        except Exception as e:
            print(f"Email sending failed: {e}")
    
    return templates.TemplateResponse(
        "reset_success.html", 
        {"request": request, "send_email": send_email}
    )

@app.post("/send-reset-email")
async def send_reset_email(
    request: Request,
    username: str = Form(...),
    send_email: bool = Form(False),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    
    if send_email and user and user.email:
        try:
            reset_mail(user.email)
        except Exception as e:
            print(f"Email sending failed: {e}")
    
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
async def logout():
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)