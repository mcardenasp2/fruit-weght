
from app.db.database import Database

class CartaCorteRepository:
    def __init__(self):
        self.db = Database()



    def get_cut_off_letter(self, fecha_str = None):
        query = """
            select * 
            from pe_cortes_encabezados
            where fecha = %s
            limit 1
        """
        data = self.db.execute(query, (fecha_str,), fetch=True)
        return data[0] if data else None

        
    def get_cut_off_letter_details(self, fecha_str=None):
        query = """
            select
            pcd.id corte_detalle_id,
            c.descripcion caja,
            cc.descripcion calidad_caja,
            pcd.cantidad ,
            pce.fecha,
            ppi.peso_ideal ,
            ppi.peso_maximo ,
            ppi.peso_minimo ,
            ppi.tara
            from public.pe_cortes_detalles pcd 
            join public.pe_cortes_encabezados pce on pcd.corte_encabezado_id = pce.id 
            join public.pe_pesos_indicados ppi on ppi.id = pcd.peso_indicado_id 
            join public.cajas c on c.id = ppi.caja_id 
            join public.calidad_cajas cc on cc.id = c.calidad_id 
            where pcd.estado = 1 and pce.fecha = %s
            order by c.descripcion, cc.descripcion
        """
        cursor = self.db.execute(query, (fecha_str,), fetch=True)
        return cursor if cursor else []
    

    def update_cut_off_chart_by_date(self, fecha_str):
        query = """
            UPDATE pe_cortes_detalles
            SET estado = 0
            where corte_encabezado_id in (
                select id from pe_cortes_encabezados where fecha = %s)
                
        """
        self.db.execute(query, (fecha_str,))



    def updateStatusCutDeatil(self, corte_detalle_id, cantidad):
        query = """
            Update pe_cortes_detalles
            set estado = 1, cantidad = %s
            where id = %s
            """
        self.db.execute(query, (cantidad, corte_detalle_id,))

    


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



    def save_cut_off_chart(self, localidad_id, fecha, hora):
        query = """
        INSERT INTO pe_cortes_encabezados (localidad_id, fecha, hora)
            VALUES (%s, %s, %s)
            returning *
            """
        data = self.db.execute(query,(localidad_id, fecha, hora), fetch=True)
        return data[0] if data else None



    def save_cutting_detail(self, corte_encabezado_id, peso_indicado_id, cantidad):
        query = """
            INSERT INTO pe_cortes_detalles (corte_encabezado_id, peso_indicado_id, cantidad, estado)
            VALUES (%s, %s, %s, %s)
        """
        self.db.execute(query, (corte_encabezado_id, peso_indicado_id, cantidad, 1))




    def save_weight(self, *args):
        corte_detalle_id, cantidad, fecha, hora = args
        query = """
             insert into pe_cortes_detalles (corte_detalle_id, cantidad, fecha, hora)
                values (?, ?, ?, ?)
            """
        self.db.execute(query, (corte_detalle_id, cantidad, fecha, hora))
    
    