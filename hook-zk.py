# Hook personalizado para la biblioteca zk
from PyInstaller.utils.hooks import collect_all

# Recolectar todos los módulos relacionados con zk
datas, binaries, hiddenimports = collect_all('zk')

# Agregar imports específicos que pueden faltar
hiddenimports += [
    'zk',
    'zk.zk',
    'zk.zkconst',
    'zk.zkexception',
    'zk.zkfinger',
    'zk.zkuser',
    'zk.zkworkcode',
    'zk.zkattendance',
    'zk.zkface',
    'zk.zkfp',
    'zk.zkoperator',
    'zk.zkoption',
    'zk.zkparameter',
    'zk.zkpin',
    'zk.zkproduct',
    'zk.zkrealtime',
    'zk.zkreport',
    'zk.zkserial',
    'zk.zksms',
    'zk.zksupervisor',
    'zk.zktime',
    'zk.zktransaction',
    'zk.zkuser',
    'zk.zkworkcode',
]

# Excluir módulos que pueden causar problemas
excludes = [
    'tkinter.test',
    'unittest',
    'test',
]
