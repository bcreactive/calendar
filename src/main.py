from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

from datetime import datetime
import calendar
import time
import json

# Uncomment to block multitouch for mouse in windows version:
# from kivy.config import Config
# Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class CalendarApp(App):
    """This class creates a simple Kivy calendar-app for Android. When clicking
    on a day-button, users can write, edit, save and delete an entry in the 
    'today-view'. Swipe motions left or right increase/decrease the displayed
    month. To jump to a specific date swipe up or click the '^'-button to set a 
    date using the up and down buttons. If the displayed month is not the 
    current one, the '^'-button becomes a home-button to switch to the actual
    month. Swipe down to display the settings-popup where you can chose a
    colorset, change swipe-directions, disable/enable buttonsounds and change
    the language."""

    def __init__(self, **kwargs):
        """Initalizing attributes."""
        super(CalendarApp, self).__init__(**kwargs)
        # Get todays date.
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.current_day = datetime.now().day

        # Get the weeks with days in lists.
        self.week_start = 0
        self.weeks = self.load_month()

        # Get the amount of days for a month.
        self.month_lenght = calendar.monthrange(self.current_year,
                                           self.current_month)[1]

        self.save_file = self.load_json()

        # Load settings.
        self.color_set = self.save_file['color']
        self.swipe_x_default = self.save_file['inv_x']
        self.swipe_y_default = self.save_file['inv_y']
        self.sound = self.save_file['sound']
        self.language = self.save_file['language']

        self.load_colors()
        Window.clearcolor = self.main_win_col

        self.month_name = self.get_month_name(self.current_month)       
        self.day_labels = self.get_day_labels()
        self.entered_text = ''
        self.day_entry = ''  
        self.input = ""
        self.day_entries = {}
        self.active_entry = "1"

        self.start_pos = (0, 0)
        self.btns = []
        self.prev_btns = []
        self.next_btns = []
        self.nr = 0
        self.touch_down_time = 0

        # Load sounds.
        self.swipe_r_sound = SoundLoader.load('swipe_r.mp3')
        self.swipe_l_sound = SoundLoader.load('swipe_l.mp3')
        self.ok_sound = SoundLoader.load('ok.mp3')
        self.btn_sound = SoundLoader.load('btn.mp3')
        self.credits_sound = SoundLoader.load('credits.mp3')
        self.credits_playing = False

    def on_touch_down(self, instance, touch):
        self.touch_down_time = time.time()
        self.start_pos = touch.pos
        self.touch_x = touch.x
        self.touch_y = touch.y
            
        for i in self.btns:
            if i.collide_point(touch.x, touch.y):
                self.nr = int(i.text)
                return
            
        # for i in self.prev_btns:
        #     if i.collide_point(touch.x, touch.y):
        #         self.nr = int(i.text)
        #         return
            
        # for i in self.next_btns:
        #     if i.collide_point(touch.x, touch.y):
        #         self.nr = int(i.text)

    def on_touch_up(self, instance, touch):
        # Prevent from swipe actions when close buttons are hold.
        touch_up_time = time.time()
        time_threshold = 0.5  
        # Execute swipe or click actions.
        if touch_up_time - self.touch_down_time < time_threshold:
            if abs(touch.x - self.start_pos[0]) > 40 or abs(
                touch.y - self.start_pos[1]) > 40:
                self.buttons_locked = True

                if self.swipe_x_default:
                    if touch.x > self.touch_x + 80:
                        self.dec_month()       
                    elif touch.x < self.touch_x - 80:
                        self.inc_month()
                    
                    if self.swipe_y_default:
                        if touch.y > self.touch_y + 250:
                            self.set_date()   
                        elif touch.y < self.touch_y - 250:
                            self.open_menu_popup()

                    else:
                        if touch.y < self.touch_y - 250:
                            self.set_date()
                        elif touch.y > self.touch_y + 250:
                            self.open_menu_popup()
                
                else:
                    if touch.x < self.touch_x - 80:
                        self.dec_month()    
                    elif touch.x > self.touch_x + 80:
                        self.inc_month()

                    if self.swipe_y_default:   
                        if touch.y > self.touch_y + 250:
                            self.set_date()
                        elif touch.y < self.touch_y - 250:
                            self.open_menu_popup()

                    else:
                        if touch.y < self.touch_y - 250:
                            self.set_date()                        
                        elif touch.y > self.touch_y + 250:
                            self.open_menu_popup()

                self.input = ""
                self.start_pos = (0,0)
                self.buttons_locked = True
                return
            
        # Enable buttonpress, if input is not a swipe gesture.
        if self.input == "click":
            self.buttons_locked = False
            self.day_popup(self.nr)
            self.buttons_locked = True

        self.input = ""
        self.start_pos = (0,0)

    def check_day_popup(self, instance):
        # Check, if clicked or swiped, when the move starts on a day-button.
        if abs(self.touch_x - self.start_pos[0]) > 40 or abs(
            self.touch_y - self.start_pos[1]) > 40:
            self.input = "swipe"
            self.buttons_locked = True
        else:
            self.input = "click"
            self.buttons_locked = False

    # def check_prevday_popup(self, instance):
    #     # Check, if clicked or swiped, when the move starts on a day-button.
    #     if abs(self.touch_x - self.start_pos[0]) > 40 or abs(
    #         self.touch_y - self.start_pos[1]) > 40:
    #         self.input = "swipe"
    #         self.buttons_locked = True
    #     else:
    #         # self.dec_month()  
    #         self.input = "click"
    #         # self.buttons_locked = False
    #         self.button_nr = int(instance.text)
    #         self.day_popup(self.button_nr)

    # def check_nextday_popup(self, instance):
    #     # Check, if clicked or swiped, when the move starts on a day-button.
    #     if abs(self.touch_x - self.start_pos[0]) > 40 or abs(
    #         self.touch_y - self.start_pos[1]) > 40:
    #         self.input = "swipe"
    #         self.buttons_locked = True
    #     else:
    #         self.inc_month()
    #         self.input = "click"
    #         self.buttons_locked = False

    def build(self):
        """Create the main view when the app is launched."""

        main_layout = self.main_window()
        main_layout.bind(on_touch_down=self.on_touch_down, 
                         on_touch_up=self.on_touch_up)
        return main_layout
    
    def main_window(self):
        """Main view with buttons to navigate and to chose a day."""

        # Create buttons and labels for the main_window.
        self.year_rwd = RoundedButton(text="<", font_size=64,
                                background_color=self.navi_btn_col)
        
        self.year = Label(text=f'{self.current_year}', font_size=64,
                          color=self.main_text_col, bold=True)
        
        self.year_fwd = RoundedButton(text=">", font_size=64,
                                background_color=self.navi_btn_col)

        self.spaceholder = Label(text='', font_size=20)

        self.home_button = RoundedButton(text="^", font_size=60,
                                background_color=self.home_btn_col)

        self.month_rwd = RoundedButton(text="<", font_size=64,
                                background_color=self.navi_btn_col)
        
        self.month = Label(text=f'{self.month_name}', font_size=50,
                          color=self.main_text_col, bold=True)
        
        self.month_fwd = RoundedButton(text=">", font_size=64,
                                background_color=self.navi_btn_col)
        
        # Bindings for buttons.
        self.year_rwd.bind(on_press=self.dec_year)
        self.year_fwd.bind(on_press=self.inc_year)
        self.month_rwd.bind(on_press=self.dec_month)
        self.month_fwd.bind(on_press=self.inc_month)
        self.home_button.bind(on_press=self.set_date)

        # Building the layout:
        # Create the top row of buttons and labels: swithch year/month.
        self.top_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1),
                                 spacing=40)
        first_row = [self.year_rwd, self.year, self.year_fwd, self.home_button,
                     self.month_rwd, self.month, self.month_fwd]
        for i in first_row:
            self.top_row.add_widget(i)
        
        # Create middle row to show the days names.
        self.mid_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        for i in self.day_labels:
            self.mid_row.add_widget(i)

        # A grid of enumerated buttons, starting at the correct weekday.
        if len(self.weeks) == 4:
            self.bottom_row = GridLayout(cols=7, rows=4, spacing=15)
            self.set_buttons()

        elif len(self.weeks) == 5:
            self.bottom_row = GridLayout(cols=7, rows=5, spacing=15)
            self.set_buttons()

        elif len(self.weeks) == 6:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=15)
            self.set_buttons()

        # Create the main layout by stacking the top row, middle row and grid.
        self.main_layout = BoxLayout(orientation='vertical',
                                     padding=(10,10,10,10))
        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.mid_row)
        self.main_layout.add_widget(self.bottom_row)
        
        return self.main_layout

    def update_values(self):
        """Update the values and the view for the main-window."""
        self.month.text = self.get_month_name(self.current_month)
        self.year.text = f'{self.current_year}'
        self.weeks = self.load_month()
        self.month_lenght = calendar.monthrange(self.current_year,
                                           self.current_month)[1]
        self.input = ""
        self.entered_text = ""

        self.load_colors()
        Window.clearcolor = self.main_win_col
        
        # Remove the existing widgets to load the actualized content.
        self.top_row.clear_widgets()
        self.mid_row.clear_widgets()
        self.bottom_row.clear_widgets()
        self.main_layout.clear_widgets()

        # Update the home-buttons text and binding.
        today = self.check_today_visible()

        if today:
            self.home_button = RoundedButton(text="^", font_size=60,
                                background_color=self.home_btn_col)
            self.home_button.bind(on_press=self.set_date)

        else:
            self.home_button = RoundedButton(text="\u221A", font_size=60,
                                background_color=self.home_btn_col)
            self.home_button.bind(on_press=self.show_today)

        # Recreate rows with updated values.
        self.year_rwd = RoundedButton(text="<", font_size=64,
                                background_color=self.navi_btn_col)
        
        self.year = Label(text=f'{self.current_year}', font_size=64,
                          color=self.main_text_col, bold=True)
        
        self.year_fwd = RoundedButton(text=">", font_size=64,
                                background_color=self.navi_btn_col)

        self.spaceholder = Label(text='', font_size=20)

        self.month_rwd = RoundedButton(text="<", font_size=64,
                                background_color=self.navi_btn_col)
        
        self.month_name = self.get_month_name(self.current_month)
        self.month = Label(text=f'{self.month_name}', font_size=50,
                          color=self.main_text_col, bold=True)
        
        self.month_fwd = RoundedButton(text=">", font_size=64,
                                background_color=self.navi_btn_col)
        
        # Bindings for buttons.
        self.year_rwd.bind(on_press=self.dec_year)
        self.year_fwd.bind(on_press=self.inc_year)
        self.month_rwd.bind(on_press=self.dec_month)
        self.month_fwd.bind(on_press=self.inc_month)

        self.top_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1),
                                 spacing=40)
        
        first_row = [self.year_rwd, self.year, self.year_fwd, self.home_button,
                     self.month_rwd, self.month, self.month_fwd]
        for i in first_row:
            self.top_row.add_widget(i)
        
        self.mid_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        self.day_labels = self.get_day_labels()
        for i in self.day_labels:
            self.mid_row.add_widget(i)

        if len(self.weeks) == 4:
            self.bottom_row = GridLayout(cols=7, rows=4, spacing=15)
            self.set_buttons()
        elif len(self.weeks) == 5:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=15)
            self.set_buttons()
        elif len(self.weeks) == 6:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=15)
            self.set_buttons()

        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.mid_row)
        self.main_layout.add_widget(self.bottom_row)
        
        self.credits_sound.stop()

    def load_json(self):
        # Load savefile.
        with open('save_file.json', 'r') as file:
            data = json.load(file)
            return data

    def load_colors(self):
        # if self.color_set == 1: #green
        #     self.main_win_col = (0.7, 1, 0.1, 1)
        #     self.empty_col = (0, 0.6, 0.3)
        #     self.entry_col = get_color_from_hex('#13ecb9')
        #     self.today_col = get_color_from_hex('#9523fa')#ff69b4
        #     self.today_entry_col = get_color_from_hex('#ee23fa')
        #     self.navi_btn_col = get_color_from_hex('#0a748a')
        #     self.home_btn_col = get_color_from_hex('#50befc')
        #     self.main_text_col = get_color_from_hex('#03573b')

        #     # Colors for popups.
        #     self.bg_popups = (0,1,1,1)
        #     self.popup_btn_col = get_color_from_hex('#0a748a')
        #     self.chosen_btn_col = (1,0.3,1.1,1)
        #     self.setdate_text_col = (0.5,0.75,1,1)

        if self.color_set == 1: #metroid
            self.main_win_col = get_color_from_hex('#222034')
            self.empty_col = get_color_from_hex('#5fcde4')
            self.entry_col = get_color_from_hex('#cbdbfc')
            self.today_col = get_color_from_hex('#306082')#ff69b4
            self.today_entry_col = get_color_from_hex('#639bff')
            self.navi_btn_col = get_color_from_hex('#76428a')
            self.home_btn_col = get_color_from_hex('#76428a')
            self.main_text_col = get_color_from_hex('#d77bba')

            # Colors for popups.
            self.bg_popups = get_color_from_hex('#76428a')
            self.popup_btn_col = get_color_from_hex('#306082')
            self.chosen_btn_col = get_color_from_hex('#5fcde4')
            self.setdate_text_col = get_color_from_hex('#d77bba')

        elif self.color_set == 2: #sepia
            self.main_win_col = get_color_from_hex('#87738f')
            self.empty_col = get_color_from_hex('#d4b8b8')
            self.entry_col = get_color_from_hex('#c090a9')
            self.today_col = get_color_from_hex('#966888')
            self.today_entry_col = get_color_from_hex('#88a3bc')
            self.navi_btn_col = get_color_from_hex('#88a3bc')
            self.home_btn_col = get_color_from_hex('#bda499')
            self.main_text_col = get_color_from_hex('#bda499')

            # Colors for popups.
            self.bg_popups = get_color_from_hex('#c68bb4')#966888
            self.popup_btn_col = get_color_from_hex('#87738f')
            self.chosen_btn_col = get_color_from_hex('#d4b8b8')
            self.setdate_text_col = get_color_from_hex('#bda499')
        
        # elif self.color_set == 2: #space
        #     self.main_win_col = get_color_from_hex('#282c3c')
        #     self.empty_col = get_color_from_hex('#d4b8b8')
        #     self.entry_col = get_color_from_hex('#966888')
        #     self.today_col = get_color_from_hex('#b8ccd8')
        #     self.today_entry_col = get_color_from_hex('#d480bb')
        #     self.navi_btn_col = get_color_from_hex('#64878c')
        #     self.home_btn_col = get_color_from_hex('#64878c')
        #     self.main_text_col = get_color_from_hex('#afe9df')

        #     # Colors for popups.
        #     self.bg_popups = get_color_from_hex('#282c3c')
        #     self.popup_btn_col = get_color_from_hex('#966888')
        #     self.chosen_btn_col = get_color_from_hex('#d4b8b8')
        #     self.setdate_text_col = get_color_from_hex('#afe9df')

        elif self.color_set == 3: #b/w
            self.main_win_col = get_color_from_hex('#ffffff')
            self.empty_col = get_color_from_hex('#c1b9b9')
            self.entry_col = get_color_from_hex('#6c6767')
            self.today_col = get_color_from_hex('#000000')
            self.today_entry_col = get_color_from_hex('#424242')
            self.navi_btn_col = get_color_from_hex('#4f4f4f')
            self.home_btn_col = get_color_from_hex('#000000')
            self.main_text_col = get_color_from_hex('#818181')

            # Colors for popups.
            self.bg_popups = get_color_from_hex('#ffffff')
            self.popup_btn_col = get_color_from_hex('#4f4f4f')
            self.chosen_btn_col = get_color_from_hex('#a09d9d')
            self.setdate_text_col = get_color_from_hex('#ffffff')

        elif self.color_set == 4: #forest
            self.main_win_col = get_color_from_hex('#181c19')
            self.empty_col = get_color_from_hex('#5d9b79')
            self.entry_col = get_color_from_hex('#c6b858')
            self.today_col = get_color_from_hex('#8fd032')
            self.today_entry_col = get_color_from_hex('#97edca')
            self.navi_btn_col = get_color_from_hex('#586335')
            self.home_btn_col = get_color_from_hex('#586335')
            self.main_text_col = get_color_from_hex('#c6b858')

            # Colors for popups.
            self.bg_popups = get_color_from_hex('#333c24')
            self.popup_btn_col = get_color_from_hex('#5d9b79')
            self.chosen_btn_col = get_color_from_hex('#97edca')
            self.setdate_text_col = get_color_from_hex('#c6b858')

    def set_buttons(self):
        """Setting up the day-buttongrid."""

        # Set the buttons for the previous month if needed.
        prev_month_len = self.get_prev_month_len()
        
        days = []
        for i in range(self.week_start):
            days.append(str(prev_month_len))
            prev_month_len -= 1
        days.reverse()

        self.prev_btns = []
        for i in days:
            button = Label(text=i, color=self.navi_btn_col, font_size='30sp')
            self.bottom_row.add_widget(button)
            self.prev_btns.append(button)
            # button.bind(on_press=self.check_prevday_popup)

        # Set button-grid for the days of the current month.
        self.current_day = datetime.now().day
        current_day_visible = self.check_today_visible()

        self.btns = []
        for i in range(self.month_lenght):
            # Set fontsize and color of the "today" button to stand out.
            entry = self.check_entry(i+1)
            if current_day_visible and self.current_day == i+1:
                if entry:
                    button = RoundedButton(text=str(i+1), font_size=102,
                                background_color=self.today_entry_col,
                                bold=True)
                else:
                    button = RoundedButton(text=str(i+1), font_size=102,
                                background_color=self.today_col, bold=True)
                            
            else:
                if entry:
                    button = RoundedButton(text=str(i+1), font_size=50,
                                background_color=self.entry_col)
                else:
                    button = RoundedButton(text=str(i+1), font_size=50,
                                background_color=self.empty_col)
                     
            button.bind(on_press=self.check_day_popup)
            self.bottom_row.add_widget(button)
            self.btns.append(button)

        # Set the buttons of the next month if needed.
        amount_next_btns = self.amount_next_btns()
        if amount_next_btns:
            days = []
            for i in range(1, amount_next_btns + 1):
                days.append(str(i))

            self.prev_btns = []
            for i in days:
                button = Label(text=i, color=self.navi_btn_col,
                               font_size='30sp')
                self.bottom_row.add_widget(button)
                self.next_btns.append(button)
                # button.bind(on_press=self.check_nextday_popup)

    def get_prev_month_len(self):
        month = self.current_month - 1
        year = self.current_year
        if month > 12:
            month = 1
            year += 1
        if month < 1:
            month = 12
            year -= 1

        prev_month_len = calendar.monthrange(year, month)[1]
        return prev_month_len

    def amount_next_btns(self):
        x = 0
        amount = 0

        for i in self.btns:
            x += 1
        for i in self.prev_btns:
            x += 1

        if len(self.weeks) == 4:
            if x < 28:
                amount = 28 - x
        elif len(self.weeks) == 5:
            if x < 35:
                amount = 35 - x
        elif len(self.weeks) == 6:
            if x < 42:
                amount = 42 - x
        
        return amount

    def open_text_popup(self, instance):
        """Creates a popup with textbox to write an entry, save and delete."""
        if self.sound:
            self.btn_sound.play()

        if instance.btn_nr > 0:
            content = instance.text
            self.entered_text = content
            self.active_entry = instance.btn_nr

            text_input = TextInput(text=content, multiline=True)
            
        else:
            if self.language == "EN":
                text_input = TextInput(hint_text='Write here...',
                                multiline=True)
            else:
                text_input = TextInput(hint_text='Platz für Notizen...', 
                                       multiline=True)
              
        text_input.bind(text=self.on_text_input)
                        # focus=text_input.setter('focus'))
                        
        text_input.focus = True

        # Create and bind the cancel, delete and save buttons.
        if self.language == "EN":
            close_button = RoundedButton(text='Close', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
        else:
            close_button = RoundedButton(text='Zurück', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
            
        close_button.bind(on_press=self.close_text_popup)

        if self.language == "EN":
            save_button = RoundedButton(text='Save', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
        else:
            save_button = RoundedButton(text='Sichern', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
            
        save_button.bind(on_press=self.update_entries)

        if self.language == "EN":
            delete_button = RoundedButton(text='Delete', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
        else:
            delete_button = RoundedButton(text='Löschen', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
            
        # Close popup without confirmation, if no entry is saved.
        entry = self.check_entry(self.nr)

        if entry:
            delete_button.bind(on_press=self.ask_delete)
        else:
            delete_button.bind(on_press=self.close_text_popup)
    
        # Create the layout of the day-view.
        main_box = BoxLayout(orientation='vertical', padding=(10,0,10,0))

        content_box = BoxLayout(orientation='vertical')
        content_box.add_widget(text_input)

        button_box = BoxLayout(orientation='horizontal',
                               size_hint=(1,0.18), spacing=70)
            
        button_box.add_widget(close_button)
        # remove the delete button from the textbox, if creating a new entry.
        if self.entered_text:
            button_box.add_widget(delete_button)
        button_box.add_widget(save_button)

        spaceholder = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
            
        main_box.add_widget(content_box)
        main_box.add_widget(button_box)
        main_box.add_widget(spaceholder)

        # Create the Popup window with customized content
        month = self.get_month_name(self.current_month)   
        self.text_popup = Popup(title=f'{self.current_year} {month}' + 
                            f' {self.button_nr}.', content=main_box,
                            size_hint=(1, 1), title_align='center')
        
        if self.language == "DE":
            self.text_popup.title = (f'{self.button_nr}. {month}' +
                                    f' {self.current_year}')

        self.text_popup.background_color = self.bg_popups
        
        self.text_popup.open()
        self.input = ""
    
    def close_text_popup(self, instance):
        self.entered_text = ''
        self.active_entry = None
        self.text_popup.dismiss()
        self.update_day_popup(instance)

    def update_entries(self, instance):
        self.save_entry(instance)
        self.update_day_popup(instance)

    def day_popup(self, instance):
        """Create the day-view with a textbox and buttons."""

        if self.sound:
            self.btn_sound.play()
        self.credits_sound.stop()

        month = self.get_month_name(self.current_month)
        if isinstance(instance, int):
            self.button_nr = instance
        else:
            self.button_nr = instance.text

        # Check, if an entry exists at the chosen date.
        key = self.check_entry(self.button_nr)

        # Load entries or an add button, if no saved info is available.
        if key:
            self.entries = BoxLayout(orientation='vertical', spacing=10, 
                                     padding=(0,10,0,10))

            self.day_entries = self.save_file.get(key)

            for i in self.day_entries:
                content = self.day_entries[i]
                self.day_entry = RoundedButton(text=content, rad=30,
                                        btn_nr=int(i),
                                        background_color=self.navi_btn_col,
                                        font_size=48, size_hint=(1, 0.3))
                
                self.day_entry.bind(on_press=self.open_text_popup)

                self.entries.add_widget(self.day_entry)
        
        else:
            if self.language == "EN":
                self.empty_entry = RoundedButton(text='Add entry',
                                            rad=30, font_size=48,
                                            background_color=
                                            self.chosen_btn_col,
                                            size_hint=(1, 0.3))
            else:
                self.empty_entry = RoundedButton(text='Eintrag erstellen',
                                        rad=30, font_size=48,
                                        background_color=self.chosen_btn_col,
                                        size_hint=(1, 0.3))
            
            self.empty_entry.bind(on_press=self.open_text_popup)

        # Create and bind the cancel, delete and save buttons.
        if self.language == "EN":
            self.close_button = RoundedButton(text='Close', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
        else:
            self.close_button = RoundedButton(text='Zurück', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
            
        self.close_button.bind(on_press=self.close_day_popup)

        if self.language == "EN":
            self.add_button = RoundedButton(text='Add', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
        else:
            self.add_button = RoundedButton(text='Neu', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
            
        self.add_button.bind(on_press=self.open_text_popup)

        self.spaceholder_3 = Label(size_hint=(1,0.2))
        self.spaceholder_4 = Label(size_hint=(1,0.2))
        self.spaceholder_5 = Label(size_hint=(0.2,0.2))
        self.spaceholder_6 = Label(size_hint=(0.2,0.2))

        # # Create the layout of the 'today-view' by stacking the widgets.
        self.main_box = BoxLayout(orientation='vertical', spacing=20)

        # content_box
        self.content_box = BoxLayout(orientation='vertical')

        if key:
            
            self.content_box.add_widget(self.spaceholder_3)
            self.content_box.add_widget(self.entries)
            self.content_box.add_widget(self.spaceholder_4)
        else:
            self.content_box.add_widget(self.spaceholder_3)
            self.content_box.add_widget(self.empty_entry)
            self.content_box.add_widget(self.spaceholder_4)

        self.day_button_box = BoxLayout(orientation='horizontal',
                               size_hint=(1,0.14), spacing=70,
                               padding=(30,10,30,10))
        
        if key:
            self.day_button_box.add_widget(self.close_button)
            self.day_button_box.add_widget(self.add_button)
        else:
            self.day_button_box.add_widget(self.spaceholder_5)
            self.day_button_box.add_widget(self.close_button)
            self.day_button_box.add_widget(self.spaceholder_6)
            
        self.main_box.add_widget(self.content_box)
        self.main_box.add_widget(self.day_button_box)

        # # Create the Popup window with customized content
        self.day_pop = Popup(title=f'{self.current_year} {month}' + 
                            f' {self.button_nr}.', content=self.main_box,
                            title_align='center')
        
        if self.language == "DE":
            self.day_pop.title = (f'{self.button_nr}. {month}' +
                                    f' {self.current_year}')

        self.day_pop.background_color = self.bg_popups
        
        self.day_pop.open()
        self.input = ""

    def update_day_popup(self, instance): 
        """Update the day view."""

        self.close_day_popup()
        self.content_box.clear_widgets()
        self.day_button_box.clear_widgets()
        self.main_box.clear_widgets()

        month = self.get_month_name(self.current_month)

        # Check, if an entry exists at the chosen date.
        key = self.check_entry(self.nr)
        
        # Load entries or an add button, if no saved info is available.
        if key:
            self.entries = BoxLayout(orientation='vertical', spacing=10,
                                     padding=(0,10,0,10))

            self.day_entries = self.save_file.get(key)
            
            for i in self.day_entries:
                content = self.day_entries[i]
                self.day_entry = RoundedButton(text=content, rad=30, 
                                        btn_nr=int(i),
                                        background_color=self.navi_btn_col,
                                        font_size=48, size_hint=(1, 0.3))
                self.day_entry.bind(on_press=self.open_text_popup)

                self.entries.add_widget(self.day_entry)

        else:
            if self.language == "EN":
                self.empty_entry = RoundedButton(text='Add entry',
                                            rad=30, font_size=48,
                                            background_color=
                                            self.chosen_btn_col,
                                            size_hint=(1, 0.3))
            else:
                self.empty_entry = RoundedButton(text='Eintrag erstellen',
                                        rad=30, font_size=48,
                                        background_color=self.chosen_btn_col,
                                        size_hint=(1, 0.3))
            
            self.empty_entry.bind(on_press=self.open_text_popup)

        # Create and bind the cancel, delete and save buttons.
        if self.language == "EN":
            self.close_button = RoundedButton(text='Close', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
        else:
            self.close_button = RoundedButton(text='Zurück', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
            
        self.close_button.bind(on_press=self.close_day_popup)

        if self.language == "EN":
            self.add_button = RoundedButton(text='Add', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
        else:
            self.add_button = RoundedButton(text='Neu', 
                                    background_color=self.popup_btn_col,
                                    font_size=48)
            
        self.add_button.bind(on_press=self.open_text_popup)

        self.spaceholder_3 = Label(size_hint=(1,0.2))
        self.spaceholder_4 = Label(size_hint=(1,0.2))
        self.spaceholder_5 = Label(size_hint=(0.2,0.2))
        self.spaceholder_6 = Label(size_hint=(0.2,0.2))

        # # Create the layout of the 'today-view' by stacking the widgets.
        self.main_box = BoxLayout(orientation='vertical', spacing=20)

        # content_box
        self.content_box = BoxLayout(orientation='vertical')

        if key:
            
            self.content_box.add_widget(self.spaceholder_3)
            self.content_box.add_widget(self.entries)
            self.content_box.add_widget(self.spaceholder_4)
        else:
            self.content_box.add_widget(self.spaceholder_3)
            self.content_box.add_widget(self.empty_entry)
            self.content_box.add_widget(self.spaceholder_4)

        self.day_button_box = BoxLayout(orientation='horizontal',
                               size_hint=(1,0.14), spacing=70,
                               padding=(30,10,30,10))
        
        if key:
            self.day_button_box.add_widget(self.close_button)
            self.day_button_box.add_widget(self.add_button)
        else:
            self.day_button_box.add_widget(self.spaceholder_5)
            self.day_button_box.add_widget(self.close_button)
            self.day_button_box.add_widget(self.spaceholder_6)
            
        self.main_box.add_widget(self.content_box)
        self.main_box.add_widget(self.day_button_box)

        # # Create the Popup window with customized content
        self.day_pop = Popup(title=f'{self.current_year} {month}' + 
                            f' {self.button_nr}.', content=self.main_box,
                            # size_hint=(0.8, 0.8),
                            title_align='center')
        
        if self.language == "DE":
            self.day_pop.title = (f'{self.button_nr}. {month}' +
                                    f' {self.current_year}')

        self.day_pop.background_color = self.bg_popups
        
        self.day_pop.open()
        self.input = ""
        
    def on_text_input(self, instance, x=None):
        self.entered_text = instance.text
        
    def inc_year(self, x=None):
        # Increase year in main-window.
        self.current_year += 1
        self.update_values()
        if self.sound:
            self.swipe_l_sound.play()
    
    def dec_year(self, x=None):
        # Decrease year in main-window.
        self.current_year -= 1
        self.update_values()
        if self.sound:
            self.swipe_l_sound.play()

    def inc_month(self, x=None):
        # Increase month in main-window.
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_values()
        if self.sound:
            self.swipe_l_sound.play()

    def dec_month(self, x=None):
        # Decrease month in main-window.
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_values()
        if self.sound:
            self.swipe_l_sound.play()
    
    def check_today_visible(self):
        # Check, if the current date is visible on screen.
        if (self.current_year == datetime.now().year and
            self.current_month == datetime.now().month):
            return True
        return False

    def show_today(self, x=None):
        # Set the current year and month and update the view.
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.update_values()

    def check_entry(self, number):
        # Format the date and check if an entry is saved for the passed date.
        if len(str(number)) == 1:
            if len(str(self.current_month)) == 1:
                date = f'{self.current_year}0{self.current_month}0{number}'
            elif len(str(self.current_month)) == 2:
                date = f'{self.current_year}{self.current_month}0{number}'
        elif len(str(number)) == 2:
            if len(str(self.current_month)) == 1:
                date = f'{self.current_year}0{self.current_month}{number}'
            elif len(str(self.current_month)) == 2:
                date = f'{self.current_year}{self.current_month}{number}'

        if date in self.save_file:  
            return date
        else:
            return False

    def close_day_popup(self, x=None):
        self.input = ""
        self.day_pop.dismiss()
        if self.sound:
            self.btn_sound.play()

    def delete_entry(self, instance):
        self.close_ask()
        key = self.check_entry(self.nr)
        if key and not key == None:
            entries = self.save_file.get(key)
            if len(entries) > 1:
                del entries[str(self.active_entry)]
                self.save_file[key] = entries
            else:
                del self.save_file[key]
                    
            with open('save_file.json', 'w') as file:
                json.dump(self.save_file, file)

            self.update_values()
            self.close_text_popup(instance)

            if self.sound:
                self.ok_sound.play()

    def ask_delete(self, instance):
        if self.sound:
            self.btn_sound.play()

        # Creates a popup to confirm to delete the entry.
        if self.language == "EN":
            cancel_button = RoundedButton(text='No',
                                    background_color=self.popup_btn_col,
                                    font_size=40)
        else:
            cancel_button = RoundedButton(text='Nein',
                                    background_color=self.popup_btn_col,
                                    font_size=40)
        cancel_button.bind(on_press=self.prep_close_ask)

        if self.language == "EN":
            ok_button = RoundedButton(text='Ok',
                                    background_color=self.popup_btn_col,
                                    font_size=40)
        else:
            ok_button = RoundedButton(text='Ja',
                                    background_color=self.popup_btn_col,
                                    font_size=40)
        
        ok_button.bind(on_press=self.delete_entry)

        main_box = BoxLayout(orientation='vertical', padding=(10,10,10,10))
        button_box = BoxLayout(orientation='horizontal', size_hint=(1,0.4),
                               spacing=30)     
         
        button_box.add_widget(cancel_button)
        button_box.add_widget(ok_button)
        main_box.add_widget(button_box)

        self.ask_popup = Popup(title='erase entry?', content=main_box,
                                    size_hint=(0.5, 0.3), title_align='center')
        
        if self.language == "DE":
            self.ask_popup.title = 'Eintrag löschen?'
                
        self.ask_popup.background_color = self.bg_popups
        self.ask_popup.pos_hint = {'center_x': 0.5, 'center_y': 0.45}
        
        self.ask_popup.open()

    def prep_close_ask(self, x=None):
        self.close_ask()
        if self.sound:
            self.btn_sound.play()

    def close_ask(self, x=None):
        self.ask_popup.dismiss()
        self.update_values()

    def save_entry(self, instance):
        # Format the date and save the entered text in json safe file.
        month = len(str(self.current_month))
        day = len(str(self.button_nr))

        if month == 1 and day == 1:
            date = f'{self.current_year}0{self.current_month}0{self.button_nr}'
        elif month == 1 and day == 2:
            date = f'{self.current_year}0{self.current_month}{self.button_nr}'
        elif month == 2 and day == 1:
            date = f'{self.current_year}{self.current_month}0{self.button_nr}'
        else:
            date = f'{self.current_year}{self.current_month}{self.button_nr}'

        if self.entered_text:
            if date in self.save_file:
                self.day_entries = self.save_file.get(date)
                if str(self.active_entry) in self.day_entries:
                    self.day_entries[str(self.active_entry)] =self.entered_text
                else:
                    if self.day_entries:
                        max_key = max(map(int, self.day_entries.keys())) + 1 
                    else:
                        max_key = 1

                    new_entry = {str(max_key): self.entered_text}
                    self.day_entries.update(new_entry)
                self.save_file[date] = self.day_entries
            else: 
                new_entry = {"1": self.entered_text}
                self.save_file[date] = new_entry

            with open('save_file.json', 'w') as file:
                json.dump(self.save_file, file)

            if self.sound:
                self.ok_sound.play()

            self.day_entries = None
            self.active_entry = None
            self.update_values()
            self.update_day_popup(instance)
            self.close_text_popup(instance)
            return
        
        if not self.entered_text:
            self.close_text_popup(instance)
            self.active_entry = None

    def get_month_name(self, value):
        if self.language == "EN":
            months = ["Jan", "Feb", "March", "April", "Mai", "June", "July",
                    "Aug", "Sept", "Oct", "Nov", "Dec"]
        else:
            months = ["Jan", "Feb", "März", "April", "Mai", "Juni", "Juli",
                    "Aug", "Sept", "Okt", "Nov", "Dez"]
            
        return months[value-1]
       
    def get_day_labels(self):
        if self.language == "EN":
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fry", "Sat", "Sun"]
        else:
            day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

        labels = []
        for i in day_names:
            label = Label(text=f'{i}', color=self.main_text_col, font_size=40,
                          bold=True)
            labels.append(label)

        return labels
       
    def load_month(self):
        # Get the weeks in lists and get the 1. weekday of the month.
        weeks = calendar.monthcalendar(self.current_year, self.current_month)
        self.week_start = weeks[0].index(1)
        return weeks

    def set_date(self, x=None):
        """Create the set-date view to chose a date and jump to day-view."""
        if self.sound:
            self.btn_sound.play()

        self.chose_d = datetime.now().day
        self.chose_m = datetime.now().month
        self.chose_y = datetime.now().year
        month_name = self.get_month_name(self.chose_m)

        # Setting up the buttons and labels.
        if self.language == "EN":
            self.y_label = Label(text='Year', font_size=48,
                            color=self.setdate_text_col)
            self.m_label = Label(text='Month', font_size=48,
                            color=self.setdate_text_col)
            self.d_label = Label(text='Day', font_size=48,
                            color=self.setdate_text_col)
        
        else:
            self.d_label = Label(text='Tag', font_size=48,
                            color=self.setdate_text_col)
            self.m_label = Label(text='Monat', font_size=48,
                            color=self.setdate_text_col)
            self.y_label = Label(text='Jahr', font_size=48,
                            color=self.setdate_text_col)
            
        self.dy = Label(text=f'{self.chose_d}', font_size=56,
                        color=self.setdate_text_col)
        self.mnt = Label(text=f'{month_name}', font_size=56,
                        color=self.setdate_text_col)
        self.yr = Label(text=f'{self.chose_y}', font_size=56,
                        color=self.setdate_text_col)
        
        self.y_fwd = RoundedButton(text="^", font_size=64,
                                background_color=self.popup_btn_col)
        self.y_rwd = RoundedButton(text="v", font_size=46,
                                background_color=self.popup_btn_col)
        self.m_fwd = RoundedButton(text="^", font_size=64,
                                background_color=self.popup_btn_col)
        self.m_rwd = RoundedButton(text="v", font_size=46,
                                background_color=self.popup_btn_col)
        self.d_fwd = RoundedButton(text="^", font_size=64,
                                background_color=self.popup_btn_col)
        self.d_rwd = RoundedButton(text="v", font_size=46,
                                background_color=self.popup_btn_col)
 
        self.ok = RoundedButton(text="ok", font_size=48,
                                    # size_hint=(1, 0.5),
                                    background_color=self.popup_btn_col)
        
        self.spaceholder_1 = Label(text='', font_size=64, size_hint=(1, 0.2))
        
        # Button bindings.
        self.y_fwd.bind(on_press=self.inc_y)
        self.y_rwd.bind(on_press=self.dec_y)
        self.m_fwd.bind(on_press=self.inc_m)
        self.m_rwd.bind(on_press=self.dec_m)
        self.d_fwd.bind(on_press=self.inc_d)
        self.d_rwd.bind(on_press=self.dec_d)

        self.ok.bind(on_press=self.jump_to)

        # Setting up the Layoutboxes for the set-date view.
        self.label_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                   spacing=30)
        if self.language == "EN":
            labels = [self.y_label, self.m_label, self.d_label]
        else:
            labels = [self.d_label, self.m_label, self.y_label]

        for i in labels:
            self.label_row.add_widget(i)
        
        self.fwd_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                 spacing=30)
        if self.language == "EN":
            fwd_buttons = [self.y_fwd, self.m_fwd, self.d_fwd]
        else:
            fwd_buttons = [self.d_fwd, self.m_fwd, self.y_fwd]

        for i in fwd_buttons:
            self.fwd_row.add_widget(i)

        self.date_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                  spacing=30)
        
        if self.language == "EN":
            date_values = [self.yr, self.mnt, self.dy]
        else:
            date_values = [self.dy, self.mnt, self.yr]

        for i in date_values:
            self.date_row.add_widget(i)

        self.rwd_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                 spacing=30)
        if self.language == "EN":
            rwd_buttons = [self.y_rwd, self.m_rwd, self.d_rwd]
        else:
            rwd_buttons = [self.d_rwd, self.m_rwd, self.y_rwd]
            
        for i in rwd_buttons:
            self.rwd_row.add_widget(i)

        # Create the main set-date layout by stacking the Layoutboxes.
        self.setdate_layout = BoxLayout(orientation='vertical', spacing=20,
                                        padding=(10,10,10,10))
        self.setdate_layout.add_widget(self.label_row)
        self.setdate_layout.add_widget(self.fwd_row)
        self.setdate_layout.add_widget(self.date_row)
        self.setdate_layout.add_widget(self.rwd_row)
        self.setdate_layout.add_widget(self.spaceholder_1)
        self.setdate_layout.add_widget(self.ok)

        
        self.setdate_popup = Popup(title='Jump to date:',
                                    content=self.setdate_layout,
                                   size_hint=(0.6, 0.6), title_align='center')
        
        if self.language == "DE":
            self.setdate_popup.title = 'Wechsle zu Datum:'
        self.setdate_popup.background_color = self.bg_popups
        
        self.nr = self.chose_d
        self.setdate_popup.open()
    
    def prep_close(self, x=None):
        self.close_setdate()
        if self.sound:
            self.btn_sound.play()

    def close_setdate(self, x=None):
        self.setdate_popup.dismiss()
        self.update_values()

    def inc_y(self, x=None):
        # Increase set-date year.
        self.chose_y += 1
        self.update_setdate()
        if self.sound:
            self.btn_sound.play()

    def dec_y(self, x=None):
        # Decrease set-date year.
        self.chose_y -= 1
        self.update_setdate()
        if self.sound:
            self.btn_sound.play()
        
    def inc_m(self, x=None):
        # Increase set-date month.
        if self.chose_m == 12:
            self.chose_m = 1
            self.update_setdate()
            return
        self.chose_m += 1
        self.update_setdate()
        if self.sound:
            self.btn_sound.play()
    
    def dec_m(self, x=None):
        # Decrease set-date month.
        if self.chose_m == 1:
            self.chose_m = 12
            self.update_setdate()
            return
        self.chose_m -= 1
        self.update_setdate()
        if self.sound:
            self.btn_sound.play()

    def inc_d(self, x=None):
        # Increase set-date day.
        days = self.get_days_in_month(self.chose_y, self.chose_m)[1]
        if self.chose_d >= days:
            self.chose_d = 1
            self.update_setdate()
            return
        self.chose_d += 1
        self.update_setdate()
        if self.sound:
            self.btn_sound.play()
    
    def dec_d(self, x=None):
        # Decrease set-date day.
        days = self.get_days_in_month(self.chose_y, self.chose_m)[1]
        if self.chose_d <= 1:
            self.chose_d = days
            self.update_setdate()
            return
        self.chose_d -= 1
        self.update_setdate()
        if self.sound:
            self.btn_sound.play()

    def get_days_in_month(self, year, month):
        days_in_month = calendar.monthrange(year, month)
        return days_in_month

    def update_setdate(self):
        """Update the values and the view for the set-date popup."""
        # Remove the existing widgets to load the actualized content.
        self.label_row.clear_widgets()
        self.fwd_row.clear_widgets()
        self.date_row.clear_widgets()
        self.rwd_row.clear_widgets()       
        self.setdate_layout.clear_widgets()

        # Check, if day value is possible and correct if not so.
        days = self.get_days_in_month(self.chose_y, self.chose_m)[1]
        if self.chose_d > days or self.chose_d < 1:
            self.chose_d = 1
        
        month_name = self.get_month_name(self.chose_m)

        if self.language == "EN":
            self.y_label = Label(text='Year', font_size=48,
                            color=self.setdate_text_col)
            self.m_label = Label(text='Month', font_size=48,
                            color=self.setdate_text_col)
            self.d_label = Label(text='Day', font_size=48,
                            color=self.setdate_text_col)
            
        elif self.language == "DE":
            self.d_label = Label(text='Tag', font_size=48,
                            color=self.setdate_text_col)
            self.m_label = Label(text='Monat', font_size=48,
                            color=self.setdate_text_col)
            self.y_label = Label(text='Jahr', font_size=48,
                            color=self.setdate_text_col)
            
        self.dy = Label(text=f'{self.chose_d}', font_size=56,
                        color=self.setdate_text_col)
        self.mnt = Label(text=f'{month_name}', font_size=56,
                        color=self.setdate_text_col)
        self.yr = Label(text=f'{self.chose_y}', font_size=56,
                        color=self.setdate_text_col)

        self.label_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                   spacing=30)
        
        if self.language == "EN":
            labels = [self.y_label, self.m_label, self.d_label]
        else:
            labels = [self.d_label, self.m_label, self.y_label]

        for i in labels:
            self.label_row.add_widget(i)
        
        self.fwd_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                 spacing=30)
        
        if self.language == "EN":
            fwd_buttons = [self.y_fwd, self.m_fwd, self.d_fwd]
        else:
            fwd_buttons = [self.d_fwd, self.m_fwd, self.y_fwd]

        for i in fwd_buttons:
            self.fwd_row.add_widget(i)

        self.date_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                  spacing=30)
        
        if self.language == "EN":
            date_values = [self.yr, self.mnt, self.dy]
        else:
            date_values = [self.dy, self.mnt, self.yr]
        for i in date_values:
            self.date_row.add_widget(i)

        self.rwd_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                 spacing=30)
        
        if self.language == "EN":
            rwd_buttons = [self.y_rwd, self.m_rwd, self.d_rwd]
        else:
            rwd_buttons = [self.d_rwd, self.m_rwd, self.y_rwd]

        for i in rwd_buttons:
            self.rwd_row.add_widget(i)

        self.setdate_layout.add_widget(self.label_row)
        self.setdate_layout.add_widget(self.fwd_row)
        self.setdate_layout.add_widget(self.date_row)
        self.setdate_layout.add_widget(self.rwd_row)
        self.setdate_layout.add_widget(self.spaceholder_1)
        self.setdate_layout.add_widget(self.ok)

        self.nr = self.chose_d
        self.input = ""

    def jump_to(self, instance):
        # Jump to the chosen date and open the today-view.
        self.close_setdate()
        self.current_year = self.chose_y
        self.current_month = self.chose_m
        self.current_day = self.chose_d

        entry = self.check_entry(self.current_day)
        if entry:
            self.day_popup(self.current_day)
        else:
            self.open_text_popup(instance)

        self.update_values()
        self.input = ""

    def open_menu_popup(self, x=None):
        """Popup to change settings."""

        if self.sound:
            self.btn_sound.play()
        self.credits_sound.stop()

        # Labels, buttons, bindings for color settings.
        if self.language == "EN":
            self.col_title = Label(text='Color', font_size=48, 
                            color=self.setdate_text_col)
        else:
            self.col_title = Label(text='Farbe', font_size=48, 
                          color=self.setdate_text_col)

        if self.color_set == 1:
            col_1_bg_color = self.chosen_btn_col
            col_2_bg_color = self.popup_btn_col
            col_3_bg_color = self.popup_btn_col
            col_4_bg_color = self.popup_btn_col
        elif self.color_set == 2:
            col_1_bg_color = self.popup_btn_col
            col_2_bg_color = self.chosen_btn_col
            col_3_bg_color = self.popup_btn_col
            col_4_bg_color = self.popup_btn_col
        elif self.color_set == 3:
            col_1_bg_color = self.popup_btn_col
            col_2_bg_color = self.popup_btn_col
            col_3_bg_color = self.chosen_btn_col
            col_4_bg_color = self.popup_btn_col
        elif self.color_set == 4:
            col_1_bg_color = self.popup_btn_col
            col_2_bg_color = self.popup_btn_col
            col_3_bg_color = self.popup_btn_col
            col_4_bg_color = self.chosen_btn_col

        self.col_select_1 = RoundedButton(text='1', font_size=42,
                                          background_color=col_1_bg_color)
        self.col_select_2 = RoundedButton(text='2', font_size=42,
                                          background_color=col_2_bg_color)
        self.col_select_3 = RoundedButton(text='3', font_size=42,
                                          background_color=col_3_bg_color)
        self.col_select_4 = RoundedButton(text='4', font_size=42,
                                          background_color=col_4_bg_color)

        self.col_select_1.bind(on_release=self.colorset_1)
        self.col_select_2.bind(on_release=self.colorset_2)
        self.col_select_3.bind(on_release=self.colorset_3)
        self.col_select_4.bind(on_release=self.colorset_4)

        # Labels, buttons, bindings for axis inversion settings. 
        self.invert_title = Label(text='Invert', font_size=48,
                                color=self.setdate_text_col)
            
        if self.swipe_x_default:
            invert_x_bg_color = self.popup_btn_col
        else:
            invert_x_bg_color = self.chosen_btn_col

        if self.swipe_y_default:
            invert_y_bg_color = self.popup_btn_col
        else:
            invert_y_bg_color = self.chosen_btn_col

        self.invert_x_btn = RoundedButton(text='X', font_size=48,
                                          background_color=invert_x_bg_color)
        self.invert_y_btn = RoundedButton(text='Y', font_size=48,
                                          background_color=invert_y_bg_color)

        self.invert_x_btn.bind(on_release=self.invert_x)
        self.invert_y_btn.bind(on_release=self.invert_y)

        # Labels, buttons, bindings for sound settings.
        if self.language == "EN":
            self.sound_title = Label(text='Sound', font_size=48,
                                color=self.setdate_text_col)
        else:
            self.sound_title = Label(text='Musik', font_size=48,
                             color=self.setdate_text_col)
        
        if self.sound:
            if self.language == "EN":
                self.sound_btn = RoundedButton(text='On', font_size=48,
                                        background_color=self.chosen_btn_col)
            else:
                self.sound_btn = RoundedButton(text='Ein', font_size=48,
                                          background_color=self.chosen_btn_col)
        else:
            if self.language == "EN":
                self.sound_btn = RoundedButton(text='Off', font_size=48,
                                          background_color=self.popup_btn_col)
            else:
                self.sound_btn = RoundedButton(text='Aus', font_size=48,
                                          background_color=self.popup_btn_col)
        
        self.sound_btn.bind(on_release=self.set_sound)

        self.about_btn = RoundedButton(text='Info', font_size=24,
                                       size_hint=(1, 0.5),
                                       background_color=self.popup_btn_col)
        
        self.about_btn.bind(on_release=self.open_credits)

        # Labels, buttons, bindings for language settings.
        if self.language == "EN":
            self.language_title = Label(text='Language', font_size=48,
                                color=self.setdate_text_col)
        else:
            self.language_title = Label(text='Sprache', font_size=48,
                                color=self.setdate_text_col)

        if self.language == "EN":
            self.language_button = RoundedButton(text='English', font_size=48,
                                          background_color=self.popup_btn_col)
        else:
            self.language_button = RoundedButton(text='Deutsch', font_size=48,
                                          background_color=self.popup_btn_col)
        
        self.language_button.bind(on_release=self.switch_language)

        self.spaceholder_2 = Label(text='', font_size=64, size_hint=(1, 0.7))

        # Boxes in boxes with titles and buttons.
        self.title_box = BoxLayout(orientation='vertical', spacing=30,
                                   size_hint=(0.4, 1))
        self.title_box.add_widget(self.col_title)
        self.title_box.add_widget(self.invert_title)
        self.title_box.add_widget(self.sound_title)
        self.title_box.add_widget(self.language_title)
        self.title_box.add_widget(self.spaceholder_2)

        self.clr_btns = BoxLayout(orientation='horizontal', spacing=20)
        self.clr_btns.add_widget(self.col_select_1)
        self.clr_btns.add_widget(self.col_select_2)
        self.clr_btns.add_widget(self.col_select_3)
        self.clr_btns.add_widget(self.col_select_4)

        self.inv_btns = BoxLayout(orientation='horizontal', spacing=20) 
        self.inv_btns.add_widget(self.invert_x_btn)
        self.inv_btns.add_widget(self.invert_y_btn)

        self.snd_btn = BoxLayout(orientation='horizontal', spacing=0)
        self.snd_btn.add_widget(self.sound_btn)

        self.lang_btn = BoxLayout(orientation='horizontal')
        self.lang_btn.add_widget(self.language_button)

        self.btn_box = BoxLayout(orientation='vertical', spacing=30)
        self.btn_box.add_widget(self.clr_btns)
        self.btn_box.add_widget(self.inv_btns)
        self.btn_box.add_widget(self.snd_btn)
        self.btn_box.add_widget(self.lang_btn)
        self.btn_box.add_widget(self.about_btn)

        self.btns_title_box = BoxLayout(orientation='horizontal', spacing=20)
        self.btns_title_box.add_widget(self.title_box)
        self.btns_title_box.add_widget(self.btn_box)

        # Main layoutbox for the settings.
        self.menu_layout = BoxLayout(orientation='vertical', spacing=20,
                                     padding=(10,10,10,10))
        
        self.menu_layout.add_widget(self.btns_title_box)
        
        self.menu_popup = Popup(title='Settings', content=self.menu_layout,
                                    size_hint=(0.7, 0.7), title_align="center")
        
        if self.language == "DE":
            self.menu_popup.title = 'Einstellungen'
        self.menu_popup.background_color = self.bg_popups

        self.menu_popup.open()
        self.input = ""

    def colorset_1(self, instance):
        self.color_set = 1
        self.update_values()
        self.update_menu(instance)
        if self.sound:
            self.btn_sound.play()

    def colorset_2(self, instance):
        self.color_set = 2
        self.update_values()
        self.update_menu(instance)
        if self.sound:
            self.btn_sound.play()

    def colorset_3(self, instance):
        self.color_set = 3
        self.update_values()
        self.update_menu(instance)
        if self.sound:
            self.btn_sound.play()
    
    def colorset_4(self, instance):
        self.color_set = 4
        self.update_values()
        self.update_menu(instance)
        if self.sound:
            self.btn_sound.play()

    def invert_x(self, instance):
        if self.swipe_x_default:
            self.swipe_x_default = False
        else:
            self.swipe_x_default = True
        self.update_menu(instance)
        if self.sound:
            self.btn_sound.play()

    def invert_y(self, instance):
        if self.swipe_y_default:
            self.swipe_y_default = False
        else:
            self.swipe_y_default = True
        self.update_menu(instance)
        if self.sound:
            self.btn_sound.play()

    def set_sound(self, instance):
        if self.sound:
            self.sound = False
        else:
            self.sound = True
        self.update_menu(instance)
        if self.sound:
            self.btn_sound.play()

    def switch_language(self, instance):
        if self.language == "DE":
            self.language = "EN"
        else:
            self.language = "DE"
        self.update_values()
        self.update_menu(instance)
        if self.sound:
            self.btn_sound.play()

    def close_menu(self, x=None):
        self.menu_popup.dismiss()
        if self.sound:
            self.btn_sound.play()
        self.credits_sound.stop()

    def update_menu(self, instance):
        # Update button-colors of the chosen options.

        # Clear all layout-boxes to update with actualized elements.
        self.btns_title_box.clear_widgets()
        self.btn_box.clear_widgets()
        self.title_box.clear_widgets()
        self.clr_btns.clear_widgets()
        self.inv_btns.clear_widgets()
        self.snd_btn.clear_widgets()
        self.menu_layout.clear_widgets()
        
        # Update labels, buttons, bindings for color settings.
        if self.language == "EN":
            self.col_title = Label(text='Color', font_size=48, 
                            color=self.setdate_text_col)
        else:
            self.col_title = Label(text='Farbe', font_size=48, 
                          color=self.setdate_text_col)
        
        self.menu_popup.background_color = self.bg_popups

        if self.language == "EN":
            self.menu_popup.title = 'Settings'
        else:
            self.menu_popup.title = 'Einstellungen'
        
        if self.color_set == 1:
            col_1_bg_color = self.chosen_btn_col
            col_2_bg_color = self.popup_btn_col
            col_3_bg_color = self.popup_btn_col
            col_4_bg_color = self.popup_btn_col
        elif self.color_set == 2:
            col_1_bg_color = self.popup_btn_col
            col_2_bg_color = self.chosen_btn_col
            col_3_bg_color = self.popup_btn_col
            col_4_bg_color = self.popup_btn_col
        elif self.color_set == 3:
            col_1_bg_color = self.popup_btn_col
            col_2_bg_color = self.popup_btn_col
            col_3_bg_color = self.chosen_btn_col
            col_4_bg_color = self.popup_btn_col
        elif self.color_set == 4:
            col_1_bg_color = self.popup_btn_col
            col_2_bg_color = self.popup_btn_col
            col_3_bg_color = self.popup_btn_col
            col_4_bg_color = self.chosen_btn_col

        self.col_select_1 = RoundedButton(text='1', font_size=42,
                                          background_color=col_1_bg_color)
        self.col_select_2 = RoundedButton(text='2', font_size=42,
                                          background_color=col_2_bg_color)
        self.col_select_3 = RoundedButton(text='3', font_size=42,
                                          background_color=col_3_bg_color)
        self.col_select_4 = RoundedButton(text='4', font_size=42,
                                          background_color=col_4_bg_color)

        self.col_select_1.bind(on_release=self.colorset_1)
        self.col_select_2.bind(on_release=self.colorset_2)
        self.col_select_3.bind(on_release=self.colorset_3)
        self.col_select_4.bind(on_release=self.colorset_4)

        # Update labels, buttons, bindings for axis inversion settings.
        self.invert_title = Label(text='Invert', font_size=48,
                             color=self.setdate_text_col)

        if self.swipe_x_default:
            invert_x_bg_color = self.popup_btn_col
        else:
            invert_x_bg_color = self.chosen_btn_col

        if self.swipe_y_default:
            invert_y_bg_color = self.popup_btn_col
        else:
            invert_y_bg_color = self.chosen_btn_col

        self.invert_x_btn = RoundedButton(text='X', font_size=48,
                                          background_color=invert_x_bg_color)
        self.invert_y_btn = RoundedButton(text='Y', font_size=48,
                                          background_color=invert_y_bg_color)

        self.invert_x_btn.bind(on_release=self.invert_x)
        self.invert_y_btn.bind(on_release=self.invert_y)

        # Update labels, buttons, bindings for sound settings.
        if self.language == "EN":
            self.sound_title = Label(text='Sound', font_size=48,
                                color=self.setdate_text_col)
        else:
            self.sound_title = Label(text='Musik', font_size=48,
                             color=self.setdate_text_col)
        
        if self.sound:
            if self.language == "EN":
                self.sound_btn = RoundedButton(text='On', font_size=48,
                                          background_color=self.chosen_btn_col)
            else:
                self.sound_btn = RoundedButton(text='Ein', font_size=48,
                                          background_color=self.chosen_btn_col)
        else:
            if self.language == "EN":
                self.sound_btn = RoundedButton(text='Off', font_size=48,
                                          background_color=self.popup_btn_col)
            else:
                self.sound_btn = RoundedButton(text='Aus', font_size=48,
                                          background_color=self.popup_btn_col)
                
        self.sound_btn.bind(on_release=self.set_sound)

        self.about_btn = RoundedButton(text='Info', font_size=24,
                                       size_hint=(1, 0.5),
                                       background_color=self.popup_btn_col)
        
        self.about_btn.bind(on_release=self.open_credits)

        self.button_box = BoxLayout(orientation='horizontal',
                                    size_hint=(1, 0.3))
        
        # Labels, buttons, bindings for language settings.
        if self.language == "EN":
            self.language_title = Label(text='Language', font_size=48,
                                color=self.setdate_text_col)
        else:
            self.language_title = Label(text='Sprache', font_size=48,
                                color=self.setdate_text_col)

        if self.language == "EN":
            self.language_button = RoundedButton(text='English', font_size=48,
                                          background_color=self.popup_btn_col)
        else:
            self.language_button = RoundedButton(text='Deutsch', font_size=48,
                                          background_color=self.popup_btn_col)
        
        self.language_button.bind(on_release=self.switch_language)

        # Boxes in boxes with titles and buttons.
        self.title_box = BoxLayout(orientation='vertical', spacing=30,
                                   size_hint=(0.4, 1))
        self.title_box.add_widget(self.col_title)
        self.title_box.add_widget(self.invert_title)
        self.title_box.add_widget(self.sound_title)
        self.title_box.add_widget(self.language_title)
        self.title_box.add_widget(self.spaceholder_2)

        self.clr_btns = BoxLayout(orientation='horizontal', spacing=20)
        self.clr_btns.add_widget(self.col_select_1)
        self.clr_btns.add_widget(self.col_select_2)
        self.clr_btns.add_widget(self.col_select_3)
        self.clr_btns.add_widget(self.col_select_4)

        self.inv_btns = BoxLayout(orientation='horizontal', spacing=20) 
        self.inv_btns.add_widget(self.invert_x_btn)
        self.inv_btns.add_widget(self.invert_y_btn)

        self.snd_btn = BoxLayout(orientation='horizontal', spacing=0)
        self.snd_btn.add_widget(self.sound_btn)

        self.lang_btn = BoxLayout(orientation='horizontal', spacing=0)
        self.lang_btn.add_widget(self.language_button)

        self.btn_box = BoxLayout(orientation='vertical', spacing=30)
        self.btn_box.add_widget(self.clr_btns)
        self.btn_box.add_widget(self.inv_btns)
        self.btn_box.add_widget(self.snd_btn)
        self.btn_box.add_widget(self.lang_btn)
        self.btn_box.add_widget(self.about_btn)

        self.btns_title_box = BoxLayout(orientation='horizontal', spacing=20)
        self.btns_title_box.add_widget(self.title_box)
        self.btns_title_box.add_widget(self.btn_box)

        # Main layoutbox for the settings.
        self.menu_layout.add_widget(self.btns_title_box)
        self.save_setting()
        self.input = ""
        self.credits_sound.stop()

    def save_setting(self):
        color = {"color": self.color_set}
        inv_x = {"inv_x": self.swipe_x_default}
        inv_y = {"inv_y": self.swipe_y_default}
        sound = {"sound": self.sound}
        language = {"language": self.language}
        self.save_file.update(color)
        self.save_file.update(inv_x)
        self.save_file.update(inv_y)
        self.save_file.update(sound)
        self.save_file.update(language)

        with open('save_file.json', 'w') as file:
                json.dump(self.save_file, file)

    def open_credits(self, instance):
        # Creates a popup to show creators credits.
        title = Label(text='', font_size=40, size_hint=(1, 0.05),
                             color=self.setdate_text_col)
         
        close_button = RoundedButton(
            text="""            made with kivy/python

            by bc-reactive:
            github.com/bcreactive

            soundcloud.com/awtomatsupabreakz

            thanks for testing!""",

            background_color=self.popup_btn_col,
                                font_size=28, bold=True)
    
        if self.language == "DE":
            close_button.text = """            Erstellt mit Kivy/Python
            
            von bc-reactive:
            github.com/bcreactive

            soundcloud.com/awtomatsupabreakz

            Danke fürs Testen!"""
        
        close_button.bind(on_press=self.close_credits)

        credits_box = BoxLayout(orientation='vertical', spacing=30,
                                padding=(10,10,10,10))
            
        credits_box.add_widget(title)
        credits_box.add_widget(close_button)

        self.credits_popup = Popup(title='Info', content=credits_box,
                                size_hint=(0.7, 0.7), title_align='center')
        
        self.credits_popup.background_color = self.bg_popups
    
        self.credits_popup.open()

        if self.sound:
            self.credits_sound.play()
        
    def close_credits(self, instance):
        self.credits_popup.dismiss()
        self.sound = self.save_file["sound"]
        self.credits_sound.stop()

   
class RoundedButton(Button):
    """This class creates buttons with rounded edges."""
    
    def __init__(self, text="", background_color=(0, 0.6, 0.3), rad=68,
                 btn_nr=0, **kwargs):

        super(RoundedButton, self).__init__(**kwargs)
        with self.canvas.before:
            Color(*background_color)
            self._rounded_rect = RoundedRectangle(pos=self.pos, size=self.size,
                                                  radius=[rad])

        self.btn_nr = btn_nr
        self.text = text
        self.background_color = [0, 0, 0, 0] # Background color: transparent

    def on_pos(self, instance, pos):
        self._rounded_rect.pos = pos

    def on_size(self, instance, size):
        self._rounded_rect.size = size


if __name__ == '__main__':
    calendar_app = CalendarApp()
    calendar_app.run()