


class CutOffLetterCloudMapper:
    @staticmethod
    def from_get_cutting_letter_header_cloud(row):
        """Mapeo de la consulta de corte desde la nube"""
        return {
            "caja": row.get("caja"),
            "calidad_caja": row.get("calidad_caja"),
            "cantidad": row.get("cantidad"),
            "fecha": row.get("fecha"),
            "hora": row.get("hora"),
            "peso_minimo": row.get("peso_minimo"),
            "peso_ideal": row.get("peso_ideal"),
            "peso_maximo": row.get("peso_maximo"),
            "tara": row.get("tara"),
        }
    
    