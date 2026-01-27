from flask import session, redirect, url_for

USERS = {"admin": "password123"}

def check_login(username, password):
    if username in USERS and USERS[username] == password:
        session['user'] = username
        return True
    return False

def is_authenticated():
    return 'user' in session
