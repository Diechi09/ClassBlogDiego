async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function loadStats() {
  const el = document.getElementById("statsContent");
  try {
    const data = await fetchJSON("/api/stats");
    const { counts, latest } = data;
    el.innerHTML = `
      <div style="display:flex; gap:1rem; flex-wrap:wrap;">
        <div><strong>Total:</strong> ${counts.TOTAL}</div>
        <div><strong>Trade:</strong> ${counts.TRADE_HELP}</div>
        <div><strong>Waiver:</strong> ${counts.WAIVER_WIRE}</div>
        <div><strong>Injury:</strong> ${counts.INJURY_TALK}</div>
        <div><strong>Other:</strong> ${counts.OTHER}</div>
      </div>
      <h3 style="margin:.75rem 0 .25rem;">Latest</h3>
      <ul style="margin:0; padding-left:1rem;">
        ${latest.map(p => `
          <li>
            <a href="/post/${p.id}">${p.title}</a>
            <span class="badge" style="margin-left:.25rem;">${p.flair.replace('_',' ')}</span>
            <small> • ${p.author}</small>
          </li>`).join("")}
      </ul>
    `;
  } catch (e) {
    el.textContent = "Failed to load stats.";
  }
}

async function loadSearch(page = 1) {
  const q = document.getElementById("q").value.trim();
  const flair = document.getElementById("flair").value;
  const params = new URLSearchParams({ page });
  if (q) params.set("q", q);
  if (flair) params.set("flair", flair);

  const resEl = document.getElementById("results");
  const pagerEl = document.getElementById("pager");
  resEl.textContent = "Loading…";
  pagerEl.textContent = "";

  try {
    const data = await fetchJSON(`/api/posts?${params.toString()}`);
    if (!data.items.length) {
      resEl.textContent = "No results.";
      return;
    }
    resEl.innerHTML = data.items.map(p => `
      <article style="margin:.5rem 0; padding:.5rem; border:1px solid #1f2937; border-radius:8px;">
        <div style="display:flex; justify-content:space-between; gap:.5rem; align-items:baseline;">
          <h3 style="margin:.25rem 0;">
            <a href="/post/${p.id}" style="color:#60a5fa; text-decoration:none;">${p.title}</a>
            <span class="badge">${p.flair.replace('_',' ')}</span>
          </h3>
          <a href="/api/posts/${p.id}" style="font-size:.85rem;">View JSON</a>
        </div>
        <small>by ${p.author} • ${new Date(p.date_posted).toLocaleString()}</small>
      </article>
    `).join("");

    // simple pager
    const { page, pages, total } = data;
    const prev = page > 1 ? `<button class="btn" data-goto="${page - 1}">Prev</button>` : "";
    const next = page < pages ? `<button class="btn" data-goto="${page + 1}">Next</button>` : "";
    pagerEl.innerHTML = `
      <div style="display:flex; align-items:center; gap:.5rem;">
        ${prev}
        <span>Page ${page} / ${pages} • ${total} results</span>
        ${next}
      </div>
    `;
    pagerEl.querySelectorAll("button[data-goto]").forEach(btn => {
      btn.addEventListener("click", () => loadSearch(parseInt(btn.dataset.goto, 10)));
    });
  } catch (e) {
    resEl.textContent = "Search failed.";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadStats();
  const form = document.getElementById("searchForm");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    loadSearch(1);
  });
});
