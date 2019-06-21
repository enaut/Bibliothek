from pymarc import Record, Field
import sqlite3
import sys
import csv
import os

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)),'../new10.db'))
conn.row_factory = dict_factory


with open('issuedata.csv', 'w', newline='') as csvfile:
    csvfile.write('Version=1.0\tGenerator=kocPHP\tGeneratorVersion=0.1\n')
    fieldnames = ["time", "command", "arg1", "arg2"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
    n = 0
    with conn:
        c = conn.cursor()
        d = conn.cursor()
        for i in c.execute("""
    select a.prottyp,a.kndnr, a.mednr, a.datum, a.zeit, b.name1, c.titel from DBF_Database_daaprotx_dbf as a
    join DBF_Database_daknd_dbf as b on a.kndnr = b.kndnr
    JOIN DBF_Database_damed_dbf as c on a.mednr = c.mednr
        """):
            if i["prottyp"] != "2":
                line={  "time":"",
                        "command":"",
                        "arg1":"",
                        "arg2":""}
                line["time"] = "{} {}:{}:00 {}".format(i["datum"], i["zeit"][:2], i["zeit"][2:],n )
                n += 1
                barcode = d.execute("""SELECT e.mednrx FROM DBF_Database_damedb_dbf as e
         WHERE e.mednr = "{}"
		 LIMIT 1""".format(i['mednr'])).fetchone()
                if barcode:
                    barcode = barcode['mednrx']

                    if i["prottyp"] == "0":
                        line["command"] = "issue"
                        line["arg1"] = i["kndnr"]
                        line["arg2"] = barcode
                    if i["prottyp"] == "1":
                        line["command"] = "return"
                        line["arg1"] = barcode
                    writer.writerow(line)
                else:
                    print("####### no such mednr: ", i['mednr'])

                    if i["prottyp"] == "0":
                        line["command"] = "issue"
                        line["arg1"] = i["kndnr"]
                        line["arg2"] = barcode
                    if i["prottyp"] == "1":
                        line["command"] = "return"
                        line["arg1"] = barcode
                    print(line)
