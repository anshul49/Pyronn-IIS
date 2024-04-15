from ._protocols import Parameter, NumericalParameter, ListParameter, ArrayParameter, Validator  # noqa: F401
from ._types import Bool, Int, Float, Option, String, Tuple, List, Array, PathParam, GenericData
from ._validators import DefaultValidator, TypeValidator  # noqa: F401
from ._validators import SequenceValidator, ArrayValidator, NumericalValidator, PathValidator  # noqa: F401


def parameter_factory(parameter_id: str, parameter_values_as_dict: dict) -> Parameter:
    """
    Factory to create Parameter from a type id.
    """
    id_parameter_map = {
        'genericdata': GenericData,
        'bool': Bool,
        'int': Int,
        'float': Float,
        'string': String,
        'option': Option,
        'list': List,
        'pathparam': PathParam,
        'tuple': Tuple,
        'array': Array,
    }
    try:
        parameter = id_parameter_map[parameter_id]
    except KeyError:
        raise NotImplementedError(
            f'parameter with ID "{parameter_id}" not implemented yet (possible IDs: {tuple(id_parameter_map.keys())})'
        )

    return parameter.from_dict(parameter_values_as_dict)
