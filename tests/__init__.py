# coding=utf-8

# set default encoding to utf8 for testing so that running tests that
# mimic reading utf-8 encoded data from a dict file on non-ascii encoding
# python installations still work even though tests are being run on a
# python 2 that uses 'ascii' as the default encoding
import sys
if sys.version_info <= (3,):
    reload(sys)
    sys.setdefaultencoding('UTF-8')


test_words = (
    'A', 'Be', 'Cee', 'FOO', "Foo's", 'fo10', 'Bar', 'bar',
    'qUx', 'Qux', 'quúux', 'quux', 'quuux', 'quuuux', 'quuuuux', 'quuuuuuux',
    'quuuuuuuux'
)
