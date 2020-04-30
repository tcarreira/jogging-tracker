import os
from unittest import expectedFailure

from django.db.models import Q
from django.test import TestCase
from rest_framework import generics, serializers, status
from rest_framework.test import APIRequestFactory

from advanced_filters.filters import AdvancedFilter, ParseError
from api.models import User


class SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class SimpleTestFilterBackend(AdvancedFilter):
    def filter_queryset(self, request, queryset, view):
        queryset = super(SimpleTestFilterBackend, self).filter_queryset(
            request, queryset, view
        )
        queryset = queryset.filter(is_superuser=False)
        return queryset


class SimpleTestView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = SimpleSerializer
    filter_backends = (SimpleTestFilterBackend,)


class TestFilters(TestCase):
    def setUp(self):
        self.filter = AdvancedFilter()

    def test_skip_whitespaces(self):
        self.filter._init_query_builder("     hello")
        self.filter._skip_whitespaces()
        self.assertEqual(self.filter.q_pos, 5)

    def test_find_expression_start(self):
        self.filter._init_query_builder(")false")
        self.assertFalse(self.filter._find_expression_start())

        self.filter._init_query_builder("(true")
        self.assertTrue(self.filter._find_expression_start())

    def test_find_expression_end(self):
        self.filter._init_query_builder("(false")
        self.assertFalse(self.filter._find_expression_end())

        self.filter._init_query_builder(")exception")
        with self.assertRaises(ParseError) as e:
            self.filter._find_expression_end()
        self.assertIn("Unmatched ending delimiter )", str(e.exception))

        self.filter._init_query_builder("()true")
        self.assertTrue(self.filter._find_expression_start())
        self.assertTrue(self.filter._find_expression_end())

        self.filter._init_query_builder("[]true")
        self.assertTrue(self.filter._find_expression_start())
        self.assertTrue(self.filter._find_expression_end())

        self.filter._init_query_builder("(]exception")
        with self.assertRaises(ParseError) as e:
            self.assertTrue(self.filter._find_expression_start())
            self.filter._find_expression_end()
        self.assertIn("Unmatched delimiters ( and ]", str(e.exception))

    def test_find_field(self):
        self.filter._init_query_builder("detected field")
        self.filter._find_field()
        self.assertEqual(self.filter.q_field_stack.pop(), "detected")

        self.filter._init_query_builder("'detected' field")
        self.filter._find_field()
        self.assertEqual(self.filter.q_field_stack.pop(), "detected")

        self.filter._init_query_builder('"detected" field')
        self.filter._find_field()
        self.assertEqual(self.filter.q_field_stack.pop(), "detected")

        self.filter._init_query_builder('"detected") field')
        self.filter._find_field()
        self.assertEqual(self.filter.q_field_stack.pop(), "detected")

        self.filter._init_query_builder("detected) field")
        self.filter._find_field()
        self.assertEqual(self.filter.q_field_stack.pop(), "detected")

        self.filter._init_query_builder('"both detected" fields')
        self.filter._find_field()
        self.assertEqual(self.filter.q_field_stack.pop(), "both detected")

        self.filter._init_query_builder("'raised exception")
        with self.assertRaises(ParseError) as e:
            self.filter._find_field()
        self.assertIn("Unmatched field delimiter at position 1", str(e.exception))

    def test_find_logical_operator(self):
        self.filter._init_query_builder(" OR - detected")
        self.filter._find_logical_operator()
        self.assertEqual(self.filter.q_logic_stack.pop(), "OR")

        self.filter._init_query_builder("AND - detected")
        self.filter._find_logical_operator()
        self.assertEqual(self.filter.q_logic_stack.pop(), "AND")

        self.filter._init_query_builder("OOPS - exception")
        self.filter._find_logical_operator()  # nothing happens
        self.assertEqual(len(self.filter.q_logic_stack), 0)
        self.assertEqual(self.filter.q_pos, 0)

    def test_find_arithmetic_operator(self):

        for op in ["eq", "ne", "lt", "lte", "gt", "gte"]:
            self.filter._init_query_builder(" %s detected" % op)
            self.filter._find_arithmetic_operator()
            self.assertEqual(self.filter.q_oper_stack.pop(), op)

        for op in ["=", "!=", "<", "<=", ">", ">="]:
            with self.assertRaises(ParseError) as e:
                self.filter._init_query_builder(" %s invalid" % op)
                self.filter._find_arithmetic_operator()
            self.assertIn("Invalid Arithmetic Operator %s" % op, str(e.exception))

    def test_queue_logic_expression(self):
        self.filter._init_query_builder("")
        self.filter.q_expr_stack.append(Q(a="a"))
        self.filter.q_expr_stack.append(Q(b="b"))
        self.filter.q_logic_stack.append("AND")
        self.filter._queue_logic_expression()

        q1 = Q(a="a") & Q(b="b")
        self.assertEqual(self.filter.q_expr_stack[-1], q1)

        self.filter.q_expr_stack.append(Q(c="c"))
        self.filter.q_logic_stack.append("OR")
        self.filter._queue_logic_expression()
        q2 = q1 | Q(c="c")
        self.assertEqual(self.filter.q_expr_stack[-1], q2)

    def test_queue_arithmetic_expression(self):
        self.filter._init_query_builder("")

        self.filter.q_field_stack.append("left")
        self.filter.q_field_stack.append("right")
        self.filter.q_oper_stack.append("eq")
        self.filter._queue_arithmetic_expression()
        self.assertEqual(self.filter.q_expr_stack.pop(), Q(left="right"))

        self.filter.q_field_stack.append("left")
        self.filter.q_field_stack.append("right")
        self.filter.q_oper_stack.append("lt")
        self.filter._queue_arithmetic_expression()
        self.assertEqual(self.filter.q_expr_stack.pop(), Q(left__lt="right"))

        self.filter.q_field_stack.append("left")
        self.filter.q_field_stack.append("right")
        self.filter.q_oper_stack.append("ne")
        self.filter._queue_arithmetic_expression()
        self.assertEqual(self.filter.q_expr_stack.pop(), ~Q(left="right"))

    def test_make_unit_Q(self):
        q = self.filter._make_unit_Q("left", "lte", "right")
        self.assertEqual(q, Q(left__lte="right"))


class TestFiltersBlackBox(TestCase):
    def setUp(self):
        pass
        self.factory = APIRequestFactory()

        for i in range(1, 10):  # 9
            User.objects.create(username=f"user_type1_{i}")

        User.objects.create_superuser(
            username="admin", email=None, password="123456"
        )  # always hidden from resulst

    def test_simple_no_filter(self):
        request = self.factory.get("/endpoint")
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 9)

    def test_simple_simple_filter(self):
        request = self.factory.get("/endpoint", {"q": "id eq 5"})
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], 5)

    def test_simple_simple_gt(self):
        request = self.factory.get("/endpoint", {"q": "id gt 5"})
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)  # admin should be hidden
        self.assertEqual(response.data["results"][0]["id"], 6)
        self.assertEqual(response.data["results"][-1]["id"], 9)

    def test_simple_simple_lte(self):
        request = self.factory.get("/endpoint", {"q": "id lte 5"})
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(response.data["results"][0]["id"], 1)
        self.assertEqual(response.data["results"][-1]["id"], 5)

    def test_simple_simple_ne(self):
        request = self.factory.get("/endpoint", {"q": "id ne 5"})
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 8)

    def test_simple_and_operator(self):
        request = self.factory.get(
            "/endpoint", {"q": "id ne 5 AND id gt 3 AND id lt 7"}
        )
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["id"], 4)
        self.assertEqual(response.data["results"][1]["id"], 6)

    def test_simple_or_operator(self):
        request = self.factory.get("/endpoint", {"q": "id eq 4 OR id eq 6"})
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["id"], 4)
        self.assertEqual(response.data["results"][1]["id"], 6)

    def test_precedence_operator(self):
        request = self.factory.get(
            "/endpoint", {"q": "(id gt 5 AND id lt 7) OR id eq 4"}
        )
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        actual = [response.data["results"][0]["id"], response.data["results"][1]["id"]]
        self.assertListEqual(sorted(actual), [4, 6])

    def test_precedence_operator_reverse(self):
        request = self.factory.get(
            "/endpoint", {"q": "id eq 4 OR (id gt 5 AND id lt 7)"}
        )
        view = SimpleTestView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        actual = [response.data["results"][0]["id"], response.data["results"][1]["id"]]
        self.assertListEqual(sorted(actual), [4, 6])
