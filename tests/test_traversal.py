import pytest

import odin
from odin import traversal
from odin.exceptions import InvalidPathError, MultipleMatchesError, NoMatchError


class Level3(odin.Resource):
    class Meta:
        key_field_name = "name"
        namespace = "odin.traversal"

    name = odin.StringField()


class Level2(odin.Resource):
    class Meta:
        namespace = "odin.traversal"

    name = odin.StringField()
    label = odin.StringField(null=True)
    level3s = odin.ListOf(Level3)


class Level1(odin.Resource):
    class Meta:
        namespace = "odin.traversal"

    name = odin.StringField()
    level2 = odin.DictAs(Level2)
    level2s = odin.DictOf(Level2)


TEST_STRUCTURE = Level1(
    name="a",
    level2=Level2(name="b", level3s=[]),
    level2s={
        "a": Level2(name="c", level3s=[]),
        "b": Level2(
            name="d", label="not_empty", level3s=[Level3(name="e"), Level3(name="f")]
        ),
        "c": Level2(name="g", label="not_empty", level3s=[Level3(name="h")]),
    },
)

TEST_LIST_STRUCTURE = [
    Level1(
        name="a",
        level2=Level2(name="b", level3s=[]),
        level2s={
            "a": Level2(name="c", level3s=[]),
            "b": Level2(name="d", level3s=[Level3(name="e"), Level3(name="f")]),
            "c": Level2(name="g", level3s=[Level3(name="h")]),
        },
    ),
    Level1(
        name="i",
        level2=Level2(name="j", level3s=[]),
        level2s={
            "a": Level2(name="k", level3s=[]),
            "b": Level2(name="l", level3s=[Level3(name="m"), Level3(name="n")]),
            "c": Level2(name="o", level3s=[Level3(name="p")]),
        },
    ),
]


class ResourceTraversalIteratorTest(traversal.ResourceTraversalIterator):
    def __init__(self, resource):
        super().__init__(resource)
        self.events = []

    def on_pre_enter(self):
        self.events.append(f"on_pre_enter: {self.path}")

    def on_enter(self):
        self.events.append(f"on_enter: {self.path}")

    def on_exit(self):
        self.events.append(f"on_exit: {self.path}")


class TestTraversal:
    def test_structure(self):
        TEST_STRUCTURE.full_clean()

        resource_iter = ResourceTraversalIteratorTest(TEST_STRUCTURE)
        resources = [f"{r} {r.name} {resource_iter.depth}" for r in resource_iter]

        assert resource_iter.events == [
            "on_enter: ",
            "on_enter: level2",
            "on_exit: level2",
            "on_enter: level2s[a]",
            "on_exit: level2s[a]",
            "on_enter: level2s[b]",
            "on_enter: level2s[b].level3s{name=e}",
            "on_exit: level2s[b].level3s{name=e}",
            "on_enter: level2s[b].level3s{name=f}",
            "on_exit: level2s[b].level3s{name=f}",
            "on_exit: level2s[b]",
            "on_enter: level2s[c]",
            "on_enter: level2s[c].level3s{name=h}",
            "on_exit: level2s[c].level3s{name=h}",
            "on_exit: level2s[c]",
            "on_exit: ",
        ]

        assert resources == [
            "odin.traversal.Level1 resource a 0",
            "odin.traversal.Level2 resource b 1",
            "odin.traversal.Level2 resource c 1",
            "odin.traversal.Level2 resource d 1",
            "odin.traversal.Level3 resource e 2",
            "odin.traversal.Level3 resource f 2",
            "odin.traversal.Level2 resource g 1",
            "odin.traversal.Level3 resource h 2",
        ]

    def test_list_structure(self):
        TEST_STRUCTURE.full_clean()

        resource_iter = ResourceTraversalIteratorTest(TEST_LIST_STRUCTURE)
        resources = [f"{r} {r.name} {resource_iter.depth}" for r in resource_iter]

        assert resource_iter.events == [
            "on_enter: ",
            "on_enter: level2",
            "on_exit: level2",
            "on_enter: level2s[a]",
            "on_exit: level2s[a]",
            "on_enter: level2s[b]",
            "on_enter: level2s[b].level3s{name=e}",
            "on_exit: level2s[b].level3s{name=e}",
            "on_enter: level2s[b].level3s{name=f}",
            "on_exit: level2s[b].level3s{name=f}",
            "on_exit: level2s[b]",
            "on_enter: level2s[c]",
            "on_enter: level2s[c].level3s{name=h}",
            "on_exit: level2s[c].level3s{name=h}",
            "on_exit: level2s[c]",
            "on_exit: ",
            "on_enter: ",
            "on_enter: level2",
            "on_exit: level2",
            "on_enter: level2s[a]",
            "on_exit: level2s[a]",
            "on_enter: level2s[b]",
            "on_enter: level2s[b].level3s{name=m}",
            "on_exit: level2s[b].level3s{name=m}",
            "on_enter: level2s[b].level3s{name=n}",
            "on_exit: level2s[b].level3s{name=n}",
            "on_exit: level2s[b]",
            "on_enter: level2s[c]",
            "on_enter: level2s[c].level3s{name=p}",
            "on_exit: level2s[c].level3s{name=p}",
            "on_exit: level2s[c]",
            "on_exit: ",
        ]

        assert resources == [
            "odin.traversal.Level1 resource a 0",
            "odin.traversal.Level2 resource b 1",
            "odin.traversal.Level2 resource c 1",
            "odin.traversal.Level2 resource d 1",
            "odin.traversal.Level3 resource e 2",
            "odin.traversal.Level3 resource f 2",
            "odin.traversal.Level2 resource g 1",
            "odin.traversal.Level3 resource h 2",
            "odin.traversal.Level1 resource i 0",
            "odin.traversal.Level2 resource j 1",
            "odin.traversal.Level2 resource k 1",
            "odin.traversal.Level2 resource l 1",
            "odin.traversal.Level3 resource m 2",
            "odin.traversal.Level3 resource n 2",
            "odin.traversal.Level2 resource o 1",
            "odin.traversal.Level3 resource p 2",
        ]


class TestTraversalPath:
    @pytest.mark.parametrize(
        "path, expected",
        (
            (
                "level2",
                traversal.TraversalPath(
                    (
                        traversal.PathAtom(
                            traversal.NotSupplied, traversal.NotSupplied, "level2"
                        ),
                    )
                ),
            ),
            (
                "level2.name",
                traversal.TraversalPath(
                    (
                        traversal.PathAtom(
                            traversal.NotSupplied, traversal.NotSupplied, "level2"
                        ),
                        traversal.PathAtom(
                            traversal.NotSupplied, traversal.NotSupplied, "name"
                        ),
                    )
                ),
            ),
            (
                "level2s[b].level3s[1].name",
                traversal.TraversalPath(
                    (
                        traversal.PathAtom("b", traversal.NotSupplied, "level2s"),
                        traversal.PathAtom("1", traversal.NotSupplied, "level3s"),
                        traversal.PathAtom(
                            traversal.NotSupplied, traversal.NotSupplied, "name"
                        ),
                    )
                ),
            ),
            (
                "level2s[b].level3s{code=abc}.name",
                traversal.TraversalPath(
                    (
                        traversal.PathAtom("b", traversal.NotSupplied, "level2s"),
                        traversal.PathAtom("code", "abc", "level3s"),
                        traversal.PathAtom(
                            traversal.NotSupplied, traversal.NotSupplied, "name"
                        ),
                    )
                ),
            ),
        ),
    )
    def test_parse(self, path, expected):
        """Test parsing of traversal path strings into TraversalPath objects."""

        actual = traversal.TraversalPath.parse(path)
        assert actual == expected

    def test_add(self):
        actual = traversal.TraversalPath.parse("level2") + "name"
        assert traversal.TraversalPath.parse("level2.name") == actual

        actual = traversal.TraversalPath.parse(
            "level2s[b]"
        ) + traversal.TraversalPath.parse("level3s[1].name")
        assert traversal.TraversalPath.parse("level2s[b].level3s[1].name") == actual

    @pytest.mark.parametrize(
        "path, expected",
        (
            ("name", "a"),
            ("level2.name", "b"),
        ),
    )
    def test_valid_path__with_simple_value(self, path, expected):
        target = traversal.TraversalPath.parse(path)
        actual = target.get_value(TEST_STRUCTURE)

        assert actual == expected

    @pytest.mark.parametrize(
        "path, expected",
        (
            ("level2s[b].level3s[1]", "f"),
            ("level2s[b].level3s{name=f}", "f"),
            ("level2s{name=g}.level3s{name=h}", "h"),
        ),
    )
    def test_valid_path__target_parent(self, path, expected):
        target = traversal.TraversalPath.parse(path)
        actual = target.get_value(TEST_STRUCTURE)

        assert isinstance(actual, Level3)
        assert actual.name == expected

    @pytest.mark.parametrize(
        "path, expected",
        (
            ("level2s[b].level3s[4]", NoMatchError),
            ("level2s[b].level3s_sd[1]", InvalidPathError),
            ("level2s[b].level3s{name=h}", NoMatchError),
            ("level2s{label=not_empty}.level3s{name=h}", MultipleMatchesError),
        ),
    )
    def test_invalid_path(self, path, expected):
        target = traversal.TraversalPath.parse(path)

        pytest.raises(expected, target.get_value, TEST_STRUCTURE)

    @pytest.mark.parametrize(
        "index, expected",
        (
            (0, (False, False)),
            (1, (True, False)),
            (2, (False, True)),
        ),
    )
    def test_atom_properties(self, index, expected):
        target = traversal.TraversalPath.parse("foo.bar[1].eek{name=h}")

        assert (target[index].is_indexed, target[index].is_filter) == expected

    @pytest.mark.parametrize(
        "path, expected",
        (
            ("foo.bar[1].eek", "foo.bar[1]"),
            ("foo.bar[1]", "foo"),
            ("foo", None),
            ("", None),
        ),
    )
    def test_parent(self, path, expected):
        target = traversal.TraversalPath.parse(path)
        expected = traversal.TraversalPath.parse(expected) if expected else None

        assert target.parent == expected
