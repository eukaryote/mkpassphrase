import mkpassphrase
from setuptools import setup

setup(
    name=mkpassphrase.__name__,
    version=mkpassphrase.__version__,
    license='http://www.opensource.org/licenses/mit-license.php',
    description='Word-based passphrase generator',
    packages=[mkpassphrase.__name__],
    platforms='any',
    entry_points={
        'console_scripts': [
            '{name} = {name}.main:main'.format(name=mkpassphrase.__name__),
        ]
    },
)
