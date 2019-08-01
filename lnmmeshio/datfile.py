import numpy as np
from typing import List, Dict
from .ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value
from collections import OrderedDict
import re
from .element.element import Element
from .element.element_container import ElementContainer
from .node import Node
from .fiber import Fiber
from .progress import progress
from .discretization import Discretization
from .functions.function import Function
from .conditions.condition import ConditionsType
from .conditions.conditionreader import read_conditions
from .head import Head
from .result_description import ResultDescription

"""
This class holds all information in the datfiles, consisting out of the discretization, conditions
and options.
"""
class Datfile:
    
    def __init__(self):
        self.discretization = Discretization()

        # initialize functions
        self.functions: List[Function] = []

        # initialize conditions
        self.conditions: List[ConditionsType] = []

        # initialize result description
        self.result_description: List[ResultDescription] = []

        # initialize head
        self.head: Head = Head()
    
    """
    Computes the ids of the elements and nodes. 

    Args:
        zero_based: If true, the first node id is 0, otherwise 1
    """
    def compute_ids(self, zero_based: bool):
        
        self.discretization.compute_ids(zero_based)
        
        id: int = 0 if zero_based else 1
        for f in self.functions:
            f.id = id
            id += 1
        
    """
    Resets the computed ids
    """
    def reset(self):
        self.discretization.reset()

        for f in self.functions:
            f.reset()

    """
    Writes the content of the datfile into dest

    Args:
        dest: Stream to write the datfile to
    """
    def write(self, dest):
        sections = OrderedDict()

        # write head
        sections.update(self.head.get_sections())

        # write functions
        for f in self.functions:
            sections.update(f.get_sections())
        
        # write conditions
        for c in self.conditions:
            sections.update(c.get_sections())
            c.write(dest)
        
        # write result description
        sections['RESULT DESCRIPTION'] = []
        for d in self.result_description:
            sections['RESULT DESCRIPTION'].append(d.get_line())

        # write discretization
        sections.update(self.discretization.get_sections())

        # reorder sections
        sections = Datfile.reorder_sections(sections)

        # write sections
        for title, lines in sections.items():
            write_title(dest, title, True)
            for l in lines:
                dest.write('{0}\n'.format(l))
    
    """
    Reorderes the sections of the datfile into a specific order

    Args:
        sections: Dictionary of sections as keys and section lines as values
    
    Return:
        ordered dictionary of sections as keys and section lines as values
    """
    @staticmethod
    def reorder_sections(sections):
        ORDER_RULES = [
            '',
            'TITLE',
            'PROBLEM SIZE',
            'PROBLEM TYP',
            None, # this will be filled by the rest
            'MATERIALS', # materials
            re.compile(r'^FUNCT\d+$'), # functions
            'RESULT DESCRIPTION',
            re.compile(r'.*\sCONDITIONS$'), # conditions
            'DESIGN DESCRIPTION',
            'DNODE-NODE TOPOLOGY',
            'DLINE-NODE TOPOLOGY',
            'DSURF-NODE TOPOLOGY',
            'DVOL-NODE TOPOLOGY',
            'NODE COORDS',
            re.compile(r'[A-Z]+\s+ELEMENTS$'),
            'END'
        ]
        to_process = list(sections.keys())
        myorder = []

        # order keys
        rest_pos = None
        for order_rule in ORDER_RULES:
            if isinstance(order_rule, re.Pattern):
                # look for all keys that fit and are not added yet
                matches = []
                for i in to_process:
                    if order_rule.match(i):
                        matches.append(i)


                myorder.extend(sorted(matches))
                to_process = [i for i in to_process if i not in matches]

            elif order_rule is None:
                if rest_pos is None:
                    rest_pos = len(myorder)
            else:
                # this is a single string
                if order_rule in to_process:
                    myorder.append(order_rule)
                    to_process.remove(order_rule)
        
        if rest_pos is None:
            rest_pos = len(myorder)
        
        for i in sorted(to_process):
            myorder.insert(rest_pos, i)
            rest_pos += 1

        return OrderedDict((k, sections[k]) for k in myorder)

    """
    Static method that creates the discretizations file from the input lines of a .dat file

    Args:
        sections: Dictionary with header titles as keys and list of lines as value
    
    Retuns:
        Discretization object
    """
    @staticmethod
    def read(sections: Dict[str, List[str]], out: bool = False) -> 'Discretization':
        dat = Datfile()
        
        # read discretization
        dat.discretization = Discretization.read(sections, out=out)

        # read functions
        dat.functions = Function.read_functions(sections)

        # read boundary conditions
        dat.conditions = read_conditions(sections, dat)

        # read result description
        dat.result_description = ResultDescription.parseall(sections, dat)

        # read head
        dat.head = Head.read(sections)