import pandas as pd
import sys, datetime

"""
    This script will calculate connections by month/year over time
    based on an input csv called "Connections.csv" that you can get
    from the LinkedIn Data Privacy page
"""

# the fields we care about
fields = ["Connected On"]

filePth = None

try:
    filePth = sys.argv[1]
except:
    print("No cmd args found! Running with default Connections.csv file instead.\n")

# Connections.csv is the default export name for LinkedIn Messages
connectionsDF = None

# NOTE: skiprows=3 is to ignore the stupid notes that LinkedIn adds to the csv file!
try:
    if filePth:
        print(filePth)
        connectionsDF = pd.read_csv(filePth, usecols=fields, skiprows=3)
    else:
        connectionsDF = pd.read_csv("csv/Connections.csv", usecols=fields, skiprows=3)
except Exception as e:
    print("\n\n!!!Error: you need to provide me with a Connections.csv file from LinkedIn for me to parse!!\n\n")
    print(e)

    # Ye this is apparently not recommended but it doesn't quit the Idle shell on my Windows box so...
    raise SystemExit

# Filter for unique senders
connectionsDF = connectionsDF.drop_duplicates(subset = ["Connected On"])

# Dictionary for counting, printing & saving data off to CSV later on
connectionsDates = {}

# Pandas dataframe for exporting back to csv
exportedConnectionsDF = pd.DataFrame(columns = ["MONTH_YEAR", "COUNT"])

# Group it ourselves based on year and month.
for index, row in connectionsDF.iterrows():

    # This looks like "25 Aug 2021" in the CSV file
    dateSplit = str(row["Connected On"]).split(" ")

    month_name = dateSplit[1]
    year = dateSplit[2]
    
    # Convert "Aug" to 08
    datetime_object = datetime.datetime.strptime(month_name, "%b")
    month_number = datetime_object.month

    datePart = str(month_number) + "/01/" + year
    if datePart in connectionsDates:
        connectionsDates[datePart] += 1

    else:
        connectionsDates[datePart] = 1

# Print Month/Year: Count
# Also builds up the exportedConnectionsDF at the same time
for date in sorted(connectionsDates):
    print(date + ": " + str(connectionsDates[date]))
    exportedConnectionsDF = exportedConnectionsDF.append({"MONTH_YEAR": date, "COUNT": connectionsDates[date]},
                                                         ignore_index=True)

# Should be good to export exportedConnectionsDF to csv now
try:
    exportedConnectionsDF.to_csv("analyzed/connections_analyzed.csv", sep=",")
except:
    print("\n\n¡¡¡ERROR: Close the damn file you dummy!!!\n\n")


