import sys
from cx_Freeze import setup, Executable

base = 'Win32GUI' if sys.platform == 'win32' else None

includes = []
excludes = []

executable = Executable(
    script='FlashcardsManager.pyw',
    base=base,
    icon='res/icon.ico',
)

setup(
    name='Flashcards Manager',
    version='1.0.0',
    description='An application that generates flashcards by looking up dictionaries',
    author='Shramana',
    options={
        'build_exe': {
            'includes': includes,
            'excludes': excludes,
        }
    },
    executables=[executable],
)
