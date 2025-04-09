import pandas as pd
import json

class DataHandlerAgent:
    def handle_file(self, file_path, collection):
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            data = df.to_dict(orient="records")
            return {"task": "insert", "collection": collection}, data
        elif file_path.endswith(".json"):
            with open(file_path, "r") as f:
                data = json.load(f)
            return {"task": "insert", "collection": collection}, data

    def handle_chat(self, chat_data, collection):
        data = [dict(item.split(": ") for item in chat_data.split(", "))]
        return {"task": "insert", "collection": collection}, data