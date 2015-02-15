from inspect import getargspec, stack
from collections import OrderedDict
from itertools import izip
from functools import wraps

class prototype(object):
    _registry_collection = {}

    def __init__(self, **prototype):
        self._prototype = prototype

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
            )
        )

        return wraps(fn)(
            lambda *args, **kwargs: self.handler(function_key, registry, args, kwargs)
        )

    @staticmethod
    def handler(function_key, registry, args, kwargs):
        for fn, spec, _prototype, _permissible_values in registry[function_key]:
            parameter_names = spec.args

            # Capture the parameters and their defaults
            instance_parameters = OrderedDict(
                izip(
                    parameter_names,
                    [] if spec.defaults is None else spec.defaults,
                )
            )

            # Merge in the positional parameter values
            instance_parameters.update(
                izip(
                    parameter_names,
                    args,
                )
            )

            # Add in the keyword argument values
            instance_parameters.update(kwargs)

            if len(instance_parameters) < len(args):
                continue
            elif set(kwargs.keys()).difference(instance_parameters.keys()):
                continue

            # Get the types of each parameter
            instance_prototype = {
                _key: _value if type(_value) == type else type(_value)
                for _key, _value
                in instance_parameters.iteritems()
            }

            # Not a candidate if the type signatures don't match
            if _prototype != instance_prototype:
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
                # All values were found to be permissible, so call the function
                return fn(**instance_parameters)

        raise NotImplementedError(
            "Function '%s' cannot be found with the expressed signature (%s, %s)" % (
                ":".join(function_key),
                args,
                kwargs,
            )
        )
