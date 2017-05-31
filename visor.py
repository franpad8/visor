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
		self.instruction4.pack(side=LEFT, padx=5, pady=5, anchor=E)

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
				conn = pymssql.connect(HOST, USUARIO, PASSWORD, 'Matcher1')
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
		self.conn = pymssql.connect(HOST, USUARIO, PASSWORD, 'Matcher1')

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

	def get_msgs_text(self):
		""" Retrieve a string with all text messages concatenated """
		cursor = self.get_cursor()
		cursor.execute(
			"""	SELECT texto_msg as text
				FROM h_msgs """)
		txt = '\n'.join([row[0] for row in cursor.fetchall() if row[0] is not None])
		txt = re.sub('}','}\n', txt)
		return re.sub(r'(:\d+[A-Z]:)',r'\n\1', txt)
					


	def close_connection():
		self.conn.close()


class Busqueda(Frame):

	def __init__(self, master):
		""" Inicialización del contenedor gráfico principal """
		Frame.__init__(self, master)
		master.geometry('750x500')
		self.pack(fill=BOTH, expand=True, padx=20, pady=20)

		self.bd = BD()
		self.bd.create_table()

		self.crear_widgets()
			

	def crear_widgets(self):
		""" Crear los elementos de interfaz del usuario """
		def on_change(varname, index, mode):
                        txt = s.get()
                        num_lines = len(re.findall('\n', txt))
                        canvas.itemconfigure(idx, text=s.get())
                        canvas.config(scrollregion=(0, 0, 1000, 400 + num_lines * 13))
    	

		self.frame1 = Frame(self, bd=1, relief=SUNKEN)
		self.frame1.pack(fill=X)
		self.frame2 = Frame(self, bd=1, relief=SUNKEN, width=300, height=300)
		self.frame2.pack(fill=X)
		
		
		self.carga_button = Button(self, text='Ir a Carga', command=lambda:(self.destroy(), change_frame(Carga)))
		self.carga_button.pack(side=RIGHT, padx=5, pady=(10, 5))
		self.carga_button.place(rely=1.0, relx=1.0, x=0, y=0, anchor=SE)

		
		canvas = Canvas(self.frame2, bg='#FFFFFF', width=300, height=400)
		canvas.config(highlightthickness=0)
		hbar=Scrollbar(self.frame2, orient=HORIZONTAL)
		hbar.pack(side=BOTTOM, fill=X)
		hbar.config(command=canvas.xview)
		vbar = Scrollbar(self.frame2, orient=VERTICAL)
		vbar.pack(side=RIGHT, fill=Y)
		vbar.config(command=canvas.yview)
		canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
		canvas.pack(side=LEFT, expand=True, fill=X)
		s = StringVar()
		idx = canvas.create_text(10, 10, anchor="nw", text=s.get())

		s.trace_variable('w', on_change)

		s.set(self.bd.get_msgs_text())


		 


class Carga(Frame):

	def __init__(self, master):
		""" Inicialización del contenedor gráfico principal """
		Frame.__init__(self, master)
		self.pack(fill=BOTH, expand=True, padx=20, pady=20)
		master.geometry('550x200')
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

		self.busqueda_button = Button(self, text='Ir a Busqueda', command=lambda:(self.destroy(), change_frame(Busqueda)))
		self.busqueda_button.pack(side=RIGHT, padx=5, pady=(10, 5))
		self.busqueda_button.place(rely=1.0, relx=1.0, x=0, y=0, anchor=SE)


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

carga = Busqueda(root)

#raise_frame(inicio)

root.mainloop()
