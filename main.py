import time 
import pandas as pd
from core.AnguixBaseFormat import AnguixBaseFormat
from util import getIntInput, print_stats, print_organism_list
from dotenv import load_dotenv

load_dotenv()

apbf = AnguixBaseFormat()
print("Loading some data...\n")

organismsAvailable_df, reactomeSize, sabioSize = apbf.fetch_organisms_list()

msg  = f'There is {sabioSize} organisms available in SABIO-RK and {reactomeSize} organisms available in Reactome\n'
msg += f'In which, {organismsAvailable_df.shape[0]} are available to be added on Reactome Graph Database using Anguix.\n'

print(msg)

mode = str(input('Please, choose an operation mode (Auto, Manual or Custom): '))
statistics = []

if mode == 'Manual':
    print('You chose the Manual mode, please select an organism that you desire to add to Reactome Graph Database: ')
    print_organism_list(organismsAvailable_df['displayName'])

    option = getIntInput('\nOption: ')

    while option < 0 or option > len(organismsAvailable_df):
        print('Invalid Option!')
        option = getIntInput('Option: ')

    organism = organismsAvailable_df.iloc[option]

    print(f'Organism Name: {organism["displayName"]} -> Abbreviation: {organism["abbreviation"]}')
    print('Downloading data...')

    start = time.time()
    stats = apbf.work(organism)
    end   = time.time()

    statistics.append(stats)
    print(f'Took {round((end-start)/60, 3)} minutes.')

elif mode == 'Auto':

    organismsAvailable_df.style.set_properties({'text-align': 'left'})
    pd.set_option('display.max_rows', None)

    print("You chose the Auto mode, please note that all organisms in common to both Reactome and SABIO-RK will be added: ")
    print (f"This is the available organisms list:")
    print_organism_list(organismsAvailable_df['displayName'])
    
    pd.set_option('display.max_rows', 10)

    print('Working on it...\n')
    
    start = time.time()
    for i in range(organismsAvailable_df.shape[0]):

        n = i+1
        organism = organismsAvailable_df.iloc[i]
        progress = '- Organism Name: {:30} Abbreviation: {}'.format(organism["displayName"], organism["abbreviation"])
        
        print(f'{n if (n > 9) else "0" + str(n)}/{organismsAvailable_df.shape[0]} {progress}')

        stats = apbf.work(organism)
        statistics.append(stats)
    end = time.time()

    print(f'\nTook {round((end-start)/60, 3)} minutes.')

elif mode == 'Custom':
    pass

print_stats(statistics)