"""The reviewed exception path for the aggregate growth trigger.

Its own file because these tests are one unit, and because the per-file
net cap is unwaivable by design -- an arriving file is exempt from that
cap, which is the exemption working rather than a way around it.
"""

from __future__ import annotations

import subprocess

import pytest

import check_no_ceremony as cnc


def test_a_growth_exception_is_structural_and_cannot_be_stretched(tmp_path):
    """The ceiling becomes a trigger without becoming optional.

    An entry cannot key on the final head -- writing a head into a commit
    changes it -- so it names the code head and no Python may follow. Each arm
    is a way to reuse a reviewed exception for bytes nobody reviewed.
    """
    root = tmp_path / "repo"
    (root / "config").mkdir(parents=True)
    manifest = root / "config/growth-exceptions.toml"

    def git(*args):
        out = subprocess.run(["git", "-C", str(root), *args], check=True,
                             capture_output=True, text=True)
        return out.stdout.strip()

    def write(**over):
        entry = {"net": 115, "rationale": "reviewer judged proportionality", **over}
        manifest.write_text("[[exception]]\n" + "".join(
            f"{k} = {v!r}\n" if isinstance(v, str) else f"{k} = {v}\n"
            for k, v in entry.items()), encoding="utf-8")

    for setup in (("init", "-q", "-b", "main"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t")):
        git(*setup)
    (root / "a.py").write_text("x = 1\n")
    git("add", "-A"), git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    (root / "a.py").write_text("x = 1\ny = 2\n")
    git("add", "-A"), git("commit", "-qm", "code")
    head = git("rev-parse", "HEAD")

    write(base=base, code_head=head)
    assert cnc._approved_growth_exception(root, base, 115), "the reviewed range must pass"
    for over in ({"net": 116}, {"code_head": base}, {"base": head}, {"rationale": " "}):
        write(**{"base": base, "code_head": head, **over})
        assert cnc._approved_growth_exception(root, base, 115) is None, over

    manifest.write_text(manifest.read_text() * 2, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        cnc._approved_growth_exception(root, base, 115)
    manifest.write_text("[[exception\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unreadable"):
        cnc._approved_growth_exception(root, base, 115)

    write(base=base, code_head=head)
    (root / "a.py").write_text("x = 1\ny = 2\nz = 3\n")
    git("add", "-A"), git("commit", "-qm", "python after the reviewed code head")
    assert cnc._approved_growth_exception(root, base, 115) is None, "no Python after G"


def test_the_exception_seam_refuses_unreviewed_working_tree_bytes(tmp_path, monkeypatch):
    """Through rule_python_growth, which is where the decision is actually made.

    The direct-helper controls above all passed while this shipped: a code head
    of 100 committed lines, a pin of 115, and an untracked 15-line file summed
    to the pinned arithmetic and returned PASS. A comparison between two
    commits cannot see working-tree bytes, so the tree must be clean before an
    exception is consulted.
    """
    root = tmp_path / "repo"
    (root / "config").mkdir(parents=True)

    def git(*args):
        out = subprocess.run(["git", "-C", str(root), *args], check=True,
                             capture_output=True, text=True)
        return out.stdout.strip()

    for setup in (("init", "-q", "-b", "main"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t")):
        git(*setup)
    (root / "a.py").write_text("x = 0\n")
    git("add", "-A"), git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    # An introduced file: the per-file cap exempts arrivals and is unwaivable
    # anyway, so growing one existing file would fail for the right reason and
    # prove nothing about the aggregate exception.
    over = cnc.MAX_PYTHON_NET_GROWTH + 15
    (root / "new.py").write_text("".join(f"x{n} = {n}\n" for n in range(over)))
    git("add", "-A"), git("commit", "-qm", "reviewed code")
    code_head = git("rev-parse", "HEAD")

    monkeypatch.setattr(cnc, "ROOT", root)
    monkeypatch.setattr(cnc, "_growth_base", lambda: base)
    (root / "config/growth-exceptions.toml").write_text(
        f'[[exception]]\nbase = "{base}"\ncode_head = "{code_head}"\n'
        f'net = {over}\nrationale = "reviewer judged proportionality"\n', encoding="utf-8")

    assert cnc.rule_python_growth()[0] == "PASS", "the reviewed, clean range must pass"

    (root / "extra.py").write_text("y = 1\n")
    assert cnc.rule_python_growth()[0] == "FAIL", "untracked Python must void it"
    (root / "extra.py").unlink()
    (root / "new.py").write_text((root / "new.py").read_text() + "tail = 1\n")
    assert cnc.rule_python_growth()[0] == "FAIL", "a dirty tracked file must void it"
