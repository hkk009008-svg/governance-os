import subprocess
import system_health_check


def test_check_system_health_returns_status():
    status = system_health_check.check_system_health()
    assert isinstance(status.git_clean, bool)
    assert isinstance(status.venv_active, bool)
    assert "Git:" in status.summary


def test_system_health_check_cli():
    res = subprocess.run(
        [".venv/bin/python", "scripts/system_health_check.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "SYSTEM HEALTH CHECK —" in res.stdout
