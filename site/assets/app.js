async function fetchJSON(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path}: HTTP ${response.status}`);
  }
  return response.json();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function metricValue(row) {
  return row.delta == null ? row.stars : row.delta;
}

function boardRows(rows) {
  return rows
    .map(
      (row) => `<tr>
        <td>${row.rank}</td>
        <td><a href="${escapeHtml(row.repo)}" target="_blank" rel="noopener">${escapeHtml(row.name)}</a></td>
        <td>${metricValue(row)}</td>
        <td>${row.categories.map(escapeHtml).join(", ")}</td>
        <td>${escapeHtml(row.description)}</td>
      </tr>`
    )
    .join("");
}

function renderBoard(rows, tableId, emptyText = "暂无数据") {
  const tbody = document.querySelector(`#${tableId} tbody`);
  tbody.innerHTML = rows.length
    ? boardRows(rows)
    : `<tr><td colspan="5">${escapeHtml(emptyText)}</td></tr>`;
}

async function initHome() {
  const [rankings, skills] = await Promise.all([
    fetchJSON("data/rankings.json"),
    fetchJSON("data/skills.json"),
  ]);
  renderBoard(rankings.weekly.slice(0, 10), "weekly-table", "周榜暂无数据（快照积累中，1–4 周后自动出现）");
  renderBoard(rankings.yearly.slice(0, 10), "yearly-table");
  document.querySelector("#updated-at").textContent = rankings.updated_at || "暂无";
  document.querySelector("#skill-count").textContent = skills.skills.length;
}

async function initRankings() {
  const rankings = await fetchJSON("data/rankings.json");
  renderBoard(rankings.weekly, "weekly-table");
  renderBoard(rankings.monthly, "monthly-table");
  renderBoard(rankings.yearly, "yearly-table");
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach((b) => b.classList.remove("active"));
      button.classList.add("active");
      document.querySelectorAll(".board").forEach((board) => (board.style.display = "none"));
      document.querySelector(`#${button.dataset.target}`).style.display = "";
    });
  });
}

async function initCategories() {
  const [categories, skills] = await Promise.all([
    fetchJSON("data/categories.json"),
    fetchJSON("data/skills.json"),
  ]);
  const container = document.querySelector("#category-cards");
  container.innerHTML = categories.categories
    .map((category) => {
      const count = skills.skills.filter((s) => s.categories.includes(category.key)).length;
      return `<div class="card category-card" data-key="${escapeHtml(category.key)}">
        <h3>${escapeHtml(category.name)}</h3>
        <p class="muted">${escapeHtml(category.audience)}</p>
        <span class="count">${count} 个技能</span>
      </div>`;
    })
    .join("");
  container.querySelectorAll(".category-card").forEach((card) => {
    card.addEventListener("click", () => {
      const key = card.dataset.key;
      const filtered = skills.skills.filter((s) => s.categories.includes(key));
      document.querySelector("#skill-list").innerHTML = filtered
        .map(
          (s) => `<div class="skill-item">
            <a href="${escapeHtml(s.entry)}" target="_blank" rel="noopener">${escapeHtml(s.name)}</a>
            <span class="muted"> — ${escapeHtml(s.description)}</span>
          </div>`
        )
        .join("");
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page === "home") {
    initHome().catch((error) => console.error(error));
  } else if (document.body.dataset.page === "rankings") {
    initRankings().catch((error) => console.error(error));
  } else if (document.body.dataset.page === "categories") {
    initCategories().catch((error) => console.error(error));
  }
});
