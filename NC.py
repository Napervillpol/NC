import requests
import json
import pandas as pd
from lxml import etree

from zipfile import ZipFile
from urllib.request import urlopen

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sb
sb.set()
pd.options.mode.chained_assignment = None

def write_to_excel(race,race_name):
    writer = pd.ExcelWriter('NC_'+race_name+ '.xlsx', engine='xlsxwriter')

    race.mail.to_excel(writer,sheet_name="Mail",index=False)
    race.eday.to_excel(writer,sheet_name="Election Day",index=False)
    race.advance.to_excel(writer,sheet_name="One Stop",index=False)
    race.prov.to_excel(writer,sheet_name="Provisonal",index=False)
    race.total.to_excel(writer,sheet_name="Total",index=False)

    writer.save()

def safediv(x,y):
    try:
        return x/y
    except ZeroDivisionError:
        return 0
class race:
    mail=[]
    eday=[]
    advance=[];
    prov=[]
    total=[]
    def __init__(self, mail,eday,advance,prov,total):
        self.mail=mail
        self.eday=eday
        self.advance=advance
        self.prov=prov
        self.total=total

def assign_race(Dem,Rep,Dem_name,Rep_name):
       
    #Mail 
    Dem_mail = Dem[['County','Absentee by Mail']]
    Dem_mail.columns=['County',Dem_name]

    Rep_mail = Rep[['County','Absentee by Mail']]
    Rep_mail.columns=['County',Rep_name]
    mail = Dem_mail.merge(Rep_mail, on='County')
    calculations(mail,Dem_name,Rep_name)
   
    #Election day
    Dem_eday = Dem[['County','Election Day']]
    Dem_eday.columns=['County',Dem_name]

    Rep_eday = Rep[['County','Election Day']]
    Rep_eday.columns=['County',Rep_name]
    eday = Dem_eday.merge(Rep_eday, on='County')
    calculations(eday,Dem_name,Rep_name)

    #Advance
    Dem_advance = Dem[['County','One Stop']]
    Dem_advance.columns=['County',Dem_name]

    Rep_advance  = Rep[['County','One Stop']]
    Rep_advance.columns=['County',Rep_name]
    advance = Dem_advance.merge(Rep_advance, on='County')
    calculations(advance,Dem_name,Rep_name)

    #Provisonal
    Dem_prov= Dem[['County','Provisional']]
    Dem_prov.columns=['County',Dem_name]

    Rep_prov = Rep[['County','Provisional']]
    Rep_prov.columns=['County',Rep_name]
    prov = Dem_prov.merge(Rep_prov, on='County')
    calculations(prov,Dem_name,Rep_name)

     #Total
    Dem_total= Dem[['County','Total Votes']]
    Dem_total.columns=['County',Dem_name]

    Rep_total = Rep[['County','Total Votes']]
    Rep_total.columns=['County',Rep_name]
    total = Dem_total.merge(Rep_total, on='County')
    calculations(total,Dem_name,Rep_name)

    Race = race(mail,eday,advance,prov,total)
    return Race;

def calculations(df,Dem_name,Rep_name):
   
    df[Dem_name]=df[Dem_name].astype(str)
    df[Rep_name]=df[Rep_name].astype(str)
    
    df[Dem_name]=df[Dem_name].str.replace(',','')
    df[Rep_name]=df[Rep_name].str.replace(',','')

    df[Dem_name]=df[Dem_name].astype(int)
    df[Rep_name]=df[Rep_name].astype(int)
    
    df.insert(3, "Total", df[Dem_name]+df[Rep_name])
    df.insert(4, "Net Votes", df[Dem_name]-df[Rep_name])
    df.insert(5, Dem_name+" Pct", df[Dem_name]/(df[Dem_name]+df[Rep_name]))
    df.insert(6, Rep_name+" Pct", df[Rep_name]/(df[Dem_name]+df[Rep_name]))
    df.insert(7, "Margin",(df[Dem_name]/(df[Dem_name]+df[Rep_name])) -(df[Rep_name]/(df[Dem_name]+df[Rep_name])))

def calculate_shift(df_2022,df_2020):
     
     df_2022.mail.insert(8, "Pct Shift",df_2022.mail["Margin"]-df_2020.mail["Margin"])
     df_2022.mail.insert(9, "Turnout",df_2022.mail["Total"]/df_2020.mail["Total"])

     df_2022.eday.insert(8, "Pct Shift",df_2022.eday["Margin"]-df_2020.eday["Margin"])
     df_2022.eday.insert(9, "Turnout",df_2022.eday["Total"]/df_2020.eday["Total"])

     df_2022.advance.insert(8, "Pct Shift",df_2022.advance["Margin"]-df_2020.advance["Margin"])
     df_2022.advance.insert(9, "Turnout",df_2022.advance["Total"]/df_2020.advance["Total"])

     df_2022.prov.insert(8, "Pct Shift",df_2022.prov["Margin"]-df_2020.prov["Margin"])
     df_2022.prov.insert(9, "Turnout",df_2022.prov["Total"]/df_2020.prov["Total"])

     df_2022.total.insert(8, "Pct Shift",df_2022.total["Margin"]-df_2020.total["Margin"])
     df_2022.total.insert(9, "Turnout",df_2022.total["Total"]/df_2020.total["Total"])


url = 'https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2020_11_03/results_pct_20201103.zip'

r = requests.get(url)

filename = url.split('/')[-1]  # this will take only -1 splitted part of the url

with open(filename, 'wb') as output_file:
    output_file.write(r.content)

zf = ZipFile('results_pct_20201103.zip', 'r')
zf.extractall()
zf.close()

df1 = pd.read_csv("results_pct_20201103.txt", sep="\t")

Biden =df1.loc[(df1['Contest Name']  =='US PRESIDENT' ) & (df1['Choice Party']  =='DEM' )]
Trump =df1.loc[(df1['Contest Name']  =='US PRESIDENT' ) & (df1['Choice Party']  =='REP' )]

Cal =df1.loc[(df1['Contest Name']  =='US SENATE' ) & (df1['Choice Party']  =='DEM' )]
Tillis =df1.loc[(df1['Contest Name']  =='US SENATE') & (df1['Choice Party']  =='REP' )]

Cooper =df1.loc[(df1['Contest Name']  =='NC GOVERNOR' ) & (df1['Choice Party']  =='DEM' )]
Forest =df1.loc[(df1['Contest Name']  =='NC GOVERNOR') & (df1['Choice Party']  =='REP' )]

Biden = Biden.groupby(Biden['County'])[['Election Day','One Stop','Absentee by Mail','Provisional','Total Votes']].sum().reset_index()
Trump =Trump.groupby(Trump['County'])[['Election Day','One Stop','Absentee by Mail','Provisional','Total Votes']].sum().reset_index()

Cal = Cal.groupby(Cal['County'])[['Election Day','One Stop','Absentee by Mail','Provisional','Total Votes']].sum().reset_index()
Tillis =Tillis.groupby(Tillis['County'])[['Election Day','One Stop','Absentee by Mail','Provisional','Total Votes']].sum().reset_index()

Cooper = Cooper.groupby(Cooper['County'])[['Election Day','One Stop','Absentee by Mail','Provisional','Total Votes']].sum().reset_index()
Forest =Forest.groupby(Forest['County'])[['Election Day','One Stop','Absentee by Mail','Provisional','Total Votes']].sum().reset_index()

President =assign_race(Biden,Trump,"Biden","Trump")
write_to_excel(President,"President")

Senate =assign_race(Cal,Tillis,"Cal","Tillis")
calculate_shift(Senate,President)
write_to_excel(Senate,"Senate")

Governor =assign_race(Cooper,Forest,"Cooper","Forest")
calculate_shift(Governor,President)
write_to_excel(Governor,"Governor")


#Plots

#Mail
plt.figure(1)
plt.title('Governor (Mail)')
plt.scatter(President.mail['Biden Pct'],Governor.mail['Cooper Pct'],Governor.mail['Total']/1000)

x = President.mail['Biden Pct'].reset_index()
y = Governor.mail['Cooper Pct'].dropna().reset_index()


Gov_graph =x.merge(y,on="index")
Gov_graph=Gov_graph.drop(columns=['index'])

x = Gov_graph['Biden Pct']
y = Gov_graph['Cooper Pct']

b, a = np.polyfit(x, y, deg=1)

xseq = np.linspace(0, 1,5)

plt.plot(xseq, a + b * xseq, color="k", lw=2.5);

x = np.linspace(0,1,5)
y = x
plt.plot(x, y, '-r', label='y=x+1')
plt.grid()
print(a)
plt.show()



#One Stop
plt.figure(2)
plt.title('Governor (One Stop)')
plt.scatter(President.advance['Biden Pct'],Governor.advance['Cooper Pct'],Governor.advance['Total']/1000)

x = President.advance['Biden Pct'].reset_index()
y = Governor.advance['Cooper Pct'].dropna().reset_index()

Gov_graph =x.merge(y,on="index")
Gov_graph=Gov_graph.drop(columns=['index'])

x = Gov_graph['Biden Pct']
y = Gov_graph['Cooper Pct']

b, a = np.polyfit(x, y, deg=1)

xseq = np.linspace(0, 1,5)

plt.plot(xseq, a + b * xseq, color="k", lw=2.5);

x = np.linspace(0,1,5)
y = x
plt.plot(x, y, '-r', label='y=x+1')
plt.grid()
print(a)
plt.show()

#Election Day
plt.figure(3)
plt.title('Governor (Election Day)')
plt.scatter(President.eday['Biden Pct'],Governor.eday['Cooper Pct'],Governor.eday['Total']/1000)

x = President.eday['Biden Pct'].reset_index()
y = Governor.eday['Cooper Pct'].dropna().reset_index()

Gov_graph =x.merge(y,on="index")
Gov_graph=Gov_graph.drop(columns=['index'])

x = Gov_graph['Biden Pct']
y = Gov_graph['Cooper Pct']

b, a = np.polyfit(x, y, deg=1)

xseq = np.linspace(0, 1,5)

plt.plot(xseq, a + b * xseq, color="k", lw=2.5);

x = np.linspace(0,1,5)
y = x
plt.plot(x, y, '-r', label='y=x+1')
plt.grid()
print(a)
plt.show()



#Total
plt.figure(4)
plt.title('Governor (Total)')
plt.scatter(President.total['Biden Pct'],Governor.total['Cooper Pct'],Governor.total['Total']/1000)

x = President.total['Biden Pct'].reset_index()
y = Governor.total['Cooper Pct'].dropna().reset_index()

Gov_graph =x.merge(y,on="index")
Gov_graph=Gov_graph.drop(columns=['index'])

x = Gov_graph['Biden Pct']
y = Gov_graph['Cooper Pct']

b, a = np.polyfit(x, y, deg=1)

xseq = np.linspace(0, 1,5)

plt.plot(xseq, a + b * xseq, color="k", lw=2.5);

x = np.linspace(0,1,5)
y = x
plt.plot(x, y, '-r', label='y=x+1')
plt.grid()
print(a)
plt.show()

