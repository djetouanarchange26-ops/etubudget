current_user_id = None
current_username = None

def set_user(user_id: int, username: str):
    global current_user_id, current_username
    current_user_id  = user_id
    current_username = username

def clear_user():
    global current_user_id, current_username
    current_user_id  = None
    current_username = None