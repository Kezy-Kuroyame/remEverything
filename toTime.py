import re
import datetime


def toListTime(date_time):
    print(date_time)
    date_time = re.split(r"\W", date_time)
    print(date_time)
    time = f"\n\n[⏰]  *Время:* {date_time[3]}:{date_time[4]}:{date_time[5]} | " \
           f"[📆]  *Дата:* {date_time[2]}/{date_time[1]}/{date_time[0]}\n"

    return time


class TimeMessage:
    def __init__(self, text):
        self.text = text

    def inNormalTime(self):
        valueError = True
        message = str(self.text).lower()
        months = {
            "января": "01",
            "февраля": "02",
            "марта": "03",
            "апреля": "04",
            "мая": "05",
            "июня": "06",
            "июля": "07",
            "августа": "08",
            "сентября": "09",
            "октября": "10",
            "ноября": "11",
            "декабря": "12"
        }
        # hours - 0, minutes - 1, seconds - 2, day - 3, month - 4, year - 5: in list 'time'
        dataTime = datetime.datetime.today()

        if re.search(r'\d\d\W\d\d\W\d\d\d\d', message.split()[0]) is not None:
            date = list(map(int, re.split(r'\W', message.split()[0])))
            dataTime_list = list(map(int, re.split(r'\W', dataTime.strftime("%Y %m %d %H %M %S"))))
            dataTime = datetime.datetime.combine(
                datetime.date(date[2], date[1], date[0]),
                datetime.time(dataTime_list[3], dataTime_list[4], dataTime_list[5]))
            valueError = False

        elif re.search(r'\d\d\d\d\W\d\d\W\d\d', message.split()[0]) is not None:
            date = list(map(int, re.split(r'\W', message.split()[0])))
            dataTime_list = list(map(int, re.split(r'\W', dataTime.strftime("%Y %m %d %H %M %S"))))
            dataTime = datetime.datetime.combine(
                datetime.date(date[0], date[1], date[2]),
                datetime.time(dataTime_list[3], dataTime_list[4], dataTime_list[5]))
            valueError = False

        elif re.search(r'\d\d\W\d\d в', message.split()[0]) is not None:
            date = list(map(int, re.split(r'\W', message.split()[0])))
            dataTime_list = list(map(int, re.split(r'\W', dataTime.strftime("%Y %m %d %H %M %S"))))
            dataTime = datetime.datetime.combine(
                datetime.date(dataTime_list[0], date[1], date[0]),
                datetime.time(dataTime_list[3], dataTime_list[4], dataTime_list[5]))
            valueError = False


        if 'завтра' in message:
            delta = datetime.timedelta(days=1)
            dataTime = (dataTime + delta)
            valueError = False
        elif 'послезавтра' in message:
            delta = datetime.timedelta(days=1)
            dataTime = (dataTime + delta)
            valueError = False

        if 'в ' in message:
            dataTime_list = list(map(int, re.split(r'\W', dataTime.strftime("%Y %m %d %H %M %S"))))

            if 'час' in message:
                dataTime = datetime.datetime.combine(
                    datetime.date(dataTime_list[0], dataTime_list[1], dataTime_list[2]),
                    datetime.time(1, 0, 0))
                valueError = False


            if 'минут' in message:
                minutes = int(message.split(" минут")[0].split()[-1])
                dataTime = datetime.datetime.combine(
                    datetime.date(dataTime_list[0], dataTime_list[1], dataTime_list[2]),
                    datetime.time(dataTime_list[3], minutes, 0))
                valueError = False
            else:
                hourMinutes = re.split(r'\W', message.split('в ')[1])
                valueError = False

                if len(hourMinutes) == 2:
                    hour = int(hourMinutes[0])
                    minutes = int(hourMinutes[1])
                    dataTime = datetime.datetime.combine(
                        datetime.date(dataTime_list[0], dataTime_list[1], dataTime_list[2]),
                        datetime.time(hour, minutes, 0))
                else:
                    hour = int(hourMinutes[0])
                    dataTime = datetime.datetime.combine(
                        datetime.date(dataTime_list[0], dataTime_list[1], dataTime_list[2]),
                        datetime.time(hour, 0, 0))

        if 'через' in message:
            delta = ''
            if 'минуту' in message:
                valueError = False
                delta = datetime.timedelta(minutes=1)
                dataTime = dataTime + delta
            elif 'минут' in message:
                valueError = False
                print(message.split('минут')[0].split()[-1])
                delta = datetime.timedelta(minutes=int(message.split('минут')[0].split()[-1]))
                dataTime = dataTime + delta

            if 'секунд' in message:
                delta = datetime.timedelta(seconds=int(message.split('секунд')[0].split()[-1]))
                dataTime = dataTime + delta
                valueError = False

            if 'часов' in message:
                print(message.split('часов')[0].split()[-1])
                delta = datetime.timedelta(hours=int(message.split('часов')[0].split()[-1]))
                dataTime = dataTime + delta
                valueError = False

            if 'часа' in message:
                valueError = False
                delta = datetime.timedelta(hours=int(message.split('часа')[0].split()[-1]))
                dataTime = dataTime + delta
            elif 'час' in message:
                valueError = False
                delta = datetime.timedelta(hours=1)
                dataTime = dataTime + delta


        if datetime.datetime.today() > dataTime or valueError:
            print("------->ERROR<-------")
            raise ValueError
        else:
            return dataTime

