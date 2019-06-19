#! /usr/bin/env python3
import dbf
import sys
import os
import sqlite3
import argparse
import re
parser = argparse.ArgumentParser(description="read and convert DBF (dBASE) database files")
group = parser.add_mutually_exclusive_group()
group.add_argument("-f", "--fields", action="store_true", help="display field names")
group.add_argument("-p", "--pretty", action="store_true", help="display pretty-printed table")
group.add_argument("-t", "--table", action="store_true", help="display tab-separated table")
group.add_argument("-d", "--dump", action="store_true", help="dump table")
group.add_argument("-s", "--sqlite", metavar='DB', help="write to sqlite database file DB")
parser.add_argument("-F", "--force", action="store_true", help="overwrites existing table in sqlite database")
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-i", "--ignore-errors", action="store_true", help="tell DBF library to ignore typecasting errors")
parser.add_argument('infiles', metavar='DBF', nargs='+', help="input files in dBASE (.DBF) format")
args = parser.parse_args()

conn = None

filenames = set()

for file in  args.infiles:
    path,filename = os.path.split(file)
    files = os.listdir(path)

    for filename in files:
        nn = filename.lower()
        nn = os.path.join(path,nn)
        src = os.path.join(path,filename)
        if nn[-4:] in [".dbf", ".dbt" ]:
            os.rename(src, nn)
            if nn.endswith(".dbf"):
                filenames.add(nn)

def onIni():
    global conn
    if args.sqlite:
        print("sqlite: Opening db %s ..." % (args.sqlite))
        conn = sqlite3.connect(args.sqlite)

    try:
        for dbfName in filenames:
            print("converting db: ", dbfName)
            try:
                run(dbfName, codepage="cp850")
            except UnicodeDecodeError as e:
                print("failed retrying with other codepage")
                run(dbfName, codepage="cp850")
    except sqlite3.Error as e:
        print("sqlite: " + e.args[0])
    finally:
        if args.sqlite:
            print("sqlite: Commit and close ...")
            conn.commit()
            conn.close()


def run(dbfName, codepage=None):
    global conn
    if codepage:
        dbf1 = dbf.Table(dbfName).open(mode=dbf.READ_WRITE)
    else:
        dbf1 = dbf.Table(dbfName, codepage="cp850").open(mode=dbf.READ_WRITE)

    dbf1.codepage = dbf.CodePage.__new__(dbf.CodePage, "cp850")



    if args.verbose: print("--> " + dbfName + " <--")
    if args.table:
        for fldName in dbf1.field_names:
            sys.stdout.write('%s\t'%(fldName))
        print()
        for i1 in range(min(3,len(dbf1))):
            rec = dbf1[i1]
            for fldName in dbf1.field_names:
                sys.stdout.write('%s\t'%(rec[fldName]))
            print()

    elif args.pretty:
        out = [ dbf1.field_names ]
        for el in dbf1:
            out.append([ str(s).strip() for s in el ])
        print_table(out)

    elif args.sqlite:
        netto_name = re.sub('[^A-Za-z0-9]', '_', dbfName).strip('_')
        print("Importing %s into table %s ..." % (dbfName, netto_name))
        cr_stat = "CREATE TABLE `%s` (`%s`)" % (netto_name, '`,`'.join(dbf1.field_names))
        if args.force: conn.execute('DROP TABLE IF EXISTS `%s` ' % (netto_name))
        try:
            conn.execute(cr_stat)
        except Exception as e:
            print("sqlite: Error creating table %s!" % netto_name)
            print("You might want to try the --force option.")
            raise e
        for el in dbf1:
            ins_stat = "INSERT INTO `%s` VALUES ('%s')" % (netto_name, "','".join([ str(s).strip().replace("'","''").replace('\x00','') for s in el ]))
            if args.verbose: print("sqlite: executing: %s" % ins_stat)
            conn.execute(ins_stat)

    elif args.dump:
        print(( "\t%s\t%s\t" % (os.path.getsize(dbfName),dbfName)))
        for i1 in range(min(3,len(dbf1))):
            rec = dbf1[i1]
            for fldName in dbf1.field_names:
               print(('%s: %s'%(fldName, rec[fldName])))
            print()
    else:
        sys.stdout.write( "\t%s\t%s\t" % (os.path.getsize(dbfName),dbfName))
        #for i1 in range(min(3,len(dbf1))):
        #    rec = dbf1[i1]
        for fldName in dbf1.field_names:
            sys.stdout.write('%s, '%(fldName))
        print()
    dbf1.close()


def print_table(rows):
    """print_table(rows)

    Prints out a table using the data in `rows`, which is assumed to be a
    sequence of sequences with the 0th element being the header.
    """

    # - figure out column widths
    widths = [ len(max(columns, key=len)) for columns in zip(*rows) ]

    # - print the separator
    print(('+-'+ '-+-'.join( '-' * width for width in widths ) +'-+'))
    # - print the header
    header, data = rows[0], rows[1:]
    print(('| '+
        ' | '.join( format(title, "%ds" % width) for width, title in zip(widths, header) )
        +' |'))

    # - print the separator
    print(('|-'+ '-+-'.join( '-' * width for width in widths ) +'-|'))

    # - print the data
    for row in data:
        print(('| '+
            " | ".join( format(cdata, "%ds" % width) for width, cdata in zip(widths, row) )
            +' |'))

    # - print the separator
    print(('+-'+ '-+-'.join( '-' * width for width in widths ) +'-+'))

onIni()
