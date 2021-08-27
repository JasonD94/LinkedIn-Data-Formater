import pandas as pd
import sys, math
from datetime import datetime

"""
    This script will take an input (Positions.csv) from LinkedIn which looks something like:
    Company | Title | Description | Location | Started On | Finished On

    And it will automagically calculate the following:
    1. Years of experience at each company
    2. Total Years of Experience combined
"""

default_csv_filename = "csv/Positions.csv"

# the fields we care about
fields = ["Company Name", "Started On", "Finished On"]

filePth = None

try:
    filePth = sys.argv[1]
except:
    print("No cmd args found! Running with default %s file instead.\n" % default_csv_filename)

jobsDF = None

# NOTE: skiprows=3 is to ignore the stupid notes that LinkedIn adds to the csv file!
try:
    if filePth:
        print(filePth)
        jobsDF = pd.read_csv(filePth, usecols=fields, skiprows=3)
    else:
        jobsDF = pd.read_csv(default_csv_filename, usecols=fields)
except Exception as e:
    print("\n\n!!!Error: you need to provide me with a %s file from LinkedIn for me to parse!!\n\n" %
          default_csv_filename)
    print(e)

    # Ye this is apparently not recommended but it doesn't quit the Idle shell on my Windows box so...
    raise SystemExit

totalYearsExp = 0

print("Company".ljust(43), "Start".ljust(8), "End".rjust(7), "Years Exp".rjust(15))

# Now calculate the years of experience!
for index, row in jobsDF.iterrows():

    company = row["Company Name"]
    startedOnParts = str(row["Started On"]).split(" ")
    startedOnMonth = startedOnParts[0]
    startedOnYear = startedOnParts[1]

    # Finished On might be blank if it's your current role we're checking,
    # so we have to handle that edge case by assuming the end of the current
    # month is your "end date" for that job
    if type(row["Finished On"]) == float:
        if math.isnan(row["Finished On"]):
            finishedOnMonth = datetime.now().month
            finishedOnYear = datetime.now().year

    else:
        finishedOnParts = str(row["Finished On"]).split(" ")
        finishedOnMonth = finishedOnParts[0]
        finishedOnYear = finishedOnParts[1]

        datetime_object = datetime.strptime(finishedOnMonth, "%b")
        finishedOnMonth = datetime_object.month

    # Convert "Aug" to 08
    datetime_object = datetime.strptime(startedOnMonth, "%b")
    startedOnMonth = datetime_object.month

    # (shhh this is a very liberal estimate)
    # (also I picked 28 to avoid datetime errors)
    startedOnDate = str(startedOnMonth) + "/01/" + str(startedOnYear)
    finishedOnDate = str(finishedOnMonth) + "/28/" + str(finishedOnYear)

    # total years of experience time!
    startedOnDateObj = datetime.strptime(startedOnDate, "%m/%d/%Y")
    finishedOnDateObj = datetime.strptime(finishedOnDate, "%m/%d/%Y")
    yearsExpDateObj = finishedOnDateObj - startedOnDateObj
    daysExp = yearsExpDateObj.days
    yearsExp = round(daysExp / 365, 2)
    totalYearsExp += yearsExp

    print("%s %s %s      %.2f" % (company.ljust(40), startedOnDate, finishedOnDate.rjust(12), yearsExp))

# FINALLY, we have our number
print("\n\nYou sir/madam have %.2f years of total experience doing whatever it is you do for a living" % totalYearsExp)
