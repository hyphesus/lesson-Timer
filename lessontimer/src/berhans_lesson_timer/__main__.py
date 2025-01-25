# src/berhans_lesson_timer/__main__.py

import time
import threading

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# Attempt to import Plyer's vibrator and notification.
try:
    from plyer import vibrator, notification
except ImportError:
    vibrator = None
    notification = None


class TimerData:
    """Holds data/state for a single countdown timer."""
    def __init__(self, title, start_seconds):
        self.title = title
        self.start_seconds = start_seconds
        self.time_left = start_seconds
        self.running = False


class LessonTimerApp(toga.App):
    def startup(self):
        """Set up the main window and UI components."""
        self.main_window = toga.MainWindow(title=self.formal_name)

        # Initialize two timers
        self.timer1 = TimerData("40-min Timer", 40 * 60)
        self.timer2 = TimerData("13-min Timer", 13 * 60)

        # Timer 1 UI
        self.timer1_label = toga.Label(
            self.format_time(self.timer1.time_left),
            style=Pack(font_size=24, padding=(0, 10))
        )
        self.timer1_start_button = toga.Button(
            "Start", on_press=self.on_timer1_start, style=Pack(padding=5)
        )
        self.timer1_reset_button = toga.Button(
            "Reset", on_press=self.on_timer1_reset, style=Pack(padding=5)
        )

        # Timer 2 UI
        self.timer2_label = toga.Label(
            self.format_time(self.timer2.time_left),
            style=Pack(font_size=24, padding=(0, 10))
        )
        self.timer2_start_button = toga.Button(
            "Start", on_press=self.on_timer2_start, style=Pack(padding=5)
        )
        self.timer2_reset_button = toga.Button(
            "Reset", on_press=self.on_timer2_reset, style=Pack(padding=5)
        )

        # Layout setup
        timer1_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        timer1_box.add(self.timer1_label)
        timer1_box.add(self.timer1_start_button)
        timer1_box.add(self.timer1_reset_button)

        timer2_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        timer2_box.add(self.timer2_label)
        timer2_box.add(self.timer2_start_button)
        timer2_box.add(self.timer2_reset_button)

        main_box = toga.Box(style=Pack(direction=ROW, padding=20))
        main_box.add(timer1_box)
        main_box.add(timer2_box)

        self.main_window.content = main_box
        self.main_window.show()

        # Start the timer update thread
        self._running = True
        self.update_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.update_thread.start()

    def on_timer1_start(self, widget):
        """Handle Timer 1 Start/Pause button press."""
        self.start_pause_timer(self.timer1, self.timer1_start_button)

    def on_timer2_start(self, widget):
        """Handle Timer 2 Start/Pause button press."""
        self.start_pause_timer(self.timer2, self.timer2_start_button)

    def on_timer1_reset(self, widget):
        """Handle Timer 1 Reset button press."""
        self.reset_timer(self.timer1)
        self.timer1_label.text = self.format_time(self.timer1.time_left)

    def on_timer2_reset(self, widget):
        """Handle Timer 2 Reset button press."""
        self.reset_timer(self.timer2)
        self.timer2_label.text = self.format_time(self.timer2.time_left)

    def timer_loop(self):
        """Background thread that updates timers every second."""
        while self._running:
            time.sleep(1)
            self.invoke_later(self.on_tick)

    def on_tick(self):
        """Update timers and handle countdown logic."""
        if self.timer1.running:
            self.reset_timer(self.timer2)
            self.decrement_timer(
                self.timer1, self.timer1_label, self.timer1_start_button
            )

        if self.timer2.running:
            self.reset_timer(self.timer1)
            self.decrement_timer(
                self.timer2, self.timer2_label, self.timer2_start_button
            )

    def start_pause_timer(self, timer_data, start_button):
        """Toggle start/pause state for a timer."""
        if not timer_data.running:
            timer_data.running = True
            start_button.label = "Pause"
        else:
            timer_data.running = False
            start_button.label = "Start"

    def reset_timer(self, timer_data):
        """Reset a timer to its initial value."""
        timer_data.running = False
        timer_data.time_left = timer_data.start_seconds

    def decrement_timer(self, timer_data, label, start_button):
        """Decrement the timer and handle completion."""
        if timer_data.time_left > 0:
            timer_data.time_left -= 1

        if timer_data.time_left <= 0:
            timer_data.time_left = 0
            timer_data.running = False
            start_button.label = "Start"

            # Vibrate the device
            if vibrator:
                vibrator.vibrate(time=1.0)

            # Send a notification
            if notification:
                notification.notify(
                    title="Timer Complete",
                    message=f"{timer_data.title} is done!",
                    timeout=5
                )

        # Update the label with the new time
        label.text = self.format_time(timer_data.time_left)

    def format_time(self, t):
        """Format time in seconds to mm:ss."""
        m, s = divmod(t, 60)
        return f"{m:02d}:{s:02d}"

    def on_exit(self):
        """Handle app exit."""
        self._running = False


def main():
    """Briefcase entry point."""
    return LessonTimerApp(
        name="berhans_lesson_timer",
        app_id="com.example.lesson_timer",
        formal_name="Berhan's Lesson Timer"
    )
