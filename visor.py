# Código Fuente de Visor.
# Programa para cargar, visualizar y exportar datos
# de transacciones financieras.
# Creadores: BCG


from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
import pymssql
from datetime import datetime
import re
import os

#Set DB arguments
from Crypto.Cipher import AES
import base64
import binascii

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_bd_args():

    global BASE_DIR
    global HOST
    global USUARIO
    global PASSWORD

    #ruta del archivo a leer
    ruta = BASE_DIR + "\Configuracion.txt"
    print(ruta)

    try:
        #abrir archivo
        fo = open(ruta, 'r')
    except FileNotFoundError:
        print("No se encuentra el archivo de configuración.")
        exit(1)

    lines = fo.readlines()
    obj1 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
    obj2 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
    obj3 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')

    try:
        for line in lines[1:4]:
            opcion = line[:3]

            cargar = line[5:][:-1]
            b = bytes(cargar, 'utf-8')
            bla = binascii.hexlify(b)
            ciphertext = binascii.unhexlify(bla)
            ciphertext = base64.b64decode(ciphertext)
                 
            

            if opcion == "[H]":
                plaintext = obj1.decrypt(ciphertext)
                HOST = str(plaintext)[2:][:-1]

            elif opcion == "[U]":
                plaintext = obj2.decrypt(ciphertext)
                USUARIO = str(plaintext)[2:][:-1]

            elif opcion == "[C]":
                plaintext = obj3.decrypt(ciphertext)
                PASSWORD = str(plaintext)[2:][:-1]

    except IndexError:
        print("Archivo de Configuración corrupto.")
        exit(1)



# VARIABLES GLOBALES
HOST, PUERTO, USUARIO, PASSWORD = ('', '', '', '')




def change_frame(newframe):

    carga = newframe(root)
    carga.tkraise()


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

    def get_all_msgs_text(self):
        """ Retrieve a string with all text messages concatenated """
        cursor = self.get_cursor()
        cursor.execute(
            """ SELECT texto_msg as text
                FROM h_msgs """)
        txt = '\n'.join([row[0] for row in cursor.fetchall() if row[0] is not None])
        txt = re.sub('(}}?)','\1\n', txt)
        return re.sub(r'(:\d+[A-Z]?:)',r'\n\1', txt)

    def get_msgs_text(self, text, fecha1, fecha2, tipo):
        """ Retrieve a string with all text messages that match the given criteria """
        cursor = self.get_cursor()
        query = (""" SELECT texto_msg as text
                     FROM h_msgs 
                     WHERE texto_msg COLLATE Latin1_General_CI_AS LIKE '%%%s%%'
                     AND fecha BETWEEN %s AND %s
                     AND tipo LIKE '%%%s%%'
                 """) % (text, fecha1, fecha2, tipo)
        print(query)
        cursor.execute(query)
        txt = '\n'.join([row[0] for row in cursor.fetchall() if row[0] is not None])
        txt = re.sub(r'(\}\}?)',r'\1\n', txt)
        return re.sub(r'(:\d+[A-Z]?:)',r'\n\1', txt)


    def close_connection():
        self.conn.close()


class Busqueda(Frame):

    def __init__(self, master):
        """ Inicialización del contenedor gráfico principal """
        Frame.__init__(self, master)
        master.geometry('800x600')
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)

        self.bd = BD()
        self.bd.create_table()

        self.crear_widgets()
            

    def crear_widgets(self):
        """ Crear los elementos de interfaz del usuario """

        def on_change(varname, index, mode):
            txt = s.get()
            num_lines = len(re.findall('\n', txt))
            self.txt.config(state=NORMAL)
            self.txt.delete(1.0, END)
            self.txt.insert(INSERT, txt)
            self.txt.config(state=DISABLED)

                        
        def buscar():
            """ Obtiene de bd y muestra el texto de los mensajes solicitados """
            if validar_input():
                date1 = '\'01/01/1977\'' if not self.date1.get() else ('DATEFROMPARTS(' + self.date1.get()[6:] + ',' + self.date1.get()[3:5]+ ',' +  self.date1.get()[0:2] + ')')
                date2 = 'GETDATE()' if not self.date2.get() else ('DATEFROMPARTS(' + self.date2.get()[6:] + ',' + self.date2.get()[3:5]+ ',' +  self.date2.get()[0:2] + ')')
                tipo = self.VarTipo.get()
                s.set(self.bd.get_msgs_text(self.text.get(), date1, date2, tipo))
                        
        def validar_input():
            date1, date2 = (self.date1.get(), self.date2.get())
            if date1 and not re.match(r'\d{2}/\d{2}/\d{4}', date1) or date2 and not re.match(r'\d{2}/\d{2}/\d{4}', date2):
                messagebox.showerror('Error de formato', 'La fecha debe contener el formato dd\mm\\aaaa')
                return False

            if date1:
                try:
                    date = datetime(int(date1[6:]), int(date1[3:5]), (int(date1[0:2])))
                except ValueError:
                    messagebox.showerror('Error de formato', '%s no es una fecha valida' % date1)
                    return False

            if date2:
                try:
                    date = datetime(int(date2[6:]), int(date2[3:5]), (int(date2[0:2])))
                except ValueError:
                    messagebox.showerror('Error de formato', '%s no es una fecha valida' % date2)
                    return False

            return True

        def imprimir():
            archivo = BASE_DIR + '\\%s.txt' %  datetime.now().strftime('%Y%m%d-%H%M%S')
            fo = open(archivo, 'w')
            fo.write(s.get())
            fo.close()
            messagebox.showinfo('', 'Archivo generado')
                     

        self.frame1 = Frame(self, bd=1, relief=SUNKEN)
        self.frame1.pack(fill=X)

        self.instruction1 = Label(self.frame1, text="Texto: ", width=8, anchor=E)
        self.instruction1.pack(side=LEFT, padx=5, pady=5)

        self.text = Entry(self.frame1)
        self.text.pack(side=LEFT, padx=(0, 5))

        self.instruction2 = Label(self.frame1, text="Fecha: ", width=8, anchor=E)
        self.instruction2.pack(side=LEFT, padx=5, pady=5)

        self.date1 = Entry(self.frame1, width=10)
        self.date1.pack(side=LEFT, padx=(0, 5))
        
        self.date2 = Entry(self.frame1, width=10)
        self.date2.pack(side=LEFT, padx=(0, 5))

        self.VarTipo = StringVar()
        self.VarTipo.set('')

        self.instruction2 = Label(self.frame1, text="Tipo: ", width=8, anchor=E)
        self.instruction2.pack(side=LEFT, padx=5, pady=5)

        self.listbox = OptionMenu(self.frame1, self.VarTipo, "", "103", "199")
        self.listbox.pack(side=LEFT, padx=(0, 5))

        self.search_button = Button(self.frame1, text='Buscar', width=10, command=buscar)
        self.search_button.pack(side=LEFT, padx=(60, 5), pady=5)

        self.frame3 = Frame(self, bd=0)
        self.frame3.pack(fill=X, pady=(20, 5))
        
        self.print_button = Button(self.frame3, text='Imprimir', width=8, command=imprimir)
        self.print_button.pack(side=LEFT, padx=(30, 5))
        
        self.frame2 = Frame(self, bd=1, height=300)
        self.frame2.pack(fill=X, pady=(0,40))

        s = StringVar()
        s.set('Prueba')
        self.txt = scrolledtext.ScrolledText(self.frame2, undo=True, state=DISABLED)
        self.txt['font'] = ('consolas', '12')
        self.txt.pack(fill=X)

        self.frame4 = Frame(self, bd=1)
        self.frame4.pack(fill=X, pady=(0,10))
        
        self.carga_button = Button(self, text='Ir a Carga', command=lambda:(self.destroy(), change_frame(Carga)))
        self.carga_button.place(rely=1.0, relx=1.0, x=0, y=0, anchor=SE)

        s.trace_variable('w', on_change)

         


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

if __name__ == '__main__':
    get_bd_args()

    root = Tk()
    root.title('Visor')

    carga = Busqueda(root)

    root.mainloop()
