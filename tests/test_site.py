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


def test_board_ids_on_table_elements():
    for page in ["index.html", "rankings.html"]:
        html = (SITE / page).read_text(encoding="utf-8")
        for table_id in ["weekly-table", "monthly-table", "yearly-table"]:
            if table_id in html:
                assert f'<table id="{table_id}">' in html, f"{page}: {table_id} 应挂在 <table> 上"


def test_categories_uses_left_right_layout():
    html = (SITE / "categories.html").read_text(encoding="utf-8")
    assert "categories-layout" in html
    assert "category-panel" in html
    assert "skill-panel" in html
