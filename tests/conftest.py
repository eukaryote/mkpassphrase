from __future__ import print_function

import pytest
import tempfile
import os

from tests import test_words


@pytest.fixture
def word_file(request):
    tmp = tempfile.mktemp()
    request.addfinalizer(lambda: os.remove(tmp))
    with open(tmp, 'w') as f:
        for word in test_words:
            print(word, file=f)
    return tmp
