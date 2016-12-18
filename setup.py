from cx_Freeze import setup, Executable
import sys

base = 'Win32GUI' if sys.platform == 'win32' else None
executables = Executable(
    script='PyFlashcardsManager.pyw',
    base=base,
    shortcutName='Flashcards Manager',
    shortcutDir='DesktopFolder'
)

build_exe_options = {
    'include_files': [r'res/'],
}

bdist_msi_options = {
    'upgrade_code': '{EF063422-3DDC-4C70-9FB9-1D8591E2D561}'
}

setup(
    name='Flashcards Manager',
    version='0.0.1',
    description='A simple GUI application that generates flashcards',
    author='shramana',
    options={
        'build_exe': build_exe_options,
        'build_msi': bdist_msi_options
    },
    executables=[executables]
)
