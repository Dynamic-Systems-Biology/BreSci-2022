from typing import List, Tuple
import pandas as pd
import time

from core.StepInfo import StepInfo
from core.Neo4jDB import Neo4jDB
from core.NodeCreator import NodeCreator

from .StepInfo import StepInfo
from .ReactomeApi import ReactomeApi
from .SabioRkApi import SabioRkApi

class AnguixBaseFormat:

    def __init__(self) -> None:
        self._reactomeApi = ReactomeApi()
        self._sabioRkApi  = SabioRkApi()
        self._nodeCreator = NodeCreator()
        self._neo4jDB     = Neo4jDB()

    def fetch_organisms_list(self) -> Tuple[pd.DataFrame, int, int]:
        """Get all Reactome and SabioRK organisms, but 
        return only those that are common to each other.

        Returns:
            Tuple[list, int, pd.DataFrame]: 
                - data frame of available organisms to Anguix with two columns: displayName, abbreviation 
                - size of reactome list 
                - size of SabioRK list 
        """

        reactome_df  = self._reactomeApi.fetch_organisms_list()
        sabioRkList  = self._sabioRkApi.fetch_organisms_list()
        common_index = reactome_df['displayName'].str.lower().isin(sabioRkList) 

        return reactome_df[common_index], reactome_df.shape[0], len(sabioRkList)

    def work(self, organism: pd.DataFrame)-> List[StepInfo]:
        """Download and process SabioRK's data

        Args:
            organism (pd.DataFrame): row of a dataframe with two columns: displayName, abbreviation

        Returns:
            List[StepInfo]: List of information of each step
        """
        
        df, stats = self._sabioRkApi.fetch_data_from(
            organism['displayName'].lower(), organism['abbreviation']
        )
        
        print('Generating queries...')
        start = time.time()
        queries = self._nodeCreator.create_queries(df)
        end = time.time()
        
        stat = StepInfo(f'Time Spent on generating queries', round((end - start)/60, 3), 'min.')
        stats.append(stat)
        
        print('Saving into the database...')
        start = time.time()
        self._neo4jDB.insert(queries)
        end = time.time()
        
        stat = StepInfo(f'Time Spent on saving into the database', round((end - start)/60, 3), 'min.')
        stats.append(stat)
        
        return stats

