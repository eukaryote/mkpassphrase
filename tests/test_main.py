from subprocess import Popen, PIPE
import sys

import pytest

# import mkpassphrase
from mkpassphrase import internal, __version__


def run(*args):
    cmd = [sys.executable, "-m", "mkpassphrase.main"] + list(args)
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr


@pytest.mark.parametrize("arg", ["-V", "--version"])
def test_main_version(arg):
    rc, out, err = run(arg)
    assert rc == 0
    expected = "mkpassphrase {}".format(__version__)
    assert out.strip().decode("ascii") == expected
    assert not err


@pytest.mark.parametrize("param", ["-n", "--num-words"])
@pytest.mark.parametrize("arg", ["0", "-1"])
def test_main_invalid_num_words(param, arg):
    rc, out, err = run(param, arg)
    assert rc == 1
    assert not out
    msg = err.decode("utf-8").strip()
    assert msg == "--num-words must be positive if provided"


@pytest.mark.parametrize("param", ["-t", "--times"])
@pytest.mark.parametrize("arg", ["0", "-1"])
def test_main_invalid_times(param, arg):
    rc, out, err = run(param, arg)
    assert rc == 1
    assert not out
    msg = err.decode("utf-8").strip()
    assert msg == "--times must be positive if provided"


@pytest.mark.parametrize("param", ["-f", "--word-file"])
def test_main_not_both_word_list_and_word_file(param, word_file):
    rc, out, err = run(param, word_file, "--word-list", internal.WORD_LIST_DEFAULT)
    assert not out
    assert rc == 1
    msg = err.decode("utf-8").strip()
    assert msg == "only one of --word-list and --word-file is allowed"


@pytest.mark.parametrize("param", ["-f", "--word-file"])
def test_main_word_file_not_accessible(param, word_file):
    path = word_file + ".xxx"
    rc, out, err = run(param, path)
    assert not out
    assert rc == 1
    msg = err.decode("utf-8").strip()
    assert msg == "word file does not exist or is not readable: {}".format(path)


def test_main_run_success_defaults():
    rc, out, err = run()
    assert not err
    assert rc == 0
    lines = [l.strip() for l in out.decode("utf-8").strip().split("\n") if l.strip()]
    assert len(lines) == 2
    assert len(lines[0].split(internal.DELIMITER)) >= 4
    assert "security level" in lines[1]


def test_main_run_success_non_default_wordlist():
    rc, out, err = run("--word-list", "eff1")
    assert rc == 0
    assert not err
    lines = [l.strip() for l in out.decode("utf-8").strip().split("\n") if l.strip()]
    assert len(lines) == 2
    assert len(lines[0].split(internal.DELIMITER)) >= 4
    assert "security level" in lines[-1]


def test_main_run_success_times_multiple():
    times = 5
    rc, out, err = run("--times", str(times))
    assert rc == 0
    assert not err
    lines = [l.strip() for l in out.decode("utf-8").strip().split("\n") if l.strip()]
    assert len(lines) == times + 1
    for i in range(times):
        assert len(lines[i].split(internal.DELIMITER)) >= 4
    assert "security level" in lines[-1]


@pytest.mark.parametrize("param", ["-q", "--quiet"])
def test_main_quiet(param):
    rc, out, err = run(param)
    assert rc == 0
    assert not err
    lines = [l.strip() for l in out.decode("utf-8").strip().split("\n") if l.strip()]
    assert len(lines) == 1
    assert "security level" not in lines[0]
    assert len(lines[0].split(internal.DELIMITER)) >= 4


def test_main_not_run(capsys):
    import mkpassphrase.main  # noqa

    out, err = capsys.readouterr()
    assert not out
    assert not err
