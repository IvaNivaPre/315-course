import re


def validate_email(email):
    """
    Validate email format
    Returns: dict with 'is_valid' and 'message'
    """
    if not email or not email.strip():
        return {"is_valid": False, "message": "Email is required"}
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return {"is_valid": False, "message": "Please enter a valid email address"}
    
    return {"is_valid": True, "message": "Email is valid"}


def validate_password(password, confirm_password=None):
    """
    Validate password strength and confirmation
    Returns: dict with 'is_valid' and 'message'
    """
    if not password:
        return {"is_valid": False, "message": "Password is required"}
    
    # Check minimum length
    if len(password) < 6:
        return {"is_valid": False, "message": "Password must be at least 6 characters long"}
    
    # Check password confirmation if provided
    if confirm_password is not None and password != confirm_password:
        return {"is_valid": False, "message": "Passwords do not match"}
    
    return {"is_valid": True, "message": "Password is valid"}


def validate_nickname(nickname):
    """
    Validate nickname
    Returns: dict with 'is_valid' and 'message'
    """
    if not nickname or not nickname.strip():
        return {"is_valid": False, "message": "Nickname is required"}
    
    # Check minimum length
    if len(nickname.strip()) < 3:
        return {"is_valid": False, "message": "Nickname must be at least 3 characters long"}
    
    # Check maximum length
    if len(nickname.strip()) > 30:
        return {"is_valid": False, "message": "Nickname must be less than 30 characters"}
    
    # Check for allowed characters (letters, numbers, underscores, hyphens)
    if not re.match(r'^[a-zA-Z0-9_-]+$', nickname):
        return {"is_valid": False, "message": "Nickname can only contain letters, numbers, underscores and hyphens"}
    
    return {"is_valid": True, "message": "Nickname is valid"}


# For backward compatibility with login form
def simple_validate_email(email):
    """Simple email validation for login form"""
    result = validate_email(email)
    return result["is_valid"]