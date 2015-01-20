import unittest
import odin
from odin import traversal


class Level3(odin.Resource):
    class Meta:
        namespace = 'odin.traversal'

    name = odin.StringField()


class Level2(odin.Resource):
    class Meta:
        namespace = 'odin.traversal'

    name = odin.StringField()
    level3s = odin.ListOf(Level3)


class Level1(odin.Resource):
    class Meta:
        namespace = 'odin.traversal'

    name = odin.StringField()
    level2 = odin.DictAs(Level2)
    level2s = odin.DictOf(Level2)


TEST_STRUCTURE = Level1(
    name='a',
    level2=Level2(name='b', level3s=[]),
    level2s=dict(
        a=Level2(name='c', level3s=[]),
        b=Level2(name='d', level3s=[Level3(name='e'), Level3(name='f')]),
        c=Level2(name='g', level3s=[Level3(name='h')]),
    )
)

TEST_LIST_STRUCTURE = [
    Level1(
        name='a',
        level2=Level2(name='b', level3s=[]),
        level2s=dict(
            a=Level2(name='c', level3s=[]),
            b=Level2(name='d', level3s=[Level3(name='e'), Level3(name='f')]),
            c=Level2(name='g', level3s=[Level3(name='h')]),
        )
    ),
    Level1(
        name='i',
        level2=Level2(name='j', level3s=[]),
        level2s=dict(
            a=Level2(name='k', level3s=[]),
            b=Level2(name='l', level3s=[Level3(name='m'), Level3(name='n')]),
            c=Level2(name='o', level3s=[Level3(name='p')]),
        )
    )
]


class TestResourceTraversalIterator(traversal.ResourceTraversalIterator):
    def __init__(self, resource):
        super(TestResourceTraversalIterator, self).__init__(resource)
        self.events = []

    def on_pre_enter(self):
        self.events.append("on_pre_enter: %s" % self.path)

    def on_enter(self):
        self.events.append("on_enter: %s" % self.path)

    def on_exit(self):
        self.events.append("on_exit: %s" % self.path)


class TraversalTestCase(unittest.TestCase):
    def test_structure(self):
        TEST_STRUCTURE.full_clean()

        resource_iter = TestResourceTraversalIterator(TEST_STRUCTURE)
        resources = ["%s %s %s" % (r, r.name, resource_iter.depth) for r in resource_iter]

        self.assertListEqual([
            'on_enter: ',
                'on_enter: level2',
                'on_exit: level2',
                'on_enter: level2s[a]',
                'on_exit: level2s[a]',
                'on_enter: level2s[b]',
                    'on_enter: level2s[b].level3s[0]',
                    'on_exit: level2s[b].level3s[0]',
                    'on_enter: level2s[b].level3s[1]',
                    'on_exit: level2s[b].level3s[1]',
                'on_exit: level2s[b]',
                'on_enter: level2s[c]',
                'on_enter: level2s[c].level3s[0]',
                'on_exit: level2s[c].level3s[0]',
                'on_exit: level2s[c]',
            'on_exit: ',
        ], resource_iter.events)

        self.assertListEqual([
            'odin.traversal.Level1 resource a 0',
            'odin.traversal.Level2 resource b 1',
            'odin.traversal.Level2 resource c 1',
            'odin.traversal.Level2 resource d 1',
            'odin.traversal.Level3 resource e 2',
            'odin.traversal.Level3 resource f 2',
            'odin.traversal.Level2 resource g 1',
            'odin.traversal.Level3 resource h 2',
        ], resources)

    def test_list_structure(self):
        TEST_STRUCTURE.full_clean()

        resource_iter = TestResourceTraversalIterator(TEST_LIST_STRUCTURE)
        resources = ["%s %s %s" % (r, r.name, resource_iter.depth) for r in resource_iter]

        self.assertListEqual([
            'on_enter: ',
                'on_enter: level2',
                'on_exit: level2',
                'on_enter: level2s[a]',
                'on_exit: level2s[a]',
                'on_enter: level2s[b]',
                    'on_enter: level2s[b].level3s[0]',
                    'on_exit: level2s[b].level3s[0]',
                    'on_enter: level2s[b].level3s[1]',
                    'on_exit: level2s[b].level3s[1]',
                'on_exit: level2s[b]',
                'on_enter: level2s[c]',
                'on_enter: level2s[c].level3s[0]',
                'on_exit: level2s[c].level3s[0]',
                'on_exit: level2s[c]',
            'on_exit: ',
            'on_enter: ',
                'on_enter: level2',
                'on_exit: level2',
                'on_enter: level2s[a]',
                'on_exit: level2s[a]',
                'on_enter: level2s[b]',
                    'on_enter: level2s[b].level3s[0]',
                    'on_exit: level2s[b].level3s[0]',
                    'on_enter: level2s[b].level3s[1]',
                    'on_exit: level2s[b].level3s[1]',
                'on_exit: level2s[b]',
                'on_enter: level2s[c]',
                'on_enter: level2s[c].level3s[0]',
                'on_exit: level2s[c].level3s[0]',
                'on_exit: level2s[c]',
            'on_exit: ',
        ], resource_iter.events)

        self.assertListEqual([
            'odin.traversal.Level1 resource a 0',
            'odin.traversal.Level2 resource b 1',
            'odin.traversal.Level2 resource c 1',
            'odin.traversal.Level2 resource d 1',
            'odin.traversal.Level3 resource e 2',
            'odin.traversal.Level3 resource f 2',
            'odin.traversal.Level2 resource g 1',
            'odin.traversal.Level3 resource h 2',
            'odin.traversal.Level1 resource i 0',
            'odin.traversal.Level2 resource j 1',
            'odin.traversal.Level2 resource k 1',
            'odin.traversal.Level2 resource l 1',
            'odin.traversal.Level3 resource m 2',
            'odin.traversal.Level3 resource n 2',
            'odin.traversal.Level2 resource o 1',
            'odin.traversal.Level3 resource p 2',
        ], resources)

class TraversalPathTestCase(unittest.TestCase):
    def test_parse(self):
        actual = traversal.TraversalPath.parse('level2')
        self.assertEqual(traversal.TraversalPath((None, 'level2'),), actual)

        actual = traversal.TraversalPath.parse('level2.name')
        self.assertEqual(traversal.TraversalPath((None, 'level2'), (None, 'name')), actual)

        actual = traversal.TraversalPath.parse('level2s[b].level3s[1].name')
        self.assertEqual(traversal.TraversalPath(('b', 'level2s'), ('1', 'level3s'), (None, 'name')), actual)

    def test_add(self):
        actual = traversal.TraversalPath.parse('level2') + 'name'
        self.assertEqual(traversal.TraversalPath.parse('level2.name'), actual)

        actual = traversal.TraversalPath.parse('level2s[b]') + traversal.TraversalPath.parse('level3s[1].name')
        self.assertEqual(traversal.TraversalPath.parse('level2s[b].level3s[1].name'), actual)

    def test_valid_path(self):
        self.assertEqual('a', traversal.TraversalPath.parse('name').get_value(TEST_STRUCTURE))
        self.assertEqual('b', traversal.TraversalPath.parse('level2.name').get_value(TEST_STRUCTURE))

        r = traversal.TraversalPath.parse('level2s[b].level3s[1]').get_value(TEST_STRUCTURE)
        self.assertIsInstance(r, Level3)
        self.assertEqual('f', r.name)

    def test_invalid_path(self):
        path = traversal.TraversalPath.parse('level2s[b].level3s[4]')
        self.assertRaises(IndexError, path.get_value, TEST_STRUCTURE)

        path = traversal.TraversalPath.parse('level2s[b].level3s_sd[1]')
        self.assertRaises(KeyError, path.get_value, TEST_STRUCTURE)
