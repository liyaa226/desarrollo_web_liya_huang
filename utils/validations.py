import re
import filetype

def validate_nombre(value):
    if(not value):
        return False
    lengthValid = len(value) > 4
    return lengthValid


def validate_password(value):
    malas = ["1234", "admin1", "odio a mis Aux >:(2"]
    return bool(re.search(r"\d", value)) and not value in malas

#las validaciones como el formato específico están implementadas en validation.js
def validate_email(value):
    if(not value):
        return False
    lengthValid = len(value) > 10 
    return lengthValid and "@" in value

def validate_phone(value):
    if(not value):
        return False
    lengthValid = len(value) > 8
    return lengthValid


def validate_region(value):
    if(not value):
        return False
    lengthValid = len(value) > 3
    return lengthValid

def validate_comuna(value):
    if(not value):
        return False
    lengthValid = len(value) > 3
    return lengthValid

def validate_login_user(email):
    return validate_email(email)

def validate_register_user(nombre, email, phone, region, comuna):
    return (
        validate_nombre(nombre) and 
        validate_email(email) and 
        validate_phone(phone) and
        validate_region(region) and
        validate_comuna(comuna)
    )

def validate_lugar(lugar):
    if(not lugar):
        return False
    lengthValid = len(lugar) > 3
    return lengthValid


def validate_avistamiento(nombre_ave, lugar, fecha, hora, archivo):
    return (
        validate_lugar(lugar) and
        validate_img(archivo)
    )


def validate_img(archivo):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    ALLOWED_MIMETYPES = {"image/jpeg", "image/png", "image/gif"}

    # check if a file was submitted
    if archivo is None:
        return False

    # check if the browser submitted an empty file
    if archivo.filename == "":
        return False
    
    # check file extension
    ftype_guess = filetype.guess(archivo)
    if ftype_guess.extension not in ALLOWED_EXTENSIONS:
        return False
    # check mimetype
    if ftype_guess.mime not in ALLOWED_MIMETYPES:
        return False
    return True


