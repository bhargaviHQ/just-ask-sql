import pandas as pd
from agents.db_planner import DatabasePlannerAgent

class CSVHandlerAgent:
    def __init__(self):
        self.planner = DatabasePlannerAgent()

    def handle_csv(self, file_path, table_name):
        df = pd.read_csv(file_path)
        rows = [tuple(row) for row in df.itertuples(index=False)]
        columns = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return query, rows

# Example usage
if __name__ == "__main__":
    agent = CSVHandlerAgent()
    query, rows = agent.handle_csv("data/data.csv", "users")
    print(query, rows)