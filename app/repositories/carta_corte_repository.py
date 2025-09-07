
from app.db.database import Database

class CartaCorteRepository:
    def __init__(self):
        self.db = Database()


    def get_cut_off_letter(self):
        date = self.db.execute("SELECT date('now')").fetchone()[0]
        query = """
            select id from pe_cortes where fecha = ? and estado = 1
        """
        cursor = self.db.execute(query, (date,))
        return cursor.fetchone()
    
    
    def get_cutting_details(self, corte_id):
        query = """
            SELECT
                cd.id AS corte_detalle_id,
                c.descripcion AS caja,
                cd.cantidad,
                pi.peso_minimo
            FROM pe_cortes_detalles cd
            JOIN pe_pesos_indicados pi ON pi.id = cd.peso_indicado_id
            JOIN cajas c ON c.id = pi.caja_id
            WHERE cd.corte_id = ?


        """
        cursor = self.db.execute(query, (corte_id,))
        return cursor.fetchall()



    def save_cut_off_chart(self, *args):
        detalles, fecha, localidad_id, hora = args

        try:
            conn = self.db  # tu conexión (sqlite3.connect o similar)
            cursor = conn.cursor()

            # iniciar transacción
            cursor.execute("BEGIN")

            # insertar cabecera
            query = """
                INSERT INTO pe_cortes (fecha, localidad_id, hora)
                VALUES (?, ?, ?)
            """
            cursor.execute(query, (fecha, localidad_id, hora))
            corte_id = cursor.lastrowid

            # insertar detalles
            for detalle in detalles:
                self.save_cutting_detail(cursor, corte_id, detalle)

            # confirmar cambios
            conn.commit()
            return corte_id

        except Exception as e:
            conn.rollback()
            print(f"[ERROR] No se pudo guardar el corte: {e}")
            return None


    def save_cutting_detail(self, cursor, corte_id, detalle):
        query = """
            INSERT INTO pe_cortes_detalles (corte_id, nombre_peso_indicado, cantidad, estado)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (
            corte_id,
            detalle["nombre_peso_indicado"],
            detalle["cantidad"],
            detalle["estado"]
        ))


    def save_weight(self, *args):
        corte_detalle_id, cantidad, fecha, hora = args
        query = """
             insert into pe_cortes_detalles (corte_detalle_id, cantidad, fecha, hora)
                values (?, ?, ?, ?)
            """
        self.db.execute(query, (corte_detalle_id, cantidad, fecha, hora))
    
    