from sqlalchemy import create_engine, Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

#nombre de la base de datos
DB_NAME = "tarea2_db"
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
    fecha_registro = Column(DATETIME, nullable=False)
    comuna_id = Column(ForeignKey('comuna.id'), nullable=False)

    avistamientos = relationship("Avistamiento", back_populates="voluntarios")

class Avistamiento(Base):
    __tablename__ = 'avistamiento'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    voluntario_id = Column(ForeignKey('voluntario.id'), nullable=False)
    ave_id = Column(ForeignKey('ave.id'), nullable=True)
    #si no se registra la hora de avistamiento, por defecto usa la hora actual para guardarla en la bse de datos 
    fecha_hora = Column(DATETIME, nullable=False, default=datetime.datetime.now) 
    lugar = Column(VARCHAR(200), nullable=True)
    descripcion = Column(TEXT(500), nullable=False)

    registro = relationship("Regitro", back_populates="avistamientos")

class Registro(Base):
    __tablename__ = 'registro'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ruta_archivo = Column(VARCHAR(300), nullable=False)
    nombre_archivo = Column(VARCHAR(300), nullable=False)
    avistamiento_id = Column(ForeignKey('avistamiento.id'), nullable=False)


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

def get_voluntario_by_email(email):
    session = SessionLocal()
    voluntario = session.query(Voluntario).filter_by(email=email).first()
    session.close()
    return voluntario

def get_voluntarios_by_comuna(comuna_id):
    session = SessionLocal()
    voluntarios = session.query(Voluntario).filter_by(comuna_id=comuna_id).all()
    session.close()
    return voluntarios



def create_voluntario(nombre, email, comuna_id, telefono=None, fecha_registro=None):
    session = SessionLocal()
    
    # Si no se provee una fecha, usamos la fecha y hora exacta de este momento
    if fecha_registro is None:
        fecha_registro = datetime.now()
        
    new_voluntario = Voluntario(
        nombre=nombre, 
        email=email, 
        telefono=telefono, 
        fecha_registro=fecha_registro, 
        comuna_id=comuna_id
    )
    session.add(new_voluntario)
    session.commit()
    session.close()
    

def get_avistamiento(page_size):
    session = SessionLocal()
    avistamientos = session.query(Avistamieto).limit(page_size).all()
    session.close()
    return avistamientos

def create_avistamiento(conf_text, conf_img, user_id):
    session = SessionLocal()
    new_confession = Confesion(conf_text=conf_text, conf_img=conf_img, user_id=user_id)
    session.add(new_confession)
    session.commit()
    session.close()

def register_user(username, password, email):
    if get_user_by_email(email) is not None:
        return False, "El correo ya esta en uso."
    
    if get_user_by_username(username) is not None:
        return False, "El nombre de usuario esta en uso."
    
    create_user(username, password, email)
    return True, None

def login_user(username, password):
    a_user = get_user_by_username(username)
    if a_user is None:
        return False, "Usuario o contraseña incorrectos."
    
    if a_user.password != password:
        return False, "Usuario o contraseña incorrectos."
    
    return True, None
