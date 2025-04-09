try:
    import tkinter as tk
except ImportError:
    tk = None

class ChatbotUI:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("Database Chatbot")
        self.controller = controller
        self.session_state = {}  # Store session state

        # Chat display
        self.chat_display = tk.Text(root, height=20, width=80, font=("Courier", 10))
        self.chat_display.pack(pady=10)

        # Input field
        self.input_field = tk.Entry(root, width=40)
        self.input_field.pack(pady=5)
        self.input_field.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        # Show history button
        self.history_button = tk.Button(root, text="Show Query History", command=self.show_history)
        self.history_button.pack(pady=5)

    def send_message(self, event=None):
        user_input = self.input_field.get().strip()
        if user_input:
            self.chat_display.insert(tk.END, f"You: {user_input}\n")
            response = self.controller.create_execution_plan(user_input, self.session_state)
            self.chat_display.insert(tk.END, f"Bot: {response}\n\n")
            self.input_field.delete(0, tk.END)
            self.chat_display.see(tk.END)

    def show_history(self):
        """Display query history in the chat window."""
        history = self.controller.get_history()
        self.chat_display.insert(tk.END, f"Bot: {history}\n\n")
        self.chat_display.see(tk.END)

def run_ui(controller):
    if tk is None:
        print("Tkinter not available. Falling back to CLI.")
        return False
    root = tk.Tk()
    app = ChatbotUI(root, controller)
    root.mainloop()
    return True