import csv
with open("MedienListe-exp_20170504-utf8.csv", 'r') as f:
    myr = csv.DictReader(f, delimiter=';')
    heads = ["TITEL",	"TITEL2",	"DEWEYNR",	"STANDORT",	"STYP",	"SNUMMER",	"HETYP",	"HEBENE",	"OST",	"ERSCHJAHR"]
    for line in myr:
        if len(line) > 40:
            print(len(line))
            for i in range(len(line) - 39):
                print(line[heads[i]])
            print("#"*50)
        #print(len(list(line)))
