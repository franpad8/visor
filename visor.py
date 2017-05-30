# Código Fuente de Visor.
# Programa para cargar, visualizar y exportar datos
# de transacciones financieras.
# Creadores: BCG


from tkinter import *
import pymssql
from datetime import datetime
import re


# VARIABLES GLOBALES
HOST, PUERTO, USUARIO, PASSWORD = ('localhost', '1433', 'sa', '..asdf1234')

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


		global HOST 
		HOST = self.host.get()
		global PUERTO 
		PUERTO = self.puerto.get()
		global USUARIO 
		USUARIO = self.usuario.get()
		global PASSWORD 
		PASSWORD = self.password.get()

		conn = None

		if HOST and PUERTO and USUARIO and PASSWORD:
			try:
				conn = pymssql.connect(HOST, USUARIO, PASSWORD, 'Matcher')
				conn.close()

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



class BD():

	def __init__(self):
		self.conn = pymssql.connect(HOST, USUARIO, PASSWORD, 'Matcher')

	def get_cursor(self):
		return self.conn.cursor()

	def create_table(self):
		self.get_cursor().execute("""
		IF OBJECT_ID('h_msgs', 'U') IS NULL
			CREATE TABLE h_msgs (
				id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
			    swift_tid VARCHAR(16) NOT NULL UNIQUE,
			    io VARCHAR(1),
			    fecha DATE,
			    tipo VARCHAR(3),
			    receiver VARCHAR(12),
			    texto_msg TEXT
			)
		""")
		self.conn.commit()

	def save_trxs(self, trans):
		""" Persist a list of trxs in DB """
		self.get_cursor().executemany(
			"INSERT INTO h_msgs VALUES (%s, %s, %s, %s, %s, %s)",
			trans)
		self.conn.commit()


	def close_connection():
		self.conn.close()

			


class Carga(Frame):

	def __init__(self, master):
		""" Inicialización del contenedor gráfico principal """
		Frame.__init__(self, master)
		self.pack(padx=20, pady=20)

		self.bd = BD()
		self.bd.create_table()

		self.crear_widgets()

	def crear_widgets(self):
		
		MyText = StringVar()
		varNumTrans = StringVar()
		varProcStatus = StringVar()

		self.frame1 = Frame(self, bd=1, relief=SUNKEN)
		self.frame1.pack(fill=X)
		"""crear boton, text y entrada"""
		self.instruction1 = Label(self.frame1,text="Archivo de carga: ")
		self.instruction1.pack(side=LEFT, padx=5, pady=5)

		self.filename = Entry(self.frame1, textvariable = MyText, width=40)
		self.filename.pack(side=LEFT, expand=True, padx=(0, 5))

		self.search_button = Button(self.frame1, text='Buscar', command=lambda:buscar_arch(MyText))
		self.search_button.pack(side=LEFT, padx=5, pady=5)

		self.load_button = Button(self.frame1, text='Cargar', command=lambda:cargar_arch(MyText))
		self.load_button.pack(side=LEFT, padx=(10, 5), pady=5)

		self.frame2 = Frame(self, bd=1)
		self.frame2.pack(fill=BOTH)

		self.proc_status = Label(self.frame2, textvariable = varProcStatus, fg='green')
		self.proc_status.pack(fill=X, expand=True, padx=(0, 5))

		self.num_trans_cargadas = Label(self.frame2, textvariable = varNumTrans)
		self.num_trans_cargadas.pack(side=LEFT, padx=(0, 5))


		def buscar_arch(Var):
			""" Despliegue de modal de búsqueda y selección de archivo de carga """
			from tkinter import filedialog
			file = filedialog.askopenfilename(title='Choose a file')
			Var.set(file)

		def cargar_arch(Var):
			""" Lectura y carga del archivo de datos """

			def obtener_texto_msg(arr):
				""" Toma el arreglo de campos del msg y retorna un string con el texto del mensaje """
				m = re.search('{1:.*-}', ''.join(arr))
				if m:
					return m.group(0)

				return None


			varProcStatus.set('Procesando...')
			self.proc_status.config(foreground='black')
					
			try:

				with open(Var.get()) as f:
					
					trans = [(str(tran[0]), str(tran[5]), datetime.strptime(tran[7], '%d/%m/%Y').date(), str(tran[8]), str(tran[10]), obtener_texto_msg(tran[25:])) for tran in map(lambda l: l.split(";") ,f.readlines()[1:]) if len(tran) > 1]
					num_trans = len(trans) # conteo de transacciones
					self.bd.save_trxs(trans)

					varProcStatus.set('El archivo se ha procesado satisfactoriamente.')
					self.proc_status.config(foreground='green')
					varNumTrans.set("%s transacciones cargadas." % num_trans)

			except IndexError:
				varProcStatus.set('El archivo no cuenta con el formato apropiado.')
				self.proc_status.config(foreground='red')
				varNumTrans.set("")

			except pymssql.IntegrityError:
				varProcStatus.set('El archivo contiene transacciones ya cargadas en BD.')
				self.proc_status.config(foreground='red')
				varNumTrans.set("")

			








def parsear_monto_moneda(linea):
	monto, moneda = linea.split("/")
	if moneda != 'XXX':
		monto = monto.replace(',', '.')

	return monto, moneda


root = Tk()
root.title('Visor')
root.geometry('550x300')

carga = Carga(root)

#raise_frame(inicio)

root.mainloop()