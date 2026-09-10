     




#imports
import sys
import random
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib
import os

#importing task code
sys.path.insert(0, 'E:/data6/ind-spacevtime/SGabor/')
from SGabor import runSG
sys.path.insert(0, 'E:/data6/ind-spacevtime/SLetter/')
from SLetter import runSL
sys.path.insert(0, 'E:/data6/ind-spacevtime/SPi/')
from SPi import runSP
sys.path.insert(0, 'E:/data6/ind-spacevtime/TGabor/')
from TGabor import runTG
sys.path.insert(0, 'E:/data6/ind-spacevtime/TLetter/')
from TLetter import runTL
sys.path.insert(0, 'E:/data6/ind-spacevtime/TPi/') 
from TPi import runTP



dbConf=exlib.data6
expName="indSVT"
n_practices = 50

n_trials = 50
refreshRate=165
exlib.setRefreshRate(refreshRate)
pool = 3
[pid,_,_]=exlib.startExp(expName,dbConf,pool,lockBox=True,refreshRate=refreshRate)
session = 0
fileCheck = f"E:/data6/ind-spacevtime/SGabor/Data/{pid}_SGabor.csv"
if os.path.exists(fileCheck):
    with open(f"E:/data6/ind-spacevtime/SGabor/Data/{pid}_SGabor.csv",'r') as f:
        line_count = sum(1 for line in f)
        session = line_count//n_trials + 1
print('Current session: ', session)


functions = [runSG, runSL, runSP, runTG, runTL, runTP]
random.shuffle(functions)
for func in functions:
    func(session, pid, n_practices, n_trials)
