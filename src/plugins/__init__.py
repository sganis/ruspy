import os

DIR = os.path.dirname(os.path.realpath(__file__))

module_list = [name[:-3] for name in os.listdir(DIR) 
    if name != '__init__.py' and name.endswith('.py')]
