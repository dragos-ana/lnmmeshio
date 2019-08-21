from .element import ElementHex
from ..node import Node
from typing import List, Dict
from .quad9 import Quad9
from .line3 import Line3
import numpy as np

"""
Implementation of a HEX27 element
"""
class Hex27 (ElementHex):
    ShapeName: str = 'HEX27'

    """
    Base constructor of a Hex27 element
    """
    def __init__(self, el_type: str, nodes: List[Node]):
        super(Hex27, self).__init__(el_type, Hex27.ShapeName, nodes)

        if len(nodes) != self.get_num_nodes():
            raise RuntimeError('You tried to created a HEX27 element with {0} nodes'.format(len(nodes)))
    
    """
    Get number of nodes of a HEX27 element

    Returns:
        Number of nodes of a Hex27 element = 27
    """
    def get_num_nodes(self) -> int:
        return 27
    
    """
    Returns a list of faces of the Hex27 element

    Returns:
        List of faces
    """
    def get_faces(self) -> List[Quad9]:
        face_node_ids = [
            [0, 1, 2, 3, 8, 9, 10, 11, 20],
            [0, 1, 5, 4, 8, 13, 16, 12, 21],
            [1, 2, 6, 5, 9, 14, 17, 13, 22],
            [2, 3, 7, 6, 10, 15, 18, 14, 23],
            [3, 0, 4, 7, 11, 12, 19, 15, 24],
            [4, 5, 6, 7, 15, 17, 18, 19, 25]]

        return [
            Quad9(None, [self.nodes[i] for i in nodes]) for nodes in face_node_ids
        ]
    
    """
    Returns the list of all edges

    Returns:
        List of edges
    """
    def get_edges(self) -> List[Line3]:
        edge_node_ids = [
            [0, 1, 8],
            [1, 2, 9],
            [2, 3, 10],
            [3, 0, 11],
            [0, 4, 12],
            [1, 5, 13],
            [2, 6, 14],
            [3, 7, 15],
            [4, 5, 16],
            [5, 6, 17],
            [6, 7, 18],
            [7, 4, 19]]
        return [
            Line3(None, [self.nodes[i] for i in nodes]) for nodes in edge_node_ids
        ]
    
    """
    Returns the value of the shape functions at the local coordinate xi
    """
    @staticmethod
    def shape_fcns(xi):

        return np.array(
            [Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[1],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[1],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[1],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[1],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[2],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[2],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[2],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[2],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[1],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[1],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[1],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[1],

            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[0],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[0]*Line3.shape_fcns(xi[2])[2],
            Line3.shape_fcns(xi[0])[1]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[2],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[1]*Line3.shape_fcns(xi[2])[2],
            Line3.shape_fcns(xi[0])[0]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[2],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[1],
            Line3.shape_fcns(xi[0])[2]*Line3.shape_fcns(xi[1])[2]*Line3.shape_fcns(xi[2])[2]])