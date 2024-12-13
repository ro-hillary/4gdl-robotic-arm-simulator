import numpy as np
from spatialmath import *
from roboticstoolbox.robot import *
import roboticstoolbox as rt

class Arm:
    def __init__(self, iq1, iq2, iq3, iq4, q1, q2, q3, q4, d1, d2, d3):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3

        self.iq1 = np.radians(iq1)
        self.iq2 = np.radians(iq2)
        self.iq3 = np.radians(iq3)
        self.iq4 = np.radians(iq4)

        self.q1 = np.radians(q1)
        self.q2 = np.radians(q2)
        self.q3 = np.radians(q3)
        self.q4 = np.radians(q4)

        pi = np.pi
        self.limits = [-70, 90, -70, 70, -35, 45]

        # Inicializando el robot
        self.robot = DHRobot([
            # Hombro
            RevoluteDH(d=d1, a=0, alpha=-pi / 2),
            # Brazo
            RevoluteDH(d=d2, a=0, alpha=pi / 2),
            # Codo
            RevoluteDH(d=0, a=0, alpha=-pi / 2),
            # Antebrazo
            RevoluteDH(d=d3, a=0, alpha=0),
        ], name='Hombro', base=SE3.Trans(0, 0, 0), manufacturer='Robert')

        # Posicion inicial
        self.ip = np.array([self.iq1, self.iq2, self.iq3, self.iq4])

        # Posicion final
        self.fp = np.array([self.q1, self.q2, self.q3, self.q4])

    def dh(self):
        """
        Funcion para obtener la configuracion del robot

        :return
            Un string con la configuracion del robot
        """
        return str(self.robot)

    def __fw_kine(self):
        """
        Funcion protegida para obtener el modelo cinematico directo del robot

        :return
            Solucion del modelo cinematico directo (T)
        """
        T = self.robot.fkine(self.fp)

        return T

    def __in_kine(self):
        """
        Funcion protegida para obtener el modelo cinematico inverso del robot

        :returns
            Solucion del modelo cinematico inverso (sol),solucion del modelo cinematico directo (T)
        """
        T = self.__fw_kine()
        sol = self.robot.ikine_LM(T)

        return sol, T

    def sol(self):
        """
        Funcion para mostrar las soluciones en forma de string

        :returns
            String con la matriz de transformacion, angulos de entrada, solucion del modelo cinematico inverso
        """

        sol, T = self.__in_kine()

        angles = f"Input:\n Q1:{self.q1} , Q2:{self.q2} , Q3:{self.q3} , Q4:{self.q4} \n "
        solution = f"Ikine Solution:\n {str(sol.q)}\n"
        t = f"Final Position:\n {str(f'X:{T.x}, Y:{T.y}, Z:{T.z}')}\n"
        return t, angles, solution

    def plot(self):
        """
        Funcion para plotear una configuracion estatica

        :return
            None
        """
        sol, T = self.__in_kine()
        self.robot.plot(sol.q, limits=self.limits, block=True)

    def control(self):
        """
        Funcion para crear un entorno de aprendizaje

        :return
            None
        """
        # Definiendo un nuevo robot con la posicion inicial en [0,0,0,0]
        robot2 = DHRobot([
            # Hombro
            RevoluteDH(d=self.d1, a=0, alpha=-np.pi / 2, qlim=[np.radians(-50), np.radians(180)]),
            # Brazo
            RevoluteDH(d=self.d2, a=0, alpha=np.pi / 2, qlim=[np.radians(0), np.radians(180)]),
            # Codo
            RevoluteDH(d=0, a=0, alpha=-np.pi / 2, qlim=[np.radians(0), np.radians(140)]),
            # Antebrazo
            RevoluteDH(d=self.d3, a=0, alpha=0, qlim=[np.radians(0), np.radians(80)]),

        ], name='Hombro', base=SE3.Trans(0, 0, 0), manufacturer='Robert')
        robot2.teach(robot2.q, limits=self.limits)

    def move(self, time):
        """
        Funcion para plotear una trayecoria

        :return
            None
        """

        time = time * 100

        t = rt.jtraj(self.ip, self.fp, time)
        t1 = rt.jtraj(self.fp, self.ip, time)
        t_t = np.concatenate((t.q, t1.q), axis=0)

        rt.tools.xplot(t.q, block=True)
        self.robot.plot(t_t, dt=0.050, limits=self.limits, block=True, loop=True, shadow=False)

    def workspace(self):
        """
        Funcion calcular el espacio de trabajo

        :return
            Una lista con los valores que toma el brazo

        """
        l = []
        for c in np.linspace(0, 140, 10):
            for b in np.linspace(0, 180, 10):
                for h in np.linspace(-50, 180, 10):
                    self.q1 = h
                    self.q2 = b
                    self.q3 = c
                    t = self.__fw_kine()
                    l.append((t.x, t.y, t.z))
        return l


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Area de trabajo
    # Crear instancia de la interfaz con posicion inicial 0
    r = Arm(0, 0, 0, 0, 5, 30, 40)

    # Realizar simulacion de movimientos
    l = r.workspace()
    # Definir subplots
    fig, ax2 = plt.subplots(2, 2, figsize=(10, 5))
    fig2, (ax3, ax4) = plt.subplots(2, 2, figsize=(10, 5))
    ax1 = fig.add_subplot(121, projection="3d")
    ax2 = fig.add_subplot(122)
    ax3 = fig2.add_subplot(121)
    ax4 = fig2.add_subplot(122)

    # Plotear puntos
    # for x, y, z in l:
    #     ax1.scatter(x, y, z)
    #     ax2.scatter(x, y)
    #     ax3.scatter(x, z)
    #     ax4.scatter(y, z)

    # Plotear lineas
    x, y, z = zip(*l)
    ax1.plot(x, y, z)
    ax2.plot(x, y)
    ax3.plot(x, z)
    ax4.plot(y, z)

    # Grafico 3d
    ax1.set_xlabel('Eje X')
    ax1.set_ylabel('Eje Y')
    ax1.set_zlabel('Eje Z')
    ax1.set_title('3D')

    # Grafico XY
    ax2.set_xlabel('Eje X')
    ax2.set_ylabel('Eje Y')
    ax2.set_title('XY')

    # Grafico XZ
    ax3.set_xlabel('Eje X')
    ax3.set_ylabel('Eje Z')
    ax3.set_title('XZ')

    # Grafico YZ
    ax4.set_xlabel('Eje Y')
    ax4.set_ylabel('Eje Z')
    ax4.set_title('YZ')

    plt.show()
