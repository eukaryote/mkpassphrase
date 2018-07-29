=======
Changes
=======


v3.0.0
------

 * dropped support for python3 before 3.5, so supported versions are
   Python 2.7 and Python 3.5+ for both CPython and PyPy


v2.0.0.post1
------------

 * update CHANGES to reflect 2.0.0 changes (no code changes compared v2.0.0)


v2.0.0
------

 * support using (bundled) `EFF wordlists`_ as the source for words, in addition to
   user-provided wordlists, with the default behavior now being to use the
   long EFF wordlist (7,776 words)
 * support specifying security level to get a passphrase with the required number of
   words for that security level (e.g., `mkpassphrase -s 80` to get a passphrase
   with enough words from the default EFF wordlist for 80 bits of entropy)
 * removed `--min` and `--max` options for ignoring words in a wordlist that are
   too short or too long
 * removed `--non-ascii` option for ignoring words that have non-ascii characters

.. _EFF wordlists: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases


v1.0.0
------

 * 1.0 bump, and change to 'stable'
 * python3 support is limited to 3.2.5+ (python2.7 still supported)
 * added testing against python-3.6 (alpha3 currently)

v0.9.1
------

 * minor adjustments to python2/3 compatibility checks
 * pep257 docstring updates

v0.9.0
------

 * much faster generation of multiple passphrases using `-t`
 * minor verbiage tweaks for non-quiet output

v0.8.0
------

 * use cryptographically secure pseudo-random number generator if available
 * added standard imports to help with python2/3 compatibility

v0.7.0
------

 * added -t|--times N to allow generating multiple passphrases w/ one command

v0.6.8
------

 * include CHANGES.rst and README.rst in sdist via MANIFEST.in

v0.6.7
------

 * cosmetic changes for better PyPI display


v0.6.6
------

 * cosmetic changes for better PyPI display


v0.6.4
-------

 * cosmetic changes for better PyPI display


v0.6.2
------

 * added -q option to omit extra information about how many unique candidate
   words were found and how many passphrases were possible
 * fix for --ascii option not being used, and improved encoding handling
 * start documenting changes in CHANGES.rst
 * use README and CHANGES as long_description for improved pypi info
