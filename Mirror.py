import forecastio
import time
import imaplib
import email
import datetime
import Tkinter

from googlefinance import getQuotes

the_temp, the_time, the_date, the_forecast, the_count, the_email_subject, the_finances = '', '', '', '', '', '', ''
yesterday_closing = None
FONT = 60
FONT_2 = 45

text_file = open("parameters.txt", "r")
parameters = text_file.read().splitlines()
text_file.close()

PASSWORD = parameters[0]
LATITUDE = parameters[1]
LONGITUDE = parameters[2]
FORECAST_IO_API = parameters[3]
SIGNIFICANT_DATE = parameters[4]
STOCK = parameters[5]


class Main(object):
    def __init__(self, master):
        self.master = master
        self.mainframe = Tkinter.Frame(self.master, bg='black')
        self.mainframe.pack(fill=Tkinter.BOTH, expand=True)
        self.build_grid()

        self.create_email_display()
        self.create_count_up()
        self.create_meteorology()
        self.create_finances()
        self.create_date_time()

    def build_grid(self):
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=0)
        self.mainframe.rowconfigure(1, weight=1)
        self.mainframe.rowconfigure(2, weight=0)

    def create_email_display(self):
        self.display_email_subject = Tkinter.Label(self.mainframe, text=the_email_subject)
        self.display_email_subject.grid(row=0, column=0, sticky='nw')

        def change_the_emails():
            global the_email_subject
            mail = initialize_mail_account()
            rv, data = mail.select("INBOX")
            if rv == 'OK':
                latest_email = process_mailbox(mail)
                mail.close()

            if the_email_subject != latest_email:
                the_email_subject = latest_email
                self.display_email_subject.config(
                    text= the_email_subject,
                    font=("Helvetica", FONT_2),
                    bg='black',
                    fg='white',
                    justify='right'
                )
            self.display_email_subject.after(300000, change_the_emails)
        change_the_emails()

    def create_count_up(self):
        self.display_count_up = Tkinter.Label(self.mainframe)
        self.display_count_up.grid(row=1, column=0,sticky='e')

        def change_the_count():
            global the_count
            today = datetime.date.today()

            sig_year = int(SIGNIFICANT_DATE[0:4])
            sig_month = int(SIGNIFICANT_DATE[5:7])
            sig_day = int(SIGNIFICANT_DATE[8:10])
            count_today = (today - datetime.date(sig_year, sig_month, sig_day)).days

            if the_count != count_today:
                the_count = count_today
                count_string = "{0} days with Sarah".format(the_count)
                self.display_count_up.config(
                    text=count_string,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )
            self.display_count_up.after(10800000, change_the_count)
        change_the_count()

    def create_meteorology(self):
        self.display_forecast = Tkinter.Label(self.mainframe)
        self.display_forecast.grid(row=2, column=0, sticky='es')

        def change_forecast_value():
            global the_forecast
            forecast = forecastio.load_forecast(FORECAST_IO_API, LATITUDE, LONGITUDE)

            now = forecast.currently()
            now_forecast = now.summary
            now_temp = now.temperature
            later = forecast.hourly()
            later_forecast = later.summary

            now_later = "{0}C {1} \n {2}".format(int(now_temp), now_forecast, later_forecast)

            if the_forecast != now_later:
                the_forecast = now_later
                self.display_forecast.config(
                    text=now_later,
                    font=("Helvetica", FONT_2),
                    bg='black',
                    fg='white',
                    justify='right',
                    )
            self.display_forecast.after(900000, change_forecast_value)
        change_forecast_value()

    def create_finances(self):
        self.display_finances = Tkinter.Label(self.mainframe)
        self.display_finances.grid(row=1, column=0, sticky='w')

        def change_finance_values():
            global the_finances
            global yesterday_closing

            current_price = float(getQuotes('MUTF_CA:INI220')[0]['LastTradePrice'])

            print datetime.datetime.now().strftime('%H')
            if datetime.datetime.now().strftime('%H') == 00:
                print "Time is 00"
                yesterday_closing = current_price

            if yesterday_closing:
                day_over_day = current_price - yesterday_closing
                if day_over_day >= 0:
                    display_string = "${0} (+{1})".format(current_price, day_over_day)
                else:
                    display_string = "${0} ({1})".format(current_price, day_over_day)
            else:
                display_string = "${0}".format(current_price)

            if the_finances != display_string:
                the_finances = display_string
                self.display_finances.config(
                    text=the_finances,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )

            self.display_finances.after(30*60*60*15, change_finance_values)
        change_finance_values()

    def create_date_time(self):
        self.display_date_time = Tkinter.Label(self.mainframe)
        self.display_date_time.grid(row=0, column=0, sticky='ne')

        def change_time_value():
            global the_time
            new_time = time.strftime('%I:%M:%S \n %b %d, %Y')
            if new_time != the_time:
                the_time = new_time
                self.display_date_time.config(
                    text=the_time,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )

            self.display_date_time.after(999, change_time_value)
        change_time_value()


def initialize_mail_account():
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        M.login('captain.eli.mirror@gmail.com', PASSWORD)
    except imaplib.IMAP4.error:
        print"Error logging into email!"
    return M



def process_mailbox(m):
    output = ""
    rv, data = m.search(None, "ALL")
    if rv != 'OK':
        print "No messages found!"
        return

    for num in reversed(data[0].split()):
        rv, data = m.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message", num
            return

        message = email.message_from_string(data[0][1])
        output += message['Subject']

        return output[0:66]

if __name__ == '__main__':
    root = Tkinter.Tk()
    root.attributes('-fullscreen', True)
    Main(root)
    root.mainloop()