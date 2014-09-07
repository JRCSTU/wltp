#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""A :dfn:`pandas-model` is a tree of strings, numbers, sequences, dicts, pandas instances and resolvable
URI-references, implemented by :class:`Pandel`. """

import abc
from collections import OrderedDict, namedtuple
from collections.abc import Mapping, Sequence
from jsonschema import Draft4Validator, ValidationError
import jsonschema
import re

import numpy as np
import pandas as pd


class BranchCntxt(namedtuple('BranchCntxt', 'inp out conv')):
    """
    Infos associated to (sub)models branches, customizing the *conversion* and *IO* operations of self-or-descedant values of the branch.
    """
    def __new__(cls, inp=None, out=None, conv=None):
        """

        :param list inp:    the `args-list` to :meth:`Pandel._read_branch()`

        :param out:         The args to :meth:`Pandel._write_branch()`, that may be specified either as:

                            * an `args-list`, that will apply for all model data-types (lists, dicts & pandas),
                            * a map of ``type`` --> ``args-list``, where the ``None`` key is the *catch-all* case,
                            * a function returning the `args-list` for some branch-value,
                              with signature: ``def get_write_branch_args(branch)``.

        :param conv:        The conversion-functions (:dfn:`convertors`) for the various model's data-types.
                            The convertors have signature ``def convert(branch)``, and they may be
                            specified either as:

                            * a map of ``(from_type, to_type)`` --> ``conversion_func()``, where the ``None`` key
                              is the *catch-all* case,
                            * a "master-switch" function returning the appropriate convertor
                              depending on the requested conversion.
                              The master-function's signature is ``def get_convertor(from_branch, to_branch)``.

                            The minimum convertors demanded by :class:`Pandel` are (at least, check the code for more):

                            * dict --> DataFrame
                            * DataFrame --> dict
                            * dict --> Series
                            * Series --> dict
        """

        return super(BranchCntxt, cls).__new__(cls, inp, out, conv)

    def choose_out_args(self, branch):
        pass

    def choose_convertor(self, from_type, to_type):
        pass




class Pandel:
    """
    Builds, validates and stores a *pandas-model*, a mergeable stack of JSON-schema abiding trees of
    strings and numbers, assembled with

    * sequences,
    * dictionaries,
    * :class:`pandas.DataFrame`,
    * :class:`pandas.Series`, and
    * URI-references to other model-trees.



    .. _pandel-overview:

    **Overview**

    The **making of a model** involves, among others, schema-validating, reading :dfn:`subtree-branches`
    from URIs, cloning, converting and merging multiple :dfn:`sub-models` in a single :dfn:`unified-model` tree,
    without side-effecting given input.
    All these happen in 4+1 steps::

                       ....................... Model Construction .................
          ------------ :  _______    ___________                                  :
         / top_model /-->|Resolve|->|PreValidate|-+                               :
         -----------'  : |___0___|  |_____1_____| |                               :
          ------------ :  _______    ___________  |   _____    ________    ______ :   --------
         / base-model/-->|Resolve|->|PreValidate|-+->|Merge|->|Validate|->|Curate|-->/ model /
         -----------'  : |___0___|  |_____1_____|    |_ 2__|  |___3____|  |__4+__|:  -------'
                       ............................................................

    All steps are executed "lazily" using generators (with :keyword:`yield`).
    Before proceeding to the next step, the previous one must have completed successfully.
    That way, any ad-hoc code in building-step-5(*curation*), for instance, will not suffer a horrible death
    due to badly-formed data.

    [TODO] The **storing of a model** simply involves distributing model parts into different files and/or formats,
    again without side-effecting the unified-model.



    .. _pandel-building-model:

    **Building model**

    Here is a detailed description of each building-step:

    1.  :meth:`_resolve` and substitute any `json-references <http://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03>`_
        present in the submodels with content-fragments fetched from the referred URIs.
        The submodels are **cloned** first, to avoid side-effecting them.

        Although by default a combination of *JSON* and *CSV* files is expected, this can be customized,
        either by the content in the json-ref, within the model (see below), or
        as :ref:`explained  <pandel-customization>` below.

        The **extended json-refs syntax** supported provides for passing arguments into :meth:`_read_branch()`
        and :meth:`_write_branch()` methods.  The syntax is easier to explain by showing what
        the default :attr:`_global_cntxt` corresponds to, for a ``DataFrame``::

            {
              "$ref": "http://example.com/example.json#/foo/bar",
              "$inp": ["AUTO"],
              "$out": ["CSV", "encoding=UTF-8"]
            }

        And here what is required to read and (later) store into a HDF5 local file with a predefined name::

            {
              "$ref": "file://./filename.hdf5",
              "$inp": ["AUTO"],
              "$out": ["HDF5"]
            }

        .. Warning:: Step NOT IMPLEMENTED YET!


    2.  Loosely :meth:`_prevalidate` each sub-model separately with :term:`json-schema`,
        where any pandas-instances (DataFrames and Series) are left as is.
        It is the duty of the developer to ensure that the prevalidation-schema is *loose enough* that
        it allows for various submodel-forms, prior to merging, to pass.


    3.  Recursively **clone**  and :meth:`_merge` sub-models in a single unified-model tree.
        Branches from sub-models higher in the stack override the respective ones from the sub-models below,
        recursively.  Different object types need to be **converted** appropriately (ie. merging
        a ``dict`` with a ``DataFrame`` results into a ``DataFrame``, so the dictionary has to convert
        to dataframe).

        The required **conversions** into pandas classes can be customized as :ref:`explained  <pandel-customization>`
        below.  Series and DataFrames cannot merge together, and Sequences do not merge
        with any other object-type (themselfs included), they just "overwrite".

        The default convertor-functions defined both for submodels and models are listed in the following table:

        ============ ========== =========================================
            From:       To:                  Method:
        ============ ========== =========================================
         dict        DataFrame  ``pd.DataFrame``  (the constructor)
         DataFrame   dict       ``lambda df: df.to_dict('list')``
         dict        Series     ``pd.Series``     (the constructor)
         Series      dict       :meth:`lambda sr: sr.to_dict()`
        ============ ========== =========================================


    4.  Strictly json-:meth:`_validate` the unified-model (ie enforcing ``required`` schema-rules).

        The required **conversions** from pandas classes can be customized as :ref:`explained  <pandel-customization>`
        below.

        The default convertor-functions are the same as above.


    5.  (Optionally) Apply the :meth:`_curate` functions on the the model to enforce dependencies and/or any
        ad-hoc generation-rules among the data.  You can think of bash-like expansion patterns,
        like ``${/some/path:=$HOME}`` or expressions like ``%len(../other/path)``.



    .. _pandel-storing:

    **Storing model**

    When storing model-parts, if unspecified, the filenames to write into will be deduced from the jsonpointer-path
    of the ``$out``'s parent, by substituting "strange" chars with undescores(``_``).

    .. Warning:: Functionality NOT IMPLEMENTED YET!



    .. _pandel-customization:

    **Customization**

    Some operations within steps (namely *conversion* and *IO*) can be customized by the following means
    (from lower to higher precedance):

    a.  The global-default :class:`BranchCntxt` instance on the :attr:`_global_cntxt`,
        applied on both submodels and unified-model.

        For example to channel the whole reading/writing of models through
        `HDF5 <http://pandas.pydata.org/pandas-docs/stable/io.html#io-hdf5>`_ data-format, it would suffice
        to modify the :attr:`_global_cntxt` like that::

            pm = FooPandelModel()                        ## some concrete model-maker
            io_args = ["HDF5"]
            pm.mod_global_cntxt(inp=io_args, out=io_args)

    b.  [TODO] Extra-properties on the json-schema applied on both submodels and unified-model for the specific path defined.
        The supported properties are the non-functional properties of :class:`BranchCntxt`.

    d.  Specific-properties regarding *IO* operations within each submodel - see the *resolve* building-step,
        above.

    c.  Context-maps of ``json_paths`` --> :class:`BranchCntxt` instances, installed by :meth:`add_submodel()` and
        :attr:`unified_contexts` on the model-maker.  They apply to self-or-descedant subtree of each model.

        The `json_path` is a strings obeying a simplified :term:`json-pointer` syntax (no char-normalizations yet),
        ie ``/some/foo/1/pointer``.  An empty-string(``''``) matches all model.

        When multiple convertors match for a model-value, the selected convertor to be used is the most specific one
        (the one with longest prefix).  For instance, on the model::

            [ { "foo": { "bar": 0 } } ]


        all of the following would match the ``0`` value:

        - the global-default :attr:`_global_cntxt`,
        - ``/``, and
        - ``/0/foo``

        but only the last's context-props will be applied.



    .. _Attributes:

    **Atributes**

    .. Attribute:: model

        The model-tree that will receive the merged submodels after :meth:`build()` has been invoked.
        Depending on the submodels, the top-value can be any of the supported model data-types.


    .. Attribute:: _submodels

        The list of (``submodel``, ``contexts_map``) tuples. The list's 1st element is the :dfn:`base-model`,
        the last one, the :dfn:`top-model`.  Use the :meth:`add_submodel()` to build this list.


    .. Attribute:: _global_cntxt

        A :class:`BranchCntxt` instance acting as the global-default context for the unified-model and all submodels.
        Use :meth:`mod_global_cntxt()` to modify it.


    .. Attribute:: _curate_funcs

        The sequence of *curate* functions to be executed as the final step by :meth:`_curate()`.
        They are "normal" functions (not generators) with signature::

            def curate_func(model_maker):
                pass      ## ie: modify ``model_maker.model``.

        Better specify this list of functions on construction time.


    .. Attribute:: _errored

            An internal boolean flag that becomes ``True`` if any build-step has failed,
            to halt proceeding to the next one.  It is ``None`` if build has not started yet.


    .. _pandel-examples:

    **Examples**

    The basic usage requires to subclass your own model-maker, just so that a *json-schema*
    is provided for both validation-steps, 2 & 4:

        >>> from collections import OrderedDict as od                           ## Json is better with stable keys-order

        >>> class MyModel(Pandel):
        ...     def _get_json_schema(self, is_prevalidation):
        ...         return {                                                    ## Define the json-schema.
        ...             '$schema': 'http://json-schema.org/draft-04/schema#',
        ...             'required': [] if is_prevalidation else ['a', 'b'],     ## Prevalidation is more loose.
        ...             'properties': {
        ...                 'a': {'type': 'string'},
        ...                 'b': {'type': 'number'},
        ...                 'c': {'type': 'number'},
        ...             }
        ...         }


    Then you can instanciate it and add your submodels:

        >>> mm = MyModel()
        >>> mm.add_submodule(od(a='foo', b=1)                                   ## submodel-1 (base)
        >>> mm.add_submodule(pd.Series(od(a='bar', c=2}))                       ## submodel-2 (top-model)


    You then have to build the final unified-model (any validation errors would be reported at this point):

        >>> mdl = mm.build()

    Note that you can also access the unified-model in the :attr:`model` attribute.
    You can now interogate it:

        >>> mdl['a'] == 'bar'                       ## Value overridden by top-model
        True
        >>> mdl['b'] == 1                           ## Value left intact from base-model
        True
        >>> mdl['c'] == 2                           ## New value from top-model
        True


    Lets try to construct an invalid model:

        >>> mm = MyModel()
        >>> mm.add_submodule({
        ...     'a': 1,                             ## According to the schema, this should have been a string,
        ...     'b': 'string'                       ## and this one, a number.
        ... }])

        >>> sorted(mm.build_iter(), key=lambda ex: ex.message)                   ## Fetch a list with all validation errors.
        [<ValidationError: "'string' is not of type 'number'">,
        <ValidationError: "1 is not of type 'string'">,
        <ValidationError: 'Gave-up building model after step 2.prevalidate (out of 5).'>]

        >>> mdl = mm.model
        >>> mdl is None                                     ## No model constructed, failed before merging.
        True


    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, curate_funcs=None):
        """

        :param sequence curate_funcs:   See :attr:`_curate_funcs`.
        """

        self.model          = None
        self._errored       = None
        self._submodels     = []
        self._curate_funcs  = list(curate_funcs)
        self._global_cntxt  = sdfddsf
        self._unified_contexts = None


    def mod_global_cntxt(self, branch_cntxt=None, **cntxt_kwargs):
        """

        Since it is the fall-back context for *conversions* and *IO* operation, it must exist and have
        all its props well-defined for the class to work correctly.

        :param branch_cntxt:     Replaces values of the installed context with non-empty values from this one.
        :param cntxt_kwargs:     Replaces the keyworded-values on the existing `branch_cntxt`.
                                 See :class:`BranchCntxt` for supported keywords.
        """
        if branch_cntxt:
            assert isinstance(branch_cntxt, BranchCntxt), (type(branch_cntxt), branch_cntxt)
            self._global_cntxt = branch_cntxt
        self._global_cntxt._replace(**cntxt_kwargs)


    @property
    def unified_contexts(self):
        """
        A map of ``json_paths`` --> :class:`BranchCntxt` instances acting on the unified-model.
        """
        return self._unified_contexts
    @unified_contexts.setter
    def unified_contexts(self, contexts_map):
        assert isinstance(contexts_map, Mapping), (type(contexts_map), contexts_map)
        self._unified_contexts = contexts_map

    def _select_context(self, path, branch):
        """
        Finds which context to use while visiting model-nodes, by enforcing the precedance-rules described
        in the :ref:`Customizations  <pandel-customization>`.

        :param str path:    the branch's jsonpointer-path
        :param str branch:  the actual branch's node
        :return:            the selected :class:`BranchCntxt`
        """
        pass


    def _read_branch(self):
        """
        Reads model-branches during *resolve* step.
        """
        pass # TODO: impl read_branch()
    def _write_branch(self):
        """
        Writes model-branches during *distribute* step.
        """
        pass # TODO: impl write_branch()

    def _get_json_schema(self, is_prevalidation):
        """
        :return: a json schema, more loose when `prevalidation` for each case
        :rtype: dictionary
        """
        pass

    def _rule_AdditionalProperties_for_dict_or_pandas(self, validator, aP, required, instance, schema):
        properties = schema.get("properties", {})
        patterns = "|".join(schema.get("patternProperties", {}))
        extras = set()
        for prop in instance:
            if prop not in properties:
                if patterns and re.search(patterns, prop):
                    continue
                extras.add(prop)

        if validator.is_type(aP, "object"):
            for extra in extras:
                for error in validator.descend(instance[extra], aP, path=extra):
                    yield error
        elif not aP and extras:
            error = "Additional properties are not allowed (%s %s unexpected)"
            yield ValidationError(error % jsonschema._utils.extras_msg(extras))


    def _rule_Required_for_dict_or_pandas(self, validator, required, instance, schema):
        if (validator.is_type(instance, "object") or
                validator.is_type(instance, "DataFrame") or
                 validator.is_type(instance, "Series")):
            for prop in required:
                if prop not in instance:
                    yield ValidationError("%r is a required property" % prop)


    def _get_model_validator(self, schema):

        validator = Draft4Validator(schema)
        validator._types.update({"ndarray": np.ndarray, "DataFrame" : pd.DataFrame, 'Series':pd.Series})
        validator.VALIDATORS['DataFrame'] = self._rule_Required_for_dict_or_pandas

        return validator


    def _validate_json_model(self, schema, mdl):
        validator = self._get_model_validator(schema)
        for err in validator.iter_errors(mdl):
            self._errored = True
            yield err

    def _clone_and_merge_submodels(self, a, b, path=''):
        """' Recursively merge b into a, cloning both. """

        if isinstance(a, pd.DataFrame) or isinstance(b, pd.DataFrame):
            a = pd.DataFrame() if a is None else pd.DataFrame(a)
            b = pd.DataFrame() if b is None else pd.DataFrame(b)

            a.update(b) #, 'outer') NOT IMPL YET
            extra_b_items = list(set(b.columns) - set(a.columns))
            a[extra_b_items] = b[extra_b_items]

        elif isinstance(a, pd.Series) or isinstance(b, pd.Series):
            a = pd.Series() if a is None else pd.Series(a)
            b = pd.Series() if b is None else pd.Series(b)
            #a.update(b) # DOES NOT append extra keys!
            a = b.combine_first(a)

        elif isinstance(a, Mapping) or isinstance(b, Mapping):
            a = OrderedDict() if a is None else OrderedDict(a)
            b = OrderedDict() if b is None else OrderedDict(b)

            for key in b:
                b_val = b[key]
                if key in a:
                    val = self._clone_and_merge_submodels(a[key], b_val, '%s/%s'%(path, key))
                else:
                    val = b_val
                a[key] = val

        elif (isinstance(a, Sequence) and not isinstance(a, str)) or \
                (isinstance(b, Sequence) and not isinstance(b, str)):
            if not b is None:
                val = b
            else:
                val = a

            l = list()
            for (i, item) in enumerate(val):
                l.append(self._clone_and_merge_submodels(item, None, '%s[%i]'%(path, i)))
            a = l

        elif a is None and b is None:
            raise ValidationError("Cannot merge Nones at path(%s)!" % path)

        else:
            if not b is None:
                a = b

        return a

    def _resolve(self):
        "Step-1"
        if False:
            yield

    def _prevalidate(self):
        "Step-1"
        for mdl in self._submodels:
            schema = self._get_json_schema(is_prevalidation=True)
            yield from self._validate_json_model(schema, mdl)

    def _merge(self):
        "Step-2"
        for mdl in self._submodels:
            self.model = self._clone_and_merge_submodels(self.model, mdl)
        if False:
            yield       ## Just mark method as generator.

    def _validate(self):
        "Step-3"
        schema = self._get_json_schema(is_prevalidation=False)
        yield from self._validate_json_model(schema, self.model)

    def _curate(self):
        "Step-4:  Invokes any curate-functions found in :attr:`_curate_funcs`."
        if False:
            yield       ## To be overriden, just mark method as generator.
        for curfunc in self._curate_funcs:
            curfunc(self)

    def add_submodel(self, model, contexts_map=None):
        """
        Pushes on top a submodel, along with its context-map.

        :param model:               the model-tree (sequence, mapping, pandas-types)
        :param dict contexts_map:   A map of ``json_paths`` --> :class:`BranchCntxt` instances acting on the
                                    unified-model.  The `contexts_map` may often be empty.

        **Examples**

        To change the default DataFrame --> dictionary convertor for a submodel, use the following:

            >>> mdl = {'foo': 'bar'}                       ## Some content
            >>> submdl = BranchCntxt(mdl, df_to_map={None: lambda df: df.to_dict('record')})

        """

        if contexts_map:
            assert isinstance(contexts_map, Mapping), (type(contexts_map), contexts_map)

        return self._submodels.append((model, contexts_map))


    def build_iter(self):
        """
        Iteratively build model, yielding any problems as :class:`ValidationError` instances.

        For debugging, the unified model at :attr:`model` my contain intermediate results at any time,
        even if construction has failed.  Check the :attr:`_errored` flag if neccessary.
        """

        steps = [
            (self._prevalidate, 'prevalidate'),
            (self._merge,       'merge'),
            (self._validate,    'validate'),
            (self._curate,      'curate'),
        ]
        self._errored = False
        self.model = None

        for (i, (step, step_name)) in enumerate(steps, start=1):
            try:
                yield from step()
            except ValidationError as ex:
                self._errored = True
                yield ex

            except Exception as ex:
                self._errored = True

                nex = ValidationError('Model step-%i(%s) failed due to: %s'%(i, step_name, ex))
                nex.cause = ex

                yield nex

            if self._errored:
                yield ValidationError('Gave-up building model after step %i.%s (out of %i).'%(i, step_name, len(steps)))
                break

    def build(self):
        """
        Attempts to build the model by exhausting :meth:`build_iter()`, or raises its 1st error.

        Use this method when you do not want to waste time getting the full list of errors.
        """

        err = next(self.build_iter(), None)
        if err:
            raise err

        return self.model

if __name__ == '__main__':
    raise "Not runnable!"
