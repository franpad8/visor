# Código Fuente de Visor.
# Programa para cargar, visualizar y exportar datos
# de transacciones financieras.
# Creadores: BCG


from tkinter import *
import pymssql


def change_frame(newframe):

	carga = newframe(root)
	carga.tkraise()


class Inicio(Frame):

	def __init__(self, master):
		""" Inicialización del contenedor gráfico principal """
		Frame.__init__(self, master)
		self.pack(fill=BOTH, expand=True)
		self.crear_widgets()

	def crear_widgets(self):
		"""crear boton, text y entrada"""

		self.frame1 = Frame(self, bd=1, relief=SUNKEN)
		self.frame1.pack(fill=X)


		self.instruction1 = Label(self.frame1, text="Host: ", width=8, anchor=E)
		self.instruction1.pack(side=LEFT, padx=5, pady=5)

		self.host = Entry(self.frame1)
		self.host.pack(fill=X, expand=True, padx=(0, 5))

		self.frame2 = Frame(self,bd=1, relief=SUNKEN)
		self.frame2.pack(fill=X)

		self.instruction2 = Label(self.frame2,text="Puerto: ", width=8, anchor=E)
		self.instruction2.pack(side=LEFT, padx=5, pady=5)

		self.puerto = Entry(self.frame2, width=5)
		self.puerto.pack(side=LEFT, padx=(0, 5))

		self.frame3 = Frame(self,bd=1, relief=SUNKEN)
		self.frame3.pack(fill=X)

		self.instruction3 = Label(self.frame3,text="Usuario: ", width=8, anchor=E)
		self.instruction3.pack(side=LEFT, padx=5, pady=5)

		self.usuario = Entry(self.frame3)
		self.usuario.pack(fill=X, expand=True, padx=(0, 5))

		self.frame4 = Frame(self,bd=1, relief=SUNKEN)
		self.frame4.pack(fill=X)

		self.instruction4 = Label(self.frame4,text="Password: ", width=8, anchor=E)
		self.instruction4.pack(side=LEFT, padx=5, pady=5)

		self.password = Entry(self.frame4, show="*")
		self.password.pack(fill=X, expand=True, padx=(0, 5))

		self.frame5 = Frame(self)
		self.frame5.pack(fill=X)

		self.submit_button = Button(self.frame5, text='Probar Conexión', command=self.probar_conexion)
		self.submit_button.pack(side=LEFT, padx=5, pady=(10, 5))

		self.frame6 = Frame(self)
		self.frame6.pack(fill=X)

		self.text = Text(self.frame6, height = 4, wrap = WORD)
		self.text.pack(fill=X, padx=5, pady=5)

		self.submit_button1 = Button(self.frame6, text = "Continuar", state=NORMAL, command=lambda:(self.destroy(), change_frame(Carga)))
		self.submit_button1.pack(side=RIGHT, padx=5)




	def probar_conexion(self):

		HOST = self.host.get()
		PUERTO = self.puerto.get()
		USUARIO = self.usuario.get()
		PASSWORD = self.password.get()

		conn = None

		if HOST and PUERTO and USUARIO and PASSWORD:
			try:
				conn = pymssql.connect(HOST, USUARIO, PASSWORD, 'Matcher')
				message = "Conexión establecida."
				COLOR = 'green'
				self.submit_button1.config(state=NORMAL)

			except pymssql.InterfaceError as eie:
				message = "Conexión fallida - " + str(eie)
				COLOR = 'red'
				self.submit_button1.config(state=DISABLED)

			except pymssql.OperationalError as eoe:
				message = "Login Fallido - " + str(eoe)
				COLOR = 'red'
				self.submit_button1.config(state=DISABLED)
		else:
			message = 'Debe llenar todos los campos.'
			COLOR = 'red'
			self.submit_button1.config(state=DISABLED)

		
		self.text.delete(1.0, END)
		self.text.insert(INSERT, message)
		self.text.config(foreground=COLOR)



			


class Carga(Frame):

	def __init__(self, master):
		""" Inicialización del contenedor gráfico principal """
		Frame.__init__(self, master)
		self.pack(padx=20, pady=20)
		master.geometry('550x300')
		self.crear_widgets()

	def crear_widgets(self):
		
		MyText = StringVar()

		self.frame1 = Frame(self, bd=1, relief=SUNKEN)
		self.frame1.pack(fill=X)
		"""crear boton, text y entrada"""
		self.instruction1 = Label(self.frame1,text="Archivo de carga: ")
		self.instruction1.pack(side=LEFT, padx=5, pady=5)

		self.filename = Entry(self.frame1, textvariable = MyText, width=40)
		self.filename.pack(side=LEFT, expand=True, padx=(0, 5))

		self.search_button = Button(self.frame1, text='Buscar', command=lambda:mostrarArch(MyText))
		self.search_button.pack(side=LEFT, padx=5, pady=5)

		self.load_button = Button(self.frame1, text='Cargar', command=lambda:exit())
		self.load_button.pack(side=LEFT, padx=(10, 5), pady=5)
		
		#self.file = Entry(self)
		#self.file.pack(fill=X, expand=True, padx=(0, 5))

def mostrarArch(Var):
	from tkinter import filedialog
	file = filedialog.askopenfilename(title='Choose a file')
	Var.set(file)

root = Tk()
root.title('Visor')
root.geometry('350x300')

inicio = Inicio(root)

#raise_frame(inicio)

root.mainloop()