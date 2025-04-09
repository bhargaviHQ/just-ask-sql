import re

class ResponseFormatterAgent:
    def format(self, execution_result):
        if execution_result["status"] == "success":
            result = execution_result.get("result", "Task completed successfully")
            if isinstance(result, list) and execution_result.get("format") == "table":
                return self._format_as_table(result)
            result_str = str(result)
            # For insert operations, exclude the _id from the message
            if "Inserted document with ID" in result_str:
                return "Success: Document inserted successfully"
            sanitized = re.sub(r'mongodb\+srv://[^ ]+', '[REDACTED]', result_str)
            return f"Success: {sanitized}"
        elif execution_result["status"] == "clarification":
            return f"Clarification needed: {execution_result['message']}"
        elif execution_result["status"] == "error_with_feedback":
            return f"Error: {execution_result['message']} - {execution_result['question']}"
        return f"Error: {execution_result['message']}"

    def _format_as_table(self, data):
        if not data or not isinstance(data, list):
            return "Success: No results found"
        
        # Get all keys from the first document to define columns
        headers = list(data[0].keys()) if data else []
        rows = [[str(row.get(header, "")) for header in headers] for row in data]
        
        # Calculate max width for each column
        col_widths = [max(len(str(header)), max((len(str(row[i])) for row in rows), default=0)) 
                     for i, header in enumerate(headers)]
        
        # Build table with proper separators
        table = [" | ".join(f"{header:<{col_widths[i]}}" for i, header in enumerate(headers))]
        table.append("-+-".join("-" * col_widths[i] for i in range(len(headers))))
        for row in rows:
            table.append(" | ".join(f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)))
        
        return "Success:\n" + "\n".join(table)