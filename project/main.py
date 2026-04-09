from kivymd.app import MDApp
from paho.mqtt.client import Client
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.label import MDLabel

def callback(client, userdata, message):
    payload = message.payload.decode()
    print(f"Received message: {payload} on topic {message.topic}")
    if payload.strip().lower() == "success":
        app = MDApp.get_running_app()
        if app is not None and hasattr(app, "feedback_label"):
            app.feedback_label.text = "Gate toggled successfully!"

client = Client()
client.connect("broker.emqx.io", 1883)
client.subscribe("relay/feedback")
client.on_message = callback
client.loop_start()

class EasyESPApp(MDApp):
    def build(self):
        # Set the UI theme colors
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light" # Can be "Dark"

        # Main Screen
        screen = MDScreen()

        # add a round button that toggles state
        self.button_state = False
        button = MDRoundFlatButton(
            text="Toggle Gate",
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            on_release=self.on_button_release,
            md_bg_color=[0.6, 0.8, 1, 1],
            text_color=[0, 0, 0, 1],
        )

        self.feedback_label = MDLabel(
            text="",
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.35},
            theme_text_color="Primary",
        )

        screen.add_widget(button)
        screen.add_widget(self.feedback_label)

        return screen

    def on_button_release(self, instance):
        self.button_state = not self.button_state
        client.publish("relay/switch", "toggle")
        self.feedback_label.text = "Waiting for response..."
        print(f"Button toggled to {'on' if self.button_state else 'off'}")


if __name__ == "__main__":
    EasyESPApp().run()