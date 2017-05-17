# Código Fuente de Visor.
# Programa para cargar, visualizar y exportar datos
# de transacciones financieras.
# Creadores: BCG


from tkinter import *
import pymssql

class Application(Frame):

	def __init__(self, master):
		""" Inicialización del contenedor gráfico principal """
		Frame.__init__(self, master)
		self.grid(padx=20, pady=20)
		self.crear_widgets()

	def crear_widgets(self):
		"""crear boton, text y entrada"""
		self.instruction1 = Label(self,text="Host: ")
		self.instruction1.grid(row = 0, column = 0, columnspan = 1, sticky = 'E')

		self.host = Entry(self)
		self.host.grid(row = 0, column = 2, sticky=W)

		self.instruction2 = Label(self,text="Puerto: ")
		self.instruction2.grid(row=1, column = 0, columnspan = 1, sticky = 'E')

		self.puerto = Entry(self)
		self.puerto.grid(row = 1, column = 2, sticky=W)

		self.instruction3 = Label(self,text="Usuario: ")
		self.instruction3.grid(row=2, column = 0, columnspan = 1, sticky ='E')

		self.usuario = Entry(self)
		self.usuario.grid(row = 2, column = 2, sticky=W)

		self.instruction4 = Label(self,text="Password: ")
		self.instruction4.grid(row=3, column = 0, columnspan = 1, sticky = 'E')

		self.password = Entry(self, show="*")
		self.password.grid(row = 3, column = 2, sticky=W)

		self.vacio1 = Label(self,text="")
		self.vacio1.grid(row=4, column = 0, columnspan = 2, sticky = W)

		self.submit_button = Button(self, text = "Prueba", command = self.probar_conexion)
		self.submit_button.grid(row=5, column=0, sticky = 'EW')

		self.vacio = Label(self,text="")
		self.vacio.grid(row=6, column = 0, columnspan = 2, sticky = W)



	def probar_conexion(self):

		HOST = self.host.get()
		PUERTO = self.puerto.get()
		USUARIO = self.usuario.get()
		PASSWORD = self.password.get()

		if HOST and PUERTO and USUARIO and PASSWORD:
			try:
				conn = pymssql.connect(HOST, USUARIO, PASSWORD, 'Matcher')
				message = "Conexión establecida"
				COLOR = 'green'
			except pymssql.InterfaceError as eie:
				message = "Conexión fallida - " + str(eie)
				COLOR = 'red'
			except pymssql.OperationalError as eoe:
				message = "Login Fallido - " + str(eoe)
				COLOR = 'red'
		else:
			message = 'Debe llenar todos los campos'
			COLOR = 'red'


		self.text = Text(self, width=25, height = 4, wrap = WORD, fg=COLOR)
		self.text.grid(row=7, column=2, sticky='N')
		self.text.insert(INSERT, message)



root = Tk()
root.title('Visor')
root.geometry('350x300')
app = Application(root)

root.mainloop()