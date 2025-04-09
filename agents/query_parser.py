from utils.llm_client import get_llm_response
import json
import re

class QueryParserAgent:
    def parse(self, user_input, clarification_response=None):
        prompt = f"""Analyze this user query and return the task type and details as a valid JSON string: '{user_input}'.
        Supported tasks: create_collection, insert_one, update_one, find, delete_one, insert_from_csv.
        Optionally include 'database' and 'collection'; use defaults if omitted.

        **Instructions:**
        - Return ONLY a valid JSON string with no additional text, comments, or prefixes.
        - Use MongoDB-specific terminology (e.g., 'collection' not 'table').
        - For 'insert_from_csv', extract the file path and collection.
        - For 'find', parse conditions like '<', '>', '=' into filters (e.g., '$lt', '$gt', '$eq') and add 'format': 'table' for multiple results.
        - If ambiguous, return 'clarification_needed' with a question in 'details'.
        - If invalid, return 'error_with_feedback' with a message and question in 'details'.
        - If clarification provided: '{clarification_response}', integrate it into '{user_input}'.

        **Examples:**
        - "create a collection users" -> {{"task": "create_collection", "details": {{"collection": "users"}}}}
        - "insert into employees name: Alice, age: 25" -> {{"task": "insert_one", "details": {{"collection": "employees", "data": {{"name": "Alice", "age": 25}}}}}}
        - "insert entry into store with storeid as 1 store name as west-store-1 and employeecount as 12" -> {{"task": "insert_one", "details": {{"collection": "store", "data": {{"storeid": 1, "store name": "west-store-1", "employeecount": 12}}}}}}
        - "find employees where age > 20" -> {{"task": "find", "details": {{"collection": "employees", "filter": {{"age": {{"$gt": 20}}}}, "format": "table"}}}}
        - "show all records from employees" -> {{"task": "find", "details": {{"collection": "employees", "filter": {{}}, "format": "table"}}}}
        - "update employee alice set salary to 50000" -> {{"task": "update_one", "details": {{"collection": "employees", "filter": {{"name": "alice"}}, "data": {{"salary": 50000}}}}}}
        - "delete from employees where age < 30" -> {{"task": "delete_one", "details": {{"collection": "employees", "filter": {{"age": {{"$lt": 30}}}}}}}}
        - "insert from csv data/sample.csv into collection employees" -> {{"task": "insert_from_csv", "details": {{"collection": "employees", "file_path": "data/sample.csv"}}}}
        """
        
        try:
            response = get_llm_response(prompt)
            print(f"DEBUG: Raw LLM response: {response}")
        except Exception as e:
            print(f"DEBUG: LLM call failed: {str(e)}")
            return {
                "task": "error_with_feedback",
                "details": {
                    "message": f"Failed to get response from LLM: {str(e)}",
                    "question": "Could you please try again?"
                }
            }

        try:
            parsed = json.loads(response)
            if not isinstance(parsed, dict) or "task" not in parsed:
                raise ValueError("Parsed response is not a valid task dictionary")
            return parsed
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parsing error: {e}, response was: {response}")
            json_match = re.search(r'\{(?:[^{}]|\{[^{}]*\})*\}', response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    if "task" not in parsed:
                        raise ValueError("Extracted JSON missing 'task'")
                    return parsed
                except (json.JSONDecodeError, ValueError) as e2:
                    print(f"DEBUG: Fallback parsing failed: {e2}, matched text: {json_match.group(0)}")
            return {
                "task": "error_with_feedback",
                "details": {
                    "message": "Failed to parse query due to invalid response",
                    "question": "Could you please rephrase your request?"
                }
            }
        except ValueError as e:
            print(f"DEBUG: Validation error: {str(e)}, response was: {response}")
            return {
                "task": "error_with_feedback",
                "details": {
                    "message": str(e),
                    "question": "Could you please rephrase your request?"
                }
            }