from cx_Freeze import setup, Executable

setup(
    name= 'Simulador',
    version = '0.1',
    description = 'Simulador de brazo robotico',
    executables = [Executable('controller.py')],
)

