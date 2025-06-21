# To run this code, save it as a Python file (e.g., timer_scene.py)
# and execute it from your terminal using:
# manim -pqh timer_scene.py BigTimer

from manim import *

class BigTimer(Scene):
    """
    A Manim scene that displays a large timer counting from 00:00 to 02:00.
    The timer changes color to green at the 01:00 mark.
    """
    def construct(self):
        # Set a white background for the scene
        self.camera.background_color = WHITE

        # Create a ValueTracker to keep track of the time in seconds.
        # This object will hold a value that we can animate smoothly.
        time = ValueTracker(0)

        # Create the main timer text object.
        # We use 'always_redraw' to ensure the timer display (text and color)
        # is updated on every frame of the animation.
        timer_display = always_redraw(
            lambda: self.get_timer_text(time.get_value())
        )
        
        # Position the timer display in the center of the screen
        timer_display.center()

        # Add the timer to the scene
        self.add(timer_display)

        # Animate the ValueTracker from 0 to 120 (seconds) over a period of 120 seconds.
        # 'run_time=120' means the whole 2-minute timer will play out in real-time.
        # 'rate_func=linear' ensures the time progresses at a constant speed.
        self.play(time.animate.set_value(120), run_time=120, rate_func=linear)

        # Hold the final frame for a moment before the video ends.
        self.wait()

    def get_timer_text(self, seconds_value: float) -> Text:
        """
        A helper function that takes a time in seconds and returns a formatted
        Text mobject for the timer.
        
        Args:
            seconds_value: The time in seconds (can be a float).
            
        Returns:
            A Manim Text object displaying the formatted time.
        """
        # Convert the float value to an integer for calculations
        seconds_int = int(seconds_value)
        
        # Calculate minutes and remaining seconds
        minutes = seconds_int // 60
        seconds = seconds_int % 60
        
        # Set the default color to dark gray, which contrasts well with the white background.
        color = DARK_GRAY
        
        # Check if the time has reached or passed the 1-minute mark
        if seconds_int >= 60:
            color = GREEN
            
        # Create the formatted time string in MM:SS format
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Create the Text object with a large font size and the determined color.
        # The font 'Monospace' is used to prevent the numbers from shifting position
        # as they change, which provides a stable-looking timer.
        timer_text = Text(
            time_str, 
            font="Monospace", 
            font_size=250, 
            color=color
        )
        
        return timer_text

