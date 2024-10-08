[//]: # (https://www.whatsminer.com/file/WhatsminerAPI%20V2.0.3.pdf)

[//]: # ([README.md]&#40;README.md&#41;)

[//]: # (---)

# Whats_control

## Описание
Программа для автоматизированного мониторинга Whatsminer's и рассылки 
уведомлений о состоянии устройств (разрабатывалась под Windows)

Данная программа применяется для автоматизированного мониторинга и управления

Имеет сл. возможности:
+ перезагрузка аппарата в случае возникновения ошибок
+ перезагрузка аппарата в случае достижения больших температур
+ уведомление на почту в случае:
    + `лето:` достижения MAX температур на платах `(+79*)` и на входе`(+39*)`
    + `зима:` достижения MIN температур на входе `(+3*)`
    + возникновение любых ошибок
    + просадки по питанию БП `(от 2900w до 3700w)`
    + превышение rejected больше нормы `(100)`

---

## Важно!

+ Для корректной работоспособности программы на компьютере должен быть установлен
[Python](https://www.python.org/downloads/)

+ Переименовать `settings_example.conf` в `settings.conf`

+ Указать в `settings.conf` ВАШ логин / пароль от почты gmail, 
`НО` пароль нужен не от самой почты, а именно от приложения. 
Т.е что бы отправить письмо из нашей программы вам нужно 
предварительно создать специальный логин/пароль для 
[приложений](https://support.google.com/accounts/answer/185833?visit_id=638093045649618309-3914306815&p=InvalidSecondFactor&rd=1)


---

## Настройка


```` 
Важно! 
Структуру файлов/папок - НЕ менять !!!
```` 

Прописать настройки для программы в файле settings.cong на основе ниже
рассмотренных примеров:

+ <b>mail_sender_login</b> - указываем ВАШ логин от почты google, с нее будет
  ийдти рассылка.<br>`Пример: test@gmail.com`
<br>
<br>

+ <b>mail_sender_password</b> - указываем ВАШ 
пароль [приложения](https://support.google.com/accounts/answer/185833?visit_id=638093045649618309-3914306815&p=InvalidSecondFactor&rd=1)

+ <b>mail_receiver_address</b> - адрес, куда будет ийдти наша рассылка 
ИЗ программы
`Пример: test@gmail.com`
<br>

+ <b>mail_subject</b> - тема письма, можно не менять...

+ установить на локальной машине через командную строку: `pip install whatsminer`


---

## Описание модулей
- [MailSend.py](https://github.com/Elelion/whats_control/blob/main/modules/MailSend.py)
модуль для отправки писем операторам

- [NetworkScanner.py](https://github.com/Elelion/whats_control/blob/main/modules/NetworkScanner.py)
модуль для асинхронного сканирования заданных подсетей

- [WhatsminerCheck.py](https://github.com/Elelion/whats_control/blob/main/modules/WhatsminerCheck.py)
модуль для проверки, что передаваемый ip, является whatminer'ом

- [WhatsminerCollectData.py](https://github.com/Elelion/whats_control/blob/main/modules/WhatsminerCollectData.py)
модуль для сбора данных с whatsminer по заданному ip

- [WhatsminerControl.py](https://github.com/Elelion/whats_control/blob/main/modules/WhatsminerControl.py)
модуль для обработки данных, которые были собраны модулем
WhatsminerCollectData.py


[//]: # (### Запуск:)

[//]: # (+ Создаем *.bat файл)

[//]: # (<br>)

[//]: # (  `Пример: py_start_whats_control.bat`)

[//]: # (<br>)

[//]: # (<br>)

[//]: # ()
[//]: # (+ В него прописываем команду на запуск, и путь до нашего сприпта:)

[//]: # (    - > Пример: start C:\whats_control.py)

[//]: # ()
[//]: # (+ Запускаем планировщик Windows, создаем простую задачу, и указываем)

[//]: # (  наш Py_1CSqlBaseBackUp.bat на запуск программы)

[//]: # ()
