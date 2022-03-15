import re
from typing import List, Tuple
import requests
import xml.etree.ElementTree as etree
import pandas as pd
import time

from io import StringIO
from .StepInfo import StepInfo

class SabioRkApi:
    """"Responsible for making calls to the SabioRK's API"""

    __slots__ = []
    BASE_URL  = "http://sabiork.h-its.org/sabioRestWebServices"

    def __init__(self) -> None:
        pass

    def fetch_organisms_list(self):
        """Fetch all organism names available on Sabio RK

        Returns:
            [list]: list containing organisms names avai
        """
        
        query = {
            'fields[]': ['Organism']
        }
        
        response = requests.post(f'{SabioRkApi.BASE_URL}/suggestions/Organisms', params=query)
        response.raise_for_status()

        tree      = etree.fromstring(response.text)
        organisms = [ organism.text.strip() for organism in tree.findall('Organism') ]

        return organisms

    def fetch_data_from(self, organism: str, abbreviation: str)-> Tuple[str, List[StepInfo]]:
        """Fetch SabioRK data from an specific organism and then 
        saves only entries that has an ReactomeReactionID

        Args:
            organism (str): organism name
            abbreviation (str): organism's abbreviation
        Returns:
            pd.DataFrame: clean data frame
            List[StepInfo]: some list of info
        """

        query = {
            'format':'tsv', 
            'fields[]':[
                'ReactomeReactionID','EntryID','SabioReactionID','ECNumber','Enzymename','Enzyme Variant', 'Parameter', 'UniprotID','ReactionEquation','Substrate','Product','Cofactor','Activator','Inhibitor','Other Modifier','CellularLocation', 'PubMedID','Publication', 'Buffer','Temperature','pH','KeggReactionID','KineticMechanismType','Rate Equation','Tissue', 'Pathway'
            ],
            'q': f'Organism:"{organism}"'
        }

        content, stat = self.__do_request(f'{SabioRkApi.BASE_URL}/kineticlawsExportTsv', query)

        # file_name  = f'tmp/{organism}_pre_anguix_base.csv'
        csv_output = re.sub(r"\t", r"|", content)

        df, stats = self.__clean_data(pd.read_csv(StringIO(csv_output), sep='|'), organism, abbreviation)
        # df.to_csv(file_name, sep='|', encoding='utf-8', index=False)

        stats.append(stat)
        stats.insert(0, StepInfo('Organism Name', organism))

        return df, stats

    def __clean_data(self, df: pd.DataFrame, organism: str, abbreviation: str)-> Tuple[pd.DataFrame, List[StepInfo]]:
        """This function makes three things:
            1 - Remove rows that doesn't have ReactomeReactionID
            2 - Each ReactomeReactionID column may have more then one reactomeReactionID so,
                for each one create another row with it.
            3 - Remove all entries that's ReactomeReactionID isn't from organism's abbreviation 
        Args:
            df (pd.DataFrame): Dataframe that contains the data
            abbreviation (str): organism's abbreviation
        Returns:
            pd.DataFrame: new clean dataframe
            List[StepInfo]: some info about this step
        """
        n_sabio_reac = df['EntryID'].nunique()
        
        start = time.time()

        df = df.dropna(subset=['ReactomeReactionID'])

        n_sabio_reac_avlb = df['EntryID'].nunique()
        
        mask = df.ReactomeReactionID.astype(str).str.contains(f'R-{abbreviation}-[0-9]+')
        df   = df[mask]
        
        remove_other_organism = lambda reactome_id_list: re.findall(f'R-{abbreviation}-[0-9]+', reactome_id_list)
        
        df  = df.assign(ReactomeReactionID=df['ReactomeReactionID'].apply(remove_other_organism))
        end = time.time()
        
        stat2 = StepInfo(f'Sabio-RK Total Reactions', n_sabio_reac)
        stat3 = StepInfo(f'Reactions Available To Anguix', n_sabio_reac_avlb)
        stat1 = StepInfo(f'Time Spent on Anguix Data Processing', round(end - start, 3), 'seconds')
        
        return df, [stat2, stat3, stat1]
    
    def __do_request(self, url: str, query: dict)-> Tuple[requests.Response, StepInfo]:
        """download the data

        Args:
            url (str): url of the data
            query (dict): query

        Returns:
            requests.Response: the response
            StepInfo: info about the time spent
        """
        
        start = time.time()
        response = requests.post(url, params=query)
        response.raise_for_status()
        end = time.time()
        
        stat = StepInfo(
            f'Time Spent on downloading SABIO-RK data',
            round((end - start)/60, 3),
            'min.'
        )

        return response.text, stat
