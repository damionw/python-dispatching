from dispatching import prototype
from unittest import TestCase

class TestBasicDispatching(TestCase):
    def test_basic_functionality(self):
        @prototype(value=int)
        def testit(value):
            return 12

        @prototype(value=str)
        def testit(value):
            return 0

        self.assertEquals(testit(99), 12)
        self.assertEquals(testit("me"), 0)

        self.assertRaises(
            NotImplementedError,
            testit,
            None,
        )

    def test_parameter_type_ordering(self):
        @prototype(value1=int, value2=str, value3=tuple)
        def testit(value1, value2, value3):
            return 0

        @prototype(value1=tuple, value2=str, value3=int)
        def testit(value1, value2, value3):
            return 1

        @prototype(value1=str, value2=int, value3=tuple)
        def testit(value1, value2, value3):
            return 2

        self.assertEquals(testit(1, "two", (3,)), 0)
        self.assertEquals(testit((1,), "two", 3), 1)
        self.assertEquals(testit("one", 2, (3,)), 2)

    def test_named_parameters(self):
        @prototype(value1=int, value2=str, value3=float)
        def testit(value1, value2, value3):
            return True

        self.assertEquals(testit(value3=1.0, value1=1, value2="1.0"), True)

        self.assertRaises(
            NotImplementedError,
            lambda: testit(testit(value3="3.0", value1=None, value2=1.0))
        )

    def test_parameter_values(self):
        @prototype(value=(int, [1,2,3]))
        def testit(value):
            return 0

        @prototype(value=(int, [4,5]))
        def testit(value):
            return 1

        @prototype(value=(int, 6))
        def testit(value):
            return 2

        @prototype(value=(str, "6"))
        def testit(value):
            return 2

        @prototype(value=int)
        def testit(value):
            return 3

        @prototype(value=str)
        def testit(value):
            return 4

        for _val in [1,2,3]:
            self.assertEquals(testit(_val), 0)

        for _val in [4,5]:
            self.assertEquals(testit(_val), 1)

        self.assertEquals(testit(6), 2)
        self.assertEquals(testit("6"), 2)
        self.assertEquals(testit(0), 3)
        self.assertEquals(testit("0"), 4)

    def test_cascading_calls(self):
        @prototype()
        def testit():
            return testit([])

        @prototype(values=list)
        def testit(values):
            return testit("Joe", values)

        @prototype(name=str, values=list)
        def testit(name, values):
            return True

        self.assertTrue(testit())

    def test_partial_prototype_matching(self):
        @prototype(value=int)
        def testit(value):
            return 1

        @prototype(value=int, allow_partial_match=True)
        def testit(value, extra):
            return 2

        @prototype(value=str, allow_partial_match=False)
        def testit(value, extra):
            return 3

        self.assertEquals(testit(1), 1)
        self.assertEquals(testit(1, 7), 2)
        self.assertEquals(testit(1, "whatever"), 2)

        self.assertRaises(
            NotImplementedError,
            testit,
            "what",
        )

        self.assertRaises(
            NotImplementedError,
            testit,
            "what",
            None
        )

