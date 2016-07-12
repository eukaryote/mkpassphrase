# coding=utf-8

from mkpassphrase import u


test_words = tuple(map(u, (
    'A', 'Be', 'Cee', 'FOO', "Foo's", 'fo10', 'Bar', 'bar',
    'qUx', 'Qux', 'quúux', 'quux', 'quuux', 'quuuux', 'quuuuux', 'quuuuuuux',
    'quuuuuuuux'
)))
