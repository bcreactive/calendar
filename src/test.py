from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
# from plyer import notification
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

from datetime import datetime
# import threading
import calendar
# import time
import json


class Screen1(Screen):
    def __init__(self, **kwargs):
        super(Screen1, self).__init__(**kwargs)
        self.add_widget(Label(text='Screen 1'))


class Screen2(Screen):
    def __init__(self, **kwargs):
        super(Screen2, self).__init__(**kwargs)
        self.add_widget(Label(text='Screen 2'))


class CalendarApp(App):
    def __init__(self, **kwargs):
        """Initalizing attributes."""
        super(CalendarApp, self).__init__(**kwargs)

        self.sm = ScreenManager(transition=SlideTransition(direction='right'))

        self.screen_1 = Screen1(name='screen1')
        self.screen_2 = Screen2(name='screen2')
        # self.screen_3 = Screen3(name='screen3')

        self.sm.add_widget(self.screen_1)
        self.sm.add_widget(self.screen_2)
        # self.sm.add_widget(self.screen_3)

        self.input = ""

    def on_touch_down(self, instance, touch):
        # Actions taken, when touching the screen.
        self.start_pos = touch.pos
        self.touch_x = touch.x
        self.touch_y = touch.y

    def on_touch_up(self, instance, touch):
        # Check, if the input is a click or a swipe and lock buttons if swiped.
        if abs(touch.x - self.start_pos[0]) > 40 or abs(
            touch.y - self.start_pos[1]) > 40:

            # Check the direction of the swipe
            if touch.x > self.touch_x + 80:  # Swipe right
                self.input = "swipe-right"
            elif touch.x < self.touch_x - 80:  # Swipe left
                self.input = "swipe-left"

            # Handle transition animation based on swipe direction
            if self.input == "swipe-right":
                self.sm.transition = SlideTransition(direction='right')
            elif self.input == "swipe-left":
                self.sm.transition = SlideTransition(direction='left')

            # Update the current screen based on swipe direction
            if self.sm.current == 'screen1' and self.input == "swipe-right":
                self.sm.current = 'screen2'
            elif self.sm.current == 'screen1' and self.input == "swipe-left":
                self.sm.current = 'screen2'

            elif self.sm.current == 'screen2' and self.input == "swipe-left":
                self.sm.current = 'screen1'
            elif self.sm.current == 'screen2' and self.input == "swipe-right":
                self.sm.current = 'screen1'

            print(self.input)
            self.input = ""
            return
            
        # Enable buttonpress, if input is not a swipe gesture.
        else: 
            self.input = "click"
            print(self.input)
            self.input = ""
        self.input = ""

    def build(self):
        self.sm.bind(on_touch_down=self.on_touch_down,
                     on_touch_up=self.on_touch_up)
        return self.sm

if __name__ == '__main__':
    CalendarApp().run()
