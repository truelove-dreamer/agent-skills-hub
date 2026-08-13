import json
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pytest

from fetch_stars import (
    backfill_from_star_history,
    fetch_current_stars,
    repo_slug,
    write_snapshot,
)


def test_repo_slug():
    assert repo_slug("https://github.com/anthropics/skills") == "anthropics/skills"


def test_fetch_current_stars():
    response = mock.MagicMock()
    response.read.return_value = json.dumps({"stargazers_count": 4242}).encode()
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value = response
        assert fetch_current_stars("a/b") == 4242


def test_fetch_current_stars_uses_token():
    response = mock.MagicMock()
    response.read.return_value = json.dumps({"stargazers_count": 1}).encode()
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value = response
        fetch_current_stars("a/b", token="secret-token")
    request = urlopen.call_args.args[0]
    assert request.get_header("Authorization") == "Bearer secret-token"


def test_fetch_error_propagates():
    with mock.patch("urllib.request.urlopen", side_effect=Exception("boom")):
        with pytest.raises(Exception):
            fetch_current_stars("a/b")


def test_write_snapshot_overwrites_same_day(tmp_path):
    first = write_snapshot(tmp_path, "2026-08-13", {"a/b": 1})
    second = write_snapshot(tmp_path, "2026-08-13", {"a/b": 2})
    assert first == second
    data = json.loads(second.read_text(encoding="utf-8"))
    assert data["repos"]["a/b"] == 2


def test_backfill_gracefully_skips_when_service_degraded(capsys):
    body = b"<text>GitHub restricted access to star data</text>"
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value.read.return_value = body
        backfill_from_star_history("2026-08-13", ["a/b"])
    assert "跳过回填" in capsys.readouterr().out


def test_backfill_ignores_network_errors(capsys):
    with mock.patch("urllib.request.urlopen", side_effect=Exception("boom")):
        backfill_from_star_history("2026-08-13", ["a/b"])
    assert "跳过" in capsys.readouterr().out
