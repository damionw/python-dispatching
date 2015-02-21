from inspect import getargspec, stack
from collections import OrderedDict
from itertools import izip
from functools import wraps

class prototype(object):
    _registry_collection = {}

    def __init__(self, **prototype):
        self._prototype = dict(prototype)
        self._allow_partial_match = self._prototype.pop('allow_partial_match', False)

    @classmethod
    def format_specification_elements(cls, prototype):
        for parameter_name, parameter_spec in prototype.iteritems():
            parameter_type = type(parameter_spec)

            if parameter_type == type:
                parameter_spec = (parameter_spec, None)
            elif parameter_type in {tuple, list}:
                pass
            else:
                raise Exception("Type specification for '%s' must be either a single type or a tuple, not %s" % (parameter_name, parameter_type))

            yield parameter_name, parameter_spec

    @classmethod
    def get_type_spec(cls, prototype):
        return (
            (_name, _type) for _name, (_type, _values) in cls.format_specification_elements(prototype)
        )

    @classmethod
    def get_value_spec(cls, prototype):
        return (
            (_name, _values) for _name, (_type, _values) in cls.format_specification_elements(prototype)
        )

    def __call__(self, fn):
        def get_scope_key_elements(stack_info):
            filename = stack_info[1][1]

            for row in stack_info[1:]:
                if row[1] != filename:
                    break

                if row[3].startswith("<"):
                    continue

                yield row[3]

            yield filename

        # Determine the function scope
        scope_key = ".".join(
            reversed(map(str, get_scope_key_elements(stack())))
        )

        # Determine the function key
        function_key = (fn.__module__, fn.__name__)

        # The function registry used is dependent on the scope
        registry = self._registry_collection.setdefault(scope_key, {})

        registry.setdefault(function_key, []).append(
            (
                fn,
                getargspec(fn),
                dict(self.get_type_spec(self._prototype)),
                dict(self.get_value_spec(self._prototype)),
                self._allow_partial_match,
            )
        )

        return wraps(fn)(
            lambda *args, **kwargs: self.handler(
                function_key,
                registry,
                args,
                kwargs,
            )
        )

    @staticmethod
    def handler(function_key, registry, args, kwargs):
        for fn, spec, _prototype, _permissible_values, allow_partial_match in registry[function_key]:
            parameter_names = spec.args

            # Capture the parameters and their defaults
            instance_parameters = OrderedDict(
                izip(
                    parameter_names,
                    [] if spec.defaults is None else spec.defaults,
                )
            )

            # Merge in the positional parameter values
            keyed_positional_args = zip(parameter_names, args)
            instance_parameters.update(keyed_positional_args)

            # Add in the keyword argument values
            instance_parameters.update(kwargs)

            if allow_partial_match:
                # Elide the consumed positional args
                remaining_positional_args = args[max(map(len, [keyed_positional_args, args])):]
            elif len(instance_parameters) < len(args):
                continue
            elif set(kwargs.keys()).difference(instance_parameters.keys()):
                continue

            # Get the types of each parameter
            instance_prototype = {
                _key: _value if type(_value) == type else type(_value)
                for _key, _value
                in instance_parameters.iteritems()
            }

            # Update with extra parameters if we're allowing partial matches
            if allow_partial_match:
                # Get unconsumed prototype arguments
                extra_keys = filter(
                    lambda _x: _x not in instance_parameters.keys(),
                    parameter_names,
                )

                # Get unconsumed positional arguments
                extra_args = OrderedDict(
                    ((_key, _value) for _key, _value in izip(extra_keys, remaining_positional_args))
                )

                # No match if all the function's parameters aren't satisfied
                supplied_keys = set(extra_args.keys() + instance_parameters.keys())

                # Not a candidate if there's a parameter mismatch
                if supplied_keys.symmetric_difference(parameter_names):
                    continue

                trimmed_instance_prototype = dict(
                    (_key, _value)
                    for _key, _value
                    in instance_prototype.iteritems()
                    if _key in _prototype
                )

                # Type match on the partial prototype
                if _prototype != trimmed_instance_prototype:
                    continue
            # Not a candidate if the type signatures don't match exactly
            elif _prototype != instance_prototype:
                continue
            # Also not a candidate if the call has supplied unexpected parameters
            elif set(parameter_names).difference(instance_prototype.keys()):
                continue

            # Check the values for permissibility
            for parameter_name, parameter_value in instance_parameters.iteritems():
                permitted_values = _permissible_values.get(parameter_name)

                if permitted_values is None:
                    continue
                elif parameter_value == permitted_values:
                    continue
                elif hasattr(permitted_values, '__iter__') and not isinstance(permitted_values, str) and parameter_value in permitted_values:
                    continue

                # Found non permissible value
                break
            else:
                # Fill in the extra parameters for partial matches
                if allow_partial_match:
                    instance_parameters.update(extra_args)

                    instance_parameters.update(
                        (_key, _value)
                        for _key, _value
                        in kwargs.iteritems()
                        if _key not in instance_parameters
                    )

                # All values were found to be permissible, so call the function
                return fn(**instance_parameters)

        raise NotImplementedError(
            "Function '%s' cannot be found with the expressed signature (%s, %s)" % (
                ":".join(function_key),
                args,
                kwargs,
            )
        )
