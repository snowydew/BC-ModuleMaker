import yaml
import csv

output_lines = []    
#Load yaml
with open("bc-en.yaml","r",encoding='utf8') as file:
    data = yaml.safe_load(file)
gdata = data['gacha']

#Read fixed list
with open('gtd.csv', 'r',encoding='utf8') as file:
    reader = csv.reader(file)
    fixed_g = list(reader)

#write fixed list to output
for i in fixed_g:
    output_lines.append(i[:2]+['']+i[2:]+['']+gdata[int(i[1])])

#write recent gatchas
recent_g = [i for i in data['events'].values()][-10:]
for row in recent_g:
    line = [row['name']+" ("+str(row['start_on'])+")",row['id'],""]
    line.append(int((10000-(row['rare']+row['supa']+row['uber'])))/100)
    line.append(row['uber']/100)
    line.append(row['supa']/100)
    line = line + [''] + gdata[int(row['id'])]
    output_lines.append(line)
    
#Write output file
with open("gatyaout.csv",mode="w",encoding='utf8') as outfile:
    wr = csv.writer(outfile,lineterminator = '\n')
    for line in output_lines:
        wr.writerow(line)