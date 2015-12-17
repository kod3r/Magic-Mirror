import forecastio
import time
import imaplib
import email
import datetime
import Tkinter
from googlefinance import getQuotes

FONT = 60
FONT_2 = 45
FONT_3 = 30

with open("parameters.txt", "r") as text_file:
    parameters = text_file.read().splitlines()

PASSWORD = parameters[0]
LATITUDE = parameters[1]
LONGITUDE = parameters[2]
FORECAST_IO_API = parameters[3]
SIGNIFICANT_DATE = parameters[4]
STOCK = parameters[5]
EMAIL = parameters[6]


# noinspection PyAttributeOutsideInit
class Main(object):
    """ Builds a Tkinter object and fills its grid with 5 strings using the
    methods: create_email_display, create_count_up, create_meteorology,
    create_finances and create_date_time """
    def __init__(self, master):
        self.master = master
        self.mainframe = Tkinter.Frame(self.master, bg='black')
        self.mainframe.pack(fill=Tkinter.BOTH, expand=True)
        self.build_grid()

        self.the_finances = None
        self.the_date_time = None
        self.yesterday_closing = 13.04
        self.the_forecast = None
        self.the_count = None
        self.the_email_subject = None

        self.create_email_display()
        self.create_count_up()
        self.create_meteorology()
        self.create_finances()
        self.create_date_time()

    def build_grid(self):
        """ Builds a 2 column x 3 row grid for the display"""
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=0)
        self.mainframe.rowconfigure(1, weight=1)
        self.mainframe.rowconfigure(2, weight=0)

    def create_email_display(self):
        """ Creates a Tkinter label where email data can be displayed """
        self.display_email_subject = Tkinter.Label(self.mainframe)
        self.display_email_subject.grid(row=0, column=0, sticky='nw')

        def change_the_emails():
            """ Invokes methods to make sure the latest email is dislpayed """

            mail = initialize_mail_account(EMAIL, PASSWORD)
            rv, data = mail.select("INBOX")
            latest_email = None
            if rv == 'OK':
                latest_email = process_mailbox(mail)
                mail.close()

            if self.the_email_subject != latest_email:
                self.the_email_subject = latest_email
                self.display_email_subject.config(
                    text=self.the_email_subject,
                    font=("Helvetica", FONT_2),
                    bg='black',
                    fg='white',
                    justify='right'
                )
            self.display_email_subject.after(300000, change_the_emails)
        change_the_emails()

    def create_count_up(self):
        """ Creates Label to display 'days since event' """
        self.display_count_up = Tkinter.Label(self.mainframe)
        self.display_count_up.grid(row=1, column=0, sticky='e')

        def change_the_count():
            today = datetime.date.today()

            sig_year = int(SIGNIFICANT_DATE[0:4])
            sig_month = int(SIGNIFICANT_DATE[5:7])
            sig_day = int(SIGNIFICANT_DATE[8:10])
            count_today = (today - datetime.date(sig_year, sig_month, sig_day)).days

            if self.the_count != count_today:
                self.the_count = count_today
                count_string = "{0} days with Sarah".format(self.the_count)
                self.display_count_up.config(
                    text=count_string,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )
            self.display_count_up.after(10800000, change_the_count)
        change_the_count()

    def create_meteorology(self, font=FONT_3):
        """ Makes label that includes temperature, weather and forecast
        :param font: Can be changed to an int if not fitting on display """
        self.display_forecast = Tkinter.Label(self.mainframe)
        self.display_forecast.grid(row=2, column=0, sticky='es')

        def change_forecast_value():
            """ Gets the most recent forecast/weather """
            forecast = forecastio.load_forecast(FORECAST_IO_API, LATITUDE, LONGITUDE)

            now = forecast.currently()
            now_forecast = now.summary
            now_temp = now.temperature

            later = forecast.hourly()
            later_forecast = later.summary

            now_later_string = "{0}C {1} \n {2}".format(int(now_temp), now_forecast, later_forecast)

            if self.the_forecast != now_later_string:
                self.the_forecast = now_later_string
                self.display_forecast.config(
                    text=now_later_string,
                    font=("Helvetica", font),
                    bg='black',
                    fg='white',
                    justify='right',
                    )
            self.display_forecast.after(900000, change_forecast_value)
        change_forecast_value()

    def create_finances(self):
        """ Makes the Label for the financial information """
        self.display_finances = Tkinter.Label(self.mainframe)
        self.display_finances.grid(row=1, column=0, sticky='w')

        def change_finance_values():
            """ Uses the Google Finance API to get most recent data. """
            current_price = float(getQuotes('MUTF_CA:INI220')[0]['LastTradePrice'])

            if datetime.datetime.now().strftime('%H') == 00:
                print "Time is 00"
                self.yesterday_closing = current_price

            if self.yesterday_closing:  # could be initialized to None
                day_over_day = current_price - self.yesterday_closing
                if day_over_day >= 0:
                    display_string = "${0} (+{1})".format(current_price, day_over_day)
                else:
                    display_string = "${0} ({1})".format(current_price, day_over_day)
            else:
                display_string = "${0}".format(current_price)

            if self.the_finances != display_string:
                self.the_finances = display_string
                self.display_finances.config(
                    text=self.the_finances,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )

            self.display_finances.after(30*60*60*15, change_finance_values)
        change_finance_values()

    def create_date_time(self):
        """ Makes the label for displaying date, time. """
        self.display_date_time = Tkinter.Label(self.mainframe)
        self.display_date_time.grid(row=0, column=0, sticky='ne')

        def change_time_value():
            """ This gets the system time and date and changes it. It updates
            every second. """
            new_date_time = time.strftime('%I:%M:%S \n %b %d, %Y')
            if self.the_date_time != new_date_time:
                self.the_date_time = new_date_time
                self.display_date_time.config(
                    text=self.the_date_time,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )

            self.display_date_time.after(1000, change_time_value)
        change_time_value()


def initialize_mail_account(email_address, password):
    """ Logs into a gmail account, given login information. """
    m = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        m.login(email_address, password)
    except imaplib.IMAP4.error:
        print"Error logging into email!"
    return m


def process_mailbox(m):
    """ Accessing a mail account to get subject from most recent email.
    :param m: A mailbox, in this case from initialize_mail_account() function.
    :return: The subject from the most recent email in inbox, a string. """
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

        return output[0:66]  # length limit

if __name__ == '__main__':
    root = Tkinter.Tk()
    root.attributes('-fullscreen', True)
    Main(root)
    root.mainloop()
