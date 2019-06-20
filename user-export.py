#!/usr/bin/env python3

import sqlite3
import csv

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('./new8.db')
conn.row_factory = dict_factory

c = conn.cursor()

users = c.execute("""select
anrede as title,
name as surname,
vorname as firstname,
gebdat as dateofbirth,
kzmw as sex,
strasse1 as address,
plz as zipcode,
ort as city,
telp as phone,
teld as mobile,
email,
kndnr as cardnumber,
beitrgrp as branchcode,
beitrgrp as categorycode,
eintrdat as dateenroled,
vorname as userid,
passw as password

FROM DBF_Database_daknd_dbf;""")

userids = []

replacedictionary = {
    "ä":"a",
    "ö":"o",
    "ü":"u",
    "é":"e",
    "è":"e",
    "ß":"ss",
    "Ä":"A",
    "Ö":"o",
    "Ü":"u",
}

def usernamegenerator(first,last, userids):
    """generate cleaner userids"""
    base = first + last[:2]
    for k in replacedictionary:
        base = base.replace(k, replacedictionary[k])
    userid = base
    enum = 0
    while userid in userids:
        enum += 1
        userid = base + str(enum)
        print("double ", base, " using ", userid)
    return userid

with open('users.csv', 'w', newline='') as csvfile:
    fieldnames = ['title', 'surname', 'firstname', 'dateofbirth', 'sex', 'address', 'zipcode', 'city', 'phone', 'mobile', 'email', 'cardnumber', 'branchcode', 'categorycode', 'dateenroled', 'userid', 'password']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for u in users:
        if u["branchcode"] in ["L", "M", "N"]:
            u["branchcode"] = "L"
        else:
            u["branchcode"] = "B"
        if u["sex"] == 'M':
            u["title"] = "Herr"
        elif u["sex"] == 'F':
            u["title"] = "Frau"
        if u["dateofbirth"] == 'None':
            u["dateofbirth"] = ""
        if u["categorycode"] == 'L':
            u["categorycode"] = 'T'
        elif u["categorycode"] == 'S':
            u["categorycode"] = 'J'
        elif u["categorycode"] == 'T':
            u["categorycode"] = 'YA'
        elif u["categorycode"] == '1':
            u["categorycode"] = 'J'
        elif u["categorycode"] == 'M':
            u["categorycode"] = 'S'
        userid = usernamegenerator(u["firstname"], u["surname"], userids)
        userids.append(userid)
        u["userid"] = userid

        writer.writerow(u)
