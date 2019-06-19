from pymarc import MARCReader
with open('marcout.mrc', 'rb') as fh:
    reader = MARCReader(fh)
    for record in reader:
        print(record)
