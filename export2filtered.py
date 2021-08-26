import pandas as pd
import sys

"""
        This script will automagically generate a nice little report for LinkedIn
        Data exports. Starting with just messages, since I'm particularly interested
        in how many messages per month / year I've gotten. But will later analysis
        some other data that is provided, such as:
        
        - Invitations
        - Contacts
        - Connections
        - Profile
        - Recommendations
"""

"""
    As of 8/25/2021, this is what the LinkedIn messages.csv export file looks like:
    CONVERSATION ID, CONVERSATION TITLE, FROM, SENDER PROFILE, URL, TO, DATE, SUBJECT, CONTENT, FOLDER

    (Note: it's actually tabbed based and not comma based, but commas are easier for displaying here)

    I want to filter by FROM on unique values, and generate a count of unique senders.
    Then I want to filter that down by month and year.
"""

# the fields we care about
fields = ["FROM", "DATE", "FOLDER"]

filePth = None

try:
    filePth = sys.argv[1]
except:
    print("No cmd args found! Running with default messages.csv file instead.\n")

# Messages.csv is the default export name for LinkedIn Messages
messagesDF = None

try:
    if filePth:
        print(filePth)
        messagesDF = pd.read_csv(filePth, usecols=fields)
    else:
        messagesDF = pd.read_csv("messages.csv", usecols=fields)
except:
    print("\n\n!!!Error: you need to provide me with a messages.csv file from LinkedIn for me to parse!!\n\n")

    # Ye this is apparently not recommended but it doesn't quit the Idle shell on my Windows box so...
    raise SystemExit

# Filter for unique senders
messagesDF = messagesDF.drop_duplicates(subset = ["FROM"])

# Convert the "DATE" column from a string(object) to a datetime,
# so we can use groupbys later
messagesDF["DATE"] = pd.to_datetime(messagesDF["DATE"])

# Report should be something like:
# Message Count
# July, 2021: 200
# August, 2021: 300
# etc

# Group by months
# This seemed to cause errors, so just going to do it manually with a loop.
# Only ~500 rows at the moment so probably fine and just as fast as whatever
# pandas does under the hood.
#monthsDF = messagesDF["DATE"].groupby(pd.Grouper(freq="M"))
#monthsDF = messagesDF["DATE"].resample("M", how='sum')

# Dictionary for ezpz printing
mapDates = {}
# Might be cool to group by year as well
mapYearDates = {}
# Filter by spam vs archive vs inbox too
inboxYearDates = {}

# Pandas dataframes for exporting back to CSV
exportedDF = pd.DataFrame(columns = ["YEAR", "MONTH", "MONTH_YEAR", "COUNT"])
exportedFolderdDF = pd.DataFrame(columns = ["YEAR", "MONTH", "MONTH_YEAR", "FOLDER", "COUNT"])

# Group it ourselves based on year and month.
for index, row in messagesDF.iterrows():

    # Split the date, then we can group by YEAR_MONTH
    dateSplit = str(row["DATE"]).split("-")
    datePart = dateSplit[0] + "/" + dateSplit[1]

    # Also check the mapYearDates one too for YEAR : Count
    yearDatePart = dateSplit[0]
    if yearDatePart in mapYearDates:
        mapYearDates[yearDatePart] += 1
    else:
        mapYearDates[yearDatePart] = 1

    # This one will check for the FOLDER value. The following values exist in my exported data:
    # INBOX
    # ARCHIVE
    # SPAM
    # We'll group by those 3 for the counts and break it out by just Inbox in the report in
    # the console, but we'll also save off that value for later too
    folder = str(row["FOLDER"])
    folderDataPart = dateSplit[0] + "/" + dateSplit[1] + "_" + folder
    
    if folderDataPart in inboxYearDates:
        inboxYearDates[folderDataPart] += 1
    else:
        inboxYearDates[folderDataPart] = 1

    #
    #   Thinking we just filter out spam/archive messages for the main analyzed csv
    #   Reason being, looking at the inbox_analyzed csv, there's something like ~50 messages
    #   that I marked spam/archived. Might as well ignore those, since they weren't useful
    #   LinkedIn messages after all!
    #
    if folder == "SPAM" or folder == "ARCHIVE":
        # Skip counting these ones. In the future, perhaps add a flag of sorts
        # to let people decide for themselves to count these messages or not.
        continue

    # See if the given YEAR_MONTH is inside our map.
    if datePart in mapDates:
        mapDates[datePart] += 1

    else:
        mapDates[datePart] = 1
    

# Generate pandas Dataframe to export back to CSV for later looking
for date in sorted(mapDates):
    dateSplit = date.split("/")

    # dateSplit[0] == year, dateSplit[1] == month
    year = dateSplit[0]
    month = dateSplit[1]
    month_year = str(dateSplit[0]) + "/" + str(dateSplit[1])

    exportedDF = exportedDF.append({'YEAR': year, 'MONTH': month, 'MONTH_YEAR': month_year,
                                    'COUNT': mapDates[date]}, ignore_index=True)

# Export a second csv with counts by MONTH_YEAR and FOLDER
# TODO: merge these into one single CSV file, or perhaps separate worksheets?
#       maybe pandas lets us export to .xls or .xlsx


# For giggles, how many spam vs inbox messages did I get each year too?
# Should try to sum that up too
# Or can do that easily in Excel with this exported!

for dateFolder in sorted(inboxYearDates):
    folderDataPart = dateFolder.replace("/", "_").split("_")
    year = folderDataPart[0]
    month = folderDataPart[1]
    month_year = year + "_" + month
    folder = folderDataPart[2]

    # Some debug prints; TODO: delete these when done
    print(year, month, folder, end=" ")
    print(inboxYearDates[dateFolder])

    exportedFolderdDF = exportedFolderdDF.append({'YEAR': year, 'MONTH': month, 'MONTH_YEAR': month_year,
                                    'FOLDER': folder, 'COUNT': inboxYearDates[dateFolder]}, ignore_index=True)

print("\n")

# Now mapDates should have a nice count for us!
# Let's pretty print it and sort it too
print("YEAR_MONTH: COUNT")
for date in sorted(mapDates):
    print(date + ": " + str(mapDates[date]))

print("\n")

# Also print YEAR: Count too
print("YEAR: COUNT")
for year in sorted(mapYearDates):
    print(year + ": " + str(mapYearDates[year]))

# This is in a try/except because if the file is open,
# you'll get a permission denied error :-)
try:
    exportedDF.to_csv('messages_analyzed.csv', sep=',')

except:
    print("\n\n¡¡¡ERROR: Close the damn file you dummy!!!\n\n")

try:
    exportedFolderdDF.to_csv('messages_inbox_analyzed.csv', sep=",")

except:
    print("\n\nERROR: something went wrong exporting messages_inbox_analyzed.csv!")
