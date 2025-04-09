import json
import os
from bson import ObjectId
from agents.query_parser import QueryParserAgent
from agents.db_planner import DBPlannerAgent
from agents.db_executor import DBExecutorAgent
from agents.response_formatter import ResponseFormatterAgent

class ControllerAgent:
    def __init__(self):
        self.parser = QueryParserAgent()
        self.planner = DBPlannerAgent()
        self.executor = DBExecutorAgent()
        self.formatter = ResponseFormatterAgent()
        self.history_file = "query_history.json"
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.query_history = json.load(f)
        else:
            self.query_history = []

    def json_serializer(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    def save_history(self, query, parsed_query, result):
        history_entry = {
            "query": query,
            "task": parsed_query.get("task", "unknown"),
            "details": parsed_query.get("details", {}),
            "result": result,
            "reversible": parsed_query.get("task", "") in ["insert_one", "insert_from_csv", "update_one", "delete_one"]
        }
        self.query_history.append(history_entry)
        with open(self.history_file, "w") as f:
            json.dump(self.query_history, f, indent=2, default=self.json_serializer)

    def get_history(self):
        if not self.query_history:
            return "No queries executed yet."
        history_str = "Query History:\n"
        for i, entry in enumerate(self.query_history):
            history_str += f"{i}: {entry['query']} -> {entry['result']['status']}: {entry['result']['result']}\n"
        return history_str

    def rollback_query(self, index):
        if index < 0 or index >= len(self.query_history):
            return {"status": "error", "message": f"Invalid query index {index}"}
        
        entry = self.query_history[index]
        if not entry["reversible"]:
            return {"status": "error", "message": f"Query '{entry['query']}' cannot be rolled back"}

        task = entry["task"]
        details = entry["details"]
        result = entry["result"]

        try:
            collection = self.executor.get_db_collection(details.get("database"), details["collection"])
            if task == "insert_one":
                inserted_id = result["result"].split("ID ")[-1] if "Inserted document with ID" in result["result"] else None
                if inserted_id:
                    collection.delete_one({"_id": ObjectId(inserted_id)})
                    return {"status": "success", "result": f"Rolled back insert: deleted document {inserted_id}"}
            elif task == "insert_from_csv":
                if "inserted_ids" not in result:
                    return {"status": "error", "message": "No inserted IDs recorded for rollback"}
                inserted_ids = result["inserted_ids"]
                collection.delete_many({"_id": {"$in": [ObjectId(id) for id in inserted_ids]}})
                return {"status": "success", "result": f"Rolled back CSV insert: deleted {len(inserted_ids)} documents"}
            elif task == "update_one":
                return {"status": "error", "message": "Update rollback not yet supported"}
            elif task == "delete_one":
                return {"status": "error", "message": "Delete rollback not yet supported"}
        except Exception as e:
            return {"status": "error", "message": f"Rollback failed: {str(e)}"}

        return {"status": "error", "message": "Rollback not implemented for this query"}

    def modify_query(self, index, new_query):
        if index < 0 or index >= len(self.query_history):
            return {"status": "error", "message": f"Invalid query index {index}"}
        
        session_state = {}
        parsed_query = self.parser.parse(new_query)
        if not isinstance(parsed_query, dict) or "task" not in parsed_query:
            return self.formatter.format({
                "status": "error",
                "message": "Invalid query parsing result"
            })
        if parsed_query["task"] in ["clarification_needed", "error_with_feedback"]:
            return self.formatter.format(parsed_query)
        
        db_operation = self.planner.plan(parsed_query)
        result = self.executor.execute(db_operation)
        if "format" in parsed_query["details"]:
            result["format"] = parsed_query["details"]["format"]
        self.save_history(new_query, parsed_query, result)
        return self.formatter.format(result)

    def create_execution_plan(self, user_input, session_state):
        if user_input.lower() == "show history":
            return self.get_history()
        elif user_input.lower().startswith("rollback query "):
            try:
                index = int(user_input.split("rollback query ")[1])
                result = self.rollback_query(index)
                return self.formatter.format(result)
            except ValueError:
                return "Error: Please specify a valid query index (e.g., 'rollback query 0')"
        elif user_input.lower().startswith("modify query "):
            try:
                parts = user_input.split(" ", 3)
                index = int(parts[2])
                new_query = parts[3] if len(parts) > 3 else ""
                if not new_query:
                    return "Error: Please specify the modified query (e.g., 'modify query 0 insert new data')"
                return self.modify_query(index, new_query)
            except ValueError:
                return "Error: Please specify a valid query index (e.g., 'modify query 0 new query')"

        if "pending_clarification" in session_state and session_state["pending_clarification"]:
            clarification_response = user_input
            original_input = session_state["pending_clarification"]["original_input"]
            if not clarification_response.strip() or clarification_response.lower() in ["yes", "no", "ok"]:
                return self.formatter.format({"status": "clarification", "message": session_state["pending_clarification"]["question"]})
            session_state["pending_clarification"] = None
            parsed_query = self.parser.parse(original_input, clarification_response)
        else:
            parsed_query = self.parser.parse(user_input)
        
        if not isinstance(parsed_query, dict) or "task" not in parsed_query:
            return self.formatter.format({
                "status": "error",
                "message": "Invalid query parsing result"
            })

        if parsed_query["task"] == "clarification_needed":
            session_state["pending_clarification"] = {"original_input": user_input, "question": parsed_query["details"]["question"]}
            return self.formatter.format({"status": "clarification", "message": parsed_query["details"]["question"]})
        
        if parsed_query["task"] == "error_with_feedback":
            session_state["pending_clarification"] = {"original_input": user_input, "question": parsed_query["details"]["question"]}
            return self.formatter.format({"status": "error_with_feedback", "message": parsed_query["details"]["message"], "question": parsed_query["details"]["question"]})

        db_operation = self.planner.plan(parsed_query)
        result = self.executor.execute(db_operation)
        if "format" in parsed_query["details"]:
            result["format"] = parsed_query["details"]["format"]
        self.save_history(user_input, parsed_query, result)
        return self.formatter.format(result)