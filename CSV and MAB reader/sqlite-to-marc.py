from pymarc import Record, Field
import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('../new8.db')
conn.row_factory = dict_factory

def log(*args):
    #print(*args)
    pass

notimpl = {}

records = {}


with conn:
    c = conn.cursor()

    for l in c.execute('SELECT * FROM DBF_database_damedmab_dbf'):
        if not l['mednr'] in records:
            print('.', end='')
            records[l['mednr']] = Record(file_encoding = "utf-8", force_utf8=True)

        """ Not needed
                if len(l.strip()) < 1:
                    if record.title():
                        log("**New record writing old one: ", record['001'], '\n', '-'*20)
                        with open('marcout.mrc', 'ab') as o:
                            o.write(record.as_marc())
                        records[record['001']] = record
                        record = Record(file_encoding = "utf-8", force_utf8=True)
                        record.myextra = {}
                    pass
        """

        if l["fldnr"] == 'M10':
            log("Urls have a non number therefore are extracted first")
            records[l['mednr']].add_field(Field(
                    tag = '856',
                    indicators = ['4','2'],
                    subfields = [
                        'u', l["txt1"]
                    ]))
        elif l["fldnr"] == 'B03':
            # TODO Lehrer/Schüler Bibliothek
            pass
        elif l["fldnr"] == '651' and l["indik"] == 'i':
            # TODO Lehrer/Schüler Bibliothek
            pass
            """
        elif (not  l[:3].isdigit()):
            log("in " + str(record['001']) + "adding to: ", last)
            if last == '331 ':
                record['245']['a'] = record['245']['a'][:-1] + ' ' + l
                log("result: " + record['245']['a'])
                """

        elif l["fldnr"] == '001':
            log( "**ID ", l["txt1"])
            # Control Number
            if not '001' in records[l['mednr']]:
                records[l['mednr']].add_field(
                    Field(
                        tag = '001'))
            else:
                print("############### ID already set with" + str(records[l['mednr']]['001']) + "-- new is: " + l["txt1"])
            records[l['mednr']]['001'].data = l["txt1"]

        elif l["fldnr"] == '010':
                log("** Zweitautor", l["txt1"])
                records[l['mednr']].add_field(Field(
                    tag = '773',
                    indicators = ['0','8'],
                    subfields = [
                        'w', l["txt1"],
                    ]))

        elif l["fldnr"] == '089':
            log( "** Band: ", l["txt1"])
            # TODO

            if '245' in records[l['mednr']]:
                records[l['mednr']]['245'].add_subfield('n', l["txt1"])
            else:
                records[l['mednr']].add_field(Field(
                        tag = '245',
                        indicators = ['1','0'],
                        subfields = [
                            'n', l["txt1"],
                        ]))

        elif l["fldnr"] == '100':
            log( "**Author ", l["txt1"])
            # Main Author
            if not '100' in records[l['mednr']]:
                records[l['mednr']].add_field(
                    Field(
                        tag = '100',
                        indicators = ['1','\\'],
                        subfields = [
                            'a', l["txt1"],
                        ]))
            elif not 'g' in records[l['mednr']]['100']:
                records[l['mednr']]['100'].add_subfield('g', l["txt1"])
            else:
                #print("tripple Author", l["txt1"])
                records[l['mednr']]['100']['g'] = records[l['mednr']]['100']['g'] + '–' + l["txt1"]
        elif l["fldnr"] == '102' and l["indik"]=='a':
            if records[l['mednr']]['100']['a'] == l["txt1"]:
                log("ignoring ", l["txt1"])
                pass
            else:
                records[l['mednr']].add_field(
                    Field(
                        tag = '700',
                        indicators = ['1','\\'],
                        subfields = [
                            'a', l["txt1"],
                            '4', 'todo'
                        ]))

        elif l["fldnr"] == '104' and l["indik"]=='a':
            log("** Zweitautor", l["txt1"])
            records[l['mednr']].add_field(Field(
                    tag = '700',
                    indicators = ['0',' '],
                    subfields = [
                        'a', l["txt1"],
                        'e', 'Mitwirkender',
                        '4', 'ctb'
                    ]))

        elif l["fldnr"] == '106' and l["indik"]=='a':
            log("** Drittautor", l["txt1"])
            records[l['mednr']].add_field(Field(
                    tag = '700',
                    indicators = ['0',' '],
                    subfields = [
                        'a', l["txt1"],
                        'e', 'Mitwirkender',
                        '4', 'ctb'
                    ]))

        elif l["fldnr"] == '108' and l["indik"]=='a':
            log("** Viertautor", l["txt1"])
            records[l['mednr']].add_field(Field(
                    tag = '700',
                    indicators = ['1',' '],
                    subfields = [
                        'a', l["txt1"],
                        'e', 'Mitwirkender',
                        '4', 'ctb'
                    ]))
        elif l["fldnr"] == '110' and l["indik"]=='a':
            # ignore (duplicate of 108a)
            pass
        elif l["fldnr"] == '114' and l["indik"]=='a':
            log("** Viertautor", l["txt1"])
            records[l['mednr']].add_field(Field(
                    tag = '700',
                    indicators = ['1',' '],
                    subfields = [
                        'a', l["txt1"],
                        'e', 'Mitwirkender',
                        '4', 'ctb'
                    ]))
        elif l["fldnr"] == '116' and l["indik"]=='a':
            # ignore (duplicate of 108a)
            pass
        elif l["fldnr"] == '304':
            log("** Originalsprachiger Titel", l["txt1"])
            records[l['mednr']].add_field(Field(
                    tag = '765',
                    indicators = ['0',' '],
                    subfields = [
                        'a', l["txt1"]
                    ]))

        elif l["fldnr"] == '331':
            log("**Main title ", l["txt1"])
            # Main title
            if not '245' in records[l['mednr']]:
                log("   adding a" + l["txt1"])
                records[l['mednr']].add_field(Field(
                        tag = '245',
                        indicators = ['1','0'],
                        subfields = [
                            'a', l["txt1"],
                        ]))
            elif not 'a' in records[l['mednr']]['245']:
                log("   adding sub a" + l["txt1"])
                records[l['mednr']]['245'].add_subfield('a', l["txt1"])
            elif not 'g' in records[l['mednr']]['245']:
                log("   adding sub g" + l["txt1"])
                records[l['mednr']]['245'].add_subfield('g', l["txt1"])
            else:
                #print("tripple title: ", record['245']['g'])
                log("   extending g" + l["txt1"])
                records[l['mednr']]['245']['g'] = records[l['mednr']]['245']['g'] + '–' + l["txt1"]
        elif l["fldnr"] == '335':
            log("**subtitle ", l["txt1"])
            # subtitle
            if '245' in records[l['mednr']]:
                records[l['mednr']]['245'].add_subfield('b', l["txt1"])
            else:
                records[l['mednr']].add_field(Field(
                        tag = '245',
                        indicators = ['1','0'],
                        subfields = [
                            'b', l["txt1"],
                        ]))
        elif l["fldnr"] == '359':
            log("**Responsability ", l["txt1"])
            # Statement of Responsability
            if '245' in records[l['mednr']]:
                records[l['mednr']]['245'].add_subfield('c', l["txt1"])
            else:
                records[l['mednr']].add_field(Field(
                        tag = '245',
                        indicators = ['1','0'],
                        subfields = [
                            'c', l["txt1"],
                        ]))

        elif l["fldnr"] == '403':
            log("** Edition Statement", l["txt1"])
            # Edition Statement
            records[l['mednr']].add_field(Field(
                    tag = '250',
                    indicators = [' ',' '],
                    subfields = [
                        'a', l["txt1"].split()[0],
                        'b', " ".join(l["txt1"].split()[1:])
                    ]))

        elif l["fldnr"] == '410':
            log("** Erscheinungsort", l["txt1"])
            # Erscheinungsort
            records[l['mednr']].add_field(Field(
                    tag = '260',
                    indicators = [' ',' '],
                    subfields = [
                        'a', l["txt1"]
                    ]))
        elif l["fldnr"] == '412':
            log("** Erscheinungsverlag", l["txt1"])
            # ErscheinungVerlag
            if '260' in records[l['mednr']]:
                records[l['mednr']]['260'].add_subfield('b', l["txt1"])
            else:
                records[l['mednr']].add_field(Field(
                        tag = '260',
                        indicators = [' ',' '],
                        subfields = [
                            'b', l["txt1"]
                        ]))
        elif l["fldnr"] == '425':
            log("** Erscheinungsdatum", l["txt1"])
            # Erscheinungsdatum
            if '260' in records[l['mednr']]:
                records[l['mednr']]['260'].add_subfield('c', l["txt1"])
            else:
                records[l['mednr']].add_field(Field(
                        tag = '260',
                        indicators = [' ',' '],
                        subfields = [
                            'c', l["txt1"]
                        ]))
        elif l["fldnr"] == '433':
            log("** Seitenzahl/Länge", l["txt1"])
            # Seitenzahl
            records[l['mednr']].add_field(Field(
                    tag = '300',
                    indicators = [' ',' '],
                    subfields = [
                        'a', l["txt1"]
                    ]))
        elif l["fldnr"] == '435':
            log("** Größe/Format", l["txt1"])
            # Größe/Fromat
            if '300' in records[l['mednr']]:
                records[l['mednr']]['300'].add_subfield('c', l["txt1"])
            else:
                records[l['mednr']].add_field(Field(
                        tag = '300',
                        indicators = [' ',' '],
                        subfields = [
                            'c', l["txt1"]
                        ]))

        elif l["fldnr"] == '501':
            #empty anyways
            pass

        elif l["fldnr"] == '540' and l["indik"] == 'a':
            log("** ISBN", l["txt1"])
            # ISBN: mit bindestrichen 9, ohne a
            records[l['mednr']].add_field(Field(
                    tag = '020',
                    indicators = [' ',' '],
                    subfields = [
                        'a', l["txt1"].replace("-","")
                    ]))
        elif l["fldnr"] == '434':
            if '300' in records[l['mednr']]:
                records[l['mednr']]['300'].add_subfield('b', l["txt1"])
            else:
                records[l['mednr']].add_field(Field(
                        tag = '300',
                        indicators = [' ',' '],
                        subfields = [
                            'b', l["txt1"]
                        ]))

        elif l["fldnr"] == '451':
            log("** Preis", l["txt1"])
            # Preis
            if not '490' in records[l['mednr']]:
                records[l['mednr']].add_field(Field(
                        tag = '490',
                        indicators = ['0',' '],
                        subfields = [
                            'b', l["txt1"]
                        ]))
            else:
                records[l['mednr']]['490'].add_subfield('b', l["txt1"])
        elif l["fldnr"] == '455':
            log("** Bandangabe", l["txt1"])
            # Preis
            if not '490' in records[l['mednr']]:
                records[l['mednr']].add_field(Field(
                        tag = '490',
                        indicators = ['0',' '],
                        subfields = [
                            'v', l["txt1"]
                        ]))
            else:
                records[l['mednr']]['490'].add_subfield('v', l["txt1"])
        elif l["fldnr"] == '540' and l["indik"]=='z':
            log("** Preis", l["txt1"])
            # Preis
            records[l['mednr']].add_field(Field(
                    tag = '365',
                    indicators = [' ',' '],
                    subfields = [
                        'b', l["txt1"]
                    ]))
        elif l["fldnr"] == '529':
            log("** Notiz", l["txt1"])
            # Preis
            records[l['mednr']].add_field(Field(
                    tag = '770',
                    indicators = ['1',' '],
                    subfields = [
                        'n', l["txt1"]
                    ]))

        elif l["fldnr"] == '700' and l["indik"]=='o':
            log("** Systematik", l["txt1"])
            # Systematik
            records[l['mednr']].add_field(Field(
                    tag = '084',
                    indicators = [' ',' '],
                    subfields = [
                        'a', l["txt1"].replace("  ", " ")
                    ]))

        elif l["fldnr"] == '750':
            log("** Zusammenfassung", l["txt1"])
            # Seitenzahl
            records[l['mednr']].add_field(Field(
                    tag = '520',
                    indicators = [' ',' '],
                    subfields = [
                        'a', l["txt1"]
                    ]))
        elif l["fldnr"] == '750' and l["indik"]=='f':
            log("** Rezension", l["txt1"])
            # Seitenzahl
            records[l['mednr']].add_field(Field(
                    tag = '520',
                    indicators = ['1',' '],
                    subfields = [
                        'a', l["txt1"]
                    ]))

        elif l["fldnr"] == '902' and l["indik"]=='s':
            log("** Schlagwort", l["txt1"])
            # Seitenzahl
            records[l['mednr']].add_field(Field(
                    tag = '650',
                    indicators = ['0','0'],
                    subfields = [
                        'a', l["txt1"]
                    ]))
        else:
            notimpl[l["fldnr"]+l["indik"]] = l["txt1"]


print("\nparsed {} records".format(len(records)))

# Constants
lehrerbib = ['Lehrerbibiothek', 'GA', 'LB', 'Lehrerbibliothelk', 'Lehrerbibliotehk', 'L', 'Lb', 'lehrerbiibliothek', 'lehrerbibliothel', 'Lehrerbiibliothek', 'Lehrerbibliothel', 'Lehreribliothek', 'Lehrerbibliothek', 'LP', 'Lehrerbibliothe', 'Lehrebibliothek']
schülerbib = ['Bibiothek', 'Biblioothek', 'Bibliothekl', 'Bibliiothek', 'Bibliothek', 'Biliothek', 'Bibiliothek', 'bibliothek', 'Bibiiothek', 'BIbliothek', 'Biblliothek', "Jugendbibliothek"]
other = ['Werkstatt', '1', '2', '4', 'Öxler', 'Kernzeit', 'Arztzimmer', 'Band 4',""]
destbib = {}
for b in lehrerbib:
    destbib[b.lower()] = "L"
for b in schülerbib:
    destbib[b.lower()] = "L"
for b in other:
    destbib[b.lower()] = "O"

def extend(code):
    v = code.split(' ')
    res = []
    for m in v:
        if len(res) > 0:
            if '.' in m:
                res += [res[-1] + ' ' + m.split('.')[0]]
                res += [res[-2] + ' ' + m]
                if len(m.split('.')) > 2:
                    res += [res[-3] + ' ' + '.'.join(m.split('.')[:2])]
            else:
                res += [res[-1] + ' ' + m]
        else:
            res=[m]
    return res

print("Fixing database")
c = conn.cursor()
# remove doublespaces in places
c.execute('UPDATE DBF_database_dasys_dbf SET deweynr = REPLACE(deweynr,"  "," ")')
def inrep(deweynr, txt):
    # add missing values to sqlite if not there already
    if c.execute("select count(*) as c from DBF_database_dasys_dbf where deweynr = '{}'".format(deweynr)).fetchone()['c'] == 0:
        c.execute("INSERT INTO DBF_database_dasys_dbf (deweynr, txt) VALUES ('{}', '{}')".format(deweynr, txt))
    else:
        print("Not inserting", deweynr, txt)
inrep('EN 7', 'Abitur')
inrep('EN 8', 'Wörterbücher')
c.execute("UPDATE DBF_database_dasys_dbf SET txt='Lektüre' where deweynr='EN 6.1'")

conn.commit()

print("Adding items")
for k in records:
    # Adding items with tag 952
    for l in c.execute('''SELECT a.mednrx as barcode,a.standort,a.deweynr,a.anschdat,a.invnr,a.leihvor,a.letausleih,a.bem1,b.mtyp,b.ean,b.titel,b.autor FROM DBF_database_damedb_dbf as a
                           JOIN DBF_database_damed_dbf as b on a.mednr = b.mednr
                           WHERE a.mednr IS "{}"'''.format(k)):

        records[k].add_field(Field(
                tag = '952',
                indicators = ['0','0'],
                subfields = [
                    'a', destbib[l["standort"].lower().strip()],
                    'b', destbib[l["standort"].lower().strip()],
                    'd', l["anschdat"],
                    'i', l["invnr"],
                    'l', l["leihvor"],
                    'o', l["deweynr"],
                    'p', l["barcode"],
                    's', l["letausleih"],
                    'x', "(Daten importiert aus library for windows)" + l["bem1"],
                    'y', l["mtyp"]

                ]))
        if l["ean"] and records[k]['020']['a'] != l["ean"]:
            #print(records[k]['020']['a'], l["ean"])
            records[k].add_field(Field(
                tag = '020',
                indicators = ['0','0'],
                subfields = [
                    'a', l["ean"]
                ]))
    # Adding Summary
    for l in c.execute('SELECT * FROM DBF_database_damedy_dbf WHERE mednr IS "{}"'.format(k)):
        if not "520" in records[k]:
            records[k].add_field(Field(
                tag = '520',
                indicators = ['0','0'],
                subfields = [
                    'a', l["txt1"],
                    ]))
        else:
            records[k]['520'].add_subfield('b', l["txt1"])

    # Adding keywords Keywords are mapped rather complicated
    for l in c.execute("""SELECT * FROM DBF_database_damedb_dbf
                                JOIN DBF_database_damedx_dbf on DBF_database_damedb_dbf.mednr = DBF_database_damedx_dbf.mednr
                                JOIN DBF_database_dakurz_dbf on DBF_database_damedx_dbf.knr=DBF_database_dakurz_dbf.knr
                                where DBF_database_damedx_dbf.mednr="{}" """.format(k)):
            records[k].add_field(Field(
                tag = '653',
                indicators = ['0','0'],
                subfields = [
                    'a', l["bez"],
                    ]))

    if '084' in records[k]:
        code = records[k]['084']['a']
        codes = extend(code)
        # Adding keywords from Systematik
        for l in c.execute(""" SELECT * FROM DBF_database_dasys_dbf where deweynr in ("{}")""".format('", "'.join(codes))):
            kws = [i.strip() for i in l['txt'].split(',')]
            for kw in kws:
                records[k].add_field(Field(
                    tag = '653',
                    indicators = ['0','0'],
                    subfields = [
                        'a', kw,
                        ]))



print("writing to file marcout.mrc")
with open('marcout.mrc', 'ab') as o:
    for k in records:
        o.write(records[k].as_marc())

if len(notimpl) > 0:
    print( "not yet implemented: ")
    for k,v in notimpl.items():
        print(k,v)

conn.commit()
conn.close()
