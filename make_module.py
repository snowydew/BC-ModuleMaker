import os
import glob
import pandas as pd
import shutil

#Filenames
talents_file = "./Raw/DataLocal/SkillAcquisition.csv"
info_file = "./Raw/DataLocal/unitbuy.csv"
catnamelist_files = glob.glob("./Raw/resLocal/Unit_Explanation*.csv")

#Using UnitExplanation to determine language in EN/JP
testfile = "./Raw/resLocal/Unit_Explanation1_"
if os.path.isfile(testfile+"ja.csv"):
    Gtype = "JP"
elif os.path.isfile(testfile+"en.csv"):
    Gtype = "EN"
else:
    print("No valid EN/JP files")

#Version +revision number
version = input("Enter Version Number : ")
rev = 1

#Create new directory if it does not exist
dir = "./"+Gtype
if not os.path.exists(dir):
    os.mkdir(dir)
    print("Making new directory for "+Gtype)
dir += "/"+version
if not os.path.exists(dir):
    os.mkdir(dir)
    print("Making new directory")
else:
    #Find revision number
    while rev<100 and os.path.isfile(dir+"/output_"+str(rev)+".xlsx"):
        rev += 1
    print("This is revision "+str(rev)+" of version "+version)
    
#ManMod is for Manual Module Setup.
cat_id_list = "./ManMod/"+Gtype+"/ids.csv"
xpm_file = "./ManMod/"+Gtype+"/xp_modes.csv"
talentname_file = "./ManMod/"+Gtype+"/talentnames.csv"
talentver_file = "./ManMod/"+Gtype+"/talent_ver.csv"
gatyaset_file = "./ManMod/"+Gtype+"/gatya_set.csv"  

#Read files
talents = pd.read_csv(talents_file, encoding = "ISO-8859-1",skipfooter=1,engine = 'python')
info = pd.read_csv(info_file, encoding = "ISO-8859-1",header=None,skipfooter=1,engine = 'python') #No header
xp_modes = pd.read_csv(xpm_file)
cat_id = pd.read_csv(cat_id_list)
talentnames = pd.read_csv(talentname_file,header=None) #No header
talentver = pd.read_csv(talentver_file)
gatyaset = pd.read_csv(gatyaset_file,header=None) #No header

#Talentnames to dict {'talentID':'talentname'}
talentnames = dict(talentnames.to_dict('split')['data'])

#Set Cat ID to index of dataframe
info['CID'] = info.index

#Boostable (1 if column 51> 0)
info['Boostable'] = [1 if x>0 else 0 for x in info[51]]

#XP modes (Left merge with xp_modes.csv)
info = pd.merge(
    info,xp_modes,
    left_on=[i for i in range(2,12)],
    right_on=[str(i) for i in range(1,11)],
    how='left')

#TalentVer merge
info = pd.merge(info,talentver,left_on=['CID'],right_on=['ID'],how='left')

#New columns for fruit and talents and names
info['Fruit'] = pd.Series().astype(object)
info['Talents'] = pd.Series().astype(object)
info['Basic']= "TBA"
info['Evolved'] = "TBA"
info['TrueForm'] = ""
info['Gatcha'] = 0

#Fruit handling (column 28-38)
fruit_map = {30:7,31:8,32:9,33:10,34:11,35:2,36:3,37:4,38:5,39:6,40:12,41:1,42:0}
for i,row in info.iterrows():
    fruits = [0,0,0,0,0,0,0,0,0,0,0,0,0]
    for j in range(5):
        if(row[2*j+28] in fruit_map):
            fruits[fruit_map[row[2*j+28]]] = row[2*j+29]
    info.at[i,'Fruit'] = fruits
    
#Gatcha set 
for i,row in gatyaset.iterrows():
    for id in row:
        if id>0:
            info.at[int(id),'Gatcha'] = i+1

#Talents
for i,row in talents.iterrows():
    info.at[int(row['ID']),'Talents'] = [talentnames[int(row["textID_"+i])] for i in ["A","B","C","D","E"]]

#Write Cat names to dataframe
for f in catnamelist_files:
    #Variations across different versions ["delimiter","_x.csv"]
    p = [",","_j"] if Gtype=="JP" else ["|","_e"]
    
    row_id = int(f[f.find("on")+2:f.find(p[1],20)])-1
    
    #Delimiter "|" for EN     "," for JP
    name_l = pd.read_csv(f,header = None,delimiter=p[0])[0]
    
    #Write names
    info.at[row_id,"Basic"] = name_l[0]
    info.at[row_id,"Evolved"] = name_l[1]
    if(len(name_l)>2 and name_l[1] != name_l[2] and len(str(name_l[2]))>0):
        info.at[row_id,"TrueForm"] = name_l[2]

#Sort order + determine Rarity
info = info.sort_values(14)
info['Rarity'] = (info[14]/1000).astype(int)


#Final output = Merge with cat_id list
#Keep CID,Boostable,TF,MaxLvl,XP_Mode ID,Fruit,Fruit_XP,Talents
#Drop all N/A rows
keepColumns = ['CID','Basic','Evolved','TrueForm','Gatcha','Rarity','Boostable',12,14,50,'XP_ID','Fruit',27,'Talents','TalentVer']
info = info[keepColumns].dropna(subset=['Boostable','Basic'])

#Assign LocID
rarityname = ['B','E','R','S','U','L']
info.insert(1,'LocID',0)
for r in range(6):
    info['Rank'] = info[14][info['Rarity']==r].rank(ascending=True,na_option='keep')
    info['LocID'] += [int(x) if x>0 else 0 for x in info['Rank']]
info['LocID'] = [rarityname[int(x)] for x in info['Rarity']]+info['LocID'].astype(str) 


#Expand fruit,talents and merge
info = pd.concat([
    info.drop(['Fruit','Talents','Rank','Rarity',27,14,'TalentVer'],axis=1),
    info['Fruit'].apply(pd.Series),
    info[[27,'TalentVer']],
    info['Talents'].apply(pd.Series)
    ],axis=1)

 
info.to_excel(dir+"/output_"+str(rev)+".xlsx",header = None,index = False)

#Move files to backup
end1 = input("Would you like to move Raw game files to Version Folder? Y or N : ")

if end1.upper() == 'Y':
    #Check if backup already exists
    if(os.path.exists(dir+"/Backup")):
        print("Backup already exists")
    else:
        os.rename("./Raw","./Backup")
        shutil.move("./Backup",dir)
        #Create new /Raw folder
        os.mkdir("./Raw")
        print("Moved files")

print("Script has finished")