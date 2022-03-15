from typing import List
import pandas as pd
import regex as re
from json import dumps as json_dumps

from .NumpyEncoder import NumpyEncoder

class NodeCreator:
    
    def __init__(self) -> None:
        self._parent_cols    = [ 'SabioReactionID', 'EntryID', 'ReactomeReactionID', 'Pathway', 'ECNumber','Enzymename', 'Product', 'ReactionEquation']
        self._child_rem_cols = ['SabioReactionID', 'ReactomeReactionID', 'Pathway', 'ECNumber','Enzymename', 'Product', 'ReactionEquation']
        self._child_groupby  = ['PubMedID', 'EnzymeVariant', 'KineticMechanismType']
        self._parent_groupby = ['SabioReactionID']
    
    def _create_query_parent_node(self, parent: pd.DataFrame, i: int):
        properties = parent.to_dict()
        
        if 'Enzymename' in properties:
            properties['EnzymeName'] = properties.pop('Enzymename')
        
        #properties['ReactomeReactionID'] = eval(properties.pop('ReactomeReactionID'))
        
        match_query = ''
        reactome_relashionship = ''
        parent_node = f'p{i}'
        
        for j, reactome_id in enumerate(properties['ReactomeReactionID']):
            if j:
                match_query += ', '
                reactome_relashionship += ', '
            
            reaction = 'r' + str(j)+str(i)
            match_query += f'({reaction}:Reaction{{stId:"{reactome_id}"}})'
            reactome_relashionship += f'({parent_node})-[:GeneralReactionFor]->({reaction})'
        
        properties = json_dumps(properties, ensure_ascii=False, cls=NumpyEncoder)
        properties = re.sub(r'"([aA-zZ. ]+)":', r'\1:', properties)
        
        create_query = f"({parent_node}:SabioRkReaction{properties}), {reactome_relashionship}"
        
        return create_query, match_query

    def _create_parameter_node(self, info: pd.DataFrame, child_label: str, parent_label: str):
        
        properties = info.iloc[0].dropna().to_dict()
        
        for key in info.columns:
            new_key = key.split('.')[1]
            properties[new_key] = properties.pop(key)
        
        properties = json_dumps(properties, ensure_ascii=False, cls=NumpyEncoder)
        properties = re.sub(r'"([aA-zZ0-9. ]+)":', r'\1:', properties)
        
        return f"({child_label}:SabioRKReactionParameter{properties}), ({parent_label})-[:ParameterInfo]->({child_label})"
        
    def _create_query_child_node(self, child: pd.DataFrame, child_id: int, parent_id: int):
        
        parameters_cols = child.filter(regex=("parameter.*|EntryID"))
        main_info       = child.drop(parameters_cols, axis=1)

        properties   = main_info.iloc[0].dropna().to_dict()
        parent_label = f'c{str(parent_id)+str(child_id)}'
        properties   = json_dumps(properties, ensure_ascii=False, cls=NumpyEncoder)
        properties   = re.sub(r'"([aA-zZ0-9. ]+)":', r'\1:', properties)
        query = f", ({parent_label}:SabioRKReactionKinectics{properties}), ({parent_label})-[:KinecticDatafor]->(p{parent_id})"
        
        for i in range(parameters_cols.shape[0]):
            data        = parameters_cols.iloc[[i]].dropna(axis=1)
            entryId     = data.iloc[0]['EntryID']
            child_label = f'pn{entryId}{i}'
            query      += ',\n' + self._create_parameter_node(data.drop(['EntryID'], axis=1), child_label, parent_label)

        return query

    def create_queries(self, df: pd.DataFrame)-> List[str]:
        
        df.columns        = df.columns.str.replace(' ', '')
        group_by_sabio_id = df.groupby(self._parent_groupby)
        queries = []
        
        for i, item in enumerate(group_by_sabio_id):
            group: pd.DataFrame  = item[1]
            parent: pd.DataFrame = group[self._parent_cols].iloc[0].dropna()
            parent_id = parent['EntryID']
            
            create_query, match_query = self._create_query_parent_node(parent, parent_id)
            children = group.groupby(self._child_groupby)
            
            for j, item in enumerate(children):
                child = item[1].drop(self._child_rem_cols, axis=1)
                create_query += self._create_query_child_node(child, j, parent_id) + '\n'

            queries.append(f'MATCH {match_query} \nCREATE {create_query}')
        
        return queries

