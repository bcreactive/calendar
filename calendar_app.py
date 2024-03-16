from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from datetime import datetime
import calendar


class CalendarApp(App):
    def __init__(self, **kwargs):
        super(CalendarApp, self).__init__(**kwargs)

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.current_day = datetime.now().day

        self.month_name = self.get_month_name(self.current_month)

        self.year_rwd = Button(text="<", height=50)
        self.year = Label(text=f'{self.current_year}', font_size=30)
        self.year_fwd = Button(text=">", height=50)

        self.year_rwd.bind(on_press=self.dec_year)
        self.year_fwd.bind(on_press=self.inc_year)

        self.spaceholder = Label(text='', font_size=30)

        self.month_rwd = Button(text="<", height=50)
        self.month = Label(text=f'{self.month_name}', font_size=30)
        self.month_fwd = Button(text=">", height=50)

        self.month_rwd.bind(on_press=self.dec_month)
        self.month_fwd.bind(on_press=self.inc_month)
        
        self.day_labels = self.get_day_labels()
        
        # get the weeks with weekdays in lists
        self.week_start = 0
        self.weeks = self.load_month()

        # get the amount of days for the passed year/month
        self.month_lenght = calendar.monthrange(self.current_year,
                                           self.current_month)[1]
        
        self.top_row = ""
        self.middle_row = ""
        self.bottom_row = ""
        self.layout = ""
                
    def build(self):
        
        # Create the top row of buttons and labels: swithch year/month
        self.top_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        first_row = [self.year_rwd, self.year, self.year_fwd, self.spaceholder,
                     self.month_rwd, self.month, self.month_fwd]
        for i in first_row:
            self.top_row.add_widget(i)
        
        # Create middle row to show the days names
        self.middle_row = BoxLayout(orientation='horizontal', size_hint=(1,0.1))
        for i in self.day_labels:
            self.middle_row.add_widget(i)

        # A grid of enumerated buttons, starting at the correct weekday
        if len(self.weeks) == 5:
            self.bottom_row = GridLayout(cols=7, rows=5, spacing=5)
            for i in range(self.week_start):
                label = Label(text="")
                self.bottom_row.add_widget(label)
            for i in range(self.month_lenght):
                button = Button(text=str(i+1))
                self.bottom_row.add_widget(button)
        elif len(self.weeks) == 6:
            self.bottom_row = GridLayout(cols=7, rows=6, spacing=5)
            for i in range(self.week_start):
                label = Label(text="")
                self.bottom_row.add_widget(label)
            for i in range(self.month_lenght):
                button = Button(text=str(i+1))
                self.bottom_row.add_widget(button)

        # Create the main layout by stacking the top row, middle row, and grid
        self.main_layout = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.top_row)
        self.main_layout.add_widget(self.middle_row)
        self.main_layout.add_widget(self.bottom_row)

        return self.main_layout

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

    def dec_year(self, x):
        self.current_year -= 1
        
    def inc_year(self, x):
        self.current_year += 1

    def dec_month(self, x):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
            return
        self.current_month -= 1

    def inc_month(self, x):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
            return
        self.current_month += 1

    
if __name__ == '__main__':
    CalendarApp().run()