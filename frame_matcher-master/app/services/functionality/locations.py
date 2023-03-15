# Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
# from Keith Finlay and Elizabeth Willhide.
import math
import pandas as pd
import os
import subprocess

def col_set(frame):
    isfulladdress = input("Do the column's frames make up a full street address?")
    if isfulladdress:
        line1input = input(
            'Enter the column names that make up the first line of the address; for example, if it were spread across STREETNUM, STREET_NAME, and STREET_TYPE you should enter: "STREETNUM" "STREET_NAME" "STREET_TYPE"')
        line1cols = line1input.split(" ")
        frame()
    # loc_cols = input(
    #     'Which of the columns contain information about location? Enter a list of column names spelled precisely with quotes around them (for example, ["FACILITYSTREET", "FACILITYZIP", "FACILITYSTATE"])')
    # for col in loc_cols:
    #     print(
    #         "What types of address information are contained in column " + col + " and in what format? Encode in the following way:")
    #     print("      Address number: ADDNUM        ex. 148")
    #     print("      Street name:    STREETNAME    ex. MAIN STREET")
    #     print("      Second line:    SECLINE       ex. APT 210")
    #     print("      City:           CITY          ex. NEWTON")
    #     print("      State:          STATE         ex. AL")
    #     print("      ZIP (5 digits): ZIP5          ex. 01234")
    #     print("      ZIP (9 digits): ZIP9          ex. 01234-5678")
    #     colfields = input(
    #         "Enter the data format using those encodings; for example, 100 MAIN ST, NEWTON, AL would be ADDNUM STREETNAME, CITY, STATE")
    #     spacelocs = re.findall(" ", colfields).groups()

def batch_lookup(frame, id, streetadd, city, state, zip):
    #standardize address input format and lookup addresses
    #return frame, zips, coord1s, coord2s
    relevant = frame[[id, streetadd, city, state, zip]]
    numrows = len(frame.index)
    batches = [relevant.iloc[10000*i:10000*(i+1)] for i in range(0, 1 + numrows//10000)]
    for i in range(1, len(batches)+1):
        batch = batches[i-1]
        batch.to_csv("batch_"+str(i)+"_geocoder_input.csv", index=False)
        # curl --form addressFile =@localfile.csv --form benchmark=4
        requeststr = "curl --form addressFile=@batch_"+str(i)+"_geocoder_input.csv --form benchmark=9 https://geocoding.geo.census.gov/geocoder/locations/addressbatch --output geocoderesult"+str(i)+".csv"
        subprocess.Popen(requeststr)
    #TODO: receive, pare down to zips, coordinates
    pass

# df = pd.read_csv("C:\\Users\\stout315\\Documents\\localfile.csv")
# batch_lookup(df, "RID", "ADDRESS1", "CITY", "STATE", "ZIP")

def is_po(address):
    """
    Detects whether a certain address is likely to be a P.O. box
    :param address: Full address or first line of address (string)
    :return: ispo (Boolean)
    """
    if not isinstance(address, str):
        return False
    elif len(address) < 3:
        return False
    elif address[0:3] == "PO " or address[0:5] == "P.O. " or address[0:4] == "POB ":
        return True
    elif address.find("P.O.") != -1 or address.find("PO Box") != -1:
        return True
    return False

def is_po_df(dataframe, addline1):
    """
    Detects whether addresses in the dataframe (given by the first line) are likely to be P.O. boxes.
    :param dataframe: dataframe of addresses (pandas DataFrame)
    :param addline1: column name of the first address line
    :return: dataframe, with additional column "IS_PO" with Boolean values
    """
    dataframe["IS_PO"] = dataframe[addline1].apply(is_po)

def coord_dist(long1, lat1, long2, lat2):
    """
    Calculates birds-eye distance between two locations in miles using longitude and latitude.
    :param long1: longitude of location 1 (float)
    :param lat1: latitude of location 1 (float)
    :param long2: longitude of location 2 (float)
    :param lat2: latitude of location 2 (float)
    :return: distance between the two locations (miles)
    """
    latdist = abs(lat1-lat2) * 69
    longdist = abs(long1-long2) * math.cos(0.5*abs(lat1 + lat2)*2*math.pi/360) * 69.172
    return math.sqrt(math.pow(latdist, 2)+math.pow(longdist, 2))

def get_long_lat(dataframe, streetadd, city, state, zip):
    """

    :param dataframe:
    :param streetadd:
    :param city:
    :param state:
    :param zip:
    :return:
    """
    pass