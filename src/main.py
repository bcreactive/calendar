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

from datetime import datetime
import calendar
import json

# Uncomment to block multitouch for mouse in windows version
# from kivy.config import Config
# Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# Window.clearcolor = (0, 1, 0, 1)
# Window.clearcolor = (0.5, 1, 0.4, 1)
# Window.clearcolor = (0.7, 1, 0.1, 1)
# Window.clearcolor = (0.8, 1, 0.4, 1)
# Window.clearcolor = get_color_from_hex('#5cd8f2')


class RoundedButton(Button):
    """This class creates a buttons with rounded edges."""
    
    def __init__(self, text="", color=get_color_from_hex('#ec6613'),
                 background_color=(0, 0.6, 0.3), **kwargs): #(0, 0.7, 0.2)
        
        super(RoundedButton, self).__init__(**kwargs)
        Window.clearcolor = (0.7, 1, 0.1, 1)
        with self.canvas.before:
            Color(*background_color)
            self._rounded_rect = RoundedRectangle(pos=self.pos, size=self.size,
                                                  radius=[68])

        self.text = text
        self.background_color = [0, 0, 0, 0]  # Background color: transparent

    def on_pos(self, instance, pos):
        self._rounded_rect.pos = pos

    def on_size(self, instance, size):
        self._rounded_rect.size = size


class CalendarApp(App):
    """This class creates a simple kivy calendar-app for android, where the
    user can write, edit, save and delete an entry in the 'today-view' when 
    clicking on a day-button. To jump to a specific date click the '^'-button 
    and set a date using the up and down buttons. If the displayed month is not
    the current one, the '^'-button becomes a home-button to switch to the 
    actual month."""

    
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
       
        self.month_name = self.get_month_name(self.current_month)       
        self.day_labels = self.get_day_labels()

        self.save_file = self.load_json()

        self.entered_text = ''
        self.day_entry = ''  
                
    def build(self):
        """Create the main view if the app is launched."""
        main_window = self.main_window()
        return main_window
    
    def main_window(self):
        # Create buttons and labels for the main_window.
        self.year_rwd = RoundedButton(text="<", font_size=64,
                                background_color=get_color_from_hex('#0a748a'))
        
        self.year = Label(text=f'{self.current_year}', font_size=64,
                          color=get_color_from_hex('#03573b'), bold=True)
        
        self.year_fwd = RoundedButton(text=">", font_size=64,
                                background_color=get_color_from_hex('#0a748a'))

        self.spaceholder = Label(text='', font_size=20)

        self.home_button = RoundedButton(text="^", font_size=60,
                                background_color=get_color_from_hex('#50befc'))

        self.month_rwd = RoundedButton(text="<", font_size=64,
                                background_color=get_color_from_hex('#0a748a'))
        
        self.month = Label(text=f'{self.month_name}', font_size=50,
                          color=get_color_from_hex('#03573b'), bold=True)
        
        self.month_fwd = RoundedButton(text=">", font_size=64,
                                background_color=get_color_from_hex('#0a748a'))
        
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
            self.bottom_row = GridLayout(cols=7, rows=4, spacing=10)
            self.set_buttons()

        elif len(self.weeks) == 5:
            self.bottom_row = GridLayout(cols=7, rows=5, spacing=10)
            self.set_buttons()

        elif len(self.weeks) == 6:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=10)
            self.set_buttons()

        # Create the main layout by stacking the top row, middle row and grid.
        self.main_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.mid_row)
        self.main_layout.add_widget(self.bottom_row)

        return self.main_layout

    def load_json(self):
        # Load savefile.
        with open('save_file.json', 'r') as file:
            data = json.load(file)
            return data
    
    def set_buttons(self):
        """Setting up the day-buttongrid."""
        # Set the placeholder labels to have the buttons start at correct day.
        for i in range(self.week_start):
            label = Label(text="")
            self.bottom_row.add_widget(label)

        self.current_day = datetime.now().day

        # Set button-grid for the days.
        current_day_visible = self.check_today()

        for i in range(self.month_lenght):
            # Set fontsize and color of the "today" button to stand out.
            entry = self.check_entry(i+1)
            if current_day_visible and self.current_day == i+1:
                if entry:
                    button = RoundedButton(text=str(i+1), font_size=90,
                                background_color=get_color_from_hex('#13ecb9'))
                else:
                    button = RoundedButton(text=str(i+1), font_size=90,
                                background_color=get_color_from_hex('#ff69b4'))
                            
            else:
                if entry:
                    button = RoundedButton(text=str(i+1), font_size=50,
                                background_color=get_color_from_hex('#13ecb9'))
                else:
                    button = RoundedButton(text=str(i+1), font_size=50)
                     
            button.bind(on_press=self.button_pressed)
            self.bottom_row.add_widget(button)

    def button_pressed(self, instance):
        """Create the day-view with a textbox and buttons."""
        
        month = self.get_month_name(self.current_month)
        self.button_nr = instance.text

        # Check, if an entry exists at the chosen date.
        key = self.check_entry(self.button_nr)

        # If saved entry: load the text in the textbox.
        if key:
            content = self.save_file[key]
            text_input = TextInput(text=content, multiline=True)
        else:
            text_input = TextInput(hint_text='Hier ist Platz für Notizen...',
                               multiline=True)
        text_input.bind(text=self.on_text_input)
        
        # Create and bind the cancel, delete and save buttons.
        self.close_button = RoundedButton(text='Close', 
                                background_color=get_color_from_hex('#0a748a'),
                                font_size=48)
        
        self.close_button.bind(on_press=self.close_popup)

        self.save_button = RoundedButton(text='Save', 
                                background_color=get_color_from_hex('#0a748a'),
                                font_size=48)
        
        self.save_button.bind(on_press=self.save_entry)

        self.delete_button = RoundedButton(text='Delete', 
                                background_color=get_color_from_hex('#0a748a'),
                                font_size=48)
        
        # Close popup without confirmation, if no entry is saved.
        entry = self.check_entry(self.button_nr)
        if entry:
            self.delete_button.bind(on_press=self.ask_delete)
        else:
           self.delete_button.bind(on_press=self.close_popup)
    
        # Create the layout of the 'today-view' by stacking the widgets.
        main_box = BoxLayout(orientation='vertical')

        content_box = BoxLayout(orientation='vertical')
        content_box.add_widget(text_input)

        button_box = BoxLayout(orientation='horizontal', size_hint=(1,0.18),
                               spacing=70)
        
        button_box.add_widget(self.close_button)
        button_box.add_widget(self.delete_button)
        button_box.add_widget(self.save_button)
        
        main_box.add_widget(content_box)
        main_box.add_widget(button_box)

        # Create the Popup window with customized content
        self.popup = Popup(title=f'{instance.text}. {month}' + 
                           f' {self.current_year}', content=main_box,
                           size_hint=(0.8, 0.8))
        
        self.popup.background_color = (0,1,1,1)
    
        self.popup.open()
    
    def on_text_input(self, instance, x=None):
        self.entered_text = instance.text
        
    def inc_year(self, x=None):
        # Increase year in main-window.
        self.current_year += 1
        self.update_values()
    
    def dec_year(self, x=None):
        # Decrease year in main-window.
        self.current_year -= 1
        self.update_values()

    def inc_month(self, x=None):
        # Increase month in main-window.
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_values()

    def dec_month(self, x=None):
        # Decrease month in main-window.
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_values()
    
    def check_today(self):
        # Check, if the current date is visible on screen.
        if (self.current_year == datetime.now().year and
            self.current_month == datetime.now().month):
            return True
        return False
    
    def update_values(self):
        """Update the values and the view for the main-window."""
        self.month.text = self.get_month_name(self.current_month)
        self.year.text = f'{self.current_year}'
        self.weeks = self.load_month()
        self.month_lenght = calendar.monthrange(self.current_year,
                                           self.current_month)[1]

        # Remove the existing widgets to load the actualized content.
        self.top_row.clear_widgets()
        self.mid_row.clear_widgets()
        self.bottom_row.clear_widgets()
        self.main_layout.clear_widgets()

        # Update the home-buttons text and binding.
        today = self.check_today()
        if today:
            self.home_button = RoundedButton(text="^", font_size=60,
                                background_color=get_color_from_hex('#50befc'))
            self.home_button.bind(on_press=self.set_date)

        else:
            self.home_button = RoundedButton(text="\u221A", font_size=60,
                                background_color=get_color_from_hex('#50befc'))
            self.home_button.bind(on_press=self.today_view)

        # Recreate rows with updated values.
        self.top_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1),
                                 spacing=40)

        first_row = [self.year_rwd, self.year, self.year_fwd, self.home_button,
                     self.month_rwd, self.month, self.month_fwd]
        for i in first_row:
            self.top_row.add_widget(i)
        
        self.mid_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        for i in self.day_labels:
            self.mid_row.add_widget(i)

        if len(self.weeks) == 4:
            self.bottom_row = GridLayout(cols=7, rows=4, spacing=10)
            self.set_buttons()
        elif len(self.weeks) == 5:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=10)
            self.set_buttons()
        elif len(self.weeks) == 6:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=10)
            self.set_buttons()

        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.mid_row)
        self.main_layout.add_widget(self.bottom_row)
    
    def today_view(self, x=None):
        # Set the current year and month and update the view.
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.update_values()

    def check_entry(self, number):
        # Format the date and check if an entry is saved for the passed day.
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

    def close_popup(self, x=None):
        self.popup.dismiss()

    def delete_entry(self, instance):
        self.close_ask()
        key = self.check_entry(self.button_nr)
        if key:
            del self.save_file[key]
            with open('save_file.json', 'w') as file:
                json.dump(self.save_file, file)
        self.update_values()
        self.close_popup(instance)

    def ask_delete(self, instance):
        # Creates a popup to confirm to delete the entry.
        cancel_button = RoundedButton(text='No',
                                background_color=get_color_from_hex('#0a748a'),
                                font_size=40)
        
        cancel_button.bind(on_press=self.close_ask)

        ok_button = RoundedButton(text='Ok',
                                background_color=get_color_from_hex('#0a748a'),
                                font_size=40)
        
        ok_button.bind(on_press=self.delete_entry)

        main_box = BoxLayout(orientation='vertical')
        button_box = BoxLayout(orientation='horizontal', size_hint=(1,0.4),
                               spacing=30)     
         
        button_box.add_widget(cancel_button)
        button_box.add_widget(ok_button)
        main_box.add_widget(button_box)

        self.ask_popup = Popup(title=f'erase?', content=main_box,
                                size_hint=(0.5, 0.3))
        self.ask_popup.background_color = (0,1,1,1)
    
        self.ask_popup.open()
        
    def close_ask(self, x=None):
        self.ask_popup.dismiss()

    def save_entry(self, instance):
        # Format the date and save the entered text in json safefile.
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
            new_entry = {date: self.entered_text}
            self.save_file.update(new_entry)

            with open('save_file.json', 'w') as file:
                json.dump(self.save_file, file)

        self.entered_text = ''
        self.update_values()
        self.close_popup(instance)
        
    def get_month_name(self, value):
        months = ["Jan", "Feb", "März", "April", "Mai", "Juni", "Juli",
                  "Aug", "Sept", "Okt", "Nov", "Dez"]
            
        return months[value-1]
       
    def get_day_labels(self):
        day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        labels = []

        for i in day_names:
            label = Label(text=f'{i}', font_size=40, color=get_color_from_hex(
                '#03573b'), bold=True)
            labels.append(label)

        return labels
       
    def load_month(self):
        # Get the weeks in lists and get the 1. weekday of the month.
        weeks = calendar.monthcalendar(self.current_year, self.current_month)
        self.week_start = weeks[0].index(1)
        return weeks

    def set_date(self, x=None):
        """Create the set-date view to chose a date and jump to day-view."""

        self.chose_y = self.current_year
        self.chose_m = self.current_month
        self.chose_d = self.current_day

        # Setting up the buttons and labels.
        self.paragraph = Label(text='Select:', font_size=64,
                          color=(0.5,0.75,1,1))
        
        self.y_label = Label(text='Year', font_size=56,
                          color=(0.5,0.75,1,1))
        self.m_label = Label(text='Month', font_size=56,
                          color=(0.5,0.75,1,1))
        self.d_label = Label(text='Day', font_size=56,
                          color=(0.5,0.75,1,1))
        
        self.yr = Label(text=f'{self.chose_y}', font_size=48,
                        color=(0.5,0.75,1,1))
        self.mnt = Label(text=f'{self.month_name}', font_size=48,
                        color=(0.5,0.75,1,1))
        self.dy = Label(text=f'{self.chose_d}', font_size=48,
                        color=(0.5,0.75,1,1))
        
        self.y_fwd = RoundedButton(text="^", font_size=64,
                                background_color=get_color_from_hex('#0a748a'))
        self.y_rwd = RoundedButton(text="v", font_size=46,
                                background_color=get_color_from_hex('#0a748a'))
        self.m_fwd = RoundedButton(text="^", font_size=64,
                                background_color=get_color_from_hex('#0a748a'))
        self.m_rwd = RoundedButton(text="v", font_size=46,
                                background_color=get_color_from_hex('#0a748a'))
        self.d_fwd = RoundedButton(text="^", font_size=64,
                                background_color=get_color_from_hex('#0a748a'))
        self.d_rwd = RoundedButton(text="v", font_size=46,
                                background_color=get_color_from_hex('#0a748a'))
 
        self.cancel = RoundedButton(text="cancel", font_size=56,
                                background_color=get_color_from_hex('#0a748a'))
        self.ok = RoundedButton(text="ok", font_size=56,
                                background_color=get_color_from_hex('#0a748a'))
        
        self.spaceholder_1 = Label(text='', font_size=64, color=(0.5,0.75,1,1))
        self.spaceholder_2 = Label(text='', font_size=64, color=(0.5,0.75,1,1))
        self.spaceholder_3 = Label(text='', font_size=64, color=(0.5,0.75,1,1))
        
        # Button bindings.
        self.y_fwd.bind(on_press=self.inc_y)
        self.y_rwd.bind(on_press=self.dec_y)
        self.m_fwd.bind(on_press=self.inc_m)
        self.m_rwd.bind(on_press=self.dec_m)
        self.d_fwd.bind(on_press=self.inc_d)
        self.d_rwd.bind(on_press=self.dec_d)

        self.cancel.bind(on_press=self.close_setdate)
        self.ok.bind(on_press=self.jump_to)

        # Title for popup.
        self.title_row = self.paragraph

        # Setting up the Layoutboxes for the set-date view.
        self.label_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                   spacing=80)
        labels = [self.y_label, self.m_label, self.d_label]
        for i in labels:
            self.label_row.add_widget(i)
        
        self.fwd_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                 spacing=80)
        fwd_buttons = [self.y_fwd, self.m_fwd, self.d_fwd]
        for i in fwd_buttons:
            self.fwd_row.add_widget(i)

        self.date_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                  spacing=80)
        date_values = [self.yr, self.mnt, self.dy]
        for i in date_values:
            self.date_row.add_widget(i)

        self.rwd_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                 spacing=80)
        rwd_buttons = [self.y_rwd, self.m_rwd, self.d_rwd]
        for i in rwd_buttons:
            self.rwd_row.add_widget(i)
        
        self.button_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                    spacing=80)
        buttons = [self.cancel, self.ok]
        for i in buttons:
            self.button_row.add_widget(i)
        
        self.placeholder_1 = BoxLayout(orientation='horizontal',
                                       size_hint=(1,1))
        self.placeholder_1.add_widget(self.spaceholder_1)

        self.placeholder_2 = BoxLayout(orientation='horizontal',
                                       size_hint=(1,1))
        self.placeholder_2.add_widget(self.spaceholder_2)

        self.placeholder_3 = BoxLayout(orientation='horizontal',
                                       size_hint=(1,1))
        self.placeholder_3.add_widget(self.spaceholder_3)

        # Create the main set-date layout by stacking the Layoutboxes.
        self.setdate_layout = BoxLayout(orientation='vertical')
        self.setdate_layout.add_widget(self.title_row)
        self.setdate_layout.add_widget(self.placeholder_1)
        self.setdate_layout.add_widget(self.label_row)
        self.setdate_layout.add_widget(self.placeholder_2)
        self.setdate_layout.add_widget(self.fwd_row)
        self.setdate_layout.add_widget(self.date_row)
        self.setdate_layout.add_widget(self.rwd_row)
        self.setdate_layout.add_widget(self.placeholder_3)
        self.setdate_layout.add_widget(self.button_row)

        self.setdate_popup = Popup(title=f'Jump to date', content=self.setdate_layout,
                                size_hint=(0.7, 0.8))
        self.setdate_popup.background_color = (0,1,1,1)
        
        self.setdate_popup.open()
    
    def close_setdate(self, x=None):
        self.setdate_popup.dismiss()

    def inc_y(self, x=None):
        # Increase set-date year.
        self.chose_y += 1
        self.update_setdate()

    def dec_y(self, x=None):
        # Decrease set-date year.
        self.chose_y -= 1
        self.update_setdate()
        
    def inc_m(self, x=None):
        # Increase set-date month.
        if self.chose_m == 12:
            self.chose_m = 1
            self.update_setdate()
            return
        self.chose_m += 1
        self.update_setdate()
    
    def dec_m(self, x=None):
        # Decrease set-date month.
        if self.chose_m == 1:
            self.chose_m = 12
            self.update_setdate()
            return
        self.chose_m -= 1
        self.update_setdate()

    def inc_d(self, x=None):
        # Increase set-date day.
        days = self.get_days_in_month(self.chose_y, self.chose_m)[1]
        if self.chose_d >= days:
            self.chose_d = 1
            self.update_setdate()
            return
        self.chose_d += 1
        self.update_setdate()
    
    def dec_d(self, x=None):
        # Decrease set-date day.
        days = self.get_days_in_month(self.chose_y, self.chose_m)[1]
        if self.chose_d <= 1:
            self.chose_d = days
            self.update_setdate()
            return
        self.chose_d -= 1
        self.update_setdate()

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
        self.button_row.clear_widgets()       
        self.placeholder_1.clear_widgets()
        self.placeholder_2.clear_widgets()
        self.placeholder_3.clear_widgets()
        self.setdate_layout.clear_widgets()

        # Check, if day value is possible and correct if not so.
        days = self.get_days_in_month(self.chose_y, self.chose_m)[1]
        if self.chose_d > days or self.chose_d < 1:
            self.chose_d = 1
        
        self.month_name = self.get_month_name(self.chose_m)

        self.yr = Label(text=f'{self.chose_y}', font_size=48,
                          color=(0.5,0.75,1,1))
        self.mnt = Label(text=f'{self.month_name}', font_size=48,
                          color=(0.5,0.75,1,1))
        self.dy = Label(text=f'{self.chose_d}', font_size=48,
                          color=(0.5,0.75,1,1))

        self.label_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                   spacing=80)
        
        labels = [self.y_label, self.m_label, self.d_label]
        for i in labels:
            self.label_row.add_widget(i)
        
        self.fwd_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                 spacing=80)
        
        fwd_buttons = [self.y_fwd, self.m_fwd, self.d_fwd]
        for i in fwd_buttons:
            self.fwd_row.add_widget(i)

        self.date_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                  spacing=80)
        
        date_values = [self.yr, self.mnt, self.dy]
        for i in date_values:
            self.date_row.add_widget(i)

        self.rwd_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                 spacing=80)
        
        rwd_buttons = [self.y_rwd, self.m_rwd, self.d_rwd]
        for i in rwd_buttons:
            self.rwd_row.add_widget(i)
        
        self.button_row = BoxLayout(orientation='horizontal', size_hint=(1,1),
                                    spacing=80)
        
        buttons = [self.cancel, self.ok]
        for i in buttons:
            self.button_row.add_widget(i)
        
        self.placeholder_1 = BoxLayout(orientation='horizontal',
                                       size_hint=(1,1))
        self.placeholder_1.add_widget(self.spaceholder_1)

        self.placeholder_2 = BoxLayout(orientation='horizontal',
                                       size_hint=(1,1))
        self.placeholder_2.add_widget(self.spaceholder_2)

        self.placeholder_3 = BoxLayout(orientation='horizontal',
                                       size_hint=(1,1))
        self.placeholder_3.add_widget(self.spaceholder_3)
        
        self.setdate_layout.add_widget(self.title_row)
        self.setdate_layout.add_widget(self.placeholder_1)
        self.setdate_layout.add_widget(self.label_row)
        self.setdate_layout.add_widget(self.placeholder_2)
        self.setdate_layout.add_widget(self.fwd_row)
        self.setdate_layout.add_widget(self.date_row)
        self.setdate_layout.add_widget(self.rwd_row)
        self.setdate_layout.add_widget(self.placeholder_3)
        self.setdate_layout.add_widget(self.button_row)

    def jump_to(self,x=None):
        # Jump to the chosen date and open the today-view.
        self.close_setdate()
        self.current_year = self.chose_y
        self.current_month = self.chose_m
        self.update_values()
        button = Button(text=f"{self.chose_d}")
        self.button_pressed(button)

    
if __name__ == '__main__':
    CalendarApp().run()