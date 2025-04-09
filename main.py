from agents.controller import ControllerAgent
from ui.chatbot_ui import run_ui

def run_cli(controller):
    print("Database Chatbot (CLI Mode) - Type 'exit' to quit")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = controller.create_execution_plan(user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    controller = ControllerAgent()
    try:
        import tkinter
        if run_ui(controller):
            pass
    except ImportError:
        print("Tkinter not found. Using CLI mode.")
        run_cli(controller)
    except Exception as e:
        print(f"Error starting UI: {e}. Falling back to CLI.")
        run_cli(controller)