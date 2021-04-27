# -*- coding: utf-8 -*-
try:
    import arrow
except ImportError:
    raise ImportError("The arrow package is not installed.")

try:
    from odin.codecs.json_codec import JSON_TYPES
except ImportError:
    pass
else:
    JSON_TYPES[arrow.Arrow] = str

try:
    from odin.codecs.yaml_codec import YAML_TYPES
except ImportError:
    pass
else:
    YAML_TYPES[arrow.Arrow] = str

try:
    from odin.codecs.msgpack_codec import TYPE_SERIALIZERS
except ImportError:
    pass
else:
    TYPE_SERIALIZERS[arrow.Arrow] = str
