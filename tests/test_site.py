from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PAGES = ["index.html", "rankings.html", "categories.html", "about.html"]


def test_pages_exist():
    for page in PAGES:
        assert (SITE / page).exists(), f"缺少 {page}"


def test_pages_use_app_js():
    for page in PAGES:
        html = (SITE / page).read_text(encoding="utf-8")
        assert "assets/app.js" in html


def test_assets_exist():
    assert (SITE / "assets" / "app.js").exists()
    assert (SITE / "assets" / "style.css").exists()


def test_about_covers_boundaries():
    html = (SITE / "about.html").read_text(encoding="utf-8")
    assert "收录边界" in html
    assert "核验" in html


def test_home_shows_yearly_board_and_count():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    assert "yearly-table" in html
    assert "年榜 Top 10" in html
    assert "skill-count" in html
