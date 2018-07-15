# coding=utf-8

from __future__ import absolute_import, division, print_function

import os

import six

tests_dir = os.path.abspath(os.path.dirname(__file__))

test_words = tuple(
    map(
        six.u,
        (
            "A",
            "Be",
            "Cee",
            "FOO",
            "fo10",
            "Bar",
            "bar",
            "anise",
            "blue",
            "green",
            "mauve",
            "qUx",
            "Qux",
            "quúux",
            "quux",
            "quuux",
            "quuuux",
            "quuuuux",
            "quuuuuuux",
            "quuuuuuuux",
        ),
    )
)
