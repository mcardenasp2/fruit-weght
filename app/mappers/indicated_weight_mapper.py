

class IndicatedWeight:
    @staticmethod
    def from_indicated_weight_local(row):
        return {
            "peso_indicado_id": row.get("peso_indicado_id"),
            "caja": row.get("caja"),
            "peso_minimo": row.get("peso_minimo"),
            "peso_ideal": row.get("peso_ideal"),
            "peso_maximo": row.get("peso_maximo"),
            "calidad_caja": row.get("calidad_caja"),
            "tara": row.get("tara"),
        }
    
    @staticmethod
    def from_indicated_weight_cloud(row):
        return {
            "peso_indicado_id": row.get("peso_indicado_id"),
            "caja": row["caja"]["descripcion"] if row.get("caja") else None,
            "peso_minimo": row.get("peso_minimo"),
            "peso_ideal": row.get("peso_ideal"),
            "peso_maximo": row.get("peso_maximo"),
            "calidad_caja": (
                row["caja"]["calidad"]["descripcion"]
                if row.get("caja") and row["caja"].get("calidad")
                else None
            ),
            "tara": row.get("tara"),
        }