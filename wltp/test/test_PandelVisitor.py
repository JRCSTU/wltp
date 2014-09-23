# Copyright (c) 2013 Julian Berman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import division, print_function, unicode_literals

from collections import deque
from contextlib import contextmanager
import json
import unittest
from unittest.case import skip
from wltp.pandel import PandelVisitor

from jsonschema import validators, FormatChecker, ValidationError
from jsonschema.validators import (
    RefResolutionError, UnknownType, RefResolver,
    Draft3Validator, Draft4Validator
)

import numpy as np
import numpy.testing as npt
import pandas as pd


try:
    from unittest import mock
except ImportError:
    import mock




def validate(instance, schema, *args, **kws):
    return PandelVisitor(schema, *args, **kws).validate(instance)

def wrap_as_sequences(seq):
    """
    Accepts a sequence and yields it like (list, tuple, ndarray),
    """


def wrap_in_pandas(dict_or_list, wrap_as_df=False):
    """
    Accepts a mapping and yields it like (dict, Series),
    """
    if isinstance(dict_or_list, dict):
            for op in (dict, pd.Series):
                yield op(dict_or_list)
            if wrap_as_df:
                yield pd.DataFrame(dict_or_list)
    else:
        for op in (list, tuple, np.array):
            yield op(dict_or_list)


class TestIterErrors(unittest.TestCase):
    def iter_errors(self, instance, schema, *args, **kwds):
        self.validator = PandelVisitor(schema)
        return self.validator.iter_errors(instance, *args, **kwds)


    #@skip("For Draft3Validator only!")
    def test_iter_errors(self):
        data = [1, 2]
        for instance in wrap_in_pandas(data):
            schema = {
                "$schema" : "http://json-schema.org/draft-03/schema#",
                u"disallow" : u"array",
                u"enum" : [["a", "b", "c"], ["d", "e", "f"]],
                u"minItems" : 3
            }

            got = (e for e in self.iter_errors(instance, schema))
            expected = [
                "disallow",
                "minItems",
                "enum",
            ]
            self.assertListEqual(sorted(e.validator for e in got), sorted(expected))

    def test_iter_errors_multiple_failures_one_validator(self):
        tree1 = {"foo" : 2, "bar" : [1], "baz" : 15, "quux" : "spam"}
        tree2 = {"foo" : 2, "bar" : np.array([1]), "baz" : 15, "quux" : "spam"}
        for data in (tree1, tree2,):
            for instance in wrap_in_pandas(data):
                schema = {
                    u"properties" : {
                        "foo" : {u"type" : "string"},
                        "bar" : {u"minItems" : 2},
                        "baz" : {u"maximum" : 10, u"enum" : [2, 4, 6, 8]},
                    }
                }

                errors = list(self.iter_errors(instance, schema))
                self.assertEqual(len(errors), 4, errors)


class TestValidationErrorMessages(unittest.TestCase):
    def message_for(self, instance, schema, *args, **kwargs):
        with self.assertRaises(ValidationError) as e:
            validate(instance, schema, *args, **kwargs)
        return e.exception.message

    def test_single_type_failure(self):
        message = self.message_for(instance=1, schema={u"type" : u"string"})
        self.assertEqual(message, "1 is not of type %r" % u"string")

    def test_single_type_list_failure(self):
        message = self.message_for(instance=1, schema={u"type" : [u"string"]})
        self.assertEqual(message, "1 is not of type %r" % u"string")

    def test_multiple_type_failure(self):
        types = u"string", u"object"
        message = self.message_for(instance=1, schema={u"type" : list(types)})
        self.assertEqual(message, "1 is not of type %r, %r" % types)

    #@skip("For Draft3Validator only!")
    def test_object_without_title_type_failure(self):
        atype = {
            u"type" : [{u"minimum" : 3}],
        }
        schema = {
            "$schema" : "http://json-schema.org/draft-03/schema#",
            u"type" : [atype]
        }
        message = self.message_for(instance=1, schema=schema)
        self.assertEqual(message, "1 is not of type %r" % (atype,))

    #@skip("For Draft3Validator only!")
    def test_object_with_name_type_failure(self):
        name = "Foo"
        schema = {
            u"type" : [{u"name" : name, u"minimum" : 3}],
            "$schema" : "http://json-schema.org/draft-03/schema#"
        }
        message = self.message_for(instance=1, schema=schema)
        self.assertEqual(message, "1 is not of type %r" % (name,))

    def test_minimum(self):
        message = self.message_for(instance=1, schema={"minimum" : 2})
        self.assertEqual(message, "1 is less than the minimum of 2")

    def test_maximum(self):
        message = self.message_for(instance=1, schema={"maximum" : 0})
        self.assertEqual(message, "1 is greater than the maximum of 0")

    def test_dependencies_failure_has_single_element_not_list(self):
        depend, on = "bar", "foo"
        schema = {
            u"dependencies" : {depend : on},
            "$schema" : "http://json-schema.org/draft-03/schema#"
        }
        data = {"bar" : 2}
        for instance in wrap_in_pandas(data):
            message = self.message_for(instance, schema)
            self.assertEqual(message, "%r is a dependency of %r" % (on, depend))

    def test_additionalItems_single_failure(self):
        data = [2]
        for instance in wrap_in_pandas(data):
            message = self.message_for(
                instance, {
                    u"items" : [], u"additionalItems" : False,
                    "$schema" : "http://json-schema.org/draft-03/schema#"
            },
            )
        self.assertIn("(2 was unexpected)", message)

    def test_additionalItems_multiple_failures(self):
        data  = [1, 2, 3]
        for instance in wrap_in_pandas(data):
            message = self.message_for(
                instance, {
                    "$schema" : "http://json-schema.org/draft-03/schema#",
                    u"items" : [], u"additionalItems" : False
                }
            )
            self.assertIn("(1, 2, 3 were unexpected)", message)

    def test_additionalProperties_single_failure(self):
        additional = "foo"
        schema = {u"additionalProperties" : False}
        data  = {additional : 2}
        for instance in wrap_in_pandas(data):
            message = self.message_for(instance, schema)
            self.assertIn("(%r was unexpected)" % (additional,), message)

    def test_additionalProperties_multiple_failures(self):
        schema = {u"additionalProperties" : False}
        data  = ["foo", "bar"]
        for instance in wrap_in_pandas(data):
            message = self.message_for(dict.fromkeys(instance), schema)

            self.assertIn(repr("foo"), message)
            self.assertIn(repr("bar"), message)
            self.assertIn("were unexpected)", message)

    def test_invalid_format_default_message(self):
        checker = FormatChecker(formats=())
        check_fn = mock.Mock(return_value=False)
        checker.checks(u"thing")(check_fn)

        schema = {u"format" : u"thing"}
        message = self.message_for("bla", schema, format_checker=checker)

        self.assertIn(repr("bla"), message)
        self.assertIn(repr("thing"), message)
        self.assertIn("is not a", message)


class TestValidationErrorDetails(unittest.TestCase):
    # TODO: These really need unit tests for each individual rule, rather
    #       than just these higher level tests.
    def test_anyOf(self):
        instance = 5
        schema = {
            "anyOf": [
                {"minimum": 20},
                {"type": "string"}
            ]
        }

        validator = PandelVisitor(schema)
        errors = list(validator.iter_errors(instance))
        self.assertEqual(len(errors), 1)
        e = errors[0]

        self.assertEqual(e.validator, "anyOf")
        self.assertEqual(e.validator_value, schema["anyOf"])
        self.assertEqual(e.instance, instance)
        self.assertEqual(e.schema, schema)
        self.assertIsNone(e.parent)

        self.assertEqual(e.path, deque([]))
        self.assertEqual(e.relative_path, deque([]))
        self.assertEqual(e.absolute_path, deque([]))

        self.assertEqual(e.schema_path, deque(["anyOf"]))
        self.assertEqual(e.relative_schema_path, deque(["anyOf"]))
        self.assertEqual(e.absolute_schema_path, deque(["anyOf"]))

        self.assertEqual(len(e.context), 2)

        e1, e2 = sorted_errors(e.context)

        self.assertEqual(e1.validator, "minimum")
        self.assertEqual(e1.validator_value, schema["anyOf"][0]["minimum"])
        self.assertEqual(e1.instance, instance)
        self.assertEqual(e1.schema, schema["anyOf"][0])
        self.assertIs(e1.parent, e)

        self.assertEqual(e1.path, deque([]))
        self.assertEqual(e1.absolute_path, deque([]))
        self.assertEqual(e1.relative_path, deque([]))

        self.assertEqual(e1.schema_path, deque([0, "minimum"]))
        self.assertEqual(e1.relative_schema_path, deque([0, "minimum"]))
        self.assertEqual(
            e1.absolute_schema_path, deque(["anyOf", 0, "minimum"]),
        )

        self.assertFalse(e1.context)

        self.assertEqual(e2.validator, "type")
        self.assertEqual(e2.validator_value, schema["anyOf"][1]["type"])
        self.assertEqual(e2.instance, instance)
        self.assertEqual(e2.schema, schema["anyOf"][1])
        self.assertIs(e2.parent, e)

        self.assertEqual(e2.path, deque([]))
        self.assertEqual(e2.relative_path, deque([]))
        self.assertEqual(e2.absolute_path, deque([]))

        self.assertEqual(e2.schema_path, deque([1, "type"]))
        self.assertEqual(e2.relative_schema_path, deque([1, "type"]))
        self.assertEqual(e2.absolute_schema_path, deque(["anyOf", 1, "type"]))

        self.assertEqual(len(e2.context), 0)

    #@skip("For Draft3Validator only!")
    def test_type(self):
        instance = {"foo": 1}
        schema = {
            "$schema" : "http://json-schema.org/draft-03/schema#",
            "type": [
                {"type": "integer"},
                {
                    "type": "object",
                    "properties": {
                        "foo": {"enum": [2]}
                    }
                }
            ]
        }

        validator = PandelVisitor(schema)
        data  = {"foo": 1}
        for instance in wrap_in_pandas(data):
            errors = list(validator.iter_errors(instance))
            self.assertEqual(len(errors), 1)
            e = errors[0]

            self.assertEqual(e.validator, "type")
            self.assertEqual(e.validator_value, schema["type"])
            npt.assert_array_equal(e.instance, instance)
            self.assertEqual(e.schema, schema)
            self.assertIsNone(e.parent)

            self.assertEqual(e.path, deque([]))
            self.assertEqual(e.relative_path, deque([]))
            self.assertEqual(e.absolute_path, deque([]))

            self.assertEqual(e.schema_path, deque(["type"]))
            self.assertEqual(e.relative_schema_path, deque(["type"]))
            self.assertEqual(e.absolute_schema_path, deque(["type"]))

            self.assertEqual(len(e.context), 2)

            e1, e2 = sorted_errors(e.context)

            self.assertEqual(e1.validator, "type")
            self.assertEqual(e1.validator_value, schema["type"][0]["type"])
            npt.assert_array_equal(e1.instance, instance)
            self.assertEqual(e1.schema, schema["type"][0])
            self.assertIs(e1.parent, e)

            self.assertEqual(e1.path, deque([]))
            self.assertEqual(e1.relative_path, deque([]))
            self.assertEqual(e1.absolute_path, deque([]))

            self.assertEqual(e1.schema_path, deque([0, "type"]))
            self.assertEqual(e1.relative_schema_path, deque([0, "type"]))
            self.assertEqual(e1.absolute_schema_path, deque(["type", 0, "type"]))

            self.assertFalse(e1.context)

            self.assertEqual(e2.validator, "enum")
            self.assertEqual(e2.validator_value, [2])
            npt.assert_array_equal(e2.instance, 1)
            self.assertEqual(e2.schema, {u"enum" : [2]})
            self.assertIs(e2.parent, e)

            self.assertEqual(e2.path, deque(["foo"]))
            self.assertEqual(e2.relative_path, deque(["foo"]))
            self.assertEqual(e2.absolute_path, deque(["foo"]))

            self.assertEqual(
                e2.schema_path, deque([1, "properties", "foo", "enum"]),
            )
            self.assertEqual(
                e2.relative_schema_path, deque([1, "properties", "foo", "enum"]),
            )
            self.assertEqual(
                e2.absolute_schema_path,
                deque(["type", 1, "properties", "foo", "enum"]),
            )

            self.assertFalse(e2.context)

    def test_single_nesting(self):
        data = {"foo" : 2, "bar" : [1], "baz" : 15, "quux" : "spam"}
        schema = {
            "properties" : {
                "foo" : {"type" : "string"},
                "bar" : {"minItems" : 2},
                "baz" : {"maximum" : 10, "enum" : [2, 4, 6, 8]},
            }
        }

        validator = PandelVisitor(schema)
        for instance in wrap_in_pandas(data):
            errors = validator.iter_errors(instance)
            errors = sorted_errors(errors)
            try:
                e1, e2, e3, e4 = errors
            except ValueError as ex:
                print(list(sorted_errors(validator.iter_errors(instance))))
                raise ex

            self.assertEqual(e1.path, deque(["bar"]))
            self.assertEqual(e2.path, deque(["baz"]))
            self.assertEqual(e3.path, deque(["baz"]))
            self.assertEqual(e4.path, deque(["foo"]))

            self.assertEqual(e1.relative_path, deque(["bar"]))
            self.assertEqual(e2.relative_path, deque(["baz"]))
            self.assertEqual(e3.relative_path, deque(["baz"]))
            self.assertEqual(e4.relative_path, deque(["foo"]))

            self.assertEqual(e1.absolute_path, deque(["bar"]))
            self.assertEqual(e2.absolute_path, deque(["baz"]))
            self.assertEqual(e3.absolute_path, deque(["baz"]))
            self.assertEqual(e4.absolute_path, deque(["foo"]))

            self.assertEqual(e1.validator, "minItems")
            self.assertEqual(e2.validator, "enum")
            self.assertEqual(e3.validator, "maximum")
            self.assertEqual(e4.validator, "type")

    #@skip("For Draft3Validator only!")
    def test_multiple_nesting(self):
        instance = [1, {"foo" : 2, "bar" : {"baz" : [1]}}, "quux"]
        schema = {
            "$schema" : "http://json-schema.org/draft-03/schema#",
            "type" : "string",
            "items" : {
                "type" : ["string", "object"],
                "properties" : {
                    "foo" : {"enum" : [1, 3]},
                    "bar" : {
                        "type" : "array",
                        "properties" : {
                            "bar" : {"required" : True},
                            "baz" : {"minItems" : 2},
                        }
                    }
                }
            }
        }

        validator = PandelVisitor(schema)
        errors = validator.iter_errors(instance)
        e1, e2, e3, e4, e5, e6 = sorted_errors(errors)

        self.assertEqual(e1.path, deque([]))
        self.assertEqual(e2.path, deque([0]))
        self.assertEqual(e3.path, deque([1, "bar"]))
        self.assertEqual(e4.path, deque([1, "bar", "bar"]))
        self.assertEqual(e5.path, deque([1, "bar", "baz"]))
        self.assertEqual(e6.path, deque([1, "foo"]))

        self.assertEqual(e1.schema_path, deque(["type"]))
        self.assertEqual(e2.schema_path, deque(["items", "type"]))
        self.assertEqual(
            list(e3.schema_path), ["items", "properties", "bar", "type"],
        )
        self.assertEqual(
            list(e4.schema_path),
            ["items", "properties", "bar", "properties", "bar", "required"],
        )
        self.assertEqual(
            list(e5.schema_path),
            ["items", "properties", "bar", "properties", "baz", "minItems"]
        )
        self.assertEqual(
            list(e6.schema_path), ["items", "properties", "foo", "enum"],
        )

        self.assertEqual(e1.validator, "type")
        self.assertEqual(e2.validator, "type")
        self.assertEqual(e3.validator, "type")
        self.assertEqual(e4.validator, "required")
        self.assertEqual(e5.validator, "minItems")
        self.assertEqual(e6.validator, "enum")

    def test_additionalProperties(self):
        data = {"bar": "bar", "foo": 2}
        schema = {
            "additionalProperties" : {"type": "integer", "minimum": 5}
        }

        validator = PandelVisitor(schema)

        for instance in wrap_in_pandas(data):
            errors = validator.iter_errors(instance)
            e1, e2 = sorted_errors(errors)

            self.assertEqual(e1.path, deque(["bar"]))
            self.assertEqual(e2.path, deque(["foo"]))

            self.assertEqual(e1.validator, "type")
            self.assertEqual(e2.validator, "minimum")

    def test_patternProperties(self):
        data = {"bar": 1, "foo": 2}
        schema = {
            "patternProperties" : {
                "bar": {"type": "string"},
                "foo": {"minimum": 5}
            }
        }

        validator = PandelVisitor(schema)

        for instance in wrap_in_pandas(data):
            errors = validator.iter_errors(instance)
            try:
                e1, e2 = sorted_errors(errors)
            except ValueError as ex:
                print(list(sorted_errors(validator.iter_errors(instance))))
                raise ex

            self.assertEqual(e1.path, deque(["bar"]))
            self.assertEqual(e2.path, deque(["foo"]))

            self.assertEqual(e1.validator, "type")
            self.assertEqual(e2.validator, "minimum")

    def test_additionalItems(self):
        data = ["foo", 1]
        schema = {
            "$schema" : "http://json-schema.org/draft-03/schema#",
            "items": [],
            "additionalItems" : {"type": "integer", "minimum": 5}
        }

        validator = PandelVisitor(schema)

        for instance in wrap_in_pandas(data):
            errors = validator.iter_errors(instance)
            e1, e2 = sorted_errors(errors)

            self.assertEqual(e1.path, deque([0]))
            self.assertEqual(e2.path, deque([1]))

            if not isinstance(instance, np.ndarray):
                ## numpy-arrays have column-types so str+int-->str and both errors are type-errors.
                self.assertSequenceEqual([e.validator for e in (e1,e2)], ("type", "minimum"), (e1,e2))

    def test_additionalItems_with_items(self):
        data = ["foo", "bar", 1]
        schema = {
            "items": [{}],
            "additionalItems" : {"type": "integer", "minimum": 5}
        }

        validator = PandelVisitor(schema)

        for instance in wrap_in_pandas(data):
            errors = validator.iter_errors(instance)
            e1, e2 = sorted_errors(errors)

            self.assertEqual(e1.path, deque([1]))
            self.assertEqual(e2.path, deque([2]))

            if not isinstance(instance, np.ndarray):
                ## numpy-arrays have column-types so str+int-->str and both errors are type-errors.
                self.assertSequenceEqual([e.validator for e in (e1,e2)], ("type", "minimum"), (e1,e2))


class ValidatorTestMixin(object):
    def setUp(self):
        self.instance = mock.Mock()
        self.schema = {}
        self.resolver = mock.Mock()
        self.validator = self.validator_class(self.schema)

    def test_valid_instances_are_valid(self):
        errors = iter([])

        with mock.patch.object(                                     # @UndefinedVariable
            self.validator, "iter_errors", return_value=errors,
        ):
            self.assertTrue(
                self.validator.is_valid(self.instance, self.schema)
            )

    def test_invalid_instances_are_not_valid(self):
        errors = iter([mock.Mock()])

        with mock.patch.object(                                     # @UndefinedVariable
            self.validator, "iter_errors", return_value=errors,
        ):
            self.assertFalse(
                self.validator.is_valid(self.instance, self.schema)
            )

    def test_non_existent_properties_are_ignored(self):
        instance, my_property, my_value = mock.Mock(), mock.Mock(), mock.Mock()
        validate(instance=instance, schema={my_property : my_value})

    def test_it_creates_a_ref_resolver_if_not_provided(self):
        self.assertIsInstance(self.validator.resolver, RefResolver)

    def test_it_delegates_to_a_ref_resolver(self):
        resolver = RefResolver("", {})
        schema = {"$ref" : mock.Mock()}

        @contextmanager
        def resolving():
            yield {"type": "integer"}

        with mock.patch.object(resolver, "resolving") as resolve:   # @UndefinedVariable
            resolve.return_value = resolving()
            with self.assertRaises(ValidationError):
                self.validator_class(schema, resolver=resolver).validate(None)

        resolve.assert_called_once_with(schema["$ref"])

    def test_is_type_is_true_for_valid_type(self):
        self.assertTrue(self.validator.is_type("foo", "string"))

    def test_is_type_is_false_for_invalid_type(self):
        self.assertFalse(self.validator.is_type("foo", "array"))

    def test_is_type_evades_bool_inheriting_from_int(self):
        self.assertFalse(self.validator.is_type(True, "integer"))
        self.assertFalse(self.validator.is_type(True, "number"))

    def test_is_type_raises_exception_for_unknown_type(self):
        with self.assertRaises(UnknownType):
            self.validator.is_type("foo", object())


class TestDraft3lValidator(ValidatorTestMixin, unittest.TestCase):
    validator_class = PandelVisitor
    def setUp(self):
        super(TestDraft3lValidator, self).setUp()
        self.validator = PandelVisitor({
            "$schema" : "http://json-schema.org/draft-03/schema#"
    })


    #@skip("For Draft3Validator only!")
    def test_is_type_is_true_for_any_type(self):
        self.assertTrue(self.validator.is_valid(mock.Mock(), { "type": "any" }))

    #@skip("For Draft3Validator only!")
    def test_is_type_does_not_evade_bool_if_it_is_being_tested(self):
        self.assertTrue(self.validator.is_type(True, "boolean"))
        self.assertTrue(self.validator.is_valid(True, { "type": "any" }))

    #@skip("The schema below in invalid under Draft3/4, but original test had averted meta-validation.")
    def test_non_string_custom_types(self):
        schema = {
            "$schema" : "http://json-schema.org/draft-03/schema#",
            'type': [None]
        }
        cls = self.validator_class(schema, types={None: type(None)}, skip_meta_validation=True)
        cls.validate(None, schema)

        schema = {
            "$schema" : "http://json-schema.org/draft-03/schema#",
            'type': 'some'
        }
        types={
            'object': dict,
            'some': pd.DataFrame,
        }
        cls = self.validator_class(schema, types=types, skip_meta_validation=True)
        cls.validate(pd.DataFrame(), schema)


class TestDraft4Validator(ValidatorTestMixin, unittest.TestCase):
    validator_class = PandelVisitor


class TestSchemaIsChecked(unittest.TestCase):  ## Was: class TestValidate
    def test_draft3_validator_is_chosen(self):
        pv = PandelVisitor({})
        schema = {"$schema" : "http://json-schema.org/draft-03/schema#"}
        with mock.patch.object(pv, "iter_errors", return_value=()) as chk_schema:      # @UndefinedVariable
            pv.validate({}, schema)
            chk_schema.assert_called_once_with({}, schema)

        # Make sure it works without the empty fragment
        pv = PandelVisitor({})
        schema = {"$schema" : "http://json-schema.org/draft-03/schema"}
        with mock.patch.object(pv, "iter_errors", return_value=()) as chk_schema:      # @UndefinedVariable
            pv.validate({}, schema)
            chk_schema.assert_called_once_with({}, schema)

    def test_draft4_validator_is_chosen(self):
        pv = PandelVisitor({})
        schema = {"$schema" : "http://json-schema.org/draft-04/schema#"}
        with mock.patch.object(pv, "iter_errors", return_value=()) as chk_schema:      # @UndefinedVariable
            pv.validate({}, schema)
            chk_schema.assert_called_once_with({}, schema)

    def test_draft4_validator_is_the_default(self):
        pv = PandelVisitor({})
        with mock.patch.object(pv, "iter_errors", return_value=()) as chk_schema:      # @UndefinedVariable
            pv.validate({}, {})
            chk_schema.assert_called_once_with({}, {})



class TestRefResolver(unittest.TestCase):

    base_uri = ""
    stored_uri = "foo://stored"
    stored_schema = {"stored" : "schema"}

    def setUp(self):
        self.referrer = {}
        self.store = {self.stored_uri : self.stored_schema}
        self.resolver = RefResolver(self.base_uri, self.referrer, self.store)

    def test_it_resolves_local_refs(self):
        ref = "#/properties/foo"
        self.referrer["properties"] = {"foo" : object()}
        with self.resolver.resolving(ref) as resolved:
            self.assertEqual(resolved, self.referrer["properties"]["foo"])

    def test_it_resolves_local_refs_with_id(self):
        schema = {"id": "foo://bar/schema#", "a": {"foo": "bar"}}
        resolver = RefResolver.from_schema(schema)
        with resolver.resolving("#/a") as resolved:
            self.assertEqual(resolved, schema["a"])
        with resolver.resolving("foo://bar/schema#/a") as resolved:
            self.assertEqual(resolved, schema["a"])

    def test_it_retrieves_stored_refs(self):
        with self.resolver.resolving(self.stored_uri) as resolved:
            self.assertIs(resolved, self.stored_schema)

        self.resolver.store["cached_ref"] = {"foo" : 12}
        with self.resolver.resolving("cached_ref#/foo") as resolved:
            self.assertEqual(resolved, 12)

    def test_it_retrieves_unstored_refs_via_requests(self):
        ref = "http://bar#baz"
        schema = {"baz" : 12}

        with mock.patch("jsonschema.validators.requests") as requests:
            requests.get.return_value.json.return_value = schema
            with self.resolver.resolving(ref) as resolved:
                self.assertEqual(resolved, 12)
        requests.get.assert_called_once_with("http://bar")

    def test_it_retrieves_unstored_refs_via_urlopen(self):
        ref = "http://bar#baz"
        schema = {"baz" : 12}

        with mock.patch("jsonschema.validators.requests", None):
            with mock.patch("jsonschema.validators.urlopen") as urlopen:
                urlopen.return_value.read.return_value = (
                    json.dumps(schema).encode("utf8"))
                with self.resolver.resolving(ref) as resolved:
                    self.assertEqual(resolved, 12)
        urlopen.assert_called_once_with("http://bar")

    def test_it_can_construct_a_base_uri_from_a_schema(self):
        schema = {"id" : "foo"}
        resolver = RefResolver.from_schema(schema)
        self.assertEqual(resolver.base_uri, "foo")
        with resolver.resolving("") as resolved:
            self.assertEqual(resolved, schema)
        with resolver.resolving("#") as resolved:
            self.assertEqual(resolved, schema)
        with resolver.resolving("foo") as resolved:
            self.assertEqual(resolved, schema)
        with resolver.resolving("foo#") as resolved:
            self.assertEqual(resolved, schema)

    def test_it_can_construct_a_base_uri_from_a_schema_without_id(self):
        schema = {}
        resolver = RefResolver.from_schema(schema)
        self.assertEqual(resolver.base_uri, "")
        with resolver.resolving("") as resolved:
            self.assertEqual(resolved, schema)
        with resolver.resolving("#") as resolved:
            self.assertEqual(resolved, schema)

    def test_custom_uri_scheme_handlers(self):
        schema = {"foo": "bar"}
        ref = "foo://bar"
        foo_handler = mock.Mock(return_value=schema)
        resolver = RefResolver("", {}, handlers={"foo": foo_handler})
        with resolver.resolving(ref) as resolved:
            self.assertEqual(resolved, schema)
        foo_handler.assert_called_once_with(ref)

    def test_cache_remote_on(self):
        ref = "foo://bar"
        foo_handler = mock.Mock()
        resolver = RefResolver(
            "", {}, cache_remote=True, handlers={"foo" : foo_handler},
        )
        with resolver.resolving(ref):
            pass
        with resolver.resolving(ref):
            pass
        foo_handler.assert_called_once_with(ref)

    def test_cache_remote_off(self):
        ref = "foo://bar"
        foo_handler = mock.Mock()
        resolver = RefResolver(
            "", {}, cache_remote=False, handlers={"foo" : foo_handler},
        )
        with resolver.resolving(ref):
            pass
        with resolver.resolving(ref):
            pass
        self.assertEqual(foo_handler.call_count, 2)

    def test_if_you_give_it_junk_you_get_a_resolution_error(self):
        ref = "foo://bar"
        foo_handler = mock.Mock(side_effect=ValueError("Oh no! What's this?"))
        resolver = RefResolver("", {}, handlers={"foo" : foo_handler})
        with self.assertRaises(RefResolutionError) as err:
            with resolver.resolving(ref):
                pass
        self.assertEqual(str(err.exception), "Oh no! What's this?")



def sorted_errors(errors):
    def key(error):
        return (
            [str(e) for e in error.path],
            [str(e) for e in error.schema_path]
        )
    return sorted(errors, key=key)
