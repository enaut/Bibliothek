from pymarc import Record, Field
import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('new3.db')
conn.row_factory = dict_factory

def log(*args):
    #print(*args)
    pass

notimpl = {}

records = {}


c = conn.cursor()

record = Record(file_encoding = "utf-8", force_utf8=True)
record.myextra = {}
last = None
for l in c.execute('SELECT * FROM DBF_database_library_DAMEDB_dbf'):
    if len(l.strip()) < 1:
        if record.title():
            log("**New record writing old one: ", record['001'], '\n', '-'*20)
            with open('marcout.mrc', 'ab') as o:
                o.write(record.as_marc())
            records[record['001']] = record
            record = Record(file_encoding = "utf-8", force_utf8=True)
            record.myextra = {}
        pass
    elif l.startswith("###"):
        pass
    elif l.startswith('M10'):
        log("Urls have a non number therefore are extracted first")
        record.add_field(Field(
                tag = '856',
                indicators = ['4','2'],
                subfields = [
                    'u', l[4:]
                ]))
    elif l.startswith('B03 '):
        # TODO Lehrer/Schüler Bibliothek
        pass
    elif l.startswith('651i'):
        # TODO Lehrer/Schüler Bibliothek
        pass

    elif (not  l[:3].isdigit()):
        log("in " + str(record['001']) + "adding to: ", last)
        if last == '331 ':
            record['245']['a'] = record['245']['a'][:-1] + ' ' + l
            log("result: " + record['245']['a'])

    elif l.startswith('001 '):
        log( "**ID ", l[4:])
        # Control Number
        if not '001' in record:
            record.add_field(
                Field(
                    tag = '001'))
        else:
            print("############### ID already set with" + str(record['001']) + "-- new is: " + l[4:])
        record['001'].data = l[4:]

    elif l.startswith('010 '):
            log("** Zweitautor", l[4:])
            record.add_field(Field(
                tag = '773',
                indicators = ['0','8'],
                subfields = [
                    'w', l[4:],
                ]))

    elif l.startswith('089 '):
        log( "** Band -saved for later use ", l[4:])
        # Main Author
        record.myextra['band'] = l[4:]

    elif l.startswith('100 '):
        log( "**Author ", l[4:])
        # Main Author
        if not '100' in record:
            record.add_field(
                Field(
                    tag = '100',
                    indicators = ['1','\\'],
                    subfields = [
                        'a', l[4:],
                    ]))
        elif not 'g' in record['100']:
            record['100'].add_subfield('g', l[4:])
        else:
            #print("tripple Author", l[4:])
            record['100']['g'] = record['100']['g'] + '–' + l[4:]
    elif l.startswith('102a'):
        # TODO Was macht das Feld 102a?
        if record['100']['a'] == l[4:]:
            log("ignoring ", l[4:])
            pass
        else:
            record.add_field(
                Field(
                    tag = '700',
                    indicators = ['1','\\'],
                    subfields = [
                        'a', l[4:],
                        '4', 'todo'
                    ]))

    elif l.startswith('104a'):
        log("** Zweitautor", l[4:])
        record.add_field(Field(
                tag = '700',
                indicators = ['0',' '],
                subfields = [
                    'a', l[4:],
                    'e', 'Mitwirkender',
                    '4', 'ctb'
                ]))

    elif l.startswith('106a'):
        log("** Drittautor", l[4:])
        record.add_field(Field(
                tag = '700',
                indicators = ['0',' '],
                subfields = [
                    'a', l[4:],
                    'e', 'Mitwirkender',
                    '4', 'ctb'
                ]))

    elif l.startswith('108a'):
        log("** Viertautor", l[4:])
        record.add_field(Field(
                tag = '700',
                indicators = ['1',' '],
                subfields = [
                    'a', l[4:],
                    'e', 'Mitwirkender',
                    '4', 'ctb'
                ]))
    elif l.startswith('110a'):
        # ignore (duplicate of 108a)
        pass
    elif l.startswith('114a'):
        log("** Viertautor", l[4:])
        record.add_field(Field(
                tag = '700',
                indicators = ['1',' '],
                subfields = [
                    'a', l[4:],
                    'e', 'Mitwirkender',
                    '4', 'ctb'
                ]))
    elif l.startswith('116a'):
        # ignore (duplicate of 108a)
        pass
    elif l.startswith('304 '):
        log("** Originalsprachiger Titel", l[4:])
        record.add_field(Field(
                tag = '765',
                indicators = ['0',' '],
                subfields = [
                    'a', l[4:]
                ]))

    elif l.startswith('331 '):
        log("**Main title ", l[4:])
        # Main title
        if not '245' in record:
            if 'band' in record.myextra:
                record.add_field(Field(
                        tag = '245',
                        indicators = ['1','0'],
                        subfields = [
                            'a', l[4:],
                            'n', record.myextra['band'],
                        ]))
            else:
                record.add_field(Field(
                        tag = '245',
                        indicators = ['1','0'],
                        subfields = [
                            'a', l[4:],
                        ]))
        elif not 'a' in record['245']:
            record['245'].add_subfield('a', l[4:])
        elif not 'g' in record['245']:
            record['245'].add_subfield('g', l[4:])
        else:
            #print("tripple title: ", record['245']['g'])
            record['245']['g'] = record['245']['g'] + '–' + l[4:]
    elif l.startswith('335 '):
        log("**subtitle ", l[4:])
        # subtitle
        if '245' in record:
            record['245'].add_subfield('b', l[4:])
        else:
            record.add_field(Field(
                    tag = '245',
                    indicators = ['1','0'],
                    subfields = [
                        'b', l[4:],
                    ]))
    elif l.startswith('359 '):
        log("**Responsability ", l[4:])
        # Statement of Responsability
        if '245' in record:
            record['245'].add_subfield('c', l[4:])
        else:
            record.add_field(Field(
                    tag = '245',
                    indicators = ['1','0'],
                    subfields = [
                        'c', l[4:],
                    ]))

    elif l.startswith('403 '):
        log("** Edition Statement", l[4:])
        # Edition Statement
        record.add_field(Field(
                tag = '250',
                indicators = [' ',' '],
                subfields = [
                    'a', l[4:].split()[0],
                    'b', " ".join(l[4:].split()[1:])
                ]))

    elif l.startswith('410 '):
        log("** Erscheinungsort", l[4:])
        # Erscheinungsort
        record.add_field(Field(
                tag = '260',
                indicators = [' ',' '],
                subfields = [
                    'a', l[4:]
                ]))
    elif l.startswith('412 '):
        log("** Erscheinungsverlag", l[4:])
        # ErscheinungVerlag
        if '260' in record:
            record['260'].add_subfield('b', l[4:])
        else:
            record.add_field(Field(
                    tag = '260',
                    indicators = [' ',' '],
                    subfields = [
                        'b', l[4:]
                    ]))
    elif l.startswith('425 '):
        log("** Erscheinungsdatum", l[4:])
        # Erscheinungsdatum
        if '260' in record:
            record['260'].add_subfield('c', l[4:])
        else:
            record.add_field(Field(
                    tag = '260',
                    indicators = [' ',' '],
                    subfields = [
                        'c', l[4:]
                    ]))
    elif l.startswith('433 '):
        log("** Seitenzahl/Länge", l[4:])
        # Seitenzahl
        record.add_field(Field(
                tag = '300',
                indicators = [' ',' '],
                subfields = [
                    'a', l[4:]
                ]))
    elif l.startswith('435 '):
        log("** Größe/Format", l[4:])
        # Größe/Fromat
        record['300'].add_subfield('c', l[4:])

    elif l.startswith('501'):
        #empty anyways
        pass

    elif l.startswith('540a'):
        log("** ISBN", l[4:])
        # ISBN: mit bindestrichen 9, ohne a
        if '-' in l:
            record.add_field(Field(
                    tag = '300',
                    indicators = [' ',' '],
                    subfields = [
                        '9', l[4:]
                    ]))
        else:
            record.add_field(Field(
                    tag = '300',
                    indicators = [' ',' '],
                    subfields = [
                        'a', l[4:]
                    ]))
    elif l.startswith('434 '):
        if '300' in record:
            record['300'].add_subfield('b', l[4:])
        else:
            record.add_field(Field(
                    tag = '300',
                    indicators = [' ',' '],
                    subfields = [
                        'b', l[4:]
                    ]))

    elif l.startswith('451x') or l.startswith("451 "):
        log("** Preis", l[4:])
        # Preis
        if not '490' in record:
            record.add_field(Field(
                    tag = '490',
                    indicators = ['0',' '],
                    subfields = [
                        'b', l[4:]
                    ]))
        else:
            record['490'].add_subfield('b', l[4:])
    elif l.startswith('455 '):
        log("** Bandangabe", l[4:])
        # Preis
        if not '490' in record:
            record.add_field(Field(
                    tag = '490',
                    indicators = ['0',' '],
                    subfields = [
                        'v', l[4:]
                    ]))
        else:
            record['490'].add_subfield('v', l[4:])
    elif l.startswith('540z'):
        log("** Preis", l[4:])
        # Preis
        record.add_field(Field(
                tag = '365',
                indicators = [' ',' '],
                subfields = [
                    'b', l[4:]
                ]))
    elif l.startswith('529 '):
        log("** Notiz", l[4:])
        # Preis
        record.add_field(Field(
                tag = '770',
                indicators = ['1',' '],
                subfields = [
                    'n', l[4:]
                ]))

    elif l.startswith('700o'):
        log("** Seitenzahl/Länge", l[4:])
        # Seitenzahl
        record.add_field(Field(
                tag = '84',
                indicators = [' ',' '],
                subfields = [
                    'a', l[4:]
                ]))

    elif l.startswith('750 '):
        log("** Zusammenfassung", l[4:])
        # Seitenzahl
        record.add_field(Field(
                tag = '520',
                indicators = [' ',' '],
                subfields = [
                    'a', l[4:]
                ]))
    elif l.startswith('750f'):
        log("** Rezension", l[4:])
        # Seitenzahl
        record.add_field(Field(
                tag = '520',
                indicators = ['1',' '],
                subfields = [
                    'a', l[4:]
                ]))

    elif l.startswith('902s'):
        log("** Schlagword", l[4:])
        # Seitenzahl
        record.add_field(Field(
                tag = '650',
                indicators = ['0','0'],
                subfields = [
                    'a', l[4:]
                ]))
    else:
        notimpl[l[:4]] = l[4:]
    if l[:3].isdigit():
        last = l[:4]

conn.close()

with open('marcout.mrc', 'ab') as o:
    o.write(record.as_marc())

if len(notimpl) > 0:
    print( "not yet implemented: ")
    for k,v in notimpl.items():
        print(k,v)

for k in records:
    print(k, ': ', records[k])
