
import datetime, decimal
class BoxMapper:
    @staticmethod
    def from_quality_boxes_local(row):
        return {
            "id": row.get("id"),
            "descripcion": row.get("descripcion"),
            "observacion": row.get("observacion") or "",
            "estado": row.get("estado"),
        }

    @staticmethod
    def from_quality_boxes_cloud(row):
        return {
            "descripcion": row.get("descripcion"),
            "observacion": row.get("observacion") or "",
        }
    
    @staticmethod
    def from_box_local(row):
        return {
            "id": row.get("id"),
            "descripcion": row.get("descripcion"),
            "calidad_caja": row.get("calidad_caja"),
            "calidad_caja_id": row.get("calidad_caja_id"),
        }
    
    @staticmethod
    def from_box_cloud(row):
        return {
            "caja": row.get("caja"),
            "calidad_caja": row.get("calidad_caja"),
        }
    
    
    @staticmethod
    def serialize_weight(row):
        return {
            "peso_id": row["peso_id"],
            "corte_fecha": row["corte_fecha"].isoformat() if isinstance(row["corte_fecha"], datetime.date) else row["corte_fecha"],
            "corte_hora": row["corte_hora"].strftime("%H:%M:%S") if isinstance(row["corte_hora"], datetime.time) else row["corte_hora"],
            "caja": row["caja"],
            "calidad_caja": row["calidad_caja"],
            "cantidad_cajas": row["cantidad_cajas"],
            "peso_maximo": float(row["peso_maximo"]) if isinstance(row["peso_maximo"], decimal.Decimal) else row["peso_maximo"],
            "peso_minimo": float(row["peso_minimo"]) if isinstance(row["peso_minimo"], decimal.Decimal) else row["peso_minimo"],
            "peso_ideal": float(row["peso_ideal"]) if isinstance(row["peso_ideal"], decimal.Decimal) else row["peso_ideal"],
            "tara": float(row["tara"]) if isinstance(row["tara"], decimal.Decimal) else row["tara"],
            "peso": float(row["peso"]) if isinstance(row["peso"], decimal.Decimal) else row["peso"],
            "fecha": row["fecha"].isoformat() if isinstance(row["fecha"], datetime.date) else row["fecha"],
            "hora": row["hora"].strftime("%H:%M:%S") if isinstance(row["hora"], datetime.time) else row["hora"],
            "uuid": row["uuid"],
        }
