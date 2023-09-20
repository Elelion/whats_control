import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailSend:
    def __init__(self, mail_body, file_path="settings.conf"):
        self.mail_sender_login = ''
        self.mail_sender_password = ''
        self.mail_receiver_address = ''
        self.mail_subject = ''
        self.mail_body = mail_body

        self.settings = {}
        self.settings_loaded = False

        self.file_path = os.path.join(os.path.dirname(__file__), file_path)

        print("MailSend - Загружаем конфиг из:", self.file_path)
        self()

    # загружаем данные из конфига в словарь settings
    def __load_settings(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()  # Удаляем лишние пробелы и символы перевода строки

                if line and not line.startswith('#'):  # Пропускаем пустые строки и комментарии
                    key, value = line.split('=')  # Разделяем ключ и значение
                    key = key.strip()  # Удаляем лишние пробелы в ключе
                    value = value.strip()  # Удаляем лишние пробелы в значении
                    self.settings[key] = value  # Добавляем ключ и значение в словарь settings

            print("Данные успешно загружены из файла")

    # парсим данные по переменным из словаря settings
    def __apply_settings(self):
        self.mail_sender_login = self.settings.get('mail_sender_login')
        self.mail_sender_password = self.settings.get('mail_sender_password')
        self.mail_receiver_address = self.settings.get('mail_receiver_address')
        self.mail_subject = self.settings.get('mail_subject')
        self.settings_loaded = True
        print("Данные успешно применены")

    # отправляем письмо
    def __send_email(self, sender_email, sender_password, receiver_email, subject, body):
        try:
            # Создание объекта MIMEText
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            # Добавление текста письма в объект MIMEText
            msg.attach(MIMEText(body, 'plain'))

            # Установка соединения с SMTP-сервером
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()

            # Авторизация на сервере
            server.login(sender_email, sender_password)

            # Отправка письма
            server.sendmail(sender_email, receiver_email, msg.as_string())

            # Закрытие соединения с сервером
            server.quit()
            print("Письмо успешно отправлено!")
        except Exception as e:
            print("Ошибка при отправке письма:", e)

    # делаем класс ф-цией, так же делаем проверку, если данные уже загружены
    # мы их НЕ загружаем повторно
    def __call__(self):
        if not self.settings_loaded:
            self.__load_settings()
            self.__apply_settings()

        self.__send_email(self.mail_sender_login,
                          self.mail_sender_password,
                          self.mail_receiver_address,
                          self.mail_subject,
                          self.mail_body)