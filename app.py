from flask import Flask, app, redirect, render_template, request, send_file, g
import sqlite3
import shutil
import os
import pandas
import csv
from plan_boxes import plan_boxes
from palletise import palletise
from calculate import calculate
from change_file import change_file
from consolidate import consolidate
#from flask_bcrypt import Bcrypt

app = Flask(__name__)
# define database
DATABASE = "///planner.db"
# create path to base directory
basedir = os.path.abspath(os.path.dirname(__file__))
# create path which will be used to upload file
app.config["LOAD_UPLOADS"] = os.path.join(basedir, "static/loads")
# create path which will be used to upload file
app.config["INPUT"] = os.path.join(basedir, "static/input")
# define global variable for load number for pallet planing functionality
load_number = ""
# define variable for password encryption
#bcrypt = Bcrypt()


def get_db():
    """
    create reference to database

    :return: variable referring to database
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.route("/")
def index():
    """
    open index web page
    """
    return render_template("index.html")


@app.route("/upload-load", methods=["GET", "POST"])
def upload_load():
    """
    prepare info for new csv file which will contain split for pallets
    details described individually below
    """
    if request.method == "POST":
        # check if input directory exist and if so, delete it
        # in this directory are stored files
        if os.path.exists(app.config["INPUT"]):
            shutil.rmtree(app.config["INPUT"])

        # check if input directory exist and if not, create it
        # in this directory are stored files
        if not os.path.exists(app.config["INPUT"]):
            os.makedirs(app.config["INPUT"])

        if request.files:
            # upload file with list of products and quantities which needs planning.
            # the file is uploaded by user
            # if file is not provided, below error will flash
            if request.files["load"]:
                conn = sqlite3.connect("planner.db")
                c = conn.cursor()
                c.execute("DROP TABLE IF EXISTS load")
                load = request.files["load"]
                if load.filename == "load.csv":
                    filepath = os.path.join(app.config["LOAD_UPLOADS"], load.filename)
                    load.save(filepath)
                else:
                    return render_template("error.html", text="you have uploaded wrong file instead of 'load.csv'")

                if request.form.get("consolidate"):
                    consolidate("static/loads/load.csv")
                df = pandas.read_csv(os.path.join(basedir, "static/loads/load.csv"))
                df.to_sql("load", conn)
                conn.commit()
                conn.close()

                # check if correct file has been uploaded
                load_file = os.path.join(app.config["LOAD_UPLOADS"], "load.csv")
                file_list = []
                # with open(load_file, "r") as file:
                #     lines = csv.reader(file)
                #     for line in lines:
                #         file_list.append(line)
                #     if file_list[0][0] == "SKU" and file_list[0][1] == "quantity":
                #         pass
                #     elif file_list[0][0] == "ï»¿SKU":
                #         file_list[0][0] = "SKU"
                #     else:
                #         return render_template("error.html",
                #                                text="you have uploaded wrong file. "
                #                                     "First column should be 'SKU' and second column 'quantity'.")

            else:
                return render_template("error.html", text="'load.csv' file must be uploaded")

            # add value to load number variable
            global load_number
            load_number = request.form.get("load_number")

            # test if load number was provided and also if contains 6 digits
            if load_number != "" and len(load_number) == 6:
                pass
            else:
                return render_template("error.html", text="load number must be provided and must have 6 digits")

            # test if load number is numeric
            try:
                test = int(load_number)
                return redirect("/loaded")
            except ValueError:
                return render_template("error.html", text="load number must number")
	
            # password verification prior execution
            #entered_password = request.form.get("password")
            #with open("static/password.csv", "br") as file:
            #    to_check = file.read()
            #if bcrypt.check_password_hash(to_check, entered_password):
            #    return redirect("/loaded")
            #else:
            #    return render_template("error.html", text="wrong password, or password not provided")

    else:
        return render_template("upload_load.html")


@app.route("/branch", methods=["GET", "POST"])
def branch():
    """
    this creates file with suggested stock order,
    taking into account current stock level, back orders and stock target
    function calls two other functions calculate() and change_file()
    :return: csv file with suggested stock order
    """
    if request.method == "POST":
        # check if input directory exist and if so, delete it
        # in this directory are stored files
        if os.path.exists(app.config["INPUT"]):
            shutil.rmtree(app.config["INPUT"])

        # check if input directory exist and if not, create it
        # in this directory are stored files
        if not os.path.exists(app.config["INPUT"]):
            os.makedirs(app.config["INPUT"])

        # allocate user selection to variable
        what_branch = request.form.get("what_branch")

        if what_branch == "...":
            return render_template("error.html", text="you must select branch")

        # user upload file with back orders
        if request.files["back_orders"]:
            back_orders = request.files["back_orders"]
            filepathBO = os.path.join(app.config["INPUT"], back_orders.filename)
            back_orders.save(filepathBO)
        else:
            return render_template("error.html", text="you must provide 'back_orders.csv' file")

        # user upload file with current stock level
        if request.files["current_stock"]:
            current_stock = request.files["current_stock"]
            filepathCS = os.path.join(app.config["INPUT"], current_stock.filename)
            current_stock.save(filepathCS)
        else:
            return render_template("error.html", text="you must provide 'current.csv' file")

        # allocate files to variables which are used by both functions below
        pp_codes_file = os.path.join(basedir, "static/" + what_branch + "/PP_codes.csv")
        b_codes_file = os.path.join(basedir, "static/" + what_branch + "/b_codes.csv")
        back_orders_file = os.path.join(basedir, "static/input/back_orders.csv")
        current_stock_file = os.path.join(basedir, "static/input/current.csv")
        branch_target = os.path.join(basedir, "static/" + what_branch + "/database.csv")
        proposal = os.path.join(basedir, "static/input/new_order.csv")

        # call calculate() function
        calculate(pp_codes_file, b_codes_file, back_orders_file, current_stock_file,
                  branch_target, proposal)

        # call change_file() function
        change_file(pp_codes_file, buildbase_codes_file, proposal,
                    branch_target, "order_proposal.csv")
	
        return send_file("order_proposal.csv", as_attachment=True)
        # action protected by password
        #entered_password = request.form.get("password")
        #with open("static/password.csv", "br") as file:
        #    to_check = file.read()

        #if bcrypt.check_password_hash(to_check, entered_password):
        #    return send_file("order_proposal.csv", as_attachment=True)
        #else:
        #    return render_template("error.html", text="wrong password, or password not provided")

    else:
        return render_template("branch.html")


@app.route("/planning")
def planning():
    return render_template("planning.html")


@app.route("/loaded")
def loaded():
    """
    function takes all inputs from upload_load() to split load to the pallets
    all details as below
    :return: csv file with pallet plan
    """
    # call plan_boxes() function
    plan_boxes()

    # call palletise() function
    palletise()

    # prepare variable, based on both above functions
    # create count for all 3 types of pallets
    conn = sqlite3.connect("planner.db")
    cursor = conn.cursor()
    cursor = cursor.execute("SELECT pallet_number,product, quantity FROM Sbox")
    itemS = cursor.fetchall()
    cursor = cursor.execute("SELECT COUNT(*) FROM tempS")
    sb = cursor.fetchone()
    small_boxes = int(sb[0])

    if small_boxes % 30 == 0:
        small_pallets = int(small_boxes / 30)
    else:
        small_pallets = int(small_boxes / 30) + 1

    cursor = cursor.execute("SELECT pallet_number,product, quantity FROM Lbox")
    itemL = cursor.fetchall()
    cursor = cursor.execute("SELECT COUNT(*) FROM tempL")
    lb = cursor.fetchone()
    large_boxes = int(lb[0])

    if large_boxes % 6 == 0:
        large_pallets = int(large_boxes / 6)
    else:
        large_pallets = int(large_boxes / 6) + 1

    cursor = cursor.execute("SELECT pallet_number,product, quantity FROM Pbox")
    itemP = cursor.fetchall()
    cursor = cursor.execute("SELECT COUNT(*) FROM tempP")
    pb = cursor.fetchone()
    pallet_boxes = int(pb[0])
    total_pallets = small_pallets + large_pallets + pallet_boxes

    # create and write to the file
    with open("planned_load.csv", "w") as file:
        # write header of the file
        file.write(f"""
                    Load {load_number} will be planned on {total_pallets} pallets:\n
                    {small_pallets} pallets with small boxes.\n
                    {large_pallets} pallets with large boxes.\n
                    {pallet_boxes} pallet boxes.\n
                    """)

        # write pallet plan for small boxes
        file.write("\n")
        if small_pallets == 1:
            file.write(str(small_pallets) + " pallet with small boxes:\n")
        else:
            file.write(str(small_pallets) + " pallets with small boxes:\n")

        for item in itemS:
            file.write("%s,%s,%s\n" % (f"PALLET {(item[0])}", item[1], item[2]))

        # write pallet plan for large boxes
        file.write("\n")
        if large_boxes == 1:
            file.write(str(large_pallets) + " pallet with large boxes:\n")
        else:
            file.write(str(large_pallets) + " pallets with large boxes:\n")

        for item in itemL:
            file.write("%s,%s,%s\n" % (f"PALLET {(item[0])}", item[1], item[2]))

        # write pallet plan for pallet boxes
        file.write("\n")
        if pallet_boxes == 1:
            file.write(f"{pallet_boxes} pallet box:\n")
        else:
            file.write(f"{pallet_boxes} pallet boxes:\n")

        for item in itemP:
            file.write("%s,%s,%s\n" % (f"PALLET {(item[0])}", item[1], item[2]))

    # return file which user can save
    return send_file("planned_load.csv", as_attachment=True)


if __name__ == '__main__':
    app.run()
