import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psycopg2

class NorthwindVerificador:
    def __init__(self, root):
        self.root = root
        self.root.title("Northwind - Verificador de Requisitos")
        self.root.geometry("1000x700")
        
        # Conexión
        try:
            self.conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_Kq6ZpclDrAP5@ep-empty-sound-adx9a6ed-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar:\n{e}")
            return
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        title = ttk.Label(main_frame, text="✅ VERIFICADOR NORTHWIND - Lo que YA está en PostgreSQL", 
                         font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Botones para VERIFICAR lo existente
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="1. Ver Vistas Creadas", 
                  command=self.ver_vistas).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="2. Ver Procedures", 
                  command=self.ver_procedures).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="3. Probar Vistas", 
                  command=self.probar_vistas).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="4. Probar Procedures", 
                  command=self.probar_procedures).pack(side="left", padx=5)
        
        # Área de resultados
        self.text_resultados = scrolledtext.ScrolledText(main_frame, width=120, height=30)
        self.text_resultados.pack(fill="both", expand=True)
        
        # Mensaje inicial
        self.text_resultados.insert("end", 
            "🔍 ESTA INTERFAZ SOLO VERIFICA LO QUE YA ESTÁ CREADO EN POSTGRESQL\n"
            "Todos los requisitos (consultas, vistas, procedures, CRUD) están en el archivo SQL\n\n"
        )
    
    def ver_vistas(self):
        """Muestra las vistas que YA existen en la BD"""
        self.text_resultados.delete(1.0, "end")
        
        # Ver qué vistas tenemos
        self.ejecutar_y_mostrar("""
            SELECT table_name as vista, table_type as tipo
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'VIEW'
            ORDER BY table_name;
        """, "VISTAS EXISTENTES EN LA BD")
    
    def ver_procedures(self):
        """Muestra los procedures que YA existen en la BD"""
        self.text_resultados.delete(1.0, "end")
        
        self.ejecutar_y_mostrar("""
            SELECT routine_name as procedimiento, routine_type as tipo
            FROM information_schema.routines 
            WHERE routine_schema = 'public'
            ORDER BY routine_name;
        """, "PROCEDURES EXISTENTES EN LA BD")
    
    def probar_vistas(self):
        """Prueba las vistas que YA están creadas"""
        self.text_resultados.delete(1.0, "end")
        
        self.ejecutar_y_mostrar("SELECT * FROM VistaPedidosDetalles LIMIT 10;", 
                               "PROBANDO VISTA: Pedidos con Detalles")
        
        self.ejecutar_y_mostrar("SELECT * FROM VistaVentasCliente LIMIT 10;", 
                               "PROBANDO VISTA: Ventas por Cliente")
    
    def probar_procedures(self):
        """Prueba los procedures que YA están creados"""
        self.text_resultados.delete(1.0, "end")
        
        self.ejecutar_y_mostrar("SELECT * FROM sp_historial_pedidos_cliente(1) LIMIT 5;", 
                               "PROBANDO PROCEDURE: Historial de Cliente")
        
        # Probar el procedure de insertar (solo una vez para demostrar)
        self.ejecutar_y_mostrar("SELECT sp_registrar_pedido_completo(1, 1, 1, 2) as nuevo_pedido_id;", 
                               "PROBANDO PROCEDURE: Registrar Pedido")
    
    def ejecutar_y_mostrar(self, sql, descripcion):
        """Ejecuta y muestra resultados"""
        try:
            self.text_resultados.insert("end", f"\n🎯 {descripcion}\n")
            self.text_resultados.insert("end", f"📋 SQL: {sql}\n")
            self.text_resultados.insert("end", "─" * 60 + "\n")
            
            self.cursor.execute(sql)
            
            if sql.strip().upper().startswith("SELECT"):
                resultados = self.cursor.fetchall()
                
                if resultados:
                    # Mostrar columnas
                    columnas = [desc[0] for desc in self.cursor.description]
                    self.text_resultados.insert("end", " | ".join(columnas) + "\n")
                    self.text_resultados.insert("end", "─" * 80 + "\n")
                    
                    # Mostrar datos
                    for fila in resultados:
                        fila_str = " | ".join(str(valor) for valor in fila)
                        self.text_resultados.insert("end", fila_str + "\n")
                else:
                    self.text_resultados.insert("end", "✅ Ejecutado (sin resultados para mostrar)\n")
            else:
                self.conn.commit()
                self.text_resultados.insert("end", "✅ Ejecutado correctamente\n")
                
            self.text_resultados.insert("end", "\n" + "="*80 + "\n\n")
            self.text_resultados.see("end")
            
        except Exception as e:
            self.text_resultados.insert("end", f"❌ Error: {e}\n\n")
            self.conn.rollback()

if __name__ == "__main__":
    root = tk.Tk()
    app = NorthwindVerificador(root)
    root.mainloop()
