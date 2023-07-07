import sys
import json
import struct
from itertools import chain
from collections import deque

obj_in_test = None

with open("../test-geojson/multipolygon.json") as json_obj:
    obj_in_test = json.load(json_obj)


def total_size(o, handlers={}, verbose=False):
    """Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {
        tuple: iter,
        list: iter,
        deque: iter,
        dict: dict_handler,
        set: iter,
        frozenset: iter,
    }
    all_handlers.update(handlers)  # user handlers take precedence
    seen = set()  # track which object id's have already been seen
    default_size = sys.getsizeof(0)  # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:  # do not double count the same object
            return 0
        seen.add(id(o))
        s = sys.getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=sys.stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)


print(f"size as python dict: {total_size(obj_in_test)}")

as_json = json.dumps(obj_in_test)
print(f"json: {sys.getsizeof(as_json)}")

stripped = "".join(as_json.split())
print(f"no whitespace: {sys.getsizeof(stripped)}")


as_bytes = memoryview(stripped.encode("ascii")).tobytes()
print(f"as bytes: {sys.getsizeof(as_bytes)}")

new_dict = json.loads(stripped)

print(f"reverted dict: {(total_size(new_dict))}")

# print(f"as bytes {as_bytes}")
