from script import *
import datetime
print "Getting everything again..."
#rockandroll("01/01/2010", "30/06/2010")
print "6 meses..."
#rockandroll("01/07/2010", "31/12/2010")
print "1 ano..."
#rockandroll("01/01/2011", "30/06/2011")

current_date = datetime.datetime(2012, 9, 1)
last_date = datetime.datetime.now()

#erro no mes 8

def everlastingscrape(current_date, last_date):
    trintaum = [1,3,5,7,8,10,12]
    trinta = [4,6,8,9,11]
    if current_date.month in trintaum:
        next_date = current_date + datetime.timedelta(30)
    elif current_date.month in trinta:
        next_date = current_date + datetime.timedelta(29)
    elif current_date.year == 2012:
        next_date = current_date + datetime.timedelta(28)
    else:
        next_date = current_date + datetime.timedelta(27)
    if current_date < last_date:
        print "From " + current_date.strftime("%d/%m/%Y") + " to " + next_date.strftime("%d/%m/%Y")
        rockandroll(current_date.strftime("%d/%m/%Y"),next_date.strftime("%d/%m/%Y"))
        current_date = next_date + datetime.timedelta(1)
        everlastingscrape(current_date, last_date)
    else:
        print "Yay!"

def everlastingloop():
    try:
        carregaIntegras(db)
    except:
        print "Falhou? Tente de novo!"
        everlastingloop()

#everlastingscrape(current_date, last_date)
everlastingloop()
