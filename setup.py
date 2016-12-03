from cx_Freeze import setup, Executable
import os

os.environ['TCL_LIBRARY'] = r"C:\Users\shram\AppData\Local\Programs\Python\Python35-32\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\shram\AppData\Local\Programs\Python\Python35-32\tcl\tk8.6"

includes      = ["tkinter"]
include_files = [r"C:\Users\shram\AppData\Local\Programs\Python\Python35-32\DLLs\tcl86t.dll", \
                 r"C:\Users\shram\AppData\Local\Programs\Python\Python35-32\DLLs\tk86t.dll"]
setup(
    name = "PyFlashcardsManager",
    version = "0.0.1",
    options = {"build_exe": {"includes": includes, "include_files": include_files}},
    executables = [Executable("PyFlashcardsManager.py")]
)