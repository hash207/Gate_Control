from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.label import MDLabel
from kivy.network.urlrequest import UrlRequest
import json

# تذكر تغيير الرابط إلى مسار الـ API الجديد /api/control
FLASK_SERVER_URL = "https://merry-bulldog-sharing.ngrok-free.app/api/control"

class EasyESPApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        screen = MDScreen()

        # زر الفتح (باللون الأخضر للتوضيح)
        btn_open = MDRoundFlatButton(
            text="Open Gate",
            pos_hint={"center_x": 0.5, "center_y": 0.60},
            on_release=lambda x: self.send_command("open"),
            md_bg_color=[0.2, 0.8, 0.2, 1],
            text_color=[1, 1, 1, 1],
        )

        # زر الإغلاق (باللون الأحمر للتوضيح)
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

        screen.add_widget(btn_open)
        screen.add_widget(btn_close)
        screen.add_widget(self.feedback_label)

        return screen

    def send_command(self, command):
        self.feedback_label.text = f"Sending '{command}' request..."
        print(f"Button pressed, sending HTTP POST request for: {command}")

        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        # تضمين الأمر (open/close) في جسم الطلب المرسل لـ Flask
        req_body = json.dumps({"source": "Android App", "command": command})

        UrlRequest(
            url=FLASK_SERVER_URL,
            req_body=req_body,
            req_headers=headers,
            on_success=self.on_request_success,
            on_failure=self.on_request_failure,
            on_error=self.on_request_error,
            timeout=5
        )

    def on_request_success(self, request, result):
        print(f"Success: {result}")
        self.feedback_label.text = result.get("message", "Command successful!")

    def on_request_failure(self, request, result):
        print(f"Failure: {result}")
        self.feedback_label.text = "Server Error! Action failed."

    def on_request_error(self, request, error):
        print(f"Error: {error}")
        self.feedback_label.text = "Connection failed. Check Server IP."

if __name__ == "__main__":
    EasyESPApp().run()