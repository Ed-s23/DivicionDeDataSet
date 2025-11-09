import arff
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import re, tempfile, os

def main(file_path=None):
    """Procesa el dataset ARFF y genera una gráfica del atributo 'protocol_type'."""

    if not file_path:
        return {"mensaje": "❌ No se recibió ningún archivo ARFF."}

    try:
        # --- Limpieza del archivo ---
        cleaned_lines = []
        with open(file_path, "r", errors="ignore") as f:
            for line in f:
                line = re.sub(r"@relation\s+'([^']+)'", r"@relation \1", line, flags=re.IGNORECASE)
                line = re.sub(r"@attribute\s+'([^']+)'", r"@attribute \1", line, flags=re.IGNORECASE)
                line = re.sub(r"numeric", "NUMERIC", line, flags=re.IGNORECASE)
                line = re.sub(r"string", "STRING", line, flags=re.IGNORECASE)
                line = re.sub(r"real", "NUMERIC", line, flags=re.IGNORECASE)
                cleaned_lines.append(line)

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".arff") as tmp:
            tmp.writelines(cleaned_lines)
            temp_path = tmp.name

        # --- Cargar dataset ---
        with open(temp_path, "r") as file:
            dataset = arff.load(file)
        attributes = [attr[0] for attr in dataset["attributes"]]
        df = pd.DataFrame(dataset["data"], columns=attributes)

        if df.empty:
            return {"mensaje": "⚠️ El archivo está vacío después de la limpieza."}

        # --- División del dataset ---
        def train_val_test_split(df, stratify=None):
            if len(df) < 3:
                return df, df, df
            strat = df[stratify] if stratify and stratify in df.columns else None
            train_set, temp_set = train_test_split(df, test_size=0.4, random_state=42, shuffle=True, stratify=strat)
            strat = temp_set[stratify] if stratify and stratify in df.columns else None
            val_set, test_set = train_test_split(temp_set, test_size=0.5, random_state=42, shuffle=True, stratify=strat)
            return train_set, val_set, test_set

        train_set, val_set, test_set = train_val_test_split(df, stratify="protocol_type" if "protocol_type" in df.columns else None)

        # --- Crear carpeta para guardar gráficos ---
        graph_dir = "dataset_app/static/graphs"
        os.makedirs(graph_dir, exist_ok=True)

        # --- Generar la gráfica como en el notebook ---
        if "protocol_type" in df.columns:
            plt.figure(figsize=(8, 5))
            df["protocol_type"].hist(color="#ff1744", edgecolor="black")
            plt.title("Distribución de Protocol Types")
            plt.xlabel("Tipo de Protocolo")
            plt.ylabel("Frecuencia")
            plt.grid(False)

            graph_path = os.path.join(graph_dir, "protocol_hist.png")
            plt.tight_layout()
            plt.savefig(graph_path)
            plt.close()
            graph_rel_path = "graphs/protocol_hist.png"
        else:
            graph_rel_path = None

        # --- Resultado final ---
        return {
            "mensaje": " Dataset procesado correctamente.",
            "total_filas": len(df),
            "train_set": len(train_set),
            "validation_set": len(val_set),
            "test_set": len(test_set),
            "grafica": graph_rel_path
        }

    except Exception as e:
        return {"mensaje": f"❌ Error procesando el dataset: {e}"}
