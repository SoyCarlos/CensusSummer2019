#Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
#from Keith Finlay and Elizabeth Willhide.
import pandas as pd
from werkzeug import secure_filename
import csv


def get_file_type(file):
    """
    Takes in file path and returns file extension.
    :param file: File Path (String)
    :return: File Extension (String)
    """
    file_type = file.split(".")[-1]
    print("You provided a " + file_type + " file.")
    return file_type


def read_frame(file, file_type):
    """
    Takes in file path and extension and returns pandas DataFrame.
    Currently works for xlsx, csv and tab-separated text files.
    :param file: File Path (String)
    :param file_type: File Extension (String)
    :return: pandas DataFrame
    """
    def xlsx(file):
        try:
            frame = pd.read_excel(file)
        except UnicodeDecodeError:
            frame = pd.read_excel(file, encoding='ISO-8859-1')
        return frame

    def csv(file):
        try:
            frame = pd.read_csv(file, encoding='ISO-8859-1')
        except UnicodeDecodeError:
            print("FILE", file)
            frame = pd.read_csv(file, encoding='ISO-8859-1')
        return frame

    def txt(file):
        try:
            frame = pd.read_csv(file, sep="|", encoding="iso-8859-1")
        except pd.errors.ParserError:
            import csv
            lst_table = []
            with open(file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter='|')
                for row in csv_reader:
                    lst_table.append(row)
                tbl = pd.DataFrame(lst_table)
                tbl.columns = tbl.iloc[0]
                frame = tbl.reindex(tbl.index.drop(0))
        except UnicodeDecodeError:
            frame = pd.read_csv(file, sep="|", encoding="iso-8859-1", error_bad_lines=False)
        return frame
    options = {
        'xlsx': xlsx,
        'csv': csv,
        'txt': txt
    }

    if file_type not in options.keys():
        print("File type " + file_type + " not supported.")
        return None

    return options[file_type](file)
