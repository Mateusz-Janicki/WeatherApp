from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.uic import loadUi
import sys
import requests

api_key = '960001ee3cd72d2a0e47e49f2c1c13f5'

class EmailSender(QMainWindow):
    def __init__(self):
        super(EmailSender, self).__init__()
        loadUi("main.ui", self)

        # Connect the button click event to a function
        self.Check_button.clicked.connect(self.check_city_weather)

    def check_city_weather(self):
        # Get the user input from the City_name QLineEdit
        user_input = self.City_name.text()

        if user_input:
            weather_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={user_input}&units=metric&APPID={api_key}")

            if weather_data.json().get('cod') == 200:
                weather = weather_data.json()['weather'][0]['main']
                temp = round(weather_data.json()['main']['temp'])
                QMessageBox.information(self, "Weather Information", f"Weather in {user_input}: {weather}, Temperature: {temp}°C")
            else:
                QMessageBox.warning(self, "Error", "City not found!")
        else:
            QMessageBox.warning(self, "Error", "Please enter a city name.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmailSender()
    window.show()
    app.exec_()

