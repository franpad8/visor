# Código Fuente de Visor.
# Programa para cargar, visualizar y exportar datos
# de transacciones financieras.
# Creadores: Business Computer Group (BCG)

import sys
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
import pymssql
from datetime import datetime
import re
import os
import _mssql
import decimal
import uuid

#Set DB arguments
from Crypto.Cipher import AES
import base64
import binascii

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# VARIABLES GLOBALES
HOST, PUERTO, USUARIO, PASSWORD, DBNAME, BIC_CODE= ('', '', '', '', '', '')


def get_bd_args():
    """ Extraer y decodificar los argumentos de conexión a la base de datos """
    global BASE_DIR
    global HOST
    global USUARIO
    global PASSWORD
    global DBNAME
    global BIC_CODE

    #ruta del archivo a leer
    ruta = BASE_DIR + "\Configuracion.txt"

    try:
        #abrir archivo
        fo = open(ruta, 'r')
    except FileNotFoundError:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error", "No se encuentra el archivo de configuración.")
        sys.exit()

    lines = fo.readlines()
    obj1 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
    obj2 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
    obj3 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
    obj4 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
    obj5 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')

    try:
        for line in lines[1:]:
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

            elif opcion == "[B]":
                plaintext = obj4.decrypt(ciphertext)
                DBNAME = str(plaintext)[2:][:-1]

            elif opcion == "[I]":
                plaintext = obj5.decrypt(ciphertext)
                BIC_CODE = str(plaintext)[2:][:-1]

    except IndexError:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error", "Archivo de Configuración corrupto.")
        sys.exit()



def change_frame(newframe):
    """ Cambia el frame o ventana principal de la aplicación """
    carga = newframe(root)
    carga.tkraise()


def formato_expandido(txt):
    """ Funcion que toma texto de mensaje en formato fast mode y lo 
        convierte a formato expandido """
    txt = re.sub(r'\{1:F01(.{8}).*?\}.*?{2:([I|O])103.{10}(.{8}).*?\}\{3:\{.*?\}\}', 
                        r"""
--------------------------- Message Header -------------------------    
        I/O: \2             : FIN 103 Single Customer Credit Transfer
        Sender : \1 
        Receiver : \3 """,
                    txt)
    txt = re.sub(r'\{4:', r"""
--------------------------- Message Text ---------------------------
""", txt)
    txt = re.sub(r':20:(.*)',
      r"""        20: Sender's Reference
            \1""", 
    txt)
    txt = re.sub(r':23B:(.*)',
      r"""        23B: Bank Operation Code
             \1""", 
    txt)
    txt = re.sub(r':23E:(.{4})/(.*)',
      r"""        23E: Instruction Code
             Instruction :  \1
             Additional info :  \2""", 
    txt)
    txt = re.sub(r':32A:(\d{2})(\d{2})(\d{2})(.{3})(.*)',
      r"""        32A: Val Dte/Curr/Interbnk Settld Amt
             Date        :  \3/\2/20\1
             Currency    :  \4
             Amount      :  #\5#""", 
    txt)
    txt = re.sub(r':50K:(/\d+)(.*)',
      r"""        50K: Ordering Customer-Name & Address
             \1
             \2""", 
    txt)
    txt = re.sub(r':53B:(/\d+)(.*)',
      r"""        53B: Sender's Correspondent-Name & Address
             \1
             \2""", 
    txt)
    txt = re.sub(r':57A:(.*)',
      r"""        57A: Account with Institution
             \1""", 
    txt)
    txt = re.sub(r':57D:(//[A-Z]*\d+)(.*)',
      r"""        57D: Account with Institution
             \1
             \2""", 
    txt)
    txt = re.sub(r':59:(/[A-Z]*\d+)(.*)',
      r"""        59: Beneficiary Customer-Name & Addr
            \1
            \2""", 
    txt)
    txt = re.sub(r':70:(.*)',
      r"""        70: Remittance Information
            \1""", 
    txt)
    txt = re.sub(r':71A:(.*)',
      r"""        71A: Details of Charges
             \1""", 
    txt)
    txt = re.sub(r':(\d{2}[A-Z]?):(.*)',
      r"""        \1: \2""", 
    txt)

    txt = re.sub(r'-\}', r'\n\n\n', txt)
    #txt = "\n\t".join(list(map(lambda x:fill(x, 75, replace_whitespace=False), txt.splitlines())))
    return txt
            


class BD():
    """ Clase que se encarga de la conexión y comunicación con la Base 
        de Datos """

    def __init__(self):
        try:
            self.conn = pymssql.connect(HOST, USUARIO, PASSWORD, DBNAME)
        except pymssql.OperationalError as oe:
            root.withdraw()
            messagebox.showerror("Error de conexión a la Base de Datos", str(oe))
            sys.exit()


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
                texto_msg TEXT,
                bic VARCHAR(11)
            )
        """)
        self.conn.commit()

    def save_trxs(self, trans):
        """ Persist a list of trxs in DB """
        self.get_cursor().executemany(
            "INSERT INTO h_msgs VALUES (%s, %s, %s, %s, %s, %s, %s)",
            trans)
        self.conn.commit()

    def get_all_msgs_text(self):
        """ Devuelve una cadena de caracteres con todos los mensajes
            concatenados """
        cursor = self.get_cursor()
        cursor.execute(
            """ SELECT texto_msg as text
                FROM h_msgs 
                WHERE bic LIKE '%s'""") % (BIC_CODE)
        txt = '\n'.join([row[0] for row in cursor.fetchall() if row[0] is not None])
        txt = re.sub('(}}?)','\1\n', txt)
        return re.sub(r'(:\d+[A-Z]?:)',r'\n\1', txt)

    def get_msgs_text(self, text, fecha1, fecha2, tipo):
        """ Devuelve una cadena de caracteres con todos los mensajes que cumplen
            con los criterios especificados en los argumentos """
        cursor = self.get_cursor()
        query = (""" SELECT texto_msg, tipo, io as text
                     FROM h_msgs
                     WHERE texto_msg COLLATE Latin1_General_CI_AS LIKE '%%%s%%'
                     AND fecha BETWEEN %s AND %s
                     AND tipo LIKE '%%%s%%'
                     AND bic LIKE '%s'
                 """) % (text, fecha1, fecha2, tipo, BIC_CODE)
        print(query)
        cursor.execute(query)
        acc = ''
        num_results = 0
        #txt = '\n'.join([row[0] for row in cursor.fetchall() if row[0] is not None])

        for row in cursor.fetchall():
            if row[0] is not None:
                txt = row[0]
                acc = acc + "\n" + txt
                num_results = num_results + 1

        return (num_results, acc)


    def close_connection():
        self.conn.close()


class Busqueda(Frame):
    """ Se encarga de la busqueda, muestra e impresión de los mensajes
        almacenados """

    def __init__(self, master):
        """ Inicialización del contenedor gráfico principal """
        Frame.__init__(self, master)
        master.geometry('900x700')
        self.pack(fill=BOTH, padx=20, pady=(20,20), expand=True)

        self.bd = BD()
        self.bd.create_table()

        self.crear_widgets()
            

    def crear_widgets(self):
        """ Crear los elementos de interfaz del usuario """

        def on_change(varname, index, mode):
            txt = s.get()
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
                num_results, text_results = self.bd.get_msgs_text(self.text.get(), date1, date2, tipo)
                VarNumResults.set(str(num_results) + " mensajes encontrados")
                s.set(text_results)
                        
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

        def limpiar():
            self.VarTipo.set('')
            self.date1.delete(0, END)
            self.date1.insert(0, "")
            self.date2.delete(0, END)
            self.date2.insert(0, "")
            self.text.delete(0, END)
            self.text.insert(0, "")
                     

        self.frame1 = Frame(self, bd=1, relief=RAISED)
        self.frame1.pack(fill=BOTH)

        self.instruction1 = Label(self.frame1, text="Texto: ", width=8, anchor=E)
        self.instruction1.pack(side=LEFT, padx=5, pady=5)

        self.text = Entry(self.frame1)
        self.text.pack(side=LEFT, padx=(0, 5))

        self.instruction2 = Label(self.frame1, text="Fecha (dd/mm/aaaa):", width=18, anchor=E)
        self.instruction2.pack(side=LEFT, padx=5, pady=5)

        self.date1 = Entry(self.frame1, width=10)
        self.date1.pack(side=LEFT, padx=0)

        self.dash = Label(self.frame1, text="-", width=1, anchor=E)
        self.dash.pack(side=LEFT, padx=(0,1), pady=5)
        
        self.date2 = Entry(self.frame1, width=10)
        self.date2.pack(side=LEFT, padx=(0, 5))

        self.VarTipo = StringVar()
        self.VarTipo.set('')

        self.instruction2 = Label(self.frame1, text="Tipo: ", width=8, anchor=E)
        self.instruction2.pack(side=LEFT, padx=5, pady=5)

        self.listbox = OptionMenu(self.frame1, self.VarTipo, "", "101","103","110","111",
                                    "112","192","195","196","199","202","299","300","410",
                                    "420","422","456","499","671","700","701","707","710",
                                    "711","730","734","740","754","760","767","769","799",
                                    "900","910","940","950","995","996","998","999")
        self.listbox.pack(side=LEFT, padx=(0, 5))

        self.search_button = Button(self.frame1, text='Buscar', width=10, font="Helvetica 10", command=buscar)
        self.search_button.pack(side=LEFT, padx=(40, 5), pady=5)

        self.clear_button = Button(self.frame1, text='Limpiar', width=10, font="Helvetica 8", command=limpiar)
        self.clear_button.pack(side=LEFT, padx=(20,5), pady=5)

        self.frame3 = Frame(self, bd=0)
        self.frame3.pack(fill=X, pady=(20, 5))
        
        self.print_button = Button(self.frame3, text='Imprimir', width=8, font="Helvetica 9", command=imprimir)
        self.print_button.pack(side=LEFT, padx=(30, 5))

        VarNumResults = StringVar()
        VarNumResults.set('')
        self.num_res = Label(self.frame3, textvariable=VarNumResults, width=30, foreground='green', font="Helvetica 9 bold")
        self.num_res.pack(side=RIGHT, padx=5, pady=0)
        
        self.frame2 = Frame(self, bd=1)
        self.frame2.pack(fill=BOTH, pady=(0,30), expand=True)

        s = StringVar()
        s.set('Prueba')
        self.txt = scrolledtext.ScrolledText(self.frame2, undo=True, state=DISABLED)
        self.txt['font'] = ('consolas', '12')
        self.txt.pack(fill=BOTH, pady=(0,0), expand=True)

       
        
        self.carga_button = Button(self, text='Ir a Carga', command=lambda:(self.destroy(), change_frame(Carga)))
        self.carga_button.place(rely=1.0, relx=1.0, x=0, y=0, anchor=SE)

        s.trace_variable('w', on_change)

         


class Carga(Frame):
    """ Se encarga de la lectura de los archivos y carga(en BD)
        de todos los mensajes que dichos archivos contienen """

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

        self.frame1 = Frame(self, bd=1, relief=RAISED)
        self.frame1.pack(fill=X)

        self.instruction1 = Label(self.frame1,text="Archivo de carga:", width=18)
        self.instruction1.pack(side=LEFT, padx=0, pady=5)

        self.filename = Entry(self.frame1, textvariable = MyText, width=40)
        self.filename.pack(side=LEFT, padx=(0, 5))

        self.search_button = Button(self.frame1, text='Buscar', font="Helvetica 10", command=lambda:buscar_arch(MyText))
        self.search_button.pack(side=LEFT, padx=(10,5), pady=5)

        self.load_button = Button(self.frame1, text='Cargar', font="Helvetica 9", command=lambda:cargar_arch(MyText))
        self.load_button.pack(side=LEFT, padx=(10, 5), pady=5)

        self.frame2 = Frame(self, bd=1)
        self.frame2.pack(fill=BOTH)

        self.proc_status = Label(self.frame2, textvariable = varProcStatus, foreground='green', font="Helvetica 9 bold")
        self.proc_status.pack(fill=X, expand=True, padx=(0, 5))

        self.num_trans_cargadas = Label(self.frame2, textvariable = varNumTrans, font="Helvetica 8 bold")
        self.num_trans_cargadas.pack(fill=X, expand=True, padx=(0, 5))

        self.busqueda_button = Button(self, text='Ir a Búsqueda', command=lambda:(self.destroy(), change_frame(Busqueda)))
        self.busqueda_button.pack(side=RIGHT, padx=5, pady=(10, 5))
        self.busqueda_button.place(rely=1.0, relx=1.0, x=0, y=0, anchor=SE)


        def buscar_arch(Var):
            """ Despliegue de modal de búsqueda y selección de archivo de carga """
            from tkinter import filedialog
            file = filedialog.askopenfilename(title='Choose a file')
            Var.set(file)

        def cargar_arch(Var):
            """ Lectura y carga del archivo de datos """

            def obtener_texto_msg(arr, tipo):
                """ Toma el arreglo de campos del msg y retorna un string con el texto del mensaje """
                m = re.search('{1:.*-}', ''.join(arr))
                if m:
                     
                    txt = m.group(0)
                    txt = re.sub(r'(:\d+[A-Z]?:)',r'\n\1', txt)
                    

                    # A los mensajes 103, los imprimimos con formato parecido a prt
                    if tipo == '103': 
                        txt = formato_expandido(txt)
                    else:
                        txt = re.sub(r'(\}\}?)',r'\1\n', txt)
                    return txt

                return None

            varProcStatus.set('Procesando...')
            self.proc_status.config(foreground='black')
                    
            try:

                with open(Var.get()) as f:
                    
                    trans = [(str(tran[0]), str(tran[5]), datetime.strptime(tran[7], '%d-%b-%y').date(), str(tran[8]), str(tran[10]), obtener_texto_msg(tran[25:], str(tran[8])), str(BIC_CODE))
                                    for tran in map(lambda l: l.split(";") ,[line for line in f.readlines()[1:] if line.strip() != ''])]
                    num_trans = len(trans) # conteo de transacciones
                    self.bd.save_trxs(trans)
                    varProcStatus.set('El archivo se ha procesado satisfactoriamente.')
                    self.proc_status.config(foreground='green')
                    varNumTrans.set("%s mensajes cargados." % num_trans)

            except IndexError as idx:
                messagebox.showerror("Error", 'El archivo no cuenta con el formato apropiado.')
                varProcStatus.set('')

            except ValueError as ve:
                messagebox.showerror("Error", 'El archivo no cuenta con el formato apropiado.')
                varProcStatus.set('')

            except pymssql.IntegrityError:
                messagebox.showerror("Error", 'El archivo contiene transacciones ya cargadas en BD.')
                varProcStatus.set('')

            except FileNotFoundError:
                messagebox.showerror("Error", 'No se encuentra el archivo seleccionado.')
                varProcStatus.set('')

            except:
                messagebox.showerror("Error", 'Ha ocurrido un error en el sistema. Por favor, contacte a BCG.')
                varProcStatus.set('')


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
