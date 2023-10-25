from PyQt5.QtWidgets import QMainWindow, QApplication, QComboBox, QCompleter, QLineEdit, QDialog, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
import sys
import requests
import sqlite3
from PyQt5.QtGui import QIcon
from datetime import datetime

api_key = '960001ee3cd72d2a0e47e49f2c1c13f5'

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("main.ui", self)

        self.cityComboBox = self.findChild(QComboBox, "CityComboBox")
        self.cityLineEdit = QLineEdit(self)
        self.cityComboBox.setLineEdit(self.cityLineEdit)

        self.conn = sqlite3.connect("weather.db")
        self.cursor = self.conn.cursor()

        self.city_data = self.retrieve_city_data()

        self.conn.close()

        self.city_names = []
        self.city_data_dict = {}
        for city_id, city_name, country_code in self.city_data:
            display_text = f"{city_name}, {country_code}"
            self.cityComboBox.addItem(display_text)
            self.city_names.append(display_text)
            self.city_data_dict[display_text] = city_id

        completer = QCompleter(self.city_names, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.cityLineEdit.setCompleter(completer)

        self.second_window = None

        self.Check_button = self.findChild(QPushButton, "Check_button")
        self.Check_button.clicked.connect(self.open_second_window)

    def retrieve_city_data(self):
        self.cursor.execute("SELECT id, name, country FROM cities GROUP BY name, country")
        return self.cursor.fetchall()

    def open_second_window(self):
        selected_city_text = self.cityComboBox.currentText()
        selected_city_id = self.city_data_dict.get(selected_city_text)

        if selected_city_id is not None:
            weather, temp, weather_condition = self.get_weather_data(selected_city_id)
            weather_icon_url = self.get_weather_icon_url(weather_condition)
            city_name = selected_city_text

            self.second_window = SecondWindow(weather, temp, weather_icon_url, city_name)
            self.second_window.SaveButton.clicked.connect(self.save_to_text_file)
            self.second_window.show()
        else:
            QMessageBox.warning(self, "Błąd", "Proszę wybrać miasto z listy.")

    def get_weather_data(self, city_id):
        try:
            weather_data = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&units=metric&APPID={api_key}")
            if weather_data.status_code == 200:
                weather_json = weather_data.json()
                if 'weather' in weather_json and 'main' in weather_json:
                    weather = weather_json['weather'][0]['main']
                    temp = round(weather_json['main']['temp'])
                    return weather, temp, weather
                else:
                    print("Nieprawidłowe dane API")
            else:
                print(f"Błąd statusu API: {weather_data.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"RequestException: {str(e)}")

    def get_weather_icon_url(self, weather_condition):
        weather_icons = {
            "Clear": "clear.png",
            "Few clouds": "few_clouds.png",
            "Scattered clouds": "scattered_clouds.png",
            "Broken clouds": "broken_clouds.png",
            "Shower rain": "shower_rain.png",
            "Rain": "rain.png",
            "Thunderstorm": "thunderstorm.png",
            "Snow": "snow.png",
            "Mist": "mist.png",
            "Clouds": "few_clouds.png"
        }
        return weather_icons.get(weather_condition, "")

    def save_to_text_file(self):
        selected_city_text = self.cityComboBox.currentText()
        selected_city_id = self.city_data_dict.get(selected_city_text)

        if selected_city_id is not None:
            weather, temp, weather_condition = self.get_weather_data(selected_city_id)
            city_name = selected_city_text

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            filename = "myMeasurements.txt"  # Nazwa pliku, w którym będą zapisywane dane

            text_content = f"City: {city_name}\nWeather: {weather}\nTemperature: {temp} degree Celsius\nMeasurement time: {timestamp}\n\n"

            with open(filename, 'a') as file:  # Użyj trybu "a" dla dopisywania
                file.write(text_content)

            QMessageBox.information(self, "Saved", f"Data was saved to: {filename}")
        else:
            QMessageBox.warning(self, "Error", "Please select city from the list :)")

class SecondWindow(QDialog):
    def __init__(self, weather, temp, weather_icon_url, city_name):
        super(SecondWindow, self).__init__()
        loadUi("second.ui", self)
        self.weather_label = self.findChild(QLabel, "WeatherLabel")
        self.temperature_label = self.findChild(QLabel, "TemperatureLabel")
        self.weather_icon_label = self.findChild(QLabel, "WeatherIconLabel")
        self.measurement_time_label = self.findChild(QLabel, "MeasurementTimeLabel")
        self.town_name_label = self.findChild(QLabel, "TownNameLabel")
        self.SaveButton = self.findChild(QPushButton, "SaveButton")

        self.weather_label.setText(f"Weather: {weather}")
        self.temperature_label.setText(f"Temperature: {temp}°C")
        self.measurement_time_label.setText(f"Measurement time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.town_name_label.setText(f"City: {city_name}")

        pixmap = QPixmap(weather_icon_url)
        self.weather_icon_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())