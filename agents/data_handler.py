import pandas as pd
import json

class DataHandlerAgent:
    def handle_file(self, file_path, collection):
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            data = df.to_dict(orient="records")  # Converts CSV rows to list of dictionaries
            return {"task": "insert", "collection": collection}, data
        elif file_path.endswith(".json"):
            with open(file_path, "r") as f:
                data = json.load(f)
            return {"task": "insert", "collection": collection}, data
        return {"task": "error", "message": "Unsupported file format"}, None