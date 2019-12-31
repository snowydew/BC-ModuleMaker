import os
import glob
import pandas as pd
import shutil

#Cat Order is done by ordering column 15 by smallest to largest, then doing a count besides them.
#(B)Basic (0-8)
#(E)Special (1000-1999)
#(R)Rare (2000-2999)
#(S)Super Rare (3000-3999)
#(U)Uber Rares (4000-4999)
#(L)Legends (5000-5999)

#Sets the location of the csv with cat guide location
info_file = "./Raw/DataLocal/unitbuy.csv"

#Sets csv read information
data = pd.read_csv(info_file, encoding = "ISO-8859-1",header=None,skipfooter=1,engine = 'python',)

#Selects the column (15-1) for the order, turns it into numeric data to sort properly.
ids = pd.to_numeric(data[14],errors='coerce')

#Orders all values, offset count is done in order, cat id is pushed to the left side.
ids_sort = ids.sort_values(ascending=True)

#Renames the header for the sorted data as GameID.
ids_finished = ids_sort.rename('GameID')

#This makes the directories for the modules if they are not there.
if not os.path.isdir("./Module"):
    os.mkdir("./Module")

#Manual Input of version number for now
version = input("Enter Version Number : ")

#This checks which version of the game files you have, then makes directories for them.
if os.path.isfile("./Raw/resLocal/Unit_Explanation1_en.csv"):
    if not os.path.isdir("./Module/EN"):
        os.mkdir("./Module/EN")
        os.mkdir("./Module/EN/"+version)
        Gtype = "./Module/EN/"+version
    if not os.path.isdir("./Module/EN/"+version):
        os.mkdir("./Module/EN/"+version)
        Gtype = "./Module/EN/"+version
    Gtype = "./Module/EN/"+version
elif os.path.isfile("./Raw/resLocal/Unit_Explanation1_ja.csv"):
    if not os.path.isdir("./Module/JP"):
        os.mkdir("./Module/JP")
        os.mkdir("./Module/JP/"+version)
        Gtype = "./Module/JP"+version
    if not os.path.isdir("./Module/JP/"+version):
        os.mkdir("./Module/JP/"+version)
        Gtype = "./Module/JP"+version
    Gtype = "./Module/JP"+version

#Saves the ids.csv for use in the modulemaker.
ids_finished.to_csv(Gtype+"/ids.csv", header=True,index_label='CatID')