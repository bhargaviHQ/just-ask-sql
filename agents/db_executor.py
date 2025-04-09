from config.config import get_db_collection
import threading

class DBExecutorAgent:
    def __init__(self):
        self.lock = threading.Lock()

    def execute(self, db_operation):
        if "error" in db_operation:
            return {"status": "error", "message": db_operation["error"]}

        try:
            with self.lock:
                collection = get_db_collection(db_operation["database"], db_operation["collection"])
                operation = db_operation["operation"]

                if operation == "create_collection":
                    # MongoDB creates collections implicitly on first insert, so this is a no-op unless validation needed
                    return {"status": "success", "result": f"Collection {db_operation['collection']} ready"}
                elif operation == "insert_one":
                    result = collection.insert_one(db_operation["document"])
                    return {"status": "success", "result": f"Inserted document with ID {result.inserted_id}"}
                elif operation == "update_one":
                    result = collection.update_one(db_operation["filter"], db_operation["update"], upsert=db_operation["upsert"])
                    return {"status": "success", "result": f"Matched {result.matched_count}, modified {result.modified_count}"}
                elif operation == "find":
                    docs = list(collection.find(db_operation["filter"]).limit(db_operation["limit"]))
                    return {"status": "success", "result": docs}
                elif operation == "delete_one":
                    result = collection.delete_one(db_operation["filter"])
                    return {"status": "success", "result": f"Deleted {result.deleted_count} document"}
        except Exception as e:
            return {"status": "error", "message": str(e)}