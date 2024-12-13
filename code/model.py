import os
import shutil
import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_NAME = 'data.db'
BACKUP_PATH = 'backup'


def backup_db(func):
    """
    Create a backup of db decorator
    :return:
    """

    def wrapper(*args, **kwargs):
        """
        Wrapper function
        :param func:
        :param args:
        :param kwargs:
        :return:
        """

        if not os.path.exists(BACKUP_PATH):
            os.makedirs(BACKUP_PATH)

        # Create before backup
        shutil.copy(DATABASE_NAME, os.path.join(BACKUP_PATH, DATABASE_NAME + '.old'))

        result = func(*args, **kwargs)

        # Create after backup
        shutil.copy(DATABASE_NAME, os.path.join(BACKUP_PATH, DATABASE_NAME))

        return result

    return wrapper


class DB:
    def __init__(self):
        self.connection = sql.connect(DATABASE_NAME)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        """
        Crea las tablas de la base de datos data.db

        :return:
            None
        """

        # Crear la tabla Users
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES Roles(id)
        )''')

        # Crear la tabla Roles
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT
        )''')

        # Crear la tabla Pacient
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Pacients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            d2 INTEGER,
            d3 INTEGER,
            conf_id INTEGER,
            user_id INTEGER,
            left BOOLEAN,
            FOREIGN KEY (conf_id) REFERENCES Config(id),
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )''')

        # Crear la tabla Configuration
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            pi_id INTEGER,
            pf_id INTEGER,
            speed INTEGER,
            FOREIGN KEY (pi_id) REFERENCES PI(id),
            FOREIGN KEY (pf_id) REFERENCES PF(id)
        )''')

        # Crear la tabla PI
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS PI (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q1 REAL,
            q2 REAL,
            q3 REAL,
            q4 REAL
        )''')

        # Crear la tabla PF
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS PF (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q1 REAL,
            q2 REAL,
            q3 REAL,
            q4 REAL
        )''')
        # Confirmar los cambios
        self.connection.commit()

    # =====================Crud Users=====================
    @backup_db
    def create_user(self, username, password, role):
        """Crea una nueva entrada en la tabla Users con los valores proporcionados.

        Args:
            name (str): Nombre del usuario.
            password (str): Contraseña del usuario.
            role (int): Rol del usuario.
        """
        self.cursor.execute(
            f"""INSERT INTO Users (username, password, role_id) 
                    VALUES ('{username}', '{password}', '{role}')"""
        )
        self.connection.commit()

    @backup_db
    def update_user(self, id, username, password):
        """Actualiza la entrada en la tabla Users con el id proporcionado con los nuevos valores.

        Args:
            name (str): Nombre del usuario.
            password (str): Contraseña del usuario.
            role (int): Rol del usuario.
        """
        self.cursor.execute(
            f"""UPDATE Users SET username = '{username}', password = '{password}' WHERE id = '{id}'"""
        )
        self.connection.commit()

    @backup_db
    def delete_user(self, id):
        """Elimina la entrada en la tabla Users con el id proporcionado.

        Args:
            id (str): Id de la entrada en la tabla Users que se va a eliminar.
        """
        self.cursor.execute(f"DELETE FROM Users WHERE id = '{id}'")
        self.connection.commit()

    def fetch_users(self):
        """Obtiene los datos de la tabla Users.

        Returns:
            tuple: Tupla con la lista de datos de la tabla Users
        """
        result = self.cursor.execute('SELECT * FROM Users ORDER BY id')
        self.connection.commit()

        return result

    def fetch_user(self, username):
        """Obtiene la passoword de la tabla Users a partir del nombre de usuario.

        Returns:
            str: str con la password desde la tabla Users
        """

        self.cursor.execute(f"SELECT password FROM Users WHERE username = '{username}'")
        result = self.cursor.fetchone()
        self.connection.commit()

        return result

    # =====================Crud Pacients=====================
    @backup_db
    def create_pacient(self, name, d2, d3, conf_id, user_id, left):
        """Crea una nueva entrada en la tabla Pacient con los valores proporcionados.

        Args:
            name (str): Nombre del paciente.
            d2 (int): Dirección del paciente.
            d3 (int): Dirección adicional del paciente.
            conf_id (int): Identificador de la consulta.
            user_id (int): Identificador del usuario que creó el registro.
            left (bool): Indica si el paciente es zurdo o no.
        """
        self.cursor.execute(
            f"""INSERT INTO Pacients (name, d2, d3, conf_id, user_id, left) 
            VALUES ('{name}', '{d2}', '{d3}', '{conf_id}', '{user_id}', '{left}')"""
        )
        self.connection.commit()

    @backup_db
    def update_pacient(self, id, name, d2, d3, left):
        """Actualiza la entrada en la tabla Pacients con el id proporcionado con los nuevos valores.

        Args:
            id (int): Id de la entrada en la tabla Pacients que se va a actualizar.
            name (str): Nuevo nombre del paciente.
            d2 (int): Nueva d2 del paciente.
            d3 (int): Nueva d3 del paciente.
            left (bool): Indica si el paciente es zurdo o no.
        """

        self.cursor.execute(
            f"""UPDATE Pacients SET name = '{name}', 
            d2 = '{d2}', d3 = '{d3}', left = '{left}' WHERE id = '{id}'"""
        )
        self.connection.commit()

    @backup_db
    def delete_pacient(self, id):
        """Elimina la entrada en la tabla Pacients con el id proporcionado.

        Args:
            id (int): Id de la entrada en la tabla Pacients que se va a eliminar.
        """

        self.cursor.execute(f"DELETE FROM Pacients WHERE id = '{id}'")
        self.connection.commit()

    def fetch_pacients(self):
        """Obtiene los datos de la tabla Pacients.

        Returns:
            tuple: Tupla con la lista de datos de la tabla Pacients
        """
        self.cursor.execute('SELECT * FROM Pacients ORDER BY id')
        result = self.cursor.fetchall()
        self.connection.commit()

        return result

    # =====================CRUD Config=====================
    @backup_db
    def create_config(self, name, pi_id, pf_id, speed):
        """Crea una nueva entrada en la tabla Config con los valores proporcionados.

        Args:
            name (str): Nombre de la configuración.
            pi_id (int): Id de la entrada en la tabla PI asociada con la configuración.
            pf_id (int): Id de la entrada en la tabla PF asociada con la configuración.
            speed (int): Velocidad de la configuración.
        """
        self.cursor.execute(
            f"""INSERT INTO Config (name, pi_id, pf_id, speed) 
                            VALUES ('{name}', '{pi_id}', '{pf_id}', '{speed}')"""
        )
        self.connection.commit()

    @backup_db
    def update_config(self, id, name, speed):
        """Actualiza la entrada en la tabla Config con el id proporcionado con los nuevos valores.

        Args:
            id (int): Id de la entrada en la tabla Config que se va a actualizar.
            name (str): Nuevo nombre de la configuración.
            speed (int): Nueva velocidad de la configuración.
        """
        self.cursor.execute(
            f"""UPDATE Config SET name = '{name}', speed = '{speed}' 
                            WHERE id = '{id}'"""
        )
        self.connection.commit()

    @backup_db
    def delete_config(self, id):
        """Elimina la entrada en la tabla Config con el id proporcionado, así como las entradas asociadas en las tablas PI y PF.

        Args:
            id (int): Id de la entrada en la tabla Config que se va a eliminar.
        """
        self.cursor.execute(f"DELETE FROM Config WHERE id = '{id}'")
        self.delete_pi(id)
        self.delete_pf(id)
        self.connection.commit()

    def fetch_config(self):
        """Obtiene el id de la última fila insertada en la tabla Config.

        Returns:
            int: Id de la última fila insertada.
        """
        result = self.cursor.lastrowid
        self.connection.commit()

        return result

    def fetch_config_byid(self, id):
        """Obtiene los datos de la configuración, los PI y PF asociados con el id proporcionado.

        Args:
            id (int): Id de la configuración que se va a obtener.

        Returns:
            tuple: Tupla que contiene los datos de la configuración, los PI y PF asociados.
        """
        self.cursor.execute(f"SELECT conf_id FROM Pacients WHERE id = '{id}'")
        pid = self.cursor.fetchone()
        self.cursor.execute(f"SELECT pi_id, pf_id, speed FROM Config WHERE id = '{pid[0]}'")
        cid = self.cursor.fetchone()

        self.cursor.execute(f"SELECT * FROM PI WHERE id = '{cid[0]}'")
        pi_data = self.cursor.fetchone()
        self.cursor.execute(f"SELECT * FROM PF WHERE id = '{cid[1]}'")
        pf_data = self.cursor.fetchone()
        self.connection.commit()

        return pi_data, pf_data, cid[2]

    def fetch_cname(self, config_id):
        """Obtiene el nombre de la configuración con el id proporcionado.

        Args:
            config_id (int): Id de la configuración cuyo nombre se va a obtener.

        Returns:
            str: Nombre de la configuración.
        """
        self.cursor.execute(f"SELECT name FROM Config WHERE id = '{config_id}'")
        result = self.cursor.fetchone()
        self.connection.commit()

        return result

    # =====================CRUD PI=====================
    @backup_db
    def create_pi(self, q1, q2, q3, q4):
        """Crea una nueva entrada en la tabla PI con los valores proporcionados.

        Args:
            q1 (float): Valor de la columna q1.
            q2 (float): Valor de la columna q2.
            q3 (float): Valor de la columna q3.
            q4 (float): Valor de la columna q4.
        """
        self.cursor.execute(
            f"""INSERT INTO PI (q1, q2, q3, q4) 
                            VALUES ('{q1}', '{q2}', '{q3}', '{q4}')"""
        )
        self.connection.commit()

    @backup_db
    def update_pi(self, id, q1, q2, q3, q4):
        """Actualiza la entrada en la tabla PI con el id proporcionado con los nuevos valores.

        Args:
            id (int): Id de la entrada en la tabla PI que se va a actualizar.
            q1 (float): Nuevo valor de la columna q1.
            q2 (float): Nuevo valor de la columna q2.
            q3 (float): Nuevo valor de la columna q3.
            q4 (float): Nuevo valor de la columna q4.
        """
        self.cursor.execute(
            f"""UPDATE PI SET q1 = '{q1}', 
                            q2 = '{q2}', q3 = '{q3}', q4 = '{q4}' WHERE id = '{id}'"""
        )
        self.connection.commit()

    @backup_db
    def delete_pi(self, id):
        """Elimina la entrada en la tabla PI con el id proporcionado.

        Args:
            id (int): Id de la entrada en la tabla PI que se va a eliminar.
        """
        self.cursor.execute(f"DELETE FROM PI WHERE id = '{id}'")
        self.connection.commit()

    def fetch_pi(self):
        """Obtiene el id de la última fila insertada en la tabla PI.

        Returns:
            int: Id de la última fila insertada.
        """
        result = self.cursor.lastrowid
        self.connection.commit()

        return result

    # =====================CRUD PF=====================
    @backup_db
    def create_pf(self, q1, q2, q3, q4):
        """Crea una nueva entrada en la tabla PF con los valores proporcionados.

        Args:
            q1 (float): Valor de la columna q1.
            q2 (float): Valor de la columna q2.
            q3 (float): Valor de la columna q3.
            q4 (float): Valor de la columna q4.
        """
        self.cursor.execute(
            f"""INSERT INTO PF (q1, q2, q3, q4) 
                                    VALUES ('{q1}', '{q2}', '{q3}', '{q4}')"""
        )
        self.connection.commit()

    @backup_db
    def update_pf(self, id, q1, q2, q3, q4):
        """Actualiza la entrada en la tabla PF con el id proporcionado con los nuevos valores.

        Args:
            id (int): Id de la entrada en la tabla PF que se va a actualizar.
            q1 (float): Nuevo valor de la columna q1.
            q2 (float): Nuevo valor de la columna q2.
            q3 (float): Nuevo valor de la columna q3.
            q4 (float): Nuevo valor de la columna q4.
        """
        self.cursor.execute(
            f"""UPDATE PF SET q1 = '{q1}', 
                            q2 = '{q2}', q3 = '{q3}', q4 = '{q4}' WHERE id = '{id}'"""
        )
        self.connection.commit()

    @backup_db
    def delete_pf(self, id):
        """Elimina la entrada en la tabla PF con el id proporcionado.

        Args:
            id (int): Id de la entrada en la tabla PF que se va a eliminar.
        """
        self.cursor.execute(f"DELETE FROM PF WHERE id = '{id}'")
        self.connection.commit()

    def fetch_pf(self):
        """Obtiene el id de la última fila insertada en la tabla PF.

        Returns:
            int: Id de la última fila insertada.
        """
        result = self.cursor.lastrowid
        self.connection.commit()

        return result

    # =====================OTHERS=====================
    def initialize(self):
        """Inicializa la base de datos con datos predeterminados.

        Crea los roles 'admin' y 'especialista' en la tabla Roles e inserta un usuario 'admin' con la contraseña 'admin' y el rol 'admin'.
        """
        self.cursor.execute("INSERT INTO Roles (type) VALUES ('admin')")
        self.cursor.execute("INSERT INTO Roles (type) VALUES ('especialista')")
        ep = generate_password_hash('admin', 'pbkdf2:sha256:30', 30)
        self.cursor.execute(f"INSERT INTO Users (username, password, role_id) VALUES ('admin', '{ep}', 1)")

        self.connection.commit()

    def validate(self, username, password):
        """Valida un usuario en la base de datos.

        Comprueba si el nombre de usuario y la contraseña proporcionados coinciden con un registro en la tabla Usuarios.

        Args:
            username (str): Nombre de usuario del usuario a validar.
            password (str): Contraseña del usuario a validar.

        Returns:
            tuple: Tupla que contiene el id, el nombre de usuario, la contraseña y el id del rol del usuario validado, o None si no se encontró ningún usuario.
        """

        self.cursor.execute(f"SELECT id, username, password, role_id FROM Users WHERE username = '{username}'")
        data = self.cursor.fetchone()

        if data is not None:
            flag = check_password_hash(data[2], password)
        else:
            flag = False

        return data, flag


if __name__ == '__main__':
    model = DB()

