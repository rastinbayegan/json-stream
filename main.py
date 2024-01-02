import json
from io import StringIO
from typing import TextIO, Union


class LazyList:

    def __init__(self, file: TextIO):
        self._file = file
        self.start_of_root_reached = False

    def __iter__(self):
        return self

    @staticmethod
    def is_start_of_item(buffer: str) -> bool:
        return len(buffer) == 1

    @staticmethod
    def is_end_of_item(start_char: str, current_char: str, buffer: str) -> bool:
        map = {
            '{': '}',
            '"': '"',
            '[': ']'
        }
        return len(buffer) > 1 and current_char == map[start_char]

    def __next__(self):
        buffer = ""
        item_start_char = None

        while True:
            char = self._file.read(1)

            if char == '[' and not self.start_of_root_reached:
                self.start_of_root_reached = True
                continue

            if char == ']' and item_start_char != '[':
                raise StopIteration

            if char in [',', ' ', '\n', '\t']:
                continue

            buffer += char

            if self.is_start_of_item(buffer):
                item_start_char = char

            if self.is_end_of_item(start_char=item_start_char, current_char=char, buffer=buffer):
                break

        return json.loads(buffer)


def lazy_json(file: TextIO) -> 'LazyList':
    return LazyList(file)


def test_returns_lazy_list():
    json_file = StringIO('[]')
    lazy = lazy_json(json_file)

    assert isinstance(lazy, LazyList)


def test_ignores_preceding_white_space():
    json_file = StringIO('  []')
    lazy = lazy_json(json_file)
    assert isinstance(lazy, LazyList)

    json_file = StringIO('\n   \t[]')
    lazy = lazy_json(json_file)

    assert isinstance(lazy, LazyList)


def test_lazy_list_is_an_iterable():
    json_file = StringIO('[]')
    lazy = lazy_json(json_file)

    assert hasattr(lazy, '__iter__')
    assert hasattr(lazy, '__next__')


def test_lazy_list_returns_strings():
    json_file = StringIO('["one", "two", "three"]')
    for i, item in enumerate(lazy_json(json_file)):
        if i == 0:
            assert item == 'one'

        if i == 1:
            assert item == 'two'

        if i == 2:
            assert item == 'three'


def test_lazy_list_returns_lists():
    json_file = StringIO('[["one"], ["two"], ["three"]]')
    for i, item in enumerate(lazy_json(json_file)):
        if i == 0:
            assert item == ['one']

        if i == 1:
            assert item == ['two']

        if i == 2:
            assert item == ['three']


def test_lazy_list_returns_dicts():
    json_file = StringIO('[{"key_1": "value_1"}, {"key_2": "value_2"}]')
    for i, item in enumerate(lazy_json(json_file)):
        if i == 0:
            assert item == {"key_1": "value_1"}

        if i == 1:
            assert item == {"key_2": "value_2"}