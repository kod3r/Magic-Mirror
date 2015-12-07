import forecastio
import time
import imaplib
import email
from yahoo_finance import Share
from Tkinter import *
from datetime import date

the_temp = ''
the_time = ''
the_date = ''
the_forecast = ''
the_count = ''
the_email_subject = ''
the_financials = ''

ELI_SARAH_DATE = date(2013, 11, 10)
FONT = 60
PASSWORD = ''
LONGITUDE = 122
LATITUDE = 49
FORECASTIO_API = ''

forecast = forecastio.load_forecast(FORECASTIO_API, LATITUDE, LONGITUDE)

mutual_fund_price = Share('F000000S68.TO')

M = imaplib.IMAP4_SSL('imap.gmail.com')
try:
    M.login('captain.eli.mirror@gmail.com', PASSWORD)
except imaplib.IMAP4.error:
    print"Error logging into email!"


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

        return output


class Main:
    def __init__(self, master):
        self.master = master
        self.mainframe = Frame(self.master, bg='black')
        self.mainframe.pack(fill=BOTH, expand=True)
        self.build_grid()
        self.create_widgets()
        self.build_meteorology()
        self.build_counter()
        self.build_emails()
        self.build_financials()

    def build_grid(self):
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=0)
        self.mainframe.rowconfigure(1, weight=0)
        self.mainframe.rowconfigure(2, weight=0)
        self.mainframe.rowconfigure(3, weight=1)
        self.mainframe.rowconfigure(4, weight=0)
        self.mainframe.rowconfigure(5, weight=0)

    def build_emails(self):
        self.display_email_subject = Label(self.mainframe, text=the_email_subject)
        self.display_email_subject.grid(
            row=0, column=0,
            sticky='w'
        )

        def change_the_emails():
            global the_email_subject
            latest_email = ''
            rv, data = M.select("INBOX")
            if rv == 'OK':
                latest_email = process_mailbox(M)
                M.close()

            if the_email_subject != latest_email:
                the_email_subject = latest_email
                self.display_email_subject.config(
                    text= the_email_subject,
                    font=("Helvetica", 26),
                    bg='black',
                    fg='white',
                    justify='right'
                )

            self.display_email_subject.after(300000, change_the_emails)
        change_the_emails()

    def build_financials(self):
        self.display_financials = Label(self.mainframe, text=the_financials)
        self.display_financials.grid(
            row=3, column=0,
            sticky='w'
        )

        def change_the_financials():
            global the_financials
            latest_data = mutual_fund_price.get_price()
            if the_financials != latest_data:
                the_financials = latest_data
                self.display_financials.config(
                    text=the_financials,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )
            self.display_financials.after(1000*60*60*15, change_the_financials)
        change_the_financials()

    def build_counter(self):
        self.display_count = Label(self.mainframe, text=the_count)
        self.display_count.grid(
            row=5, column=0,
            sticky='w'
        )

        def change_the_count():
            global the_count
            today = date.today()
            count_today = (today - ELI_SARAH_DATE).days
            if the_count != count_today:
                the_count = count_today
                count_string = str(the_count) + " days with Sarah"
                self.display_count.config(
                    text=count_string,
                    font=("Helvetica", 30),
                    bg='black',
                    fg='white',
                    justify='right'
                )
            self.display_time.after(10800000, change_the_count)
        change_the_count()

    def build_meteorology(self):
        self.display_temp = Label(self.mainframe, text=the_temp)
        self.display_temp.grid(
            row=4, column=0,
            sticky='es'
        )
        self.display_forecast = Label(self.mainframe, text=the_forecast)
        self.display_forecast.grid(
            row=5, column=0,
            sticky = 'es'
        )

        def change_value_the_temp():
            global the_temp
            now = forecast.currently()
            new_temp = now.temperature
            if new_temp != the_temp:
                the_temp = new_temp
                this_string = str(int(the_temp)) + "C"
                self.display_temp.config(
                    text=this_string,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )
            self.display_time.after(300000, change_value_the_temp)
        change_value_the_temp()

        def change_value_the_forecast():
            global the_forecast
            now = forecast.currently()
            new_forecast = now.summary

            print new_forecast

            if new_forecast != the_forecast:
                the_forecast = new_forecast
                self.display_forecast.config(
                    text=the_forecast,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right',
                )
            self.display_forecast.after(900000, change_value_the_forecast)
        change_value_the_forecast()

    def create_widgets(self):
        self.display_time = Label(self.mainframe, text=the_time)
        self.display_time.grid(
            row=1, column=0,
            sticky='e'
        )

        self.display_date = Label(self.mainframe, text=the_date)
        self.display_date.grid(
            row=0, column=0,
            sticky='e'
                               )

        def change_value_the_date():
            global the_date
            new_date = time.strftime("%b %d").upper()
            if new_date != the_date:
                the_date = new_date
                self.display_date.config(
                    text=the_date,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )

            self.display_time.after(10800000, change_value_the_date)
        change_value_the_date()

        def change_value_the_time():
            global the_time
            new_time = time.strftime('%I:%M:%S')
            if new_time != the_time:
                the_time = new_time
                self.display_time.config(
                    text=the_time,
                    font=("Helvetica", FONT),
                    bg='black',
                    fg='white',
                    justify='right'
                )

            self.display_time.after(999, change_value_the_time)
        change_value_the_time()


if __name__ == '__main__':
    root = Tk()
    root.attributes('-fullscreen', True)
    Main(root)
    root.mainloop()