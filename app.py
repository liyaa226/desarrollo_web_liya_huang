from flask import Flask, abort, flash, jsonify, request, render_template, redirect, url_for, session
from utils.validations import (
    validate_login_user,
    validate_register_user,
    validate_avistamiento,
    validate_comentario,
)
from database import db
import filetype
import os
from uuid import uuid4

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)


app.secret_key = "s3cr3t_k3y"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["NOTAS_API_URL"] = os.environ.get(
    "NOTAS_API_URL",
    "http://localhost:8080/api/avistamientos/notas",
)
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

# --- Auth Routes ---
@app.route("/registro_voluntario.html", methods=["GET", "POST"])
def registro_voluntario():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        phone = request.form.get("phone")
        region = request.form.get("select-region")
        comuna = request.form.get("select-comuna")
        if validate_register_user(nombre, email, phone, region, comuna):
            # try to register user
            status, msg = db.register_user(nombre, email, phone, region, comuna)
            if status:
                session["user"] = email
                flash("¡Registro de voluntario completado!", "success")
                return redirect(url_for("index"))
            error = msg
        else:
            error = "Revisa los datos: nombre, correo, teléfono, región y comuna deben ser válidos."

        return render_template("registro_voluntario.html", error=error)
    
    elif request.method == "GET":
        if session.get("user", None):
            return redirect(url_for("informar_avistamiento"))
        else:
            return render_template("registro_voluntario.html")


@app.route("/iniciar_sesion.html", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "POST":
        email = request.form.get("email")
        error = ""
        if validate_login_user(email):
            # try to login
            status, msg = db.login_user(email)
            if status:
                # set user field in session
                session["user"] = email
                return redirect(url_for("informar_avistamiento"))
            error += msg
        else:
            error += "Uno de los campos no es valido."

        print(error)

        return render_template("inicio_sesion.html",error=error)
    
    elif request.method == "GET":
        if session.get("user", None):
            return redirect(url_for("index"))
        else:
            return render_template("inicio_sesion.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user", None)
    return redirect(url_for("iniciar_sesion"))


# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    avistamientos = db.get_ultimos_avistamientos(2)
    
    #carga los últimos 2 avistamientos
    return render_template("index.html", avistamientos=avistamientos)

@app.route("/informar_avistamiento.html", methods=["POST", 'GET'])
def informar_avistamiento():
    username = session.get("user", None)
    if username is None:
        return redirect(url_for("iniciar_sesion"))

    if request.method == "GET":
        return render_template("informar_avistamiento.html")

    nombre_ave = request.form.get("nombre_ave", "").strip()
    lugar = request.form.get("lugar")
    fecha = request.form.get("fecha")
    hora = request.form.get("hora")
    archivos = request.files.getlist("archivos")
    errores = validate_avistamiento(nombre_ave, lugar, fecha, hora, archivos)
    if errores:
        return render_template("informar_avistamiento.html", errores=errores)

    user = db.get_voluntario_by_email(username)
    ave_id = db.get_ave_by_name(nombre_ave)
    if user is None:
        session.pop("user", None)
        return redirect(url_for("iniciar_sesion"))
    if ave_id is None:
        return render_template(
            "informar_avistamiento.html",
            errores=["El ave seleccionada no existe en la base de datos."],
        )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    registros = []
    for archivo in archivos:
        media_type = filetype.guess(archivo.stream)
        archivo.stream.seek(0)
        nombre_archivo = f"{uuid4().hex}.{media_type.extension}"
        archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo))
        ruta_archivo = f"uploads/{nombre_archivo}"
        registros.append((nombre_archivo, ruta_archivo))

    db.create_avistamiento(user.id, ave_id, fecha, hora, lugar, registros)
    flash("¡Avistamiento enviado!", "success")
    return redirect(url_for("index"))

@app.route("/listado_avistamientos.html", methods=['GET'])
def listado_avistamientos():
  
    avistamientos = db.get_avistamientos()

    return render_template("listado_avistamientos.html", avistamientos=avistamientos)

@app.route("/buscador_avistamientos.html", methods=["GET"])
def buscador_avistamientos():
    return render_template("buscador_avistamientos.html")

@app.route("/api/avistamientos/buscar", methods=["GET"])
def buscar_avistamientos():
    termino = request.args.get("q", "").strip()
    if not termino:
        return jsonify([])
    return jsonify(db.buscar_avistamientos(termino))

@app.route("/avistamientos/<int:avistamiento_id>", methods=["GET"])
def detalle_avistamiento(avistamiento_id):
    avistamiento = db.get_avistamiento_by_id(avistamiento_id)
    if avistamiento is None:
        abort(404)

    nombre_ave = db.get_ave_by_id(avistamiento.ave_id)
    archivos = db.get_archivos_by_avistamiento_id(avistamiento_id)
    for archivo in archivos:
        extension = os.path.splitext(archivo["ruta_archivo"])[1].lower()
        archivo["es_video"] = extension in {
            ".mp4", ".webm", ".mov", ".avi", ".mkv", ".mpeg", ".mpg"
        }
    return render_template(
        "detalle_avistamiento.html",
        avistamiento=avistamiento,
        nombre_ave=nombre_ave,
        archivos=archivos
    )

@app.route("/api/avistamientos/<int:avistamiento_id>/comentarios", methods=["GET"])
def comentarios_avistamiento(avistamiento_id):
    if db.get_avistamiento_by_id(avistamiento_id) is None:
        return jsonify({"error": "El avistamiento no existe."}), 404

    comentarios = db.get_comentarios_by_avistamiento(avistamiento_id)
    return jsonify([
        {
            "nombre": comentario.nombre,
            "texto": comentario.texto,
            "fecha": comentario.fecha.isoformat(),
        }
        for comentario in comentarios
    ])

@app.route("/api/avistamientos/<int:avistamiento_id>/comentarios", methods=["POST"])
def agregar_comentario(avistamiento_id):
    if db.get_avistamiento_by_id(avistamiento_id) is None:
        return jsonify({"error": "El avistamiento no existe."}), 404

    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"error": "Envía el comentario como un objeto JSON."}), 400

    nombre = datos.get("nombre")
    texto = datos.get("texto")
    if not validate_comentario(nombre, texto):
        return jsonify({
            "error": (
                "El nombre debe tener entre 3 y 50 caracteres y el comentario "
                "entre 5 y 300 caracteres."
            )
        }), 400

    db.create_comentario(avistamiento_id, nombre.strip(), texto.strip())
    return jsonify({"mensaje": "Comentario agregado."}), 201

@app.route("/estadisticas.html", methods=["GET"])
def estadisticas():
    return render_template("estadisticas.html")

@app.route("/api/estadisticas", methods=["GET"])
def estadisticas_datos():
    return jsonify(db.get_estadisticas())

if __name__ == "__main__":
    app.run(debug=True)
