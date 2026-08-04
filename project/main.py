from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.label import MDLabel
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
import json

FLASK_SERVER_URL = "https://merry-bulldog-sharing.ngrok-free.app"

class EasyESPApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        screen = MDScreen()

        # Status Label
        self.status_label = MDLabel(
            text="Checking ESP Status...",
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.80},
            theme_text_color="Custom",
            text_color=[0.5, 0.5, 0.5, 1],
            font_style="H6"
        )

        btn_open = MDRoundFlatButton(
            text="Open Gate",
            pos_hint={"center_x": 0.5, "center_y": 0.60},
            on_release=lambda x: self.send_command("open"),
            md_bg_color=[0.2, 0.8, 0.2, 1],
            text_color=[1, 1, 1, 1],
        )

        btn_close = MDRoundFlatButton(
            text="Close Gate",
            pos_hint={"center_x": 0.5, "center_y": 0.45},
            on_release=lambda x: self.send_command("close"),
            md_bg_color=[0.8, 0.2, 0.2, 1],
            text_color=[1, 1, 1, 1],
        )

        self.feedback_label = MDLabel(
            text="Ready",
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.30},
            theme_text_color="Primary",
        )

        screen.add_widget(self.status_label)
        screen.add_widget(btn_open)
        screen.add_widget(btn_close)
        screen.add_widget(self.feedback_label)

        # Start the background polling loop (every 2.0 seconds)
        Clock.schedule_interval(self.poll_server_status, 2.0)

        return screen

    # --- Background Polling Function ---
    def poll_server_status(self, dt):
        UrlRequest(
            url=f"{FLASK_SERVER_URL}/api/status",
            on_success=self.update_live_ui,
            timeout=2 # keep timeout short so it doesn't pile up
        )

    def update_live_ui(self, request, result):
        # Update connection status
        status = result.get("status", "unknown")
        self.status_label.text = f"ESP8266 Status: {status.upper()}"
        
        if status == "online":
            self.status_label.text_color = [0, 0.8, 0, 1] # Green
        elif status == "offline":
            self.status_label.text_color = [0.8, 0, 0, 1] # Red

        # Update relay feedback
        feedback = result.get("last_feedback", "None")
        if feedback != "None":
            self.feedback_label.text = f"Hardware Feedback: {feedback.upper()}"

    # --- Button Command Function ---
    def send_command(self, command):
        self.feedback_label.text = f"Sending '{command}'..."
        print(f"Button pressed, sending HTTP POST request for: {command}")

        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        req_body = json.dumps({"source": "Android App", "command": command})

        UrlRequest(
            url=f"{FLASK_SERVER_URL}/api/control",
            req_body=req_body,
            req_headers=headers,
            on_success=self.on_request_success,
            on_failure=self.on_request_failure,
            on_error=self.on_request_error,
            timeout=5
        )

    def on_request_success(self, request, result):
        print(f"Success: {result}")
        # We don't overwrite the feedback label with "success" here anymore,
        # because the polling function will update it when the ESP actually responds!

    def on_request_failure(self, request, result):
        print(f"Failure: {result}")
        self.feedback_label.text = "Server Error! Action failed."

    def on_request_error(self, request, error):
        print(f"Error: {error}")
        self.status_label.text = "CANNOT REACH FLASK SERVER"
        self.status_label.text_color = [0.8, 0, 0, 1]

if __name__ == "__main__":
    EasyESPApp().run()