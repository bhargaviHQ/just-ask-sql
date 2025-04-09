from config.config import get_db_collection
import threading
from agents.data_handler import DataHandlerAgent

class DBExecutorAgent:
    def __init__(self):
        self.lock = threading.Lock()
        self.data_handler = DataHandlerAgent()

    def get_db_collection(self, database, collection):
        return get_db_collection(database, collection)

    def execute(self, db_operation):
        if "error" in db_operation:
            return {"status": "error", "message": db_operation["error"]}

        try:
            with self.lock:
                collection = get_db_collection(db_operation["database"], db_operation["collection"])
                operation = db_operation["operation"]

                if operation == "create_collection":
                    return {"status": "success", "result": f"Collection {db_operation['collection']} ready"}
                elif operation == "insert_one":
                    result = collection.insert_one(db_operation["document"])
                    return {"status": "success", "result": f"Inserted document with ID {str(result.inserted_id)}"}
                elif operation == "update_one":
                    result = collection.update_one(db_operation["filter"], db_operation["update"], upsert=db_operation["upsert"])
                    return {"status": "success", "result": f"Matched {result.matched_count}, modified {result.modified_count}"}
                elif operation == "find":
                    docs = list(collection.find(db_operation["filter"]).limit(db_operation["limit"]))
                    for doc in docs:
                        if "_id" in doc:
                            doc["_id"] = str(doc["_id"])
                    return {"status": "success", "result": docs}
                elif operation == "delete_one":
                    result = collection.delete_one(db_operation["filter"])
                    return {"status": "success", "result": f"Deleted {result.deleted_count} document"}
                elif operation == "insert_from_csv":
                    task, data = self.data_handler.handle_file(db_operation["file_path"], db_operation["collection"])
                    if task["task"] == "insert":
                        result = collection.insert_many(data)
                        inserted_ids = [str(id) for id in result.inserted_ids]  # Convert ObjectIds to strings
                        return {"status": "success", "result": f"Inserted {len(inserted_ids)} documents from CSV", "inserted_ids": inserted_ids}
                    else:
                        return {"status": "error", "message": "Invalid task from data handler"}
        except Exception as e:
            return {"status": "error", "message": str(e)}