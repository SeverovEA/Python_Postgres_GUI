from db_connection import Connection
from gui import Gui

con = Connection()
gui = Gui(con)
con.finish_connection()
