import lnmmeshio as mio
import os, unittest, io
import numpy as np
from lnmmeshio.nodeset import LineNodeset, PointNodeset, VolumeNodeset, SurfaceNodeset
from lnmmeshio.conditions.conditionreader import read_conditions
from lnmmeshio.conditions.surf_dirich_condition import SurfaceDirichletConditions
from lnmmeshio.conditions.point_dirich_condition import PointDirichletConditions
from lnmmeshio.conditions.line_dirich_conditions import LineDirichletConditions
from lnmmeshio.conditions.volume_dirich_conditions import VolumeDirichletConditions
from lnmmeshio.conditions.surf_neumann_condition import SurfaceNeumannConditions
from lnmmeshio.conditions.point_neumann_conditions import PointNeumannConditions
from lnmmeshio.conditions.line_neumann_conditions import LineNeumannConditions
from lnmmeshio.conditions.volume_neumann_conditions import VolumeNeumannConditions
from lnmmeshio.conditions.common_condition import CommonCondition
from lnmmeshio.conditions.condition import ConditionsType

script_dir = os.path.dirname(os.path.realpath(__file__))
 
class TestConditions(unittest.TestCase):
 
    def setUp(self):
        pass
    
    @staticmethod
    def get_discretization():
                # build dummy discretization
        d: mio.Discretization = mio.Discretization()
        d.nodes = [
            mio.Node(np.array([0.0, 0.0, 0.0])),
            mio.Node(np.array([1.0, 0.0, 0.0])),
            mio.Node(np.array([0.0, 1.0, 0.0])),
            mio.Node(np.array([0.0, 0.0, 1.0]))
        ]
        
        d.pointnodesets.append(PointNodeset(1))
        d.pointnodesets.append(PointNodeset(2))
        d.linenodesets.append(LineNodeset(1))
        d.linenodesets.append(LineNodeset(2))
        d.surfacenodesets.append(SurfaceNodeset(1))
        d.surfacenodesets.append(SurfaceNodeset(2))
        d.volumenodesets.append(VolumeNodeset(1))
        d.volumenodesets.append(VolumeNodeset(2))

        d.pointnodesets[0].add_node(d.nodes[0])

        # dline
        for i in range(0, 2):
            d.linenodesets[0].add_node(d.nodes[i])

        # dsurf
        for i in range(0, 3):
            d.surfacenodesets[0].add_node(d.nodes[i])

        # dvol
        for i in range(0, 4):
            d.volumenodesets[0].add_node(d.nodes[i])

        d.elements.structure = [
            mio.Element('SOLIDT4SCATRA', 'TET4', d.nodes)
        ]
        d.elements.structure[0].options = {
            'MAT': 1, 'KINEM': 'nonlinear', 'TYPE': 'Std'
        }

        d.finalize()
        return d
    
    def test_write_common(self):
        for acton in [ConditionsType.ActOnType.POINT, ConditionsType.ActOnType.LINE, ConditionsType.ActOnType.SURFACE, ConditionsType.ActOnType.VOLUME]:
            dis = TestConditions.get_discretization()
            dis.compute_ids(True)

            bc = CommonCondition(dis.surfacenodesets[0], np.array([True]*3+[False]*2), np.array([0.1, 0.2, 0.3, 0.4, 0.5]), acton)

            dummy_file = io.StringIO()
            bc.write(dummy_file)

            self.assertEqual('E 0 - NUMDOF 5 ONOFF 1 1 1 0 0 VAL 0.1 0.2 0.3 0.4 0.5 FUNCT 0 0 0 0 0\n', dummy_file.getvalue())  

    def common_conditions(self, clsref, containerref, head, type):
        dis = TestConditions.get_discretization()
        dis.compute_ids(True)

        bcs = containerref()
        bc1 = clsref(dis.surfacenodesets[0], np.array([True]*3+[False]*2), np.array([0.1, 0.2, 0.3, 0.4, 0.5]), bcs.acton)
        bc2 = clsref(dis.surfacenodesets[1], np.array([True]*2+[False]*3), np.array([0.1, 0.2, 0.3, 0.4, 0.5]), bcs.acton)
        bcs.add(bc1)
        bcs.add(bc2)

        dummy_file = io.StringIO()
        bcs.write(dummy_file)
        content = dummy_file.getvalue()
        while content[0] == '-':
            content = content[1:]

        self.assertEqual('DESIGN {0} {1} CONDITIONS\nD{0} 2\nE 0 - NUMDOF 5 ONOFF 1 1 1 0 0 VAL 0.1 0.2 0.3 0.4 0.5 FUNCT 0 0 0 0 0\nE 1 - NUMDOF 5 ONOFF 1 1 0 0 0 VAL 0.1 0.2 0.3 0.4 0.5 FUNCT 0 0 0 0 0\n'.format(head, type), content)
    
    def test_write_surfdirich_multiple(self):
        self.common_conditions(CommonCondition, SurfaceDirichletConditions, 'SURF', 'DIRICH')
    
    def test_write_linedirich_multiple(self):
        self.common_conditions(CommonCondition, LineDirichletConditions, 'LINE', 'DIRICH')
  
    def test_write_voldirich_multiple(self):
        self.common_conditions(CommonCondition, VolumeDirichletConditions, 'VOL', 'DIRICH')
  
    def test_write_pointdirich_multiple(self):
        self.common_conditions(CommonCondition, PointDirichletConditions, 'POINT', 'DIRICH')
    
    def test_write_surfneumann_multiple(self):
        self.common_conditions(CommonCondition, SurfaceNeumannConditions, 'SURF', 'NEUMANN')
    
    def test_write_lineneumann_multiple(self):
        self.common_conditions(CommonCondition, LineNeumannConditions, 'LINE', 'NEUMANN')
  
    def test_write_volneumann_multiple(self):
        self.common_conditions(CommonCondition, VolumeNeumannConditions, 'VOL', 'NEUMANN')
  
    def test_write_pointneumann_multiple(self):
        self.common_conditions(CommonCondition, PointNeumannConditions, 'POINT', 'NEUMANN')

    def test_read_common(self):
        dis = TestConditions.get_discretization()

        bc = CommonCondition.read(
            'E 1 - NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.1 0.2 0.3 0.4 0.5 0.6 FUNCT 0 0 0 0 0 0', dis, mio.conditions.condition.ConditionsType.ActOnType.SURFACE
        )

        self.assertEqual(bc.nodeset, dis.surfacenodesets[0])
        self.assertListEqual(list(bc.onoff), [True]*3+[False]*3)
        self.assertListEqual(list(bc.value), [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    
    def read_common_multiple(self, shortname, type):
        dis = TestConditions.get_discretization()

        sections = {}
        sections['DESIGN {0} {1} CONDITIONS'.format(shortname, type)] = []
        sections['DESIGN {0} {1} CONDITIONS'.format(shortname, type)].append('D{0} 2'.format(shortname))
        sections['DESIGN {0} {1} CONDITIONS'.format(shortname, type)].append('E 1 - NUMDOF 6 ONOFF 1 1 1 0 0 0 VAL 0.1 0.2 0.3 0.4 0.5 0.6 FUNCT 0 0 0 0 0 0')
        sections['DESIGN {0} {1} CONDITIONS'.format(shortname, type)].append('E 2 - NUMDOF 3 ONOFF 1 1 1 VAL 0.1 0.2 0.3 FUNCT 0 0 0')

        bcs = read_conditions(sections, dis)

        self.assertEqual(len(bcs), 1)
        self.assertEqual(len(bcs[0]), 2)
        self.assertListEqual(list(bcs[0][0].onoff), [True]*3+[False]*3)
        self.assertListEqual(list(bcs[0][1].onoff), [True]*3)
        self.assertListEqual(list(bcs[0][0].value), [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        self.assertListEqual(list(bcs[0][1].value), [0.1, 0.2, 0.3])

    def test_read_surfdirich_multiple(self):
        self.read_common_multiple('SURF', 'DIRICH')

    def test_read_linedirich_multiple(self):
        self.read_common_multiple('LINE', 'DIRICH')

    def test_read_voldirich_multiple(self):
        self.read_common_multiple('VOL', 'DIRICH')

    def test_read_pointdirich_multiple(self):
        self.read_common_multiple('POINT', 'DIRICH')

    def test_read_surfneumann_multiple(self):
        self.read_common_multiple('SURF', 'NEUMANN')

    def test_read_lineneumann_multiple(self):
        self.read_common_multiple('LINE', 'NEUMANN')

    def test_read_volneumann_multiple(self):
        self.read_common_multiple('VOL', 'NEUMANN')

    def test_read_pointneumann_multiple(self):
        self.read_common_multiple('POINT', 'NEUMANN')