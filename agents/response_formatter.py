import re

class ResponseFormatterAgent:
    def format(self, execution_result):
        if execution_result["status"] == "success":
            result_str = str(execution_result.get("result", "Task completed successfully"))
            sanitized = re.sub(r'mongodb\+srv://[^ ]+', '[REDACTED]', result_str)
            return f"Success: {sanitized}"
        elif execution_result["status"] == "clarification":
            return f"Clarification needed: {execution_result['message']}"
        return f"Error: {execution_result['message']}"