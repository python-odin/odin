import pytest

from odin import datastructures


class TestCaseLessStringList(object):
    @pytest.mark.parametrize('needle haystack'.split(), (
        ('foo', ['foo']),
        ('FOO', ['foo']),
        ('foo', ['FOO']),
        ('Foo', ['fOO']),
        ('Foo', ['foo', 'bar']),
    ))
    def test_contains__true(self, needle, haystack):
        target = datastructures.CaseLessStringList(haystack)
        assert needle in target

    @pytest.mark.parametrize('needle haystack'.split(), (
        ('foo', ['food']),
        ('FOO', ['food']),
        ('foo', ['FOOD']),
        ('Foo', ['fOOd']),
        ('Foo', ['food', 'bar']),
    ))
    def test_contains__false(self, needle, haystack):
        target = datastructures.CaseLessStringList(haystack)
        assert needle not in target

    def test_extend(self):
        target = datastructures.CaseLessStringList(('foo', ))
        target.extend('bar')
        assert target == ['FOO', 'B', 'A', 'R']

    def test_append(self):
        target = datastructures.CaseLessStringList('foo')
        target.append('bar')
        assert 'Bar' in target

    def test_insert(self):
        target = datastructures.CaseLessStringList(('foo', 'bar'))
        target.insert(1, 'eek')
        assert 'Eek' in target
        assert target == ['FOO', 'EEK', 'BAR']

    def test_index(self):
        target = datastructures.CaseLessStringList(('foo', 'bar', 'eek'))

        assert target.index('Foo') == 0
        assert target.index('Bar') == 1
        assert target.index('EEk', 1) == 2

    def test_remove(self):
        target = datastructures.CaseLessStringList(('foo', 'bar', 'eek'))
        target.remove('Bar')
        assert target == ['FOO', 'EEK']
