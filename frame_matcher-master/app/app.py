#Developed by Carlos Eduardo Ortega and Shohini Saha with guidance & supervision
#from Keith Finlay and Elizabeth Willhide.
from flask import Flask, render_template, request, url_for, session, redirect, g, Response, send_from_directory, send_file, make_response
from werkzeug import secure_filename
import os
import atexit
import pandas as pd
import numpy as np
import json
from services.frame_matcher import frame_matcher
from services.functionality.file_proc import *
from services.functionality.cleaning import *
import sqlite3
from sqlite3 import Error
import tempfile

app = Flask(__name__)
app.config['SAVE_FOLDER'] = 'results/'
app.secret_key = os.urandom(12)
app.secret_key = 'dev'


def sql_connection():
    """Creates sqlite3 database in memory
    
    Returns:
        sqlite3 Connection Object -- Returns connection object where database is stored in memory
    """
    try:
        con = sqlite3.connect(':memory:', check_same_thread=False)
        print("Connection established in memory.")
        return con
    except Error:
        print(Error)


conn = sql_connection()


@app.route('/')
def home():
    """Renders first page
    
    Returns:
        render_template -- Home page
    """
    print("Going Home")
    return render_template('home.html')


@app.route('/prelink', methods=['GET', 'POST'])
def prelink():
    """Renders page to upload files for linking on reference IDs
    
    Returns:
        render_template -- prelink page
    """
    print("Going to Link Upload Page")
    return render_template('prelink.html')


@app.route('/link', methods=['GET', 'POST'])
def link():
    """Takes in 2-4 files for linking on reference IDs and passes to next page.
    
    Returns:
        render_template -- link page (page to choose columns to link on)
    """
    if request.method == 'POST':
        curs = conn.cursor()


        file1 = request.files.get('file')
        file2 = request.files.get('file2')
        file3 = request.files.get('file3')
        file4 = request.files.get('file4')

        link_cols = []
        if file1.filename == "":
            return 'ERROR'
        else:
            print("Obtaining First File")
            file1_type = get_file_type(file1.filename)
            frame1 = read_frame(file1, file1_type)
            frame1.rename(columns={col: col + " (" + file1.filename for col in frame1.columns}, inplace=True)
            link_cols.append(list(frame1.columns))
            frame1.to_sql('main', conn, if_exists='replace', index=False)

        if file2.filename == "":
            return 'ERROR'
        else:
            print("Obtaining Second File")
            file2_type = get_file_type(file2.filename)
            frame2 = read_frame(file2, file2_type)
            frame2.rename(columns={col: col + " (" + file2.filename for col in frame2.columns}, inplace=True)
            link_cols.append(list(frame2.columns))
            frame2.to_sql('link1', conn, if_exists='replace', index=False)

        if file3.filename == "":
            link_cols.append([None])
            session['link2'] = ""
        else:
            print("Obtaining Third File")
            file3_type = get_file_type(file3.filename)
            frame3 = read_frame(file3, file3_type)
            frame3.rename(columns={col: col + " (" + file3.filename for col in frame3.columns}, inplace=True)
            link_cols.append(list(frame3.columns))
            frame3.to_sql('link2', conn, if_exists='replace', index=False)

        if file4.filename == "":
            link_cols.append([None])
            session['link3'] = ""
        else:
            print("Obtaining Fourth File")
            file4_type = get_file_type(file4.filename)
            frame4 = read_frame(file4, file4_type)
            frame4.rename(columns={col: col + " (" + file4.filename for col in frame4.columns}, inplace=True)
            link_cols.append(list(frame4.columns))
            frame4.to_sql('link3', conn, if_exists='replace', index=False)
        print("Going to Link Page")
        return render_template('link.html', columns=link_cols)


@app.route('/home2', methods=["GET", "POST"])
def home2():
    """Takes in columns to link on and combines all files into one frame. Then takes user to next page to select 2nd frame.
    
    Returns:
        render_template -- Home page for user to choose 2nd frame
    """
    if request.method=='POST':
        print("Home2")
        curs = conn.cursor()

        main = pd.read_sql_query("SELECT * from main", conn)
        link1 = pd.read_sql_query("SELECT * FROM link1", conn)

        main1 = request.form['main_1']
        secondary1 = request.form['secondary_1']

        if session.get('link2') != "":
            main2 = request.form['main_2']
            secondary2 = request.form['secondary_2']
            link2 = pd.read_sql_query("SELECT * FROM link2", conn)

        if  session.get('link3') != "":
            main3 = request.form['main_3']
            secondary3 = request.form['secondary_3']
            link3 = pd.read_sql_query("SELECT * FROM link3", conn)
        
        print("Performing First Merge")
        link1.rename(columns={secondary1:main1}, inplace=True)
        first_link = main.merge(link1, on= main1, how='outer')
        del(main)
        del(link1)

        if  session.get('link2') != "":
            #Merge 3 files
            if  session.get('link3') == "":
                print("Performing Second Merge")
                link2.rename(columns={secondary2:main2}, inplace=True)
                result = first_link.merge(link2, on=main2, how='outer')
                result = result.reset_index().rename(columns={'index':'Frame1_Index'})
                del(link2)
                result.rename(columns={col: col + " - Frame 1)" for col in result.columns}, inplace=True)
                result.rename(columns={'Frame1_Index - Frame 1)': 'Frame1_Index'}, inplace=True)
                result.to_sql('frame1', conn, if_exists='replace', index=False)
                print("Returning to Upload Page")
                return render_template("home2.html")
            #Merge 4 files
            else:
                print("Performing Second Merge")
                link2.rename(columns={secondary2:main2}, inplace=True)
                result = first_link.merge(link2, on=main2, how='outer')
                del(link2)
                print("Performing Third Merge")
                link3.rename(columns={secondary3:main3}, inplace=True)
                result = result.merge(link3, on=main3, how='outer')
                del(link3)
                result = result.reset_index().rename(columns={'index':'Frame1_Index'})
                result.rename(columns={col: col + " - Frame 1)" for col in result.columns}, inplace=True)
                result.rename(columns={'Frame1_Index - Frame 1)': 'Frame1_Index'}, inplace=True)
                result.to_sql('frame1', conn, if_exists='replace', index=False)
                print("Returning to Upload Page")
                return render_template("home2.html")
        else:
            #Merge 2 Files
            result = first_link.reset_index().rename(columns={'index':'Frame1_Index'})
            result.rename(columns={col: col + " - Frame 1)" for col in result.columns}, inplace=True)
            result.rename(columns={'Frame1_Index - Frame 1)': 'Frame1_Index'}, inplace=True)
            result.to_sql('frame1', conn, if_exists='replace', index=False)
            print("Returning to Upload Page")
            return render_template("home2.html")
    else:
        return render_template("home2.html")


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    """Received files submitted by user and initializes them in frame_matcher.
    
    Returns:
        flask render template -- Renders columns.html if method is POST.
    """ 
    if request.method == 'POST':
        session.clear()
        cols = []
        fm = frame_matcher()
        
        file1 = request.files.get('file')
        file2 = request.files.get('file2')

        if file1.filename == "":
            return 'At least two frames required, go back.'
        elif file2.filename == "":
            return "At least two frames required, go back."
        else:
            print("Defining frames")
            fm.define_frames(file1, file1.filename, 1)
            fm.define_frames(file2, file2.filename, 2)
        
        cols.append(list(fm.frame1.columns))
        cols.append(list(fm.frame2.columns))

        for col in cols:
            col.append(None)
        
        update_database(fm.frame1, fm.frame2, conn)
        print("Sending to Columns Page")
        return render_template('columns.html', columns=cols)
    return 'something failed'

@app.route('/uploader2', methods=['GET', 'POST'])
def upload_file2():
    """Received files submitted by user and initializes them in frame_matcher.
    
    Returns:
        flask render template -- Renders columns.html if method is POST.
    """ 
    if request.method == 'POST':
        curs = conn.cursor()

        cols = []

        fm = frame_matcher()
        file2 = request.files.get('file2')

        if file2.filename == "":
            return "At least two frames required, go back."
        else:
            print("Defining Second Frame")
            fm.frame1 = pd.read_sql_query("SELECT * from frame1", conn)
            fm.define_frames(file2, file2.filename,2 )
        
        cols.append(list(fm.frame1.columns))
        cols.append(list(fm.frame2.columns))

        for col in cols:
            col.append(None)
        
        update_database(fm.frame1, fm.frame2, conn)
        print("Sending to columns Page")
        return render_template('columns.html', columns=cols)
    return 'something failed'


@app.route('/process', methods=['GET', 'POST'])
def process_columns():
    """Takes in all pairs of columns from previous page and should return pandas DataFrame in html.
    For data types:
    none: None
    city: City (e.g. Sacramento)
    state: State (e.g. California)
    state_abv: State Abbreviation (e.g. CA)
    add: Full Address (Street, City, State)
    st: Street Address (123 Grover St)
    zip: Zip Code
    id: Some reference ID that matches in both columns.
    Returns:
        String -- Current placeholder. In future should redirect to page displaying resulting pandas DataFrame.
    """
    # TODO Current process does not account for differences in data types. E.g. one frame might be full address for a column
    # while another might have a street address column, city column, state column and zip column
    if request.method == 'POST':
        print("Defining matching columns")
        curs = conn.cursor()

        fm = update_frame_matcher(conn)

        item_a_1 = request.form['item_a_1']
        item_b_1 = request.form['item_b_1']
        data_1 = request.form['data_1']
        fm.choose_columns(item_a_1, item_b_1, data_1)

        item_a_2 = request.form['item_a_2']
        item_b_2 = request.form['item_b_2']
        data_2 = request.form['data_2']
        fm.choose_columns(item_a_2, item_b_2, data_2)

        item_a_3 = request.form['item_a_3']
        item_b_3 = request.form['item_b_3']
        data_3 = request.form['data_3']
        fm.choose_columns(item_a_3, item_b_3, data_3)

        item_a_4 = request.form['item_a_4']
        item_b_4 = request.form['item_b_4']
        data_4 = request.form['data_4']
        fm.choose_columns(item_a_4, item_b_4, data_4)

        item_a_5 = request.form['item_a_5']
        item_b_5 = request.form['item_b_5']
        data_5 = request.form['data_5']
        fm.choose_columns(item_a_5, item_b_5, data_5)

        item_a_6 = request.form['item_a_6']
        item_b_6 = request.form['item_b_6']
        data_6 = request.form['data_6']
        fm.choose_columns(item_a_6, item_b_6, data_6)

        print("Checking Similarities")
        combined = fm.check_similarities()
        combined.to_sql('result', conn, if_exists='replace', index=False)
        return render_template('results.html', columns= combined.columns)
    return 'houston we have a problem'

@app.route('/result', methods=['POST', 'GET'])
def selected_result():
    """Select input columns and return to user through download button.
    
    Returns:
        render_template -- Download page with download link in button.
    """
    if request.method == "POST":
        cols = request.form.getlist('columns_selected')
        result = pd.read_sql_query("SELECT * from result", conn)
        result = result[cols]
        script_dir = os.path.dirname(__file__)
        rel_path = 'results/results.csv'
        path = os.path.join(script_dir, rel_path)
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            session['result'] = temp.name + '.csv'
            result.to_csv(temp.name + '.csv', index=False)
        return render_template('download.html', down=temp.name+".csv")
    return 'we done messed up boss'

@app.route('/results', methods=['POST', 'GET'])
def selected_result2():
    """Select all results and return to user through download button.
    
    Returns:
        render_template -- Download page with download link in button.
    """
    result = pd.read_sql_query("SELECT * from result", conn)
    script_dir = os.path.dirname(__file__)
    rel_path = 'results/results.csv'
    path = os.path.join(script_dir, rel_path)
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        session['result'] = temp.name + '.csv'
        result.to_csv(temp.name + '.csv', index=False)
    return render_template('download.html', down=temp.name+".csv")


@app.route('/getcsv/', methods=['GET', 'POST'])
def getcsv():
    """Returns the csv file to user
    
    Returns:
        Response -- Returns csv to user
    """
    csv_path = session['result']
    csv = pd.read_csv(session['result'], encoding='ISO-8859-1')
    return Response(csv.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=results.csv"})


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdowns localhost server when button is pushed or user Ctrl+C
    
    Returns:
        String -- Lets user know server is shutting down
    """
    # end_program()
    shutdown_server()  
    return 'Server shutting down...'


def shutdown_server():
    """Shuts down server.
    
    Raises:
        RuntimeError: [Error is raised if program doesn't have Werkzeug server initiated.]
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def update_database(frame1, frame2, conn):
    """Updates the instances of the frames in the sqlite3 database
    
    Arguments:
        frame1 {pandas DataFrame} -- First frame
        frame2 {pandas DataFrame} -- Second Frame
        conn {sqlite3 connection} -- Connection to sqlite3 database
    """
    frame1.to_sql('frame1', conn, if_exists='replace', index=False)
    frame2.to_sql('frame2', conn, if_exists='replace', index=False)


def update_frame_matcher(conn):
    """Creates frame matcher instance from frames stored in sqlite3 database
    
    Arguments:
        conn {sqlite3 connection} -- Connection to sqlite3 database
    
    Returns:
        frame_matcher -- Returns frame_matcher instance
    """
    fm = frame_matcher()
    fm.frame1 = pd.read_sql_query("SELECT * FROM frame1", conn)
    fm.frame2 = pd.read_sql_query("SELECT * FROM frame2", conn)
    return fm
    
if __name__ == '__main__':
    app.run(debug=True)
