import kivy
kivy.require('2.1.0')  # or the version you have installed

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, StringProperty

# Plyer imports for vibration and notifications
# Make sure to include plyer in your buildozer requirements:
# requirements = python3,kivy,plyer,...
try:
    from plyer import vibrator
    from plyer import notification
except ImportError:
    vibrator = None
    notification = None


class TimerBox(BoxLayout):
    """A custom widget containing a countdown label and buttons."""
    # Timer start values (in seconds)
    start_time = NumericProperty(0)   # e.g., 40*60 or 13*60
    time_left = NumericProperty(0)
    running = BooleanProperty(False)
    display_text = StringProperty("00:00")

    def __init__(self, title="Timer", start_time=2400, **kwargs):
        # start_time=2400 (40 min) by default
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.title = title
        self.start_time = start_time
        self.time_left = start_time
        
        # Layout: A label for the timer display, a "Start/Stop" button, and a "Reset" button
        self.label = Label(text=self.format_time(self.time_left), font_size=40)
        self.add_widget(self.label)

        self.btn_start = Button(text="Start", size_hint=(1, 0.3))
        self.btn_start.bind(on_press=self.start_timer)
        self.add_widget(self.btn_start)

        self.btn_reset = Button(text="Reset", size_hint=(1, 0.3))
        self.btn_reset.bind(on_press=self.reset_timer)
        self.add_widget(self.btn_reset)

        # We'll update the display_text property whenever time_left changes
        self.bind(time_left=self.update_display_text)

        # Kivy's Clock to schedule timer ticks (every 1 second)
        self.clock_event = None

    def format_time(self, t):
        """Format time in seconds to mm:ss."""
        minutes = t // 60
        seconds = t % 60
        return f"{minutes:02d}:{seconds:02d}"

    def update_display_text(self, instance, value):
        """Called whenever time_left changes; update the label text."""
        self.label.text = self.format_time(value)

    def start_timer(self, *args):
        """Start or resume the countdown."""
        if not self.running:
            self.running = True
            self.btn_start.text = "Pause"
            # Schedule the timer to decrement every second
            self.clock_event = Clock.schedule_interval(self.tick, 1)
        else:
            # If it's running, pause it
            self.running = False
            self.btn_start.text = "Start"
            if self.clock_event:
                self.clock_event.cancel()

    def reset_timer(self, *args):
        """Reset the timer to its initial value."""
        self.running = False
        self.time_left = self.start_time
        self.btn_start.text = "Start"
        if self.clock_event:
            self.clock_event.cancel()

    def tick(self, dt):
        """Decrement the timer by 1 second."""
        if self.running:
            self.time_left -= 1
            if self.time_left <= 0:
                self.time_left = 0
                self.running = False
                if self.clock_event:
                    self.clock_event.cancel()
                self.btn_start.text = "Start"
                
                # Vibrate the phone when time ends
                if vibrator:
                    vibrator.vibrate(time=1.0)  # Vibrate for 1 second

                # Show a notification
                if notification:
                    notification.notify(
                        title="Timer Complete",
                        message=f"{self.title} is done!",
                        timeout=5  # seconds
                    )


class LessonTimerApp(App):
    def build(self):
        self.title = "Berhan's Lesson Timer"

        # Main container
        root = BoxLayout(orientation='horizontal', spacing=20, padding=20)

        # Create two timers:
        # - Timer 1: 40 minutes
        # - Timer 2: 13 minutes
        self.timer1 = TimerBox(title="40-min Timer", start_time=40*60)
        self.timer2 = TimerBox(title="13-min Timer", start_time=13*60)

        # We'll add logic so that starting one timer resets the other
        self.timer1.btn_start.bind(on_press=self.on_timer1_start)
        self.timer2.btn_start.bind(on_press=self.on_timer2_start)

        root.add_widget(self.timer1)
        root.add_widget(self.timer2)
        return root

    def on_timer1_start(self, instance):
        """When Timer1 is started, reset Timer2."""
        if not self.timer1.running:
            # If user clicked "Pause", do nothing
            return
        # If Timer1 is starting, reset Timer2
        self.timer2.reset_timer()

    def on_timer2_start(self, instance):
        """When Timer2 is started, reset Timer1."""
        if not self.timer2.running:
            # If user clicked "Pause", do nothing
            return
        # If Timer2 is starting, reset Timer1
        self.timer1.reset_timer()


if __name__ == "__main__":
    LessonTimerApp().run()
