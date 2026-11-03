from flask import Flask, abort, flash, jsonify, request, render_template, redirect, url_for, session
from utils.validations import (
    validate_login_user,
    validate_register_user,
    validate_avistamiento,
    validate_comentario,
)
from database import db
from werkzeug.utils import secure_filename
import hashlib
import filetype
import os

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)


app.secret_key = "s3cr3t_k3y"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
        error = ""
        if validate_register_user(nombre, email, phone, region, comuna):
            # try to register user
            status, msg = db.register_user(nombre, email, phone, region, comuna)
            if status:
                # set user field in session
                session["user"] = email
                return redirect(url_for("informar_avistamiento"))
            error += msg
        else:
            error += "Uno de los campos no es valido."

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

    tipo = request.form.get('tipo')
    nombre_ave = request.form.get("nombre_ave", "").strip()
    lugar = request.form.get("lugar")
    fecha = request.form.get("fecha")
    hora = request.form.get("hora")
    archivo = request.files.get("archivo")

    if validate_avistamiento(nombre_ave, lugar, fecha, hora, archivo):
        # 1. generate random name for archivo
        _filename = hashlib.sha256(
            secure_filename(archivo.filename) # nombre del archivo
            .encode("utf-8") # encodear a bytes
            ).hexdigest()
        _extension = filetype.guess(archivo).extension
        img_filename = f"{_filename}.{_extension}"

        # 2. save img as a file
        ruta_fisica= (os.path.join(app.config["UPLOAD_FOLDER"], img_filename))
        archivo.save(ruta_fisica)
        ruta_archivo = os.path.join("uploads", img_filename).replace("\\", "/")


        # 3. guardar avistamiento en la base de datos
        user = db.get_voluntario_by_email(username)
        ave_id = db.get_ave_by_name(nombre_ave)
        if ave_id is None:
            error = "El ave seleccionada no existe en la base de datos"
            return render_template(
                "informar_avistamiento.html",
                error=error
            )
        db.create_avistamiento(user.id, ave_id, fecha, hora, lugar, img_filename, ruta_archivo)
        flash("¡Avistamiento enviado!", "success")
        return redirect(url_for("index"))
    
    return render_template("informar_avistamiento.html")

@app.route("/listado_avistamientos.html", methods=['GET'])
def listado_avistamientos():
  
    avistamientos = db.get_avistamientos()

    return render_template("listado_avistamientos.html", avistamientos=avistamientos)

@app.route("/avistamientos/<int:avistamiento_id>", methods=["GET"])
def detalle_avistamiento(avistamiento_id):
    avistamiento = db.get_avistamiento_by_id(avistamiento_id)
    if avistamiento is None:
        abort(404)

    nombre_ave = db.get_ave_by_id(avistamiento.ave_id)
    archivo = db.get_ruta_archivo_by_avistamiento_id(avistamiento_id)
    extension = os.path.splitext(archivo or "")[1].lower()
    es_video = extension in {".mp4", ".webm", ".mov", ".avi", ".mkv", ".mpeg", ".mpg", ".3gp", ".wmv", ".flv"}
    return render_template(
        "detalle_avistamiento.html",
        avistamiento=avistamiento,
        nombre_ave=nombre_ave,
        archivo=archivo,
        es_video=es_video
    )

@app.route("/api/avistamientos/<int:avistamiento_id>/comentarios", methods=["GET"])
def comentarios_avistamiento(avistamiento_id):
    if db.get_avistamiento_by_id(avistamiento_id) is None:
        return jsonify({"error": "El avistamiento no existe."}), 404

    return jsonify(db.get_comentarios_by_avistamiento(avistamiento_id))

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
