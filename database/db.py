from sqlalchemy import create_engine, Column, Integer, BigInteger, String, ForeignKey, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime



#nombre de la base de datos
DB_NAME = "tarea2"
DB_USERNAME = "cc5002"
DB_PASSWORD = "programacionweb"
DB_HOST = "localhost"
DB_PORT = 3306

DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# --- Models ---

class Voluntario(Base):
    __tablename__ = 'voluntario'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telefono = Column(String(255), nullable=True)
    fecha_registro = Column(DateTime, nullable=False, default=datetime.now)
    comuna_id = Column(Integer, nullable=False)

    avistamientos = relationship("Avistamiento", back_populates="voluntarios")

class Avistamiento(Base):
    __tablename__ = 'avistamiento'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    voluntario_id = Column(ForeignKey('voluntario.id'), nullable=False)
    ave_id = Column(Integer, nullable=False)
    #si no se registra la hora de avistamiento, se usa la hora actual por defecto para guardarla en la base de datos 
    fecha_hora = Column(DateTime, nullable=False, default=datetime.now) 
    lugar = Column(String(200), nullable=True)
    descripcion = Column(String(500), nullable=True)

    voluntarios = relationship("Voluntario", back_populates="avistamientos")
    registros = relationship("Registro", back_populates="avistamientos")

class Registro(Base):
    __tablename__ = 'registro'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ruta_archivo = Column(String(300), nullable=False)
    nombre_archivo = Column(String(300), nullable=False)
    avistamiento_id = Column(ForeignKey('avistamiento.id'), nullable=False)

    avistamientos = relationship("Avistamiento", back_populates="registros")

# --- Database Functions ---

def get_voluntario_by_id(id):
    session = SessionLocal()
    voluntario = session.query(Voluntario).filter_by(id=id).first()
    session.close()
    return voluntario

def get_voluntario_by_nombre(nombre):
    session = SessionLocal()
    voluntario = session.query(Voluntario).filter_by(nombre=nombre).first()
    session.close()
    return voluntario

def get_voluntario_by_email(email):
    session = SessionLocal()
    voluntario = session.query(Voluntario).filter_by(email=email).first()
    session.close()
    return voluntario

def get_voluntario_by_telefono(telefono):
    session = SessionLocal()
    voluntario = session.query(Voluntario).filter_by(telefono=telefono).first()
    session.close()
    return voluntario


def get_voluntarios_by_comuna(comuna_id):
    session = SessionLocal()
    voluntarios = session.query(Voluntario).filter_by(comuna_id=comuna_id).all()
    session.close()
    return voluntarios



def create_voluntario(nombre, email, comuna_id, telefono):
    session = SessionLocal()
    
    # Usamos la fecha y hora exacta de este momento
    fecha_registro = datetime.now()
        
    new_voluntario = Voluntario(
        nombre=nombre, 
        email=email, 
        telefono=telefono, 
        comuna_id=comuna_id
    )
    #SQLAlchemy pondrá automáticamente la fecha_hora cuando cree el voluntario.
    session.add(new_voluntario)
    session.commit()
    session.close()
    

def get_avistamiento(page_size):
    session = SessionLocal()
    avistamientos = session.query(Avistamiento).limit(page_size).all()
    session.close()
    return avistamientos

def get_ultimos_avistamientos(page_size):
    session = SessionLocal()
    ultimos_avistamientos = session.query(Avistamiento).order_by(Avistamiento.id.desc()).limit(page_size).all()
    session.close()
    return ultimos_avistamientos

def get_avistamiento_by_id(id):
    session = SessionLocal()
    avistamientos = session.query(Avistamiento).filter_by(id=id).first()
    session.close()
    return avistamientos

def create_avistamiento(voluntario_id ,ave_id, fecha, hora, lugar, nombre_archivo, ruta_archivo):
    session = SessionLocal()

    # Hora es opcional
    if hora:
        hora_objeto = datetime.strptime(hora, "%H:%M").time()
    else:
        hora_objeto = datetime.now().time()

    fecha_objeto = datetime.strptime(fecha, "%Y-%m-%d").date()

    fecha_hora = datetime.combine(fecha_objeto,hora_objeto)

    new_avistamiento = Avistamiento(
        voluntario_id=voluntario_id,
        ave_id=ave_id,
        fecha_hora= fecha_hora,
        lugar=lugar, 
        descripcion=None
    )
    session.add(new_avistamiento)
    #genere el ID del avistamiento sin cerrar la transacción todavía
    session.flush()
    
    nuevo_registro = Registro(
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo,
            avistamiento_id=new_avistamiento.id
        )
    session.add(nuevo_registro)
    session.commit()
    session.close()

from sqlalchemy import text

def get_ave_by_id(ave_id):
    session = SessionLocal()

    try:
        resultado = session.execute(
            text(""" SELECT * FROM ave WHERE id = :id"""),
            {"id": ave_id}
        ).fetchone()
        return resultado[0] if resultado else None

    finally:
        session.close()

def get_ave_by_name(nombre):
    session = SessionLocal()
    try:
        resultado = session.execute(
            text(""" SELECT id FROM ave WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(:nombre))"""),
            {"nombre": nombre.strip()}
        ).fetchone()
        return resultado[0] if resultado else None

    finally:
        session.close()

def get_comuna_by_name(name):
    session = SessionLocal()

    try:
        result = session.execute(
            text("SELECT id FROM comuna WHERE nombre = :nombre"),
            {"nombre": name}).fetchone()

        if result is None:
            return None
        else:
            return result[0]

    finally:
        session.close()


def register_user(nombre, email, phone, region, comuna):
    if get_voluntario_by_email(email) is not None:
        return False, "El correo ya esta en uso."
    comuna_id= get_comuna_by_name(comuna)
    create_voluntario(nombre, email, comuna_id , phone)
    return True, None

def login_user(email):
    email_registrado = get_voluntario_by_email(email)
    if email_registrado is None:
        return False, "Estás iniciando sesión con un correo diferente al que te registraste"

    return True, None
