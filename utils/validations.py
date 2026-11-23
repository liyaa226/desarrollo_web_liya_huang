from datetime import date, datetime
import re
import filetype

def validate_nombre(value):
    return isinstance(value, str) and len(value.strip()) >= 4


def validate_password(value):
    malas = ["1234", "admin1", "odio a mis Aux >:(2"]
    return bool(re.search(r"\d", value)) and not value in malas

# La validación del cliente complementa estas comprobaciones del servidor.
def validate_email(value):
    return (
        isinstance(value, str)
        and len(value) >= 6
        and len(value) <= 254
        and re.fullmatch(
            r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
            r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}",
            value,
        ) is not None
    )

def validate_phone(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9]{8,15}", value) is not None


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
    return isinstance(lugar, str) and len(lugar.strip()) >= 4


def validate_avistamiento(nombre_ave, lugar, fecha, hora, archivos):
    errores = []
    if not isinstance(nombre_ave, str) or not nombre_ave.strip():
        errores.append("Selecciona o ingresa el nombre del ave.")
    if not validate_lugar(lugar):
        errores.append("El lugar debe tener al menos 4 caracteres.")

    try:
        fecha_objeto = datetime.strptime(fecha or "", "%Y-%m-%d").date()
        if fecha_objeto.isoformat() != fecha:
            raise ValueError
    except ValueError:
        errores.append("Ingresa una fecha válida.")
    else:
        if fecha_objeto > date.today():
            errores.append("La fecha del avistamiento no puede ser futura.")

    if hora and re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", hora) is None:
        errores.append("La hora debe tener formato HH:MM.")

    archivos = [archivo for archivo in archivos if archivo and archivo.filename]
    if not archivos:
        errores.append("Adjunta al menos un archivo.")
    elif len(archivos) > 5:
        errores.append("Puedes adjuntar hasta 5 archivos.")
    elif any(not validate_media(archivo) for archivo in archivos):
        errores.append("Cada archivo debe ser una imagen o video válido.")

    return errores

def validate_comentario(nombre, texto):
    if not isinstance(nombre, str) or not isinstance(texto, str):
        return False

    nombre = nombre.strip()
    texto = texto.strip()
    return 3 <= len(nombre) <= 50 and 5 <= len(texto) <= 300


def validate_media(archivo):
    image_types = {"image/jpeg", "image/png", "image/gif"}
    video_types = {
        "video/mp4",
        "video/webm",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
        "video/mpeg",
    }

    if archivo is None or not archivo.filename:
        return False

    try:
        archivo.stream.seek(0)
        media_type = filetype.guess(archivo.stream)
    finally:
        archivo.stream.seek(0)

    return media_type is not None and media_type.mime in image_types.union(video_types)

