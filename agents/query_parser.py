from utils.llm_client import get_llm_response
import json

class QueryParserAgent:
    def parse(self, user_input, clarification_response=None):
        prompt = f"""Analyze this user query and extract the task type and details as JSON: '{user_input}'.
        Supported tasks: create_collection, insert_one, update_one, find, delete_one.
        Users can optionally specify 'database' and 'collection' in the query; otherwise, use defaults from environment.
        If the query is ambiguous or missing details (e.g., filter for find, data for insert), return a clarification task with a question.
        Example: "Insert a user named John into collection users" -> {{'task': 'insert_one', 'details': {{'collection': 'users', 'data': {{'name': 'John'}}}}}}
        Example: "Find users" -> {{'task': 'clarification_needed', 'details': {{'question': 'What filter should I use to find users?'}}}}
        If clarification was provided: '{clarification_response}', incorporate it into the original query '{user_input}'.
        Return the result as a valid JSON string."""
        
        response = get_llm_response(prompt)
        print(f"Raw response from LLM: {response}")
        
        try:
            parsed = json.loads(response)
            if parsed.get("task") == "create_table":
                parsed["task"] = "create_collection"
                parsed["details"]["collection"] = parsed["details"].pop("table_name", parsed["details"].get("collection"))
            return parsed
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"task": "error", "details": {"message": "Failed to parse query"}}