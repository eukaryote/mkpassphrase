import mkpassphrase
from setuptools import setup

setup(
    name='mkpassphrase',
    version=mkpassphrase.__version__,
    license='http://www.opensource.org/licenses/mit-license.php',
    description='Word-based passphrase generator',
    packages=['mkpassphrase'],
    platforms='any',
    entry_points={
        'console_scripts': [
            'mkpasshrase = mkpassphrase.main:main',
        ]
    },
)
