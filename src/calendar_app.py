from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from datetime import datetime
import calendar
import json


class CalendarApp(App):
    def __init__(self, **kwargs):
        super(CalendarApp, self).__init__(**kwargs)

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.current_day = datetime.now().day

        self.save_file = self.load_json()

        self.month_name = self.get_month_name(self.current_month)

        self.year_rwd = Button(text="<", height=50)
        self.year = Label(text=f'{self.current_year}', font_size=20)
        self.year_fwd = Button(text=">", height=50)

        self.spaceholder = Label(text='', font_size=20)
        self.home_button = Button(text="Home")

        self.month_rwd = Button(text="<", height=50)
        self.month = Label(text=f'{self.month_name}', font_size=20)
        self.month_fwd = Button(text=">", height=50)

        # Bindings for buttons
        self.year_rwd.bind(on_press=self.dec_year)
        self.year_fwd.bind(on_press=self.inc_year)
        self.month_rwd.bind(on_press=self.dec_month)
        self.month_fwd.bind(on_press=self.inc_month)
        self.home_button.bind(on_press=self.today_view)
        
        self.day_labels = self.get_day_labels()
        
        # get the weeks with weekdays in lists
        self.week_start = 0
        self.weeks = self.load_month()

        # get the amount of days for the passed year/month
        self.month_lenght = calendar.monthrange(self.current_year,
                                           self.current_month)[1]
       
        self.entered_text = ''
        self.day_entry = ''  
                
    def build(self):
        # Create the top row of buttons and labels: swithch year/month
        self.top_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1),
                                 spacing=5)
        first_row = [self.year_rwd, self.year, self.year_fwd, self.home_button,
                     self.month_rwd, self.month, self.month_fwd]
        for i in first_row:
            self.top_row.add_widget(i)
        
        # Create middle row to show the days names
        self.mid_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        for i in self.day_labels:
            self.mid_row.add_widget(i)

        # A grid of enumerated buttons, starting at the correct weekday
        if len(self.weeks) == 4:
            self.bottom_row = GridLayout(cols=7, rows=4, spacing=5)
            self.set_buttons()

        elif len(self.weeks) == 5:
            self.bottom_row = GridLayout(cols=7, rows=5, spacing=5)
            self.set_buttons()

        elif len(self.weeks) == 6:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=5)
            self.set_buttons()

        # Create the main layout by stacking the top row, middle row, and grid
        self.main_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.mid_row)
        self.main_layout.add_widget(self.bottom_row)
        self.mark_entries() 

        return self.main_layout
    
    def mark_entries(self):
        for child in self.bottom_row.children:
            # if isinstance(child, Button):
            if len(str(self.current_month)) == 1:
                if len(str(child.text)) == 1:
                    date = f'{self.current_year}0{self.current_month}0{child.text}'
                elif len(str(child.text)) == 2:
                    date = f'{self.current_year}0{self.current_month}{child.text}'

            if len(str(self.current_month)) == 2:
                if len(str(child.text)) == 1:
                    date = f'{self.current_year}{self.current_month}0{child.text}'
                elif len(str(child.text)) == 2:
                    date = f'{self.current_year}{self.current_month}{child.text}'
                    
             # Check if the date key is present in the save file
            if date in self.save_file:
                child.background_color = get_color_from_hex('#13ecb9')  
    
    def load_json(self):
        with open('save_file.json', 'r') as file:
            data = json.load(file)
            return data
    
    def set_buttons(self):
        # Set the placeholder labels to have buttons start at the correct day
        for i in range(self.week_start):
            label = Label(text="")
            self.bottom_row.add_widget(label)

        # Set button-grid
        current_day_visible = self.check_today()
        for i in range(self.month_lenght):
            if current_day_visible and self.current_day == i+1:
                button = Button(text=str(i+1), font_size=50,
                                color=get_color_from_hex('#ec6613') )
            else:
                button = Button(text=str(i+1))
            button.bind(on_press=self.button_pressed)
            self.bottom_row.add_widget(button)
    
    def button_pressed(self, instance):
        # Create a popup window with a textbox.
        month = self.get_month_name(self.current_month)
        self.button_nr = instance.text

        # search if there is saved text
        key = self.check_entry(self.button_nr)
        # if saved text: preload in textbox
        if key:
            content = self.save_file[key]
            text_input = TextInput(text=content, multiline=True)
        else:
            text_input = TextInput(hint_text='Enter your text here...',
                               multiline=True)
        text_input.bind(text=self.on_text_input)
        
        # Create a Button widget to close the popup
        self.close_button = Button(text='Close')
        self.close_button.bind(on_press=self.close_popup)
        self.save_button = Button(text='Save')
        self.save_button.bind(on_press=self.save_entry)
        self.delete_button = Button(text='Delete')
        self.delete_button.bind(on_press=self.ask_delete)
        
        # Create a layout to hold the TextInput and Button widgets
        main_box = BoxLayout(orientation='vertical')

        content_box = BoxLayout(orientation='vertical')
        content_box.add_widget(text_input)

        button_box = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        button_box.add_widget(self.close_button)
        button_box.add_widget(self.delete_button)
        button_box.add_widget(self.save_button)
        
        main_box.add_widget(content_box)
        main_box.add_widget(button_box)

         # Create the Popup window with customized content
        self.popup = Popup(title=f'{instance.text}. {month}' + 
                           f' {self.current_year}', content=main_box,
                           size_hint=(0.8, 0.8))
    
        self.popup.open()

    def check_entry(self, number):
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

    def close_popup(self, instance):
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
        cancel_button = Button(text='Cancel')
        cancel_button.bind(on_press=self.close_ask)
        ok_button = Button(text='OK')
        ok_button.bind(on_press=self.delete_entry)

        main_box = BoxLayout(orientation='vertical')
        button_box = BoxLayout(orientation='horizontal', size_hint=(1,0.1))      
        button_box.add_widget(cancel_button)
        button_box.add_widget(ok_button)
        main_box.add_widget(button_box)

        self.ask_popup = Popup(title=f'erase entry?', content=main_box,
                               size_hint=(0.2, 0.2))
    
        self.ask_popup.open()
    
    def close_ask(self, x=None):
        self.ask_popup.dismiss()

    def on_text_input(self, instance, value):
        self.entered_text = instance.text
        
    def save_entry(self, instance):
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
        self.mark_entries()
        self.close_popup(instance)
        
    def get_month_name(self, value):
        if value == 1:
            return "Januar"
        elif value == 2:
            return "Februar"
        elif value == 3:
            return "März"
        elif value == 4:
            return "April"
        elif value == 5:
            return "Mai"
        elif value == 6:
            return "Juni"
        elif value == 7:
            return "Juli"
        elif value == 8:
            return "August"
        elif value == 9:
            return "September"
        elif value == 10:
            return "Oktober"
        elif value == 11:
            return "November"
        elif value == 12:
            return "Dezember"

    def get_day_labels(self):
        day_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag",
                     "Samstag", "Sonntag"]
        
        labels = []
        for i in day_names:
            label = Label(text=f'{i}', font_size=20)
            labels.append(label)

        return labels
       
    def load_month(self):
        # get the weeks in lists and get the 1. weekday of the month
        weeks = calendar.monthcalendar(self.current_year, self.current_month)
        self.week_start = weeks[0].index(1)
        return weeks

    def update_values(self):
        self.month.text = self.get_month_name(self.current_month)
        self.year.text = f'{self.current_year}'
        self.weeks = self.load_month()
        self.month_lenght = calendar.monthrange(self.current_year,
                                           self.current_month)[1]

        # Clear existing buttons
        self.top_row.clear_widgets()
        self.mid_row.clear_widgets()
        self.bottom_row.clear_widgets()
        self.main_layout.clear_widgets()

        # Recreate rows with updated values.
        self.top_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1),
                                 spacing=5)
        first_row = [self.year_rwd, self.year, self.year_fwd, self.home_button,
                     self.month_rwd, self.month, self.month_fwd]
        for i in first_row:
            self.top_row.add_widget(i)
        
        self.mid_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        for i in self.day_labels:
            self.mid_row.add_widget(i)

        if len(self.weeks) == 4:
            self.bottom_row = GridLayout(cols=7, rows=4, spacing=5)
            self.set_buttons()
        elif len(self.weeks) == 5:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=5)
            self.set_buttons()
        elif len(self.weeks) == 6:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=5)
            self.set_buttons()

        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.mid_row)
        self.main_layout.add_widget(self.bottom_row)

        self.mark_entries()

    def check_today(self):
        # check, if the current date is visible on screen
        if (self.current_year == datetime.now().year and
            self.current_month == datetime.now().month):
            return True
        return False

    def today_view(self, x):
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.update_values()

    def dec_year(self, x):
        self.current_year -= 1
        

    def inc_year(self, x):
        self.current_year += 1
        self.update_values()

    def dec_month(self, x):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_values()
 
    def inc_month(self, x):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_values()
        
    
if __name__ == '__main__':
    CalendarApp().run()