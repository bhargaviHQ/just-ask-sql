class DBPlannerAgent:
    def plan(self, parsed_query):
        task = parsed_query["task"]
        details = parsed_query["details"]

        if task == "create_collection":
            return {
                "operation": "create_collection",
                "database": details.get("database"),
                "collection": details["collection"]
            }
        elif task == "insert_one":
            return {
                "operation": "insert_one",
                "database": details.get("database"),
                "collection": details["collection"],
                "document": details["data"]
            }
        elif task == "update_one":
            if "data" not in details:
                return {"operation": "error", "error": "No update data specified"}
            return {
                "operation": "update_one",
                "database": details.get("database"),
                "collection": details["collection"],
                "filter": details.get("filter", {}),
                "update": {"$set": details["data"]},
                "upsert": details.get("upsert", False)
            }
        elif task == "find":
            return {
                "operation": "find",
                "database": details.get("database"),
                "collection": details["collection"],
                "filter": details.get("filter", {}),
                "limit": details.get("limit", 10)
            }
        elif task == "delete_one":
            return {
                "operation": "delete_one",
                "database": details.get("database"),
                "collection": details["collection"],
                "filter": details.get("filter", {})
            }
        elif task == "insert_from_csv":
            return {
                "operation": "insert_from_csv",
                "database": details.get("database"),
                "collection": details["collection"],
                "file_path": details["file_path"]
            }
        return {"operation": "error", "error": "Unsupported task"}