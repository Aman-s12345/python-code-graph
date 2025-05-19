# src/app.py

from src.utils import getInitialMessage, getUpdatedMessage

class App:
    def __init__(self):
        # mirror React’s useState(getInitialMessage())
        self.message = getInitialMessage()

    def handleClick(self):
        # mirror setMessage(getUpdatedMessage())
        self.message = getUpdatedMessage()

    def render(self):
        # very simple “UI” in console
        print(f"\n=== APP UI ===")
        print(f"Message: {self.message}")
        print("(Press Enter to change greeting)")
    
    def run(self):
        # initial render
        self.render()
        # wait for user to press Enter, then update + re-render
        input()
        self.handleClick()
        self.render()
