try:
    import tkinter as tk
except ImportError:
    tk = None

class ChatbotUI:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("Database Chatbot")
        self.controller = controller

        self.chat_display = tk.Text(root, height=20, width=50)
        self.chat_display.pack(pady=10)

        self.input_field = tk.Entry(root, width=40)
        self.input_field.pack(pady=5)
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

    def send_message(self, event=None):
        user_input = self.input_field.get().strip()
        if user_input:
            self.chat_display.insert(tk.END, f"You: {user_input}\n")
            response = self.controller.create_execution_plan(user_input)
            self.chat_display.insert(tk.END, f"Bot: {response}\n")
            self.input_field.delete(0, tk.END)

def run_ui(controller):
    if tk is None:
        print("Tkinter not available. Falling back to CLI.")
        return False
    root = tk.Tk()
    app = ChatbotUI(root, controller)
    root.mainloop()
    return True