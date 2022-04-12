import pandas as pd
import time
from typing import List
from core.StepInfo import StepInfo

def print_organism_list(organisms):
    print('\n')
    for idx, key in enumerate(organisms):
        
        i = f'0{idx}' if idx < 10 else idx
        
        if (idx + 1) % 3:
            print('{} - {:30}'.format(i, key), end='\t')
        else:
            print(f'{i} - {key}', end='\n')
    print('\n')

def print_stats(stats: List[List[StepInfo]]) -> None:

    start  = time.time()
    header = []
    body   = []
    
    print('\n================= SOME INFORMATION =================\n')

    for i in range(len(stats)):
        sts = stats[i]
        row = []

        for j in range(len(sts)):
            if i == 0:
                unit = f' ({sts[j].unit})' if sts[j].unit else ''
                header.append(f'{sts[j].step_name}{unit}')

            row.append(sts[j].value)
            print(sts[j])

        print('\n')
        body.append(row)

    dframe = pd.DataFrame(body, columns=header)
    dframe.to_csv('tmp/Anguix_Eficiency_Report.csv', index=False) 
    
    end = time.time()
    print('====================================================\n')

    print(f'Time Spent to print statistics: {round(end - start, 3)} seconds\n')

def getIntInput(msg: str):
    value = input(msg)
    while not value.isnumeric():
        print("Invalid option!")
        value = input(msg)
    return int(value)