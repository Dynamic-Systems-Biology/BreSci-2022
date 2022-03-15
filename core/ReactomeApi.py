import requests
import pandas as pd

from requests.structures import CaseInsensitiveDict

class ReactomeApi:
    """"Responsible for making calls to the Reactome's API"""

    __slots__ = []
    BASE_URL  = 'https://reactome.org/ContentService'

    def __init__(self) -> None:
        pass

    def fetch_organisms_list(self) -> pd.DataFrame:
        """Fetch the current Reactome organisms list available.

        Returns:
            list: data frame with two columns displayName and abbreviation
        """

        headers  = CaseInsensitiveDict({ 'accept': 'application/json' })
        response = requests.get(f'{ReactomeApi.BASE_URL}/data/species/all', headers=headers)
        df = pd.read_json(response.text)

        return df[['displayName', 'abbreviation']]


    def fetch_organism_abbreviation(self, organism: str)-> str:
        """This function receives an organism and fetch it's 
        Reactome abbreviator. Important to do regex cleansing.

        Args:
            organism (str): [description]

        Returns:
            str: organism's abbreviation
        """
        headers  = CaseInsensitiveDict({ 'accept': 'application/json' })
        response = requests.get(f'{ReactomeApi.BASE_URL}/data/species/all', headers=headers)

        df = pd.read_json (response.text)
        index = df.index[df['displayName'].str.lower() == organism]

        return df['abbreviation'].iloc[index].values[0]