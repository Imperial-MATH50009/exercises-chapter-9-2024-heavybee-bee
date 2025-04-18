from numbers import Number as Num
from functools import singledispatch


class Expression:

    def __init__(self, *operands):
        self.operands = operands

    def __add__(self, other):
        """Add: self + other."""
        if isinstance(other, Num):
            other = Number(other)
        return Add(self, other)

    def __radd__(self, other):
        """Add: other + self."""
        other = Number(other)
        return Add(other, self)

    def __sub__(self, other):
        """Sub: self - other."""
        if isinstance(other, Num):
            other = Number(other)
        return Sub(self, other)

    def __rsub__(self, other):
        """Sub: other - self."""
        other = Number(other)
        return Sub(other, self)

    def __mul__(self, other):
        """"Mul: self * other."""
        if isinstance(other, Num):
            other = Number(other)
        return Mul(self, other)

    def __rmul__(self, other):
        """Mul: other * self."""
        other = Number(other)
        return Mul(other, self)

    def __truediv__(self, other):
        """Div: self / other."""
        if isinstance(other, Num):
            other = Number(other)
        return Div(self, other)

    def __rtruediv__(self, other):
        """Div: other / self."""
        other = Number(other)
        return Div(other, self)

    def __pow__(self, other):
        """Pow: self ^ other."""
        if isinstance(other, Num):
            other = Number(other)
        return Pow(self, other)

    def __rpow__(self, other):
        """Pow: other ^ self."""
        other = Number(other)
        return Pow(other, self)


class Operator(Expression):
    """Operator class."""

    def __repr__(self):
        """repr method."""
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        """str method."""
        a, b = self.operands[0], self.operands[1]
        if a.precedence > self.precedence:
            a_str = "(" + str(a) + ")"
        else:
            a_str = str(a)
        if b.precedence > self.precedence:
            b_str = "(" + str(b) + ")"
        else:
            b_str = str(b)
        return a_str + " " + self.exp_symbol + " " + b_str


class Terminal(Expression):
    """Terminal class."""
    precedence = 0

    def __init__(self, value):
        """define value."""
        self.value = value
        super().__init__()

    def __repr__(self):
        """Repr method."""
        return repr(self.value)

    def __str__(self):
        """Str method."""
        return str(self.value)


class Number(Terminal):
    """Number class. Gives a number to the Terminal."""

    def __init__(self, value):
        """Construct a Number expression."""
        if not isinstance(value, Num):
            raise TypeError("Val input of type: " + type(value).__name__ +
                            "Expected val of type " + type(Number).__name__ +
                            ".")
        super().__init__(value)


class Symbol(Terminal):
    """Symbol class. Gives a symbol to the terminal."""

    def __init__(self, symbol):
        """Construct a symbol."""
        super().__init__(symbol)


class Add(Operator):
    """Addition operator."""

    exp_symbol = "+"
    precedence = 3


class Sub(Operator):
    """Subtraction operator."""

    exp_symbol = "-"
    precedence = 3


class Mul(Operator):
    """Multiplication operator."""

    exp_symbol = "*"
    precedence = 2


class Div(Operator):
    """Division operator."""

    exp_symbol = "/"
    precedence = 2


class Pow(Operator):
    """Power operator."""

    exp_symbol = "^"
    precedence = 1


def postvisitor(expr, fn, **kwargs):
    """Visit an Expression in postorder applying a function to every node.

    Parameters
    ----------
    expr: Expression
        The expression to be visited.
    fn: function(node, *o, **kwargs)
        A function to be applied at each node. The function should take
        the node to be visited as its first argument, and the results of
        visiting its operands as any further positional arguments. Any
        additional information that the visitor requires can be passed in
        as keyword arguments.
    **kwargs:
        Any additional keyword arguments to be passed to fn.
    """
    stack = []
    visited = {}
    stack.append(expr)
    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)

        if unvisited_children:
            # Not ready to visit this node yet.
            # Need to visit children before e.
            stack.append(e)
            for child in unvisited_children:
                stack.append(child)
        else:
            # Any children of e have been visited, so we can visit it.
            visited[e] = fn(e, *(visited[o] for o in e.operands), **kwargs)
    # When the stack is empty, we have visited every subexpression,
    # including expr itself.
    return visited[expr]


@singledispatch
def differentiate(expr, *o, **kwargs):
    """Differentiate an expression node wrt a symbol.

    Parameters
    ----------
    expr: Expression
        The expression node to be evaluated.
    *o: numbers.Number
        The results of differentiating the operands of expr.
    **kwargs:
        Any keyword arguments required to evaluate specific types of
        expression.
    var: var
        The var denoting what to differentiate wrt.
    """
    raise NotImplementedError(
        f"Cannot differentiate a {type(expr).__name__}"
    )


@differentiate.register(Number)
def _(expr, *o, **kwargs):
    return Number(0.0)


@differentiate.register(Symbol)
def _(expr, *o, var, **kwargs):
    if expr.value == var:
        return Number(1.0)
    else:
        return Number(0.0)


@differentiate.register(Add)
def _(expr, *o, **kwargs):
    return o[0] + o[1]


@differentiate.register(Sub)
def _(expr, *o, **kwargs):
    return o[0] - o[1]


@differentiate.register(Mul)
def _(expr, *o, **kwargs):
    return o[0] * expr.operands[1] + o[1] * expr.operands[0]


@differentiate.register(Div)
def _(expr, *o, **kwargs):
    return (o[0] * expr.operands[1] - expr.operands[0] * o[1]) \
        / (expr.operands[1]**Number(2))


@differentiate.register(Pow)
def _(expr, *o, **kwargs):
    # Assumed expr.operands[1] is not var
    return (expr.operands[1] * (expr.operands[0] ** (expr.operands[1] - 1)) *
            o[0])
