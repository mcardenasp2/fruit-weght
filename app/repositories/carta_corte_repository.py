
from app.db.database import Database

from datetime import date, timedelta

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




    def save_weight(self, corte_detalle_id, cantidad, fecha, hora ):
        query = """
             insert into pe_pesos (corte_detalle_id, cantidad, fecha, hora)
                values (%s, %s, %s, %s)
            returning *
            """
        data = self.db.execute(query, (corte_detalle_id, cantidad, fecha, hora), fetch=True)
        return data[0] if data else None
    

    def get_data_to_replicate(self, tipo, fecha_str=None):
        """
        Obtiene datos pendientes de replicar según tipo:
        - tipo="actual": solo registros del día actual
        - tipo="historico": registros anteriores a hoy (o fecha_str si se pasa)
        """
        base_query = """
            SELECT 
                pp.id peso_id,
                pce.fecha corte_fecha,
                pce.hora corte_hora,
                c.descripcion caja,
                cc.descripcion calidad_caja,
                pcd.cantidad cantidad_cajas,
                ppi.peso_maximo,
                ppi.peso_minimo,
                ppi.peso_ideal,
                ppi.tara,
                pp.cantidad peso,
                pp.fecha,
                pp.hora,
                pp.uuid
            FROM public.pe_pesos pp 
            JOIN public.pe_cortes_detalles pcd ON pcd.id = pp.corte_detalle_id 
            JOIN public.pe_pesos_indicados ppi ON ppi.id = pcd.peso_indicado_id 
            JOIN public.pe_cortes_encabezados pce ON pce.id = pcd.corte_encabezado_id 
            JOIN public.cajas c ON c.id = ppi.caja_id 
            JOIN public.calidad_cajas cc ON cc.id = c.calidad_id 
            WHERE pp.replicado = 0
        """

        params = []

        if tipo == "actual":
            # Fecha actual
            if not fecha_str:
                fecha_str = date.today().strftime("%Y-%m-%d")
            base_query += " AND pp.fecha = %s"
            params.append(fecha_str)

        elif tipo == "historico":
            # Fechas anteriores a hoy
            if not fecha_str:
                fecha_str = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            base_query += " AND pp.fecha <= %s"
            params.append(fecha_str)

        # Limitar cantidad de registros por lote
        base_query += " ORDER BY pp.fecha, pp.hora LIMIT 200"

        data = self.db.execute(base_query, tuple(params), fetch=True)
        return data if data else []
    

    def update_replicated_weight_status(self, ids):
        query = """
            UPDATE pe_pesos
            SET replicado = 1
            WHERE id = ANY(%s)
        """
        self.db.execute(query, (ids,))
    
    