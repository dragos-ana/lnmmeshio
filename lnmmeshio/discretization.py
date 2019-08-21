import numpy as np
from typing import List, Dict
from .ioutils import write_title, write_option_list, write_option, read_option_item, \
    read_next_option, read_next_key, read_next_value, line_option, line_comment, line_option_list, line_title
from collections import OrderedDict
import re
from .element.element import Element
from .element.element_container import ElementContainer
from .node import Node
from .fiber import Fiber
from .progress import progress
from .nodeset import PointNodeset, LineNodeset, SurfaceNodeset, VolumeNodeset

"""
This class holds the discretization, consisting out of nodes and elements. The nodes and
elements itself hold their data (coords, element type, ...)
"""
class Discretization:

    """
    Initialize Discretization class with empty nodes and zero elements
    """
    def __init__(self):
        self.nodes: List[Node] = []
        self.elements: ElementContainer = ElementContainer()

        # initialize nodesets
        self.pointnodesets: List[PointNodeset] = []
        self.linenodesets: List[LineNodeset] = []
        self.surfacenodesets: List[SurfaceNodeset] = []
        self.volumenodesets: List[VolumeNodeset] = []

    """
    Computes the ids of the elements and nodes. 

    Args:
        zero_based: If true, the first node id is 0, otherwise 1
    """
    def compute_ids(self, zero_based: bool):
        
        id: int = 0 if zero_based else 1
        for node in self.nodes:
            node.id = id
            id += 1
        
        id: int = 0 if zero_based else 1
        for ele_i in self.elements.values():
            for ele in ele_i:
                ele.id = id
                id += 1
        
        id: int = 0 if zero_based else 1
        for ns in self.pointnodesets:
            ns.id = id
            id += 1
        
        id: int = 0 if zero_based else 1
        for ns in self.linenodesets:
            ns.id = id
            id += 1
        
        id: int = 0 if zero_based else 1
        for ns in self.surfacenodesets:
            ns.id = id
            id += 1
        
        id: int = 0 if zero_based else 1
        for ns in self.volumenodesets:
            ns.id = id
            id += 1
    
    """
    Resets the computed ids
    """
    def reset(self):
        for node in self.nodes:
            node.reset()
        
        for ele_i in self.elements.values():
            for ele in ele_i:
                ele.reset()

        for ns in self.pointnodesets:
            ns.reset()
        for ns in self.linenodesets:
            ns.reset()
        for ns in self.surfacenodesets:
            ns.reset()
        for ns in self.volumenodesets:
            ns.reset()

    """
    Returns an np.array((num_node, 3)) with the coordinates of each node
    """
    def get_node_coords(self):
        arr: np.array = np.zeros((len(self.nodes), 3))

        i: int = 0
        for node in self.nodes:
            arr[i,:] = node.coords
            i += 1
        
        return arr

    def get_sections(self, out=True):
        self.compute_ids(zero_based=False)

        sections = OrderedDict()

        # write problem size
        num_ele = 0
        for elelist in self.elements.values():
            num_ele += len(elelist)
        problem_size = []
        problem_size.append(line_option('ELEMENTS', num_ele))
        problem_size.append(line_option('NODES', len(self.nodes)))
        problem_size.append(line_option('DIM', 3))
        problem_size.append(line_option('MATERIALS', 9999)) # Write dummy value
        sections['PROBLEM SIZE'] = problem_size

        # write design description
        design_description = []
        design_description.append(line_option('NDPOINT', len(self.pointnodesets) if self.pointnodesets is not None else 0))
        design_description.append(line_option('NDLINE', len(self.linenodesets) if self.linenodesets is not None else 0))
        design_description.append(line_option('NDSURF', len(self.surfacenodesets) if self.surfacenodesets is not None else 0))
        design_description.append(line_option('NDVOL', len(self.volumenodesets) if self.volumenodesets is not None else 0))
        sections['DESIGN DESCRIPTION'] = design_description

        # write topology
        for ns in [self.pointnodesets, self.linenodesets, self.surfacenodesets, self.volumenodesets]:
            for nsi in progress(ns, out=out, label='Write Nodeset {0}'.format(type(ns))):
                section_name = nsi.get_section()
                if section_name not in sections:
                    sections[section_name] = []
                
                sections[section_name].extend(nsi.get_lines())
        
        # write nodes
        nodes = []
        for node in progress(self.nodes, out=out, label='Write Nodes'):
            nodes.append(node.get_line())
        sections['NODE COORDS'] = nodes
    
        # write elements
        sections.update(self.elements.get_sections(out=out))

        return sections

    """
    Writes the discretization related sections into the stream variable dest

    Args:
        dest: stream variable (could for example be: with open('file.dat', 'w') as dest: ...)
    """
    def write(self, dest, out=True):
        sections = self.get_sections(out=out)

        for key, lines in progress(sections.items(), out=out, label='Write sections'):
            write_title(dest, key)
            for l in lines:
                dest.write('{0}\n'.format(l))

    """
    Finalizes the discretization by creating internal references
    """
    def finalize(self):

        # remove old nodesets
        for n in self.nodes:
            n.pointnodesets.clear()
            n.linenodesets.clear()
            n.surfacenodesets.clear()
            n.volumenodesets.clear()

        # add point nodesets
        for ns in self.pointnodesets:
            for n in ns:
                n.pointnodesets.append(ns)

        # add line nodesets
        for ns in self.linenodesets:
            for n in ns:
                n.linenodesets.append(ns)

        # add surface nodesets
        for ns in self.surfacenodesets:
            for n in ns:
                n.surfacenodesets.append(ns)

        # add volume nodesets
        for ns in self.volumenodesets:
            for n in ns:
                n.volumenodesets.append(ns)

    """
    Static method that creates the discretizations file from the input lines of a .dat file

    Args:
        sections: Dictionary with header titles as keys and list of lines as value
    
    Retuns:
        Discretization object
    """
    @staticmethod
    def read(sections: Dict[str, List[str]], out: bool = False) -> 'Discretization':
        disc = Discretization()

        # read nodes
        for line in progress(sections['NODE COORDS'], out=out, label='Nodes'):
            if 'FNODE' in line:
                # this is a fiber node
                nodeid, _ = read_option_item(line, 'FNODE')
            else:
                nodeid, _ = read_option_item(line, 'NODE')
            

            if nodeid is None or nodeid == '':
                # this is not a node, probably a comment
                continue
            
            coords_str, _ = read_option_item(line, 'COORD', num=3)

            coords = np.array([float(i) for i in coords_str])

            node = Node(coords=coords)
            disc.nodes.append(node)

            # safety check for integrity of the dat file
            if int(nodeid) != len(disc.nodes):
                raise RuntimeError('Node ids in dat file have a gap at {0} != {1}!'.format(nodeid, len(disc.nodes)))
            
            # read fibers
            node.fibers = Fiber.parse_fibers(line)

        # read DPOINT topology
        if 'DNODE-NODE TOPOLOGY' in sections:
            disc.pointnodesets = PointNodeset.read(sections['DNODE-NODE TOPOLOGY'], disc.nodes)


        # read DLINE topology
        if 'DLINE-NODE TOPOLOGY' in sections:
            disc.linenodesets = LineNodeset.read(sections['DLINE-NODE TOPOLOGY'], disc.nodes)


        # read DSURF topology
        if 'DSURF-NODE TOPOLOGY' in sections:
            disc.surfacenodesets = SurfaceNodeset.read(sections['DSURF-NODE TOPOLOGY'], disc.nodes)

        # read DVOL topology
        if 'DVOL-NODE TOPOLOGY' in sections:
            disc.volumenodesets = VolumeNodeset.read(sections['DVOL-NODE TOPOLOGY'], disc.nodes)

        # read elements
        disc.elements = ElementContainer.read_element_sections(sections, disc.nodes, out=out)

        # finalize discretization -> Creates internal references
        disc.finalize()
        return disc
    
    def __str__(self):
        s = ''
        s += 'Discretization with ...\n'
        s += '{0:>10} nodes\n'.format(len(self.nodes))

        for key, eles in self.elements.items():
            s += '{0:>10} {1} elements\n'.format(len(eles), key)
        
        return s