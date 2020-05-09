#! /usr/bin/env python3
import pandas as pd

f_path = 'py/question.txt'
cols = ['序号','题目','A','B','C','D','正确选项']
# rows = [[1,'Title-1','Opt-A','Opt-B','Opt-C','Opt-D','C'],[2,'Title-2','Opt-A','Opt-B','Opt-C','Opt-D','D'],[3,'Title-3','Opt-A','Opt-B','Opt-C','Opt-D','A'],[4,'Title-4','Opt-A','Opt-B','Opt-C','Opt-D','B']]

with open(f_path,'r') as f:
    msg = f.read()
linemsg=msg.split('\n')

lst = ['','','','','','','']
rule = {'A':2,'B':3,'C':4,'D':5,}

data = []

for id in range(len(linemsg)):
    line = linemsg[id].strip()
    if line == '':continue

    if line[0] == '试':
        lst[-1] = line[-1]
        data.append(lst)
        lst = ['','','','','','','']
        continue

    if line[0] in rule:
        optidx = rule[line[0]]
        lst[optidx] = line[2:]
    else:
        try:
        except :
            print(line)
            continue
        lst[0] = title
        lst[1] = content

df = pd.DataFrame(data=data,columns=cols)
df.to_excel('mytest.xlsx')
