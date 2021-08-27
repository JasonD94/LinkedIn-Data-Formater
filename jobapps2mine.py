import pandas as pd
import sys, datetime

"""
    This script will calculate job applications by month/year over time
    based on an input csv called "Job Applications.csv" that you can get
    from the LinkedIn Data Privacy page
"""
default_csv_filename = "csv/Job Applications.csv"
app_date_column_name = "Application Date"

# the fields we care about
fields = [app_date_column_name]

filePth = None

try:
    filePth = sys.argv[1]
except:
    print("No cmd args found! Running with default %s file instead.\n" % default_csv_filename)

jobsAppsDF = None

# NOTE: skiprows=3 is to ignore the stupid notes that LinkedIn adds to the csv file!
try:
    if filePth:
        print(filePth)
        jobsAppsDF = pd.read_csv(filePth, usecols=fields, skiprows=3)
    else:
        jobsAppsDF = pd.read_csv(default_csv_filename, usecols=fields)
except Exception as e:
    print("\n\n!!!Error: you need to provide me with a %s file from LinkedIn for me to parse!!\n\n" %
          default_csv_filename)
    print(e)

    # Ye this is apparently not recommended but it doesn't quit the Idle shell on my Windows box so...
    raise SystemExit

# Dictionary for counting, printing & saving data off to CSV later on
applicationDates = {}

# Pandas dataframe for exporting back to csv
exportedjobsAppsDF = pd.DataFrame(columns = ["MONTH_YEAR", "COUNT"])

# Group it ourselves based on year and month.
for index, row in jobsAppsDF.iterrows():

    # This looks like "6/11/17, 10:19 PM" in the CSV file
    dateSplit = str(row[app_date_column_name]).split(",")
    dateSplit = dateSplit[0]            # disregard the time stuff
    dateSplit = dateSplit.split("/")    # Split again to get month/year

    month = dateSplit[0]
    year = dateSplit[2]

    datePart = month + "/01/" + year
    if datePart in applicationDates:
        applicationDates[datePart] += 1

    else:
        applicationDates[datePart] = 1

# Print Month/Year: Count
# Also builds up the exportedConnectionsDF at the same time
for date in sorted(applicationDates):
    print(date + ": " + str(applicationDates[date]))
    exportedjobsAppsDF = exportedjobsAppsDF.append({"MONTH_YEAR": date, "COUNT": applicationDates[date]},
                                                     ignore_index=True)

# Should be good to export exportedConnectionsDF to csv now
try:
    exportedjobsAppsDF.to_csv("analyzed/job_apps_analyzed.csv", sep=",")
except:
    print("\n\n¡¡¡ERROR: Close the damn file you dummy!!!\n\n")
