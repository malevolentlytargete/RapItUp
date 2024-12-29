from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.slider import Slider
import random
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from io import BytesIO
import wave
import array
import numpy as np
import matplotlib.pyplot as plt


# Screen for Neural Drum Machine
class DrumMachineScreen(Screen):
    def __init__(self, **kwargs):
        super(DrumMachineScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        grid = GridLayout(cols=17, padding=10, spacing=10)

        drum_labels = [
            'Kick', 'Snare', 'Hi-hat Closed', 'Hi-hat Open',
            'Tom Low', 'Tom Mid', 'Tom High', 'Clap', 'Rim',
            'Record scratch'  # Added new row for "Record scratch"
        ]

        self.toggle_buttons = []

        for drum in drum_labels:
            grid.add_widget(Label(text=drum, size_hint_x=0.2, color=(1, 0.65, 0, 1)))  # Orange text for labels
            row = []
            for _ in range(16):
                toggle = ToggleButton(size_hint_x=0.05)
                row.append(toggle)
                grid.add_widget(toggle)
            self.toggle_buttons.append(row)

        layout.add_widget(grid)

        controls_layout = BoxLayout(size_hint_y=0.2)
        self.play_button = Button(text="Play", size_hint=(0.2, 1), color=(0, 1, 0, 1))  # Green text for buttons
        self.play_button.bind(on_press=self.toggle_play_pause)
        controls_layout.add_widget(self.play_button)

        ai_button = Button(text="Generate Beat", size_hint=(0.2, 1), color=(0, 1, 0, 1))  # Green text for buttons
        ai_button.bind(on_press=self.generate_beat)
        controls_layout.add_widget(ai_button)

        done_button = Button(text="Done", size_hint=(0.2, 1), color=(1, 0, 0, 1))  # Red text for done button
        done_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'recording'))
        controls_layout.add_widget(done_button)

        back_button = Button(text="Back", size_hint=(0.2, 1), color=(1, 0, 0, 1))  # Red text for back button
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))
        controls_layout.add_widget(back_button)

        layout.add_widget(controls_layout)
        self.add_widget(layout)

    def toggle_play_pause(self, instance):
        if self.play_button.text == "Play":
            self.play_button.text = "Pause"
        else:
            self.play_button.text = "Play"

    def generate_beat(self, instance):
        for row in self.toggle_buttons:
            for toggle in row:
                toggle.state = 'down' if random.choice([True, False]) else 'normal'


# Recording screen
class RecordingScreen(Screen):
    def __init__(self, **kwargs):
        super(RecordingScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.recording = False
        self.audio_data = array.array('h')
        self.sound = None

        self.record_button = Button(text="Record", size_hint=(0.25, 1), color=(1, 0, 0, 1))
        self.record_button.bind(on_press=self.start_stop_recording)
        layout.add_widget(self.record_button)

        self.play_pause_button = Button(text="Play", size_hint=(0.25, 1), color=(0, 1, 0, 1))
        self.play_pause_button.bind(on_press=self.play_audio)
        layout.add_widget(self.play_pause_button)

        self.stop_button = Button(text="Stop", size_hint=(0.25, 1), color=(1, 0.65, 0, 1))
        self.stop_button.bind(on_press=self.stop_audio)
        layout.add_widget(self.stop_button)

        self.slider = Slider(min=0, max=100, value=0, size_hint=(0.25, 1))
        layout.add_widget(self.slider)

        back_button = Button(text="<-", size_hint=(0.3, 1), color=(1, 0, 0, 1))
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'drum_machine'))
        layout.add_widget(back_button)

        self.spectrogram = Image(size_hint=(1, 1))
        layout.add_widget(self.spectrogram)
        self.add_widget(layout)

    def start_stop_recording(self, instance):
        if not self.recording:
            self.start_recording()
            self.record_button.text = "Stop Recording"
        else:
            self.stop_recording()
            self.record_button.text = "Record"

    def start_recording(self):
        self.recording = True
        self.audio_data = array.array('h')

    def stop_recording(self):
        self.recording = False
        with wave.open("temp_audio.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(self.audio_data.tobytes())
        self.update_spectrogram()

    def update_spectrogram(self):
        if len(self.audio_data) > 0:
            audio_np = np.frombuffer(self.audio_data.tobytes(), dtype=np.int16)
            plt.specgram(audio_np, Fs=44100)
            plt.axis('off')
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            texture = Texture.create(size=(512, 512), colorfmt='rgb')
            texture.blit_buffer(buf.getvalue(), colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()
            self.spectrogram.texture = texture
            plt.clf()

    def play_audio(self, instance):
        self.sound = SoundLoader.load("temp_audio.wav")
        if self.sound:
            self.sound.play()

    def stop_audio(self, instance):
        if self.sound:
            self.sound.stop()


# Screen for Inbox
class InboxScreen(Screen):
    def __init__(self, **kwargs):
        super(InboxScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        inbox_messages = [
            "Hugh G.Rection: Let's see how many inches you can take at 5 PM?",
            "Harry Dixon:Tweaker Project deadline is approaching!",
            "Dirty Dan: Don't forget the Teaners.",
            "From David: Happy Birthday!"
        ]

        for message in inbox_messages:
            button = Button(text=message, color=(0, 1, 0, 1))  # Green text for buttons
            layout.add_widget(button)

        back_button = Button(text="<-", size_hint_y=0.1, color=(1, 0, 0, 1))  # Red text for back button
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))
        layout.add_widget(back_button)

        self.add_widget(layout)


class NewsFeedScreen(Screen):
    def __init__(self, **kwargs):
        super(NewsFeedScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.news_feed = BoxLayout(orientation='vertical', size_hint_y=None)
        self.news_feed.bind(minimum_height=self.news_feed.setter('height'))

        scroll_view = ScrollView(bar_width=10, scroll_type=['bars'], bar_color=(1, 0, 0, 1))
        scroll_view.add_widget(self.news_feed)
        layout.add_widget(scroll_view)

        self.post_input = TextInput(hint_text="What's on your mind?", multiline=False, size_hint_y=None, height=60)
        layout.add_widget(self.post_input)

        post_button = Button(text="Post", size_hint_y=None, height=50)
        post_button.bind(on_press=self.post_to_feed)
        layout.add_widget(post_button)

        back_button = Button(text="<-", size_hint_y=None, height=50, color=(1, 0, 0, 1))  # Red text for back button
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))
        layout.add_widget(back_button)

        self.add_widget(layout)

    def post_to_feed(self, instance):
        if self.post_input.text.strip():
            post = Label(text=self.post_input.text, size_hint_y=None, height=40, color=(0, 1, 0, 1))  # Green text for posts
            self.news_feed.add_widget(post, index=0)
            self.post_input.text = ""


# Main Menu screen
class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MainMenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Create buttons for navigating to other screens
        news_feed_button = Button(text="News Feed", size_hint=(1, 0.2), color=(0, 1, 0, 1))
        news_feed_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'news_feed'))
        layout.add_widget(news_feed_button)

        drum_machine_button = Button(text="Neural Drum Machine", size_hint=(1, 0.2), color=(0, 1, 0, 1))
        drum_machine_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'drum_machine'))
        layout.add_widget(drum_machine_button)

        inbox_button = Button(text="Inbox", size_hint=(1, 0.2), color=(0, 1, 0, 1))
        inbox_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'inbox'))
        layout.add_widget(inbox_button)

        # Add exit button
        exit_button = Button(text="Exit", size_hint=(1, 0.2), color=(1, 0, 0, 1))  # Red text for exit button
        exit_button.bind(on_press=self.exit_app)
        layout.add_widget(exit_button)

        self.add_widget(layout)

    def exit_app(self, instance):
        App.get_running_app().stop()


# Main application class
class MyApp(App):
    def build(self):
        # Set up screen manager
        sm = ScreenManager()

        # Add all screens to the screen manager
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(NewsFeedScreen(name='news_feed'))
        sm.add_widget(DrumMachineScreen(name='drum_machine'))
        sm.add_widget(RecordingScreen(name='recording'))
        sm.add_widget(InboxScreen(name='inbox'))

        return sm


# Run the app
if __name__ == '__main__':
    MyApp().run()
