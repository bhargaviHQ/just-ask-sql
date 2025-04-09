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

    def create_execution_plan(self, user_input, session_state):
        if "pending_clarification" in session_state and session_state["pending_clarification"]:
            clarification_response = user_input
            user_input = session_state["pending_clarification"]["original_input"]
            session_state["pending_clarification"] = None
        else:
            clarification_response = None

        parsed_query = self.parser.parse(user_input, clarification_response)
        if parsed_query["task"] == "clarification_needed":
            session_state["pending_clarification"] = {"original_input": user_input, "question": parsed_query["details"]["question"]}
            return self.formatter.format({"status": "clarification", "message": parsed_query["details"]["question"]})

        db_operation = self.planner.plan(parsed_query)
        result = self.executor.execute(db_operation)
        return self.formatter.format(result)