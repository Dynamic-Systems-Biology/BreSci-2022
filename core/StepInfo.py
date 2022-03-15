
class StepInfo:
    """
        Class that holds information of each step from Anguix, 
        like how many reactions into sabio, time that took to process 
        the data, etc...
    """

    __slots__ = ['step_name', 'value', 'unit']

    def __init__(self, step_name: str, value, unit: str = '') -> None:
        self.step_name = step_name
        self.value     = value
        self.unit      = unit
    
    def __str__(self) -> str:
        return f'{self.step_name}: {self.value} {self.unit}'
