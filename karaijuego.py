from tkinter import *
from tkinter import ttk
from tkinter.messagebox import *
import sqlite3 #IMPORTAMOS LA BIBLIOTECA PARA TRABAJAR CON SQLITE3
import winsound #libreria que se usa para reproducir sonidos  


class JuegoKarai:
    db_name="juegokarai.db" #NOS CONECTAMOS A LA BASE DE DATOS
    
    def __init__(self, window):
        self.wind = window
        self.wind.title("Trivia Karai Octubre 2026")
        self.wind.geometry("1050x600")

        # ---- SISTEMA DE PESTAÑAS (notebook)

        self.notebook = ttk.Notebook(self.wind)
        self.notebook.pack(fill="both", expand=True)#.pack empaqueta el panel de pestañas en la ventana principal.
        #fill="both"hace que se estire a lo ancho y a lo alto;
        #expand=true hace que la interfaz sea elasticas y se adapte si agrandamos la ventana.

        self.tab_juego = Frame(self.notebook)
        self.tab_admin = Frame(self.notebook)
        self.tab_stats = Frame(self.notebook)

        self.notebook.add(self.tab_juego, text="Vista del juego")
        self.notebook.add(self.tab_admin, text="Panel admin")
        self.notebook.add(self.tab_stats, text="Estadísticas")
        
        #variables de control de logica interna
        self.id_participante_actual= None
        self.preguntas= []
        self.indice_pregunta=0
        self.puntaje_actual=0

        
        # ---- JUEGO
        
        #cargamos la imagen de fondo de forma nativa (.png)
        self.imagen_fondo=PhotoImage(file="n.png")
        #usamos un label comun como contenedor de la imagen
        self.lbl_fondo=Label(self.tab_juego, image=self.imagen_fondo)
        #.place la ubica al fondo cubriendo toda la pestaña de forma elastica
        self.lbl_fondo.place(x=0, y=0)
        
        self.frame = LabelFrame(self.tab_juego,text="DESAFIA AL KARAI OCTUBRE", bg="#3F6350", fg="#FFFFFF" ,font=("Helvetica",11, "bold"))
        self.frame.grid(row=0,column=0,padx=20,pady=20)

        # Nombre
        self.label = Label(self.frame, text="Ingresa tu Nombre:" )
        self.label.grid(row=0, column=0, padx=10, pady=10)

        # Campo nombre
        self.nombre = Entry(self.frame, width=30)
        self.nombre.grid(row=0, column=1, padx=10, pady=10)

        # Categoría
        self.label_categoria = Label(self.frame, text="Elige tu Categoria:")
        self.label_categoria.grid(row=1, column=0, padx=10, pady=10)

        # Campo categoría
        self.categoria = ttk.Combobox(self.frame,width=27,state="readonly")
        self.categoria.grid(row=1,column=1,padx=10,pady=10)

        # Buscamos los grupos reales de forma relacional en la BD
        
        query_categorias="SELECT id_categoria, descripcion FROM Categorias"
        self.lista_categorias=self.run_query(query_categorias).fetchall() #fetchall trae los resultados y los guarda en una lista 
        #guardamos solo las descripciones textuales para mostrarlas en el desplegable
        self.categoria ['values'] = [g[1] for g in self.lista_categorias] #recorre cada tupla g de la lista y se qyeda unicamente 
        self.categoria.current(0)
        #selecciona automaticamente el primer elemento de la lsita (indice 0) para que el desplegable no quede vacio
        

        # Botón iniciar
        self.boton = Button(self.frame,text="INICIAR DESAFÍO", bg="#3F6350", fg="#FFFFFF" ,font=("Helvetica",11, "bold") ,command=self.registrar_participante)
        self.boton.grid(row=2,column=0,columnspan=2,padx=10,pady=10)

        #creamos los widgets pero no aparecen en la pantalla porque tidavia no le dimos la posicion
        self.lbl_pregunta=Label(self.frame, text="", font=("Arial Bold", 11),
                                wraplength=400, bg="white", justify=LEFT)
        self.btn_a= Button(self.frame, text="", font=("Arial", 11),
                           bg="#3E2723",fg="#F5EBE6", height=2, anchor="w", command=lambda: self.verificar_respuesta("A"))
        self.btn_b= Button(self.frame, text="", font=("Arial", 11),
                           bg="#3E2723",fg="#F5EBE6", height=2, anchor="w", command=lambda: self.verificar_respuesta("B"))
        self.btn_c= Button(self.frame, text="", font=("Arial", 11),
                           bg="#3E2723",fg="#F5EBE6", height=2, anchor="w", command=lambda: self.verificar_respuesta("C"))
                           

        # Tabla
        ranking_frame = LabelFrame(self.tab_juego,text="El tablero de la abundancia (Ranking)", bg="#3F6350", fg="#FFFFFF" ,font=("Helvetica",11, "bold"))
        ranking_frame.grid(row=0,column=1,padx=20,pady=20)

        
        self.tree = ttk.Treeview(ranking_frame,height=10,columns=("puntos", "situacion"))
        self.tree.grid(row=0,column=0,padx=10,pady=10)

        
        self.tree.column("#0",width=150,anchor=CENTER)
        self.tree.column("puntos",width=80,anchor=CENTER)
        self.tree.column("situacion",width=120,anchor=CENTER)

       
        self.tree.heading("#0",text="Participante",anchor=CENTER)
        self.tree.heading("puntos",text="Puntos",anchor=CENTER)
        self.tree.heading("situacion",text="Situacion",anchor=CENTER)

        # ---- ADMIN ----

        self.imagen_fondo1=PhotoImage(file="m.png")
        self.lbl_fondo1=Label(self.tab_admin, image=self.imagen_fondo1)
        self.lbl_fondo1.place(x=0, y=0)
        
        self.frame1 = LabelFrame(self.tab_admin, text="GESTION DE PARTICIPANTES", bg="#3F6350", fg="#FFFFFF" ,font=("Helvetica",11, "bold"))
        self.frame1.grid(row=0,column=0,padx=20,pady=20)

        

        # Nombre
        self.label_admin = Label(self.frame1, text="Espacio reservado para la gestion de la tabla 'participantes'",font=("Arial Italic", 10),fg="gray")
        self.label_admin.grid(row=0, column=0, padx=10, pady=10)

        self.tree1 = ttk.Treeview(self.frame1,height=10,columns=("puntos", "situacion"))
        self.tree1.grid(row=1,column=0,padx=10,pady=10)

        
        self.tree1.column("#0",width=150,anchor=CENTER)
        self.tree1.column("puntos",width=80,anchor=CENTER)
        self.tree1.column("situacion",width=120,anchor=CENTER)

       
        self.tree1.heading("#0",text="Participante",anchor=CENTER)
        self.tree1.heading("puntos",text="Puntos",anchor=CENTER)
        self.tree1.heading("situacion",text="Situacion",anchor=CENTER)

        # COLORES DE LAS FILAS DEL TREEVIEW
        for t in (self.tree, self.tree1):
            t.tag_configure("ABUNDANCIA", background="#3F6350",foreground="#FFFFFF")
            t.tag_configure("JUSTO", background="#9C6B1A",foreground="#FFFFFF")
            t.tag_configure("HORNO", background="#6E2C2C",foreground="#FFFFFF")

        # Botón baja
        self.boton1 = Button(self.frame1,text="Ejecutar BAJA de Registro Seleccionado", bg="#3F6350", fg="#FFFFFF" ,font=("Helvetica",11, "bold") ,command=self.delete_participante)
        self.boton1.grid(row=2,column=0,columnspan=2,padx=10,pady=10)

        # Botón vaciar
        self.boton2 = Button(self.frame1,text="Reiniciar Tabla(Vaciar Base de Datos)", bg="#3F6350", fg="#FFFFFF" ,font=("Helvetica",11, "bold") ,command=self.vaciar_base_datos)
        self.boton2.grid(row=3,column=0,columnspan=2,padx=10,pady=10)

        # ---- ESTADÍSTICAS ----

        self.imagen_fondo2=PhotoImage(file="p.png")
        self.lbl_fondo2=Label(self.tab_stats, image=self.imagen_fondo2)
        self.lbl_fondo2.place(x=0, y=0)
        
        self.frame_stats = LabelFrame(self.tab_stats, text="ESTADISTICAS", bg="#3F6350", fg="#FFFFFF" ,font=("Helvetica",11, "bold"))
        self.frame_stats.grid(row=0,column=10,padx=500,pady=300)

        # Nombre
        self.label_stats = Label(self.frame_stats, text="Metricas calculadas dinamicamente" ,font=("Arial Italic", 10),fg="gray")
        self.label_stats.grid(row=0, column=0, padx=10, pady=10)

        self.lbl_stat_total = Label(self.frame_stats, text="Total Jugadores Registrados: ", font=("Helvetica",20, "bold"))
        self.lbl_stat_total.grid(row=1, column=0, padx=10, pady=15)
                
        
        self.lbl_stat_abundancia= Label(self.frame_stats, text="Casas con Abundancia Total: ", font=("Helvetica",20, "bold"))
        self.lbl_stat_abundancia.grid(row=2, column=0, padx=10, pady=10)
        
        self.lbl_stat_horno= Label(self.frame_stats, text="Casas en Situacion Critica: ", font=("Helvetica",20, "bold"))
        self.lbl_stat_horno.grid(row=3, column=0, padx=10, pady=10)

        self.get_ranking()

    def run_query(self,query,parameters=()): #FUNCION PARA PASAR LA CONSULTA
        with sqlite3.connect(self.db_name) as conn: #CONECTO Y LO GUARDO EN CONN
            cursor=conn.cursor() #CURSOR PARA OBTENER LA POSICION EN LA BD
            result=cursor.execute(query, parameters) #EJECUTA LA CONSULTA
            conn.commit() #EJECUTA
        return result
    
    def registrar_participante(self):
        nombre = self.nombre.get().strip()# strip es un limpiador de espacios(al principio o al final)
        indice_seleccionado = self.categoria.current()
        #El método .current() en Tkinter sirve para saber qué posición (índice) seleccionó el usuario dentro
        #de un desplegable (ttk.Combobox).

        if len(nombre) == 0: #verifica que el usuario haya ingresado algo 
            showinfo("Atención", "Por favor, ingrese un nombre para jugar.")
            return

        
        id_categoria_elegido = self.lista_categorias[indice_seleccionado][0]
        

        # Restablecemos los colores bases de la interfaz interactiva
        self.frame.config(bg="#3F6350")

        query = "INSERT INTO participantes (nombre, puntaje, situacion_final) VALUES (?, 0, 'Jugando')"
        self.run_query(query, (nombre,))

        query_preguntas = "SELECT * FROM preguntas WHERE id_categoria = ?"
        self.preguntas = self.run_query(query_preguntas, (id_categoria_elegido,)).fetchall()

        # Esto solo se ejecuta si todo lo anterior salió bien
        self.label.grid_forget()
        self.nombre.grid_forget()
        self.label_categoria.grid_forget()
        self.categoria.grid_forget()
        self.boton.grid_forget()

        self.indice_pregunta = 0 #inicializa el contador de preguntas
        self.puntaje_actual = 0 #inicializa el contador de puntaje del participante

        self.mostrar_pregunta()
        self.get_ranking()

    def mostrar_pregunta(self):
        if self.indice_pregunta < len(self.preguntas):#Control de flujo, si todavía quedan preguntas sin responder
            p = self.preguntas[self.indice_pregunta]
            #Extracción de datos:Toma la tupla completa de la pregunta actual de la lista(la guarda en la
            #variable "p".
            #Si estamos en la pregunta 0, p guarda la primera tupla con
            #toda su fila de la base de datos: (id, enunciado, op_a, op_b, op_c, correcta).


        #ACÁ RECIÉN LE DAMOS LA POSICIÓN A LOS WIDGETS PARA MOSTRAR LAS PREGUNTAS
            self.lbl_pregunta.config(text=f"Desafío {self.indice_pregunta + 1}: {p[6]}", bg="#F4F1DE")
            self.lbl_pregunta.grid(row=0, columnspan=2, pady=20, padx=15, sticky=W)

            self.btn_a.config(text=f"A) {p[2]}")
            self.btn_a.grid(row=1, columnspan=2, sticky=W + E, pady=8, padx=15)

            self.btn_b.config(text=f"B) {p[3]}")
            self.btn_b.grid(row=2, columnspan=2, sticky=W + E, pady=8, padx=15)

            self.btn_c.config(text=f"C) {p[4]}")
            self.btn_c.grid(row=3, columnspan=2, sticky=W + E, pady=8, padx=15)
        else:
            self.finalizar_juego()

    def verificar_respuesta(self, opcion_elegida):
        pregunta_actual = self.preguntas[self.indice_pregunta]
        correcta = str(pregunta_actual[5]).strip().upper()

        if opcion_elegida == correcta:
            self.puntaje_actual += 1
            winsound.Beep(1000, 200)
        else:
            winsound.Beep(400, 300)

        self.indice_pregunta += 1
        self.mostrar_pregunta()

    def finalizar_juego(self):
        if self.puntaje_actual == len(self.preguntas):
            estado_final = "¡Abundancia total!"
            msg = f"¡Excelente! Completaste el desafío con éxito."
        elif self.puntaje_actual >= 1:
            estado_final = "¡Zafa con lo justo!"
            msg = f"¡Bien! Lograste responder correctamente." 
        else:
            estado_final = "¡Al horno!"
            msg = "El Karaí se queda."
        nombre_jugador = self.nombre.get().strip()


        query = "UPDATE participantes SET puntaje = ?, situacion_final = ? WHERE nombre = ? AND situacion_final = 'Jugando'"
        parametros = (int(self.puntaje_actual), estado_final, nombre_jugador)
        self.run_query(query, parametros)
         
        showinfo("Fin del Desafío", msg)



        self.lbl_pregunta.grid_forget()
        self.btn_a.grid_forget()
        self.btn_b.grid_forget()
        self.btn_c.grid_forget()

        self.nombre.delete(0, END)
        self.label.grid(row=0, column=0, pady=15, padx=15, sticky=W)
        self.nombre.grid(row=0, column=1, padx=15, pady=15)
        self.label_categoria.grid(row=1, column=0, pady=10, padx=15, sticky=W)
        self.categoria.grid(row=1, column=1, padx=15, pady=10)
        self.boton.grid(row=2, columnspan=2, pady=20, padx=15, sticky=W + E)
        self.get_ranking()
        
    def get_ranking(self):
        for t in (self.tree, self.tree1):
            for element in t.get_children():
                t.delete(element)

        query= "SELECT nombre, puntaje, situacion_final FROM Participantes ORDER BY puntaje DESC, id_participante DESC"
        db_rows=self.run_query(query).fetchall()

        for row in db_rows:
            if row[2] == "¡Abundancia total!":
                tag_asignado = "ABUNDANCIA"
            elif row[2] == "¡Zafa con lo justo!":
                tag_asignado = "JUSTO"
            else:
                tag_asignado = "HORNO"
            
            self.tree.insert("", END, text=row[0], values=(row[1], row[2]), tags=(tag_asignado,))
            self.tree1.insert("", END, text=row[0], values=(row[1], row[2]), tags=(tag_asignado,))

        self.calcular_estadisticas_sql()

    def delete_participante(self):
        seleccion = self.tree1.selection()
        if not seleccion:
            showinfo("Control Administrativo", "Por favor selecciones un afila del Treeview Admin para aplicar la BAJA.")
            return
        item_seleccionado = self.tree1.item(seleccion)
        nombre = item_seleccionado["text"]
        valores = item_seleccionado["values"]
        puntaje = valores[0]
        situacion = valores[1]

        confirmar = askyesno("Confirmacion", f"¿Confirmar la eliminacion del registro de '{nombre}'?")
        if confirmar:
            query = "DELETE FROM Participantes WHERE nombre=? AND puntaje=? AND situacion_final=?"
            self.run_query(query, (nombre, int(puntaje), situacion))
            showinfo("Proceso Completo", "El registro fue borrado satisfactoriamente.")
            self.get_ranking()

    def vaciar_base_datos(self):
        confirmar=askyesnocancel("ATENCION", "Esta por eliminar TODOS los registros del ranking.\n¿Esta seguro de que desea reiniciar la base de datos?")
        if confirmar:
            self.run_query("DELETE FROM ParticipanteS")
            showinfo("ABM", "Base de datos vaciada con exito.")
            self.get_ranking()

    def calcular_estadisticas_sql(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                tot = cursor.execute("SELECT COUNT(*) FROM Participantes").fetchone()[0]
                self.lbl_stat_total.config(text= f"Total Jugadores Registrados: {tot}")

                abund = cursor.execute("SELECT COUNT(*) FROM Participantes WHERE situacion_final = '¡Abundancia total!'").fetchone()[0]
                self.lbl_stat_abundancia.config(text= f"Casas con Abundancia Total: {abund}")
                
                horno = cursor.execute("SELECT COUNT(*) FROM Participantes WHERE situacion_final = '¡Al horno!'").fetchone()[0]
                self.lbl_stat_horno.config(text= f"Casas en Situacion Critica: {horno}")
        except Exception as e:
            print (f"Error en analiticas: {e}")
                                        
                
if __name__ == "__main__":
    window = Tk()
    application = JuegoKarai(window)
    window.mainloop()
