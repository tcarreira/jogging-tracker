from rest_framework import filters
from django.db.models import Q

from typing import List


class ParseError(Exception):
    def __init__(self, pos, msg, *args):
        self.pos = pos
        self.msg = msg
        self.args = args

    def __str__(self):
        return "%s at position %s" % (self.msg % self.args, self.pos)


class AdvancedFilter(filters.BaseFilterBackend):
    """
    Allow advaced filtering.
    Supports :
        - expression delimiters: (), []
        - comparison operators: eq, ne, gt, gte, lt, lte
                              (  =, !=,  >,  >=,  <,  <= )
        - logical operators: AND, OR
    """

    SEARCH_QUERY = "q"
    EXPR_DELIMITER = {"(": ")", "[": "]"}
    FIELD_DELIMITER = {"'": "'", '"': '"'}
    ARITMETIC_OPERATORS = {
        "eq": "",
        "ne": "",
        "gt": "__gt",
        "gte": "__gte",
        "lt": "__lt",
        "lte": "__lte",
    }
    NEGATOR_OPERATORS = ["ne"]
    LOGIC_OPERATORS = {
        "AND": lambda x, y: x & y,
        "OR": lambda x, y: x | y,
    }
    WHITESPACE_CHARS = [" "]

    def filter_queryset(self, request, queryset, view):
        if (
            hasattr(request, "query_params")
            and self.SEARCH_QUERY in request.query_params
        ):
            q = self.build_query(request.query_params[self.SEARCH_QUERY])
            return queryset.filter(q)
        return queryset

    def _init_query_builder(self, query: str):
        "This class is filled with state. Better than nothing"
        self.q_delim_stack: List[str] = []  # stack for (((
        self.q_oper_stack: List[str] = []  # stack for eq, ne, gt...
        self.q_logic_stack: List[str] = []  # # stack for AND, OR...
        self.q_field_stack: List[str] = []  # stack for "field", 42, "somevalue"
        self.q_expr_stack: List[Q] = []  # stack for Q(f__gt=1), Q(q1|Q(Q(q2)&Q(q3)))..
        self.q_pos = 0
        self.query_string = query
        self.q_len = len(query)

    def build_query(self, query: str) -> Q:
        "build a Q object from the query string"
        self._init_query_builder(query)

        while self.q_pos < self.q_len:
            self._find_expression()

        while len(self.q_logic_stack) > 0:
            # join all sequencial operations (there is no precedence)
            self._queue_logic_expression()

        if (
            len(self.q_field_stack) != 0
            or len(self.q_oper_stack) != 0
            or len(self.q_logic_stack) != 0
            or len(self.q_expr_stack) > 1
        ):
            raise ParseError(self.q_len, "Missing expression ending")

        if len(self.q_expr_stack) == 0:
            # empty search field
            return Q()

        return self.q_expr_stack.pop()

    def _find_expression(self):
        "main workflow. Parse the query for an expression"
        self._find_logical_operator()

        if self._find_expression_start():
            self._find_expression()
            return

        if self._find_expression_end():
            self._queue_logic_expression()
            return

        self._find_field()

        self._find_arithmetic_operator()

        self._find_field()

        self._queue_arithmetic_expression()

    def _skip_whitespaces(self):
        "advance the q_pos out of whitespaces"
        while self.query_string[self.q_pos] in self.WHITESPACE_CHARS:
            self.q_pos += 1

    def _find_expression_start(self) -> bool:
        "parse starting expression (parenthesis)"
        self._skip_whitespaces()
        if self.query_string[self.q_pos] in self.EXPR_DELIMITER:
            self.q_delim_stack.append(self.query_string[self.q_pos])
            self.q_pos += 1
            return True
        return False

    def _find_expression_end(self) -> bool:
        "parse ending expression (parenthesis). Tests for matching previous expr_start"
        self._skip_whitespaces()
        if self.query_string[self.q_pos] in self.EXPR_DELIMITER.values():
            if len(self.q_delim_stack) == 0:
                raise ParseError(
                    self.q_pos,
                    "Unmatched ending delimiter %s",
                    self.query_string[self.q_pos],
                )
            popped = self.q_delim_stack.pop()
            if self.EXPR_DELIMITER[popped] != self.query_string[self.q_pos]:
                raise ParseError(
                    self.q_pos,
                    "Unmatched delimiters %s and %s",
                    popped,
                    self.query_string[self.q_pos],
                )
            self.q_pos += 1
            return True
        return False

    def _find_field(self):
        "parse a string field/value, optionally delimited"
        self._skip_whitespaces()

        start = self.q_pos
        if self.query_string[self.q_pos] in self.FIELD_DELIMITER:
            # if the field is delimited
            field_delimiter = self.query_string[self.q_pos]
            self.q_pos += 1
            start = self.q_pos

            # advance until end of field
            while (
                self.q_pos < self.q_len
                and self.query_string[self.q_pos]
                != self.FIELD_DELIMITER[field_delimiter]
            ):
                self.q_pos += 1

            # if the while ended because of q_len, there was no field end
            if self.q_pos >= self.q_len:
                raise ParseError(start, "Unmatched field delimiter")

        else:
            # there is no string delimiter (eg: a number)
            field_end_chars = [*self.WHITESPACE_CHARS, *self.EXPR_DELIMITER.values()]
            while (
                self.q_pos < self.q_len
                and self.query_string[self.q_pos] not in field_end_chars
            ):
                self.q_pos += 1

        # slice end is exclusive
        self.q_field_stack.append(self.query_string[start : self.q_pos])

    def _find_logical_operator(self):
        "parse logical operators AND OR.."
        # operators must be SPACED delimited
        self._skip_whitespaces()
        start = self.q_pos
        while (
            self.q_pos < self.q_len
            and self.query_string[self.q_pos] not in self.WHITESPACE_CHARS
        ):
            self.q_pos += 1

        operator = self.query_string[start : self.q_pos]

        if operator not in self.LOGIC_OPERATORS:
            # this was not a logical operator. then backtrack
            self.q_pos = start
            return

        self.q_logic_stack.append(operator)

    def _find_arithmetic_operator(self):
        "parse binary operators (+,-,...)"
        # operators must be SPACED delimited
        self._skip_whitespaces()

        start = self.q_pos
        while (
            self.q_pos < self.q_len
            and self.query_string[self.q_pos] not in self.WHITESPACE_CHARS
        ):
            self.q_pos += 1

        operator = self.query_string[start : self.q_pos]
        if operator not in self.ARITMETIC_OPERATORS:
            raise ParseError(self.q_pos - 1, "Invalid Arithmetic Operator %s", operator)

        self.q_oper_stack.append(operator)

    def _queue_logic_expression(self):
        "join an expression with OR or AND"
        if len(self.q_logic_stack) > 0:
            right_operand = self.q_expr_stack.pop()
            left_operand = self.q_expr_stack.pop()
            operator = self.q_logic_stack.pop()

            q = self.LOGIC_OPERATORS[operator](left_operand, right_operand)
            self.q_expr_stack.append(q)

    def _queue_arithmetic_expression(self):
        "join an fields to create an expression"
        right_operand = self.q_field_stack.pop()
        left_operand = self.q_field_stack.pop()
        operator = self.q_oper_stack.pop()

        q = self._make_unit_Q(left=left_operand, operator=operator, right=right_operand)
        self.q_expr_stack.append(q)

    def _make_unit_Q(self, left: str, operator: str, right: str) -> Q:
        # create a Q object
        left_operated = left + self.ARITMETIC_OPERATORS[operator]
        params = {left_operated: right}

        if operator in self.NEGATOR_OPERATORS:
            return ~Q(**params)
        return Q(**params)
