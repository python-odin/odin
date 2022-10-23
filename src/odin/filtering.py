import abc
import operator
from typing import Callable, Iterable, Any, Sequence, Union

from .exceptions import InvalidPathError
from .resources import ResourceBase
from .traversal import TraversalPath


class FilterAtom(abc.ABC):
    """
    Base filter statement
    """

    __slots__ = ()

    @abc.abstractmethod
    def __call__(self, resource: ResourceBase) -> bool:
        """
        Call filter with a resource
        """

    def any(self, collection):
        return any(self(r) for r in collection)

    def all(self, collection):
        return all(self(r) for r in collection)


class FilterChain(FilterAtom):
    """
    Collection of filter atoms to match resources
    """

    __slots__ = ("_atoms",)

    operator_name = ""
    check_operator: Callable[[Iterable[bool]], bool] = all

    def __init__(self, *atoms):
        self._atoms = list(atoms)

    def __len__(self):
        return len(self._atoms)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(*self._atoms + other._atoms)
        elif isinstance(other, FilterComparison):
            self._atoms.append(other)
            return self
        raise TypeError(f"{other} not supported for this operation")

    def __call__(self, resource: ResourceBase) -> bool:
        return self.check_operator(a(resource) for a in self._atoms)

    def __str__(self):
        if not self._atoms:
            return ""
        pin = f" {self.operator_name} "
        return f"({pin.join(str(a) for a in self._atoms)})"


class And(FilterChain):
    """
    Chain of filters we all must match; logic AND
    """

    __slots__ = ()

    operator_name = "AND"
    check_operator = all


class Or(FilterChain):
    """
    Chain of filters we any can match; logic OR
    """

    __slots__ = ()

    operator_name = "OR"
    check_operator = any


class FilterComparison(FilterAtom, abc.ABC):
    """
    Base class for filter operator atoms
    """

    __slots__ = ("field", "value", "operation")

    # Symbol for this operator and alternatives. The first item is used when generating
    # a representation of the filter, the others are used for parsing queries.
    operator_symbols: Sequence[str] = []
    compare_operator: Callable[[Any, Any], bool]

    def __init__(
        self,
        field: Union[TraversalPath, str],
        value: Any,
        operation: Callable[[Any], Any] = None,
    ):
        self.field = TraversalPath.parse(field)
        self.value = value
        self.operation = operation

    def __call__(self, resource: ResourceBase) -> bool:
        """
        Call to the filter to compare a resource
        """
        try:
            value = self.field.get_value(resource)
        except InvalidPathError:
            return False
        else:
            if self.operation:
                value = self.operation(value)
            return self.compare_operator(value, self.value)

    def __str__(self):
        value = self.value
        if isinstance(self.value, str):
            value = f"{value!r}"

        if self.operation:
            op_name = getattr(self.operation, "name", self.operation.__name__)
            return f"{op_name}({self.field}) {self.operator_symbols[0]} {value}"
        else:
            return f"{self.field} {self.operator_symbols[0]} {value}"


class Equal(FilterComparison):
    """
    Equal filter operator
    """

    __slots__ = ()

    operator_symbols = ("==", "=", "eq")
    compare_operator = operator.eq


class NotEqual(FilterComparison):
    """
    Not equal filter operator
    """

    __slots__ = ()

    operator_symbols = ("!=", "<>", "neq")
    compare_operator = operator.ne


class LessThan(FilterComparison):
    """
    Less than filter operator
    """

    __slots__ = ()

    operator_symbols = ("<", "lt")
    compare_operator = operator.lt


class LessThanOrEqual(FilterComparison):
    """
    Less than or equal filter operator
    """

    __slots__ = ()

    operator_symbols = ("<=", "lte")
    compare_operator = operator.le


class GreaterThan(FilterComparison):
    """
    Greater than filter operator
    """

    __slots__ = ()

    operator_symbols = (">", "gt")
    compare_operator = operator.gt


class GreaterThanOrEqual(FilterComparison):
    """
    Greater than or equal filter operator
    """

    __slots__ = ()

    operator_symbols = (">=", "gte")
    compare_operator = operator.ge
