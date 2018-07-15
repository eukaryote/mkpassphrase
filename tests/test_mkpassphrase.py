import six

import mkpassphrase as M


def test_version_info():
    vinfo = M.__version_info__
    assert isinstance(vinfo, tuple)
    for vpart in vinfo[:3]:
        assert isinstance(vpart, int)
        assert vpart >= 0


def test_version():
    version = M.__version__
    str_type = six.binary_type if six.PY2 else six.text_type
    assert isinstance(version, str_type)
