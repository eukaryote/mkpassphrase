# coding=utf-8

from mkpassphrase import u


test_words = tuple(map(u, (
    'A', 'Be', 'Cee', 'FOO', 'fo10', 'Bar', 'bar',
    'anise', 'blue', 'green', 'mauve',
    'qUx', 'Qux', 'quúux', 'quux', 'quuux', 'quuuux', 'quuuuux', 'quuuuuuux',
    'quuuuuuuux'
)))
