import unittest
import lnmmeshio
import os
import meshio
import numpy as np
from typing import List
from lnmmeshio.element.parse_element import parse as parse_ele
from lnmmeshio.node import Node
from lnmmeshio.element.hex8 import Hex8
from lnmmeshio.element.tet10 import Tet10
from lnmmeshio.element.tet4 import Tet4
from lnmmeshio.element.quad4 import Quad4
from lnmmeshio.element.tri3 import Tri3
from lnmmeshio.element.tri6 import Tri6
from lnmmeshio.element.line2 import Line2
from lnmmeshio.element.line3 import Line3
from lnmmeshio.element.element import Element
from lnmmeshio import ElementContainer

script_dir = os.path.dirname(os.path.realpath(__file__))

class TestEleContainer(unittest.TestCase):
     
    def setUp(self):
        pass

    def test_elecontainer(self):
        c = ElementContainer()

        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeStructure])
        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeFluid])
        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeALE])
        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeTransport])
        self.assertRaises(KeyError, lambda: c[ElementContainer.TypeTransport])
        self.assertRaises(KeyError, lambda: c['doesnotexist'])
        with self.assertRaises(KeyError) as _:
            c['doesnotexist'] = 1
        
        c[ElementContainer.TypeStructure] = [1]
        self.assertListEqual(c[ElementContainer.TypeStructure], [1])
        self.assertListEqual(c.structure, [1])
        
        c[ElementContainer.TypeFluid] = [2]
        self.assertListEqual(c[ElementContainer.TypeFluid], [2])
        self.assertListEqual(c.fluid, [2])
        
        c[ElementContainer.TypeALE] = [3]
        self.assertListEqual(c[ElementContainer.TypeALE], [3])
        self.assertListEqual(c.ale, [3])
        
        c[ElementContainer.TypeTransport] = [4]
        self.assertListEqual(c[ElementContainer.TypeTransport], [4])
        self.assertListEqual(c.transport, [4])
        
        c[ElementContainer.TypeThermo] = [5]
        self.assertListEqual(c[ElementContainer.TypeThermo], [5])
        self.assertListEqual(c.thermo, [5])