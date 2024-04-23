import json
from datetime import datetime

current_month = 1
button_nr = 2
current_year = 2024

entered_text = "jhfghogafhoif"

def load_json():
        # Load savefile.
        with open('save_file_new.json', 'r') as file:
            data = json.load(file)
            return data

def save_entry():
    # Format the date and save the entered text in json safefile.
    month = len(str(current_month))
    day = len(str(button_nr))   
    if month == 1 and day == 1:
        date = f'{current_year}0{current_month}0{button_nr}'
    elif month == 1 and day == 2:
        date = f'{current_year}0{current_month}{button_nr}'
    elif month == 2 and day == 1:
        date = f'{current_year}{current_month}0{button_nr}'
    else:
        date = f'{current_year}{current_month}{button_nr}'
    
    if entered_text:
        # if date in save_file:
        #     entries = save_file.get(date)
            # if content:
        #         entries.remove(content)
        #     entries.append(entered_text)
        #     entries.reverse()
            #  save_file[date] = entries
        if not date in save_file:
            new_entry = {date : entered_text}
        #     new_entry = {date: [entered_text]}
            save_file.update(new_entry)

        with open('save_file_new.json', 'w') as file:
            json.dump(save_file, file)

def delete_entry(self, instance):
    key = "20240101"
    if key:
        entries = self.save_file.get(key)
        entries.pop(instance.btn_nr - 1)  
        if entries:  
            save_file[key] = entries
        else: 
            del save_file[key]
            
        with open('save_file_new.json', 'w') as file:
            json.dump(save_file, file)


save_file = load_json()
save_entry()
print(save_file)