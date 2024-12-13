import sqlite3
import sys
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import numpy as np
from robot import Arm
import matplotlib.pyplot as plt
from werkzeug.security import generate_password_hash, check_password_hash

user_section = None


class LoginWindow(tk.Tk):
    def __init__(self, model):
        super().__init__()

        self.model = model

        self.title("INGRESAR AL SISTEMA")
        self.geometry("330x270")
        self.resizable(False, False)
        self.config(bd=10)

        title = tk.Label(self, text="INICIAR SESION", fg="black", font=("Comic Sans", 13, "bold"), pady=10).pack()

        frame = tk.LabelFrame(self, text="Ingrese sus datos")
        frame.config(bd=2)
        frame.pack()

        label_user = tk.Label(frame, text="Nombre de usuario: ").grid(row=0, column=0, sticky='s', padx=5, pady=10)
        self.user = tk.Entry(frame, width=25)
        self.user.focus()
        self.user.grid(row=0, column=1, padx=5, pady=10)

        label_name = tk.Label(frame, text="Contraseña: ").grid(row=1, column=0, sticky='s', padx=10, pady=10)
        self.password = tk.Entry(frame, width=25, show="*")
        self.password.grid(row=1, column=1, padx=10, pady=10)

        frame_btn = tk.Frame(self)
        frame_btn.pack()

        self.password.bind("<Return>", lambda event: self.validate_user())
        validate_btn = tk.Button(frame_btn, text="INGRESAR", command=self.validate_user, height=2, width=12, ).grid(
            row=0, column=1, padx=10, pady=15)

        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def validate_user(self):
        if (self.validate_user_form()):
            username = self.user.get()
            password = self.password.get()
            data, flag = self.model.validate(username, password)

            if flag:
                tkinter.messagebox.showinfo("BIENVENIDO", "Datos ingresados correctamente")
                self.destroy()

                if data[-1] == 1:
                    Panel(self.model)
                else:
                    MainWindow(self.model)
                    global user_section
                    user_section = username
            else:
                tkinter.messagebox.showerror("ERROR DE INGRESO", "Usuario o contraseña incorrecto")

    def validate_user_form(self):
        if len(self.user.get()) != 0 and len(self.password.get()) != 0:
            return True
        else:
            tkinter.messagebox.showerror("ERROR DE INGRESO", "Ingrese su usuario y contraseña!!!")

    def close_window(self):
        self.destroy()
        sys.exit()


class MainWindow(tk.Tk):
    def __init__(self, model):

        super().__init__()
        self.arm = None

        self.model = model

        self.title("Simulador Brazo")
        self.resizable(False, False)

        # Entradas para los ángulos y distancias
        self.i_angle_labels = ["iQ1:", "iQ2:", "iQ3:", "iQ4:"]
        self.angle_labels = ["Q1:", "Q2:", "Q3:", "Q4:"]
        self.distance_labels = ["Brazo cm:", "Antebrazo cm:"]
        self.entries = {}

        # Tabs
        self.tab_control = ttk.Notebook(self)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text="Simular")
        self.tab_control.add(self.tab2, text="Rutinas")

        self.tab_control.grid(row=0, column=0, padx=5, pady=5)

        # Inicializando tabs
        self.simulate()
        self.pacient_info()

        self.protocol("WM_DELETE_WINDOW", self.close_window)

    # ==========================  GUI TAB1 ==================================

    def simulate(self):
        """
        Funcion para crear los elementos de la tab simulate

        """
        # Frame para las entradas
        entry_frame = tk.LabelFrame(self.tab1, text="Entradas", pady=5)
        entry_frame.config(bd=2)
        entry_frame.pack()

        vcmd1 = self.register(self.validate_angle_q1)
        vcmd2 = self.register(self.validate_angle_q2)
        vcmd3 = self.register(self.validate_angle_q3)
        vcmd4 = self.register(self.validate_angle_q4)
        vcmd5 = self.register(self.validate_dis_d2)
        cvmd6 = self.register(self.validate_dis_d3)
        self.timeval = self.register(self.validate_time)


        self.angles = [vcmd1, vcmd2, vcmd3, vcmd4]
        self.distances = [vcmd5, cvmd6]

        # Crear entradas para las angulos
        for i, label in enumerate(self.i_angle_labels):
            ttk.Label(entry_frame, text=label).grid(row=i + 1, column=0, padx=5, pady=5)
            self.entries[label] = ttk.Entry(entry_frame, width=10)
            self.entries[label].grid(row=i + 1, column=1, padx=5, pady=5)
            self.entries[label].configure(validate="key", validatecommand=(self.angles[i], '%P'))

        for i, label in enumerate(self.angle_labels):
            ttk.Label(entry_frame, text=label).grid(row=i + 1, column=2, padx=5, pady=5)
            self.entries[label] = ttk.Entry(entry_frame, width=10)
            self.entries[label].grid(row=i + 1, column=3, padx=5, pady=5)
            self.entries[label].configure(validate="key", validatecommand=(self.angles[i], '%P'))

        # Crear entradas para las distancias
        for i, label in enumerate(self.distance_labels):
            ttk.Label(entry_frame, text=label).grid(row=i + 1, column=4, padx=5, pady=5)
            self.entries[label] = ttk.Entry(entry_frame, width=10)
            self.entries[label].grid(row=i + 1, column=5, padx=5, pady=5)
            self.entries[label].configure(validate="key", validatecommand=(self.distances[i], '%P'))

        time_label = ttk.Label(entry_frame, text="Velocidad").grid(row=3, column=4, padx=5, pady=5)
        self.time_entry = ttk.Entry(entry_frame, width=10)
        self.time_entry.grid(row=3, column=5, padx=5, pady=5)
        self.time_entry.configure(validate="key", validatecommand=(self.timeval, '%P'))

        clear_btn = ttk.Button(entry_frame, text="Limpiar", command=self.clear_tab1).grid(row=4, column=5, padx=5,
                                                                                          pady=5)

        self.left_arm = tk.IntVar()
        cbutton = tk.Checkbutton(entry_frame, text='Izquierdo', variable=self.left_arm).grid(row=4, column=4, padx=5,
                                                                                             pady=5)

        # Frame para los botones
        btn_frame = tk.Frame(self.tab1)
        btn_frame.pack()

        # Botón para simular trayectoria
        simular_button = ttk.Button(btn_frame, text="Trayectoria", command=self.simulate_trajectory).grid(row=0,
                                                                                                          column=0,
                                                                                                          padx=5,
                                                                                                          pady=5)

        # Botón para graficar
        graficar_button = ttk.Button(btn_frame, text="Graficar", command=self.plot).grid(row=0, column=1, padx=5,
                                                                                         pady=5)

        # Botón para teach
        teach_button = ttk.Button(btn_frame, text="Manipular", command=self.teach).grid(row=0, column=2, padx=5, pady=5)

        # Botón para Configuracion
        c_button = ttk.Button(btn_frame, text="Config.", command=self.show_conf).grid(row=0, column=3, padx=5, pady=5)

        # Botón para Area de Trabajo
        #ws_button = ttk.Button(btn_frame, text="Área T.", command=self.show_ws).grid(row=0, column=4, padx=5, pady=5)

        # Crear una zona para mostrar texto (consola)
        self.console = tk.Text(self.tab1, height=20, width=75)
        self.console.pack()

    # ========================== FUNCTIONS TAB1 =============================
    def get_entry_values(self):
        """
        Funcion para tomar los valores de entrada de angulos y distancias

        :return:
            Retorna una variable booleana para validar que los campos esten rellenados correctamente

        """
        f = False
        time = None

        try:
            # Obtener los valores de los campos de entrada
            i_angles = [float(self.entries[label].get()) for label in self.i_angle_labels]
            angles = [float(self.entries[label].get()) for label in self.angle_labels]
            distances = [float(self.entries[label].get()) for label in self.distance_labels]
            time = int(self.time_entry.get())

            if self.left_arm.get() == 1:
                i_angles = np.multiply(i_angles, -1)
                angles = np.multiply(angles, -1)

            self.arm = Arm(i_angles[0], i_angles[1], i_angles[2], i_angles[3], angles[0], angles[1], angles[2],
                           angles[3], 5, distances[0], distances[1])

        except ValueError:
            tkinter.messagebox.showwarning(title="Error", message='Rellene todos los campos o ingrese solo números')
            f = True

        return f, time

    def get_entry_values_p(self):
        """
        Funcion para tomar los valores de entrada de las distancias

        :return:
            Retorna una variable booleana para validar que los campos esten rellenados correctamente

        """
        f = False
        try:
            # Obtener los valores de los campos de entrada
            angles = [float(self.entries[label].get()) for label in self.angle_labels]
            distances = [float(self.entries[label].get()) for label in self.distance_labels]

            if self.left_arm.get() == 1:
                angles = np.multiply(angles, -1)

            self.arm = Arm(0, 0, 0, 0, angles[0], angles[1], angles[2],
                           angles[3], 5, distances[0], distances[1])
        except ValueError:
            tkinter.messagebox.showwarning(title="Error",
                                           message='Rellene los campos de distancias o ingrese solo números')
            f = True

        return f

    def get_entry_values_t(self):
        """
        Funcion para tomar los valores de entrada de las distancias

        :return:
            Retorna una variable booleana para validar que los campos esten rellenados correctamente

        """

        f = False
        try:
            # Obtener los valores de los campos de entrada
            distances = [float(self.entries[label].get()) for label in self.distance_labels]

            self.arm = Arm(0, 0, 0, 0, 0, 0, 0, 0, d1=5, d2=distances[0], d3=distances[1])

        except ValueError:
            tkinter.messagebox.showwarning(title="Error",
                                           message='Rellene los campos de distancias o ingrese solo números')
            f = True

        return f

    def simulate_trajectory(self):
        """
        Funcion para simular trayectorias en base a las entradas

        """
        # Función para trayectorias
        f, time = self.get_entry_values()

        if f:
            self.console.delete("1.0", "end")
        else:
            self.console.delete("1.0", "end")
            self.console.insert("1.0", 'Simulando trayectoria.\n')
            self.arm.move(time)

    def plot(self):
        """
        Funcion para plotear en base a las entradas

        """
        # Función para graficar
        f = self.get_entry_values_p()
        if f:
            self.console.delete("1.0", "end")
        else:
            self.console.delete("1.0", "end")
            self.console.insert("1.0", "Generando Gráfica.\n")
            self.arm.plot()

    def teach(self):
        """
        Funcion para crear un entorno de aprendizaje

        """
        # Función para teach
        f = self.get_entry_values_t()
        if f:
            self.console.delete("1.0", "end")
        else:
            self.console.delete("1.0", "end")
            self.console.insert("1.0", "Modo enseñanza activado.\nPosición inicial [0,0,0,0]")
            self.arm.control()

    def show_conf(self):
        """
        Funcion para mostrar la configuracion del brazo en base a las entradas

        """
        f = self.get_entry_values_p()
        if f:
            self.console.delete("1.0", "end")
        else:
            self.console.delete("1.0", "end")
            self.console.insert("1.0", self.arm.dh())
            self.console.insert("end", self.arm.sol())

    # ==========================  GUI TAB2 ==================================

    def pacient_info(self):
        """
        Funcion para crear los elementos de la tab pacient_info

        """
        # Frame para la entrada
        frame = tk.LabelFrame(self.tab2, text="Guardar paciente", pady=5)
        frame.config(bd=2)
        frame.pack()

        label_name = tk.Label(frame, text='Nombre del paciente').grid(row=0, column=0, sticky='s', padx=5, pady=8)
        self.entry_name = tk.Entry(frame, width=25)
        self.entry_name.grid(row=0, column=1, padx=5, pady=8)

        label_conf = tk.Label(frame, text='Nombre de la config.').grid(row=1, column=0, sticky='s', padx=5, pady=8)
        self.entry_conf = tk.Entry(frame, width=25)
        self.entry_conf.grid(row=1, column=1, padx=5, pady=8)

        clear_btn = ttk.Button(frame, text="Limpiar", command=self.clear_tab2).grid(row=2, column=1, padx=5, pady=5)

        # Tabla
        self.tree = ttk.Treeview(self.tab2, height=13, columns=('Nombre', 'd2', 'd3', 'Config.', 'Usuario', 'Izq.'))
        self.tree.heading('#0', text='ID', anchor='center')
        self.tree.column('#0', width=90, minwidth=75, anchor='center')

        self.tree.heading('Nombre', text='Nombre', anchor='center')
        self.tree.column('Nombre', width=150, minwidth=75, anchor='center')

        self.tree.heading('d2', text='d2', anchor='center')
        self.tree.column('d2', width=50, minwidth=40, anchor='center')

        self.tree.heading('d3', text='d3', anchor='center')
        self.tree.column('d3', width=50, minwidth=40, anchor='center')

        self.tree.heading('Config.', text='Config.', anchor='center')
        self.tree.column('Config.', width=50, minwidth=40, anchor='center')

        self.tree.heading('Usuario', text='Usuario', anchor='center')
        self.tree.column('Usuario', width=50, minwidth=40, anchor='center')

        self.tree.heading('Izq.', text='Izq.', anchor='center')
        self.tree.column('Izq.', width=50, minwidth=40, anchor='center')

        self.tree.pack()
        self.__fill_table()

        btn_frame = tk.Frame(self.tab2)
        btn_frame.pack()

        # Botón para insertar
        insert_btn = ttk.Button(btn_frame, text="Guardar", command=self.create_pacient).grid(row=0, column=0, padx=5,
                                                                                             pady=5)
        # Boton para ver configuracion
        config_btn = ttk.Button(btn_frame, text='Ver Config.', command=self.update_config_window).grid(row=0, column=1,
                                                                                                       padx=5,
                                                                                                       pady=5)
        # Botón para cargar
        charge_btn = ttk.Button(btn_frame, text="Cargar", command=self.charge_config).grid(row=0, column=2, padx=5,
                                                                                           pady=5)
        # Botón para editar
        edit_btn = ttk.Button(btn_frame, text="Editar", command=self.update_pacient_window).grid(row=0, column=3,
                                                                                                 padx=5, pady=5)
        # Botón para borrar
        delete_btn = ttk.Button(btn_frame, text="Eliminar", command=self.delete_pacient).grid(row=0, column=4, padx=5,
                                                                                              pady=5)

    def update_pacient_window(self):
        """
        Funcion para crear los elementos de la ventana emergente update_pacient_window
        """
        # Comprobando que hay un item seleccionado
        try:
            si = self.tree.selection()[0]
            self.tree.item(si, 'text')
        except:
            tkinter.messagebox.showwarning(title='Error', message=f'Seleccione un paciente')
            return

        # Tomando datos de la tabla
        id = self.tree.item(si, 'text')
        name = self.tree.item(si, 'values')[0]
        d2 = self.tree.item(si, 'values')[1]
        d3 = self.tree.item(si, 'values')[2]
        left = self.tree.item(si, 'values')[5]

        # Creando la ventana para editar
        self.u_window = tk.Toplevel()
        self.u_window.title('Editar')
        self.u_window.resizable(False, False)

        # Ventana
        label_name = tk.Label(self.u_window, text='Nombre:').grid(row=0, column=0, sticky='s', padx=5, pady=8)
        entry_name = tk.Entry(self.u_window, textvariable=tk.StringVar(self.u_window, value=name), width=15)
        entry_name.grid(row=0, column=1, padx=5, pady=8)

        label_d2 = tk.Label(self.u_window, text='d2:').grid(row=1, column=0, sticky='s', padx=5, pady=8)
        entry_d2 = tk.Entry(self.u_window, textvariable=tk.StringVar(self.u_window, value=d2), width=15)
        entry_d2.configure(validate="key", validatecommand=(self.distances[0], '%P'))
        entry_d2.grid(row=1, column=1, padx=5, pady=8)

        label_d3 = tk.Label(self.u_window, text='d3:').grid(row=2, column=0, sticky='s', padx=5, pady=8)
        entry_d3 = tk.Entry(self.u_window, textvariable=tk.StringVar(self.u_window, value=d3), width=15)
        entry_d3.configure(validate="key", validatecommand=(self.distances[1], '%P'))
        entry_d3.grid(row=2, column=1, padx=5, pady=8)

        left_arm = tk.IntVar()
        _left_arm = 0 if left == 'No' else 1
        left_arm.set(_left_arm)

        cbutton = tk.Checkbutton(self.u_window, text='Izquierdo', variable=left_arm).grid(row=3, column=1, padx=5,
                                                                                          pady=5)
        edit_btn = ttk.Button(self.u_window, text="Editar",
                              command=lambda: self.update_pacient(id, entry_name.get(), entry_d2.get(), entry_d3.get(),
                                                                  left_arm.get())).grid(row=4, column=1, padx=5, pady=5)

        self.__fill_table()
        self.u_window.mainloop()

    def update_config_window(self):

        """
        Funcion para crear los elementos de la ventana emergente update_pacient_window
        """
        # Comprobando que hay un item seleccionado
        try:
            si = self.tree.selection()[0]
            self.tree.item(si, 'text')
        except:
            tkinter.messagebox.showwarning(title='Error', message=f'Seleccione un paciente')
            return

        # Tomando datos de la tabla
        id = self.tree.item(si, 'text')
        cname = self.tree.item(si, 'values')[3]

        pi, pf, speed = self.model.fetch_config_byid(id)

        # Creando la ventana para editar
        self.uc_window = tk.Toplevel()
        self.uc_window.title('Editar')
        self.uc_window.resizable(False, False)

        # Ventana
        label_name = tk.Label(self.uc_window, text='Nombre:')
        label_name.grid(row=0, column=0, sticky='s', padx=5, pady=8)
        entry_name = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=cname), width=10)
        entry_name.grid(row=0, column=1, padx=5, pady=8)

        label_speed = tk.Label(self.uc_window, text='Vel:')
        label_speed.grid(row=0, column=2, sticky='s', padx=5, pady=8)
        entry_speed = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=speed), width=10)
        entry_speed.configure( validate="key", validatecommand=(self.timeval, '%P'))
        entry_speed.grid(row=0, column=3, padx=5, pady=8)

        label_iq1 = tk.Label(self.uc_window, text='iQ1:')
        label_iq1.grid(row=1, column=0, sticky='s', padx=5, pady=8)
        entry_iq1 = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=pi[1]), width=10)
        entry_iq1.configure(validate="key", validatecommand=(self.angles[0], '%P'))
        entry_iq1.grid(row=1, column=1, padx=5, pady=8)

        label_iq2 = tk.Label(self.uc_window, text='iQ2:')
        label_iq2.grid(row=2, column=0, sticky='s', padx=5, pady=8)
        entry_iq2 = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=pi[2]), width=10)
        entry_iq2.configure(validate="key", validatecommand=(self.angles[1], '%P'))
        entry_iq2.grid(row=2, column=1, padx=5, pady=8)

        label_iq3 = tk.Label(self.uc_window, text='iQ3:')
        label_iq3.grid(row=3, column=0, sticky='s', padx=5, pady=8)
        entry_iq3 = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=pi[3]), width=10)
        entry_iq3.configure(validate="key", validatecommand=(self.angles[2], '%P'))
        entry_iq3.grid(row=3, column=1, padx=5, pady=8)

        label_iq4 = tk.Label(self.uc_window, text='iQ4:')
        label_iq4.grid(row=4, column=0, sticky='s', padx=5, pady=8)
        entry_iq4 = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=pi[4]), width=10)
        entry_iq4.configure(validate="key", validatecommand=(self.angles[3], '%P'))
        entry_iq4.grid(row=4, column=1, padx=5, pady=8)

        label_q1 = tk.Label(self.uc_window, text='Q1:')
        label_q1.grid(row=1, column=2, sticky='s', padx=5, pady=8)
        entry_q1 = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=pf[1]), width=10)
        entry_q1.configure(validate="key", validatecommand=(self.angles[0], '%P'))
        entry_q1.grid(row=1, column=3, padx=5, pady=8)

        label_q2 = tk.Label(self.uc_window, text='Q2:')
        label_q2.grid(row=2, column=2, sticky='s', padx=5, pady=8)
        entry_q2 = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=pf[2]), width=10)
        entry_q2.configure(validate="key", validatecommand=(self.angles[1], '%P'))
        entry_q2.grid(row=2, column=3, padx=5, pady=8)

        label_q3 = tk.Label(self.uc_window, text='Q3:')
        label_q3.grid(row=3, column=2, sticky='s', padx=5, pady=8)
        entry_q3 = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=pf[3]), width=10)
        entry_q3.configure(validate="key", validatecommand=(self.angles[2], '%P'))
        entry_q3.grid(row=3, column=3, padx=5, pady=8)

        label_q4 = tk.Label(self.uc_window, text='Q4:')
        label_q4.grid(row=4, column=2, sticky='s', padx=5, pady=8)
        entry_q4 = tk.Entry(self.uc_window, textvariable=tk.StringVar(self.uc_window, value=pf[4]), width=10)
        entry_q4.configure(validate="key", validatecommand=(self.angles[3], '%P'))
        entry_q4.grid(row=4, column=3, padx=5, pady=8)

        edit_btn = ttk.Button(self.uc_window, text="Editar",
                              command=lambda: self.update_config(id, entry_iq1.get(), entry_iq2.get(), entry_iq3.get(),
                                                                 entry_iq4.get(), entry_q1.get(), entry_q2.get(),
                                                                 entry_q3.get(), entry_q4.get(), entry_name.get(),
                                                                 entry_speed.get())).grid(row=5, column=2, padx=5,
                                                                                          pady=5)

        self.__fill_table()
        self.uc_window.mainloop()

    # ========================== FUNCTIONS TAB2 =============================


    def create_pacient(self):
        """
        Funcion para insertar pacientes en la base de datos

        """
        name = self.entry_name.get()
        config_name = self.entry_conf.get()
        try:
            self.model.create_pi(float(self.entries[self.i_angle_labels[0]].get()),
                                 float(self.entries[self.i_angle_labels[1]].get()),
                                 float(self.entries[self.i_angle_labels[2]].get()),
                                 float(self.entries[self.i_angle_labels[3]].get()))

            self.model.create_pf(float(self.entries[self.angle_labels[0]].get()),
                                 float(self.entries[self.angle_labels[1]].get()),
                                 float(self.entries[self.angle_labels[2]].get()),
                                 float(self.entries[self.angle_labels[3]].get()))

            self.model.create_config(config_name, self.model.fetch_pi(), self.model.fetch_pf(),
                                     float(self.time_entry.get()))

            self.model.create_pacient(name, int(self.entries[self.distance_labels[0]].get()),
                                      int(self.entries[self.distance_labels[1]].get()), self.model.fetch_config(),
                                      user_section, self.left_arm.get())

            self.__fill_table()
            tkinter.messagebox.showinfo(title='Exito', message=f'El paciente {name} se guardo correctamente')
        except sqlite3.Error as e:
            tkinter.messagebox.showwarning(title='Error', message=f'Ocurrio un error {e}')
        except ValueError:
            tkinter.messagebox.showwarning(title='Error', message=f'Debe insertar un paciente antes de guardar')

    def delete_pacient(self):
        """
        Funcion para eliminar configuraciones de la base de datos

        """
        try:
            si = self.tree.selection()[0]
            self.tree.item(si, 'text')
        except:
            tkinter.messagebox.showwarning(title='Error', message=f'Seleccione una paciente')
            return

        id = self.tree.item(si, 'text')

        pi, _, _ = self.model.fetch_config_byid(id)

        answer = tkinter.messagebox.askquestion("Advertencia", f'¿Seguro que desea eliminar este paciente?')

        if answer == 'yes':
            self.model.delete_pacient(id)
            self.model.delete_config(pi[0])

            self.__fill_table()
            tkinter.messagebox.showinfo('Exito', f'El paciente eliminado')
        else:
            tkinter.messagebox.showerror('Error', f'Error')

    def update_pacient(self, id, name, d2, d3, left):
        """
        Funcion para editar configuraciones en la base de datos

        """
        self.model.update_pacient(id, name, d2, d3, left)
        tkinter.messagebox.showinfo('Exito', f'El paciente fue editado')
        self.__fill_table()
        self.u_window.destroy()

    def update_config(self, id, iq1, iq2, iq3, iq4, q1, q2, q3, q4, name, speed):
        """
        Funcion para editar configuraciones en la base de datos

        """
        self.model.update_config(id, name, speed)
        self.model.update_pi(id, iq1, iq2, iq3, iq4)
        self.model.update_pf(id, q1, q2, q3, q4)
        tkinter.messagebox.showinfo('Exito', f'La configuración fue editada')
        self.__fill_table()
        self.uc_window.destroy()

    def charge_config(self):
        """
        Funcion para cargar configuraciones de la base de datos

        """
        try:
            si = self.tree.selection()[0]
            self.tree.item(si, 'text')
        except:
            tkinter.messagebox.showwarning(title='Error', message=f'Seleccione un paciente')
            return

        id = self.tree.item(si, 'text')
        d2 = self.tree.item(si, 'values')[1]
        d3 = self.tree.item(si, 'values')[2]

        pi, pf, speed = self.model.fetch_config_byid(id)

        distance = [d2, d3]

        for i, label in enumerate(self.i_angle_labels):
            self.entries[label].delete(0, 'end')
            self.entries[label].insert(0, int(pi[i + 1]))

        for i, label in enumerate(self.angle_labels):
            self.entries[label].delete(0, 'end')
            self.entries[label].insert(0, int(pf[i + 1]))

        # Crear entradas para las distancias
        for i, label in enumerate(self.distance_labels):
            self.entries[label].delete(0, 'end')
            self.entries[label].insert(0, distance[i])

        self.time_entry.insert(0, speed)
        # self.left_arm.set(0)
        tkinter.messagebox.showinfo(title='Exito', message=f'Configuración cargada correctamente')

    # ============================OTHER FUNCTIONS============================

    def __fill_table(self):
        """
        Funcion para tomar los datos de la base de datos y rellenar la tabla

        """
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        db_rows = self.model.fetch_pacients()

        for id, row in enumerate(db_rows):
            cname = self.model.fetch_cname(row[0])

            if row[6] == 0:
                self.tree.insert("", id, text=row[0], values=(row[1], row[2], row[3], cname, row[5], 'No'))
            else:
                self.tree.insert("", id, text=row[0], values=(row[1], row[2], row[3], cname, row[5], 'Si'))

    def clear_tab1(self):
        """
        Funcion para limpiar los campos del tab1

        """
        for label in self.i_angle_labels:
            self.entries[label].delete(0, "end")

        for label in self.angle_labels:
            self.entries[label].delete(0, "end")

        for label in self.distance_labels:
            self.entries[label].delete(0, "end")

        self.time_entry.delete(0, "end")
        self.left_arm.set(0)
        self.console.delete("1.0", "end")

    def clear_tab2(self):
        """
        Funcion para limpiar el campo del tab2

        """
        self.entry_name.delete(0, "end")
        self.entry_conf.delete(0, "end")

    def close_window(self):
        check = tkinter.messagebox.askokcancel("Cerrar", "¿Estás seguro de que deseas cerrar la sesión?")

        if check:
            self.destroy()
            LoginWindow(self.model)
            global user_section
            user_section = None

    # =======================VALIDATIONS==================================
    def validate_generic(self, value, min_val, max_val):
        if not value:
            return True
        elif value[0] == '0' and len(value) > 1:
            return False
        elif value == '-0':
            return False
        try:
            number = float(value)
            if min_val <= number <= max_val:
                return True
            else:
                return False
        except ValueError:
            return False

    def validate_angle_q1(self, value):
        return self.validate_generic(value, -180, 180)

    def validate_angle_q2(self, value):
        return self.validate_generic(value, -90, 90)

    def validate_angle_q3(self, value):
        return self.validate_generic(value, -140, 140)

    def validate_angle_q4(self, value):
        return self.validate_generic(value, -90, 90)

    def validate_dis_d2(self, value):
        return self.validate_generic(value, 1, 45)

    def validate_dis_d3(self, value):
        return self.validate_generic(value, 1, 50)

    def validate_time(self, value):
        return self.validate_generic(value, 1, 10)


class Panel(tk.Tk):
    def __init__(self, model):
        super().__init__()

        self.model = model
        self.users()
        self.resizable(False, False)
        self.title('USUARIOS')

        self.protocol("WM_DELETE_WINDOW", self.close_window)

    # ===================GUI==========================
    def users(self):
        """
        Ventana del panel de control de usuarios

        """
        # Frame para la entrada
        frame = tk.LabelFrame(self, text="Crear Usuario", pady=5)
        frame.config(bd=2)
        frame.pack()

        # Entrada para el nombre
        label_name = tk.Label(frame, text="Nombre")
        label_name.pack(side="top", padx=5, pady=8)
        self.entry_nameu = tk.Entry(frame, width=25)
        self.entry_nameu.pack(side="top", pady=5)

        # Entrada para la contraseña
        label_pass = tk.Label(frame, text="Contraseña")
        label_pass.pack(side="top", padx=5, pady=8)
        self.entry_pass = tk.Entry(frame, width=25)
        self.entry_pass.pack(side="top", pady=5)

        # Checkbox para el rol de administrador
        self.admin = tk.IntVar()
        cbutton = tk.Checkbutton(frame, text="Admin", variable=self.admin)
        cbutton.pack(side="top", pady=5)

        # Botón para limpiar los campos
        clear_btn = ttk.Button(frame, text="Limpiar", command=self.clear)
        clear_btn.pack(side="top", pady=5)

        # Tabla
        self.tree = ttk.Treeview(frame, height=13, columns=("Usuario", "Rol"))
        self.tree.heading("#0", text="ID", anchor="center")
        self.tree.column("#0", width=40, minwidth=40, anchor="center")

        self.tree.heading("Usuario", text="Usuario", anchor="center")
        self.tree.column("Usuario", width=75, minwidth=50, anchor="center")

        self.tree.heading("Rol", text="Rol", anchor="center")
        self.tree.column("Rol", width=100, anchor="center")

        self.tree.pack(side="top")
        self.__fill_table()

        # Botones
        btn_frame = tk.Frame(frame)
        btn_frame.pack(side="top")

        # Botón para insertar
        insert_btn = ttk.Button(btn_frame, text="Guardar", command=self.create_user)
        insert_btn.pack(side="left", padx=5, pady=5)

        # Botón para editar
        edit_btn = ttk.Button(btn_frame, text="Editar", command=self.update_window)
        edit_btn.pack(side="left", padx=5, pady=5)

        # Botón para borrar
        delete_btn = ttk.Button(btn_frame, text="Eliminar", command=self.delete_user)
        delete_btn.pack(side="left", padx=5, pady=5)

    def update_window(self):
        """
        Funcion para crear los elementos de la ventana emergente update_pacient_window

        """
        # Comprobando que hay un item seleccionado
        try:
            si = self.tree.selection()[0]
            self.tree.item(si, 'text')
        except:
            tkinter.messagebox.showwarning(title='Error', message=f'Seleccione un usuario')
            return

        # Tomando datos de la tabla
        self.userid = self.tree.item(si, 'text')
        self.username = self.tree.item(si, 'values')[0]
        self.password = self.model.fetch_user(self.username)

        # Creando la ventana para editar
        self.u_window = tk.Toplevel()
        self.u_window.title('Editar')
        self.u_window.resizable(False, False)

        # Ventana
        label_name = tk.Label(self.u_window, text='Usuario')
        label_name.grid(row=0, column=0, sticky='s', padx=5, pady=8)
        self.entry_nameu = tk.Entry(self.u_window, textvariable=tk.StringVar(self.u_window, value=self.username),
                                    width=25)
        self.entry_nameu.grid(row=0, column=2, padx=5, pady=8)

        label_opass = tk.Label(self.u_window, text='Contraseña actual')
        label_opass.grid(row=1, column=0, sticky='s', padx=5, pady=8)
        self.entry_opass = tk.Entry(self.u_window, width=25)
        self.entry_opass.grid(row=1, column=2, padx=5, pady=8)

        label_npass = tk.Label(self.u_window, text='Contraseña nueva')
        label_npass.grid(row=2, column=0, sticky='s', padx=5, pady=8)
        self.entry_npass = tk.Entry(self.u_window, width=25)
        self.entry_npass.grid(row=2, column=2, padx=5, pady=8)

        edit_btn = ttk.Button(self.u_window, text="Editar", command=self.update_user).grid(row=7, column=2, padx=5,
                                                                                           pady=5)

        self.u_window.mainloop()

    # ===================FUNCIONES==========================

    def __fill_table(self):
        """
        Funcion para tomar los datos de la base de datos y rellenar la tabla

        """
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        # db_rows = db.fetch_data()
        db_rows = self.model.fetch_users()

        for id, row in enumerate(db_rows):
            if row[3] == 1:
                self.tree.insert("", id, text=row[0], values=(row[1], 'admin'))
            else:
                self.tree.insert("", id, text=row[0], values=(row[1], 'especialista'))

    def create_user(self):
        """
        Funcion para crea usuarios en la base de datos

        """
        username = self.entry_nameu.get()
        password = self.entry_pass.get()

        encrypted_password = generate_password_hash(password, 'pbkdf2:sha256:30', 30)

        role = 1 if self.admin.get() == 1 else 2

        try:
            self.model.create_user(username, encrypted_password, role)
            self.__fill_table()
            tkinter.messagebox.showinfo(title='Exito', message=f'El usuario {username} se creo correctamente')

        except sqlite3.IntegrityError:
            tkinter.messagebox.showwarning(title='Error', message=f'Este nombre de usuario no esta disponible')
        except sqlite3.Error as e:
            tkinter.messagebox.showwarning(title='Error', message=f'Ocurrio un error {e}')

        except ValueError:
            tkinter.messagebox.showwarning(title='Error', message=f'Debe crear una usuario antes de guardarlo')

    def delete_user(self):
        """
        Funcion para eliminar usuarios de la base de datos

        """
        try:
            si = self.tree.selection()[0]
            self.tree.item(si, 'text')
        except:
            tkinter.messagebox.showwarning(title='Error', message=f'Seleccione un usuario')
            return

        id = self.tree.item(si, 'text')
        name = self.tree.item(si, 'values')

        answer = tkinter.messagebox.askquestion("Advertencia", f'¿Seguro que desea eliminar este usuario?')

        if answer == 'yes':
            self.model.delete_user(id)
            self.__fill_table()
            tkinter.messagebox.showinfo('Exito', f'El usuario fue eliminado')
        else:
            tkinter.messagebox.showerror('Error', f'Error')

    def update_user(self):
        """
        Funcion para editar usuarios en la base de datos

        """

        flag = check_password_hash(self.password[0], self.entry_opass.get())

        if flag:
            ep = generate_password_hash(self.entry_npass.get(), 'pbkdf2:sha256:30', 30)
            self.model.update_user(self.userid, self.entry_nameu.get(), ep)
            tkinter.messagebox.showinfo('Exito', f'El usuario fue editado')
            self.u_window.destroy()
            self.__fill_table()
        else:
            tkinter.messagebox.showerror(title='Error', message=f'La contraseña anterior es incorrecta')

    def clear(self):
        """
        Funcion para limpiar los campos

        """
        self.entry_nameu.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.admin.set(0)

    def close_window(self):
        check = tkinter.messagebox.askokcancel("Cerrar", "¿Estás seguro de que deseas cerrar la sesión?")

        if check:
            self.destroy()
            LoginWindow(self.model)
