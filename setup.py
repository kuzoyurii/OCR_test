from cx_Freeze import setup, Executable

files = {"include_files": ["OCRSIM.postman_collection.json", ("templates", "templates"), ("static", "static"),
                           ("scoreboards", "scoreboards")],
         "excludes": ["scoreboards\\scoreboard_setup.py"]
         }

setup(
    name="OCRSIM",
    version=0.96,
    description="OCR Scoreboard Simulator",
    options={'build_exe': files},
    executables=[Executable("server.py", base=None, icon="server.ico"), Executable("player.py", base="Win32GUI"), Executable("scoreboard_setup.py", base="Win32GUI")],
)