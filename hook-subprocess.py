# Hook personalizado para subprocess
from PyInstaller.utils.hooks import collect_all

# Recolectar todos los módulos relacionados con subprocess
datas, binaries, hiddenimports = collect_all('subprocess')

# Agregar imports específicos que pueden faltar
hiddenimports += [
    'subprocess',
    'subprocess_win32',
    'subprocess_win32_impl',
    'subprocess_win32_impl_win32',
    'subprocess_win32_impl_win32_impl',
    'subprocess_win32_impl_win32_impl_win32',
    'subprocess_win32_impl_win32_impl_win32_impl',
    'subprocess_win32_impl_win32_impl_win32_impl_win32',
    'subprocess_win32_impl_win32_impl_win32_impl_win32_impl',
    'subprocess_win32_impl_win32_impl_win32_impl_win32_impl_win32',
]

# Excluir módulos que pueden causar problemas
excludes = [
    'tkinter.test',
    'unittest',
    'test',
]
