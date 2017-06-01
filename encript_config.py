from tkinter import *
from tkinter import messagebox
import pymssql
import os
from Crypto.Cipher import AES
import base64
import binascii


# VARIABLES GLOBALES
HOST, USUARIO, PASSWORD = ('', '', '')

def change_frame(newframe):

    carga = newframe(root)
    carga.tkraise()


class Inicio(Frame):

    def __init__(self, master):
        """ Inicialización del contenedor gráfico principal """
        Frame.__init__(self, master)
        self.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.crear_widgets()

    def crear_widgets(self):
        """crear boton, text y entrada"""

        self.frame1 = Frame(self, bd=1, relief=SUNKEN)
        self.frame1.pack(fill=X)


        self.instruction1 = Label(self.frame1, text="Host: ", width=9, anchor=E)
        self.instruction1.pack(side=LEFT, padx=5, pady=5)

        self.host = Entry(self.frame1, width=24)
        self.host.pack(side=LEFT, padx=(0, 5))

        self.frame2 = Frame(self,bd=1, relief=SUNKEN)
        self.frame2.pack(fill=X)

        self.instruction2 = Label(self.frame2,text="Puerto: ", width=9, anchor=E)
        self.instruction2.pack(side=LEFT, padx=5, pady=5)

        self.puerto = Entry(self.frame2, width=5)
        self.puerto.pack(side=LEFT, padx=(0, 5))

        self.frame3 = Frame(self,bd=1, relief=SUNKEN)
        self.frame3.pack(fill=X)

        self.instruction3 = Label(self.frame3,text="Usuario: ", width=9, anchor=E)
        self.instruction3.pack(side=LEFT, padx=5, pady=5)

        self.usuario = Entry(self.frame3, width=24)
        self.usuario.pack(side=LEFT, padx=(0, 5))

        self.frame4 = Frame(self,bd=1, relief=SUNKEN)
        self.frame4.pack(fill=X)

        self.instruction4 = Label(self.frame4,text="Password: ", width=9, anchor=E)
        self.instruction4.pack(side=LEFT, padx=5, pady=5, anchor=E)

        self.password = Entry(self.frame4, width=24, show="*")
        self.password.pack(side=LEFT, padx=(0, 5))

        self.frame5 = Frame(self)
        self.frame5.pack(fill=X)

        self.submit_button = Button(self.frame5, text='Probar Conexión', command=self.probar_conexion)
        self.submit_button.pack(side=LEFT, padx=10, pady=(10, 0))

        self.frame6 = Frame(self)
        self.frame6.pack(fill=X)

        self.text = Text(self.frame6, height = 4, wrap = WORD)
        self.text.pack(fill=X, padx=0, pady=5)

        self.submit_button1 = Button(self.frame6, text = "Generar Archivo", state=DISABLED, command=self.generar_archivo)
        self.submit_button1.pack(side=RIGHT, padx=5)


    def generar_archivo(self):

        global HOST
        global USUARIO 
        global PASSWORD
        #Nombre del archivo a crear
        raiz = os.path.dirname(os.path.abspath(__file__))
        archivo = raiz + "\Configuracion.txt"
        obj = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
        obj1 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
        obj2 = AES.new('BCGBCG9876543210', AES.MODE_CFB, 'BCGBCG0123456789')
        ciphertext_host = obj.encrypt(HOST)
        ciphertext_usuario = obj1.encrypt(USUARIO)
        ciphertext_password = obj2.encrypt(PASSWORD)
        #abrir archivo
        fo = open(archivo, 'w')
        fo.write( "$\n")
        fo.write( "[H]"+str(base64.b64encode(ciphertext_host))+"\n")
        fo.write( "[U]"+str(base64.b64encode(ciphertext_usuario))+"\n")
        fo.write( "[C]"+str(base64.b64encode(ciphertext_password))+"\n")
        fo.write( "@@")
        #cerrar archivo
        fo.close()
        message = "Archivo generado en la ruta: " + archivo
        self.text.delete(1.0, END)
        self.text.insert(INSERT, message)
        self.text.config(foreground='GREEN')

    def probar_conexion(self):


        global HOST 
        HOST = self.host.get()
        global USUARIO
        USUARIO = self.usuario.get()
        global PASSWORD 
        PASSWORD = self.password.get()

        conn = None

        if HOST and USUARIO and PASSWORD:
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


if __name__ == '__main__':
    
    root = Tk()
    root.title('Visor')
    root.geometry('500x300')
    carga = Inicio(root)

    #raise_frame(inicio)

    root.mainloop()

