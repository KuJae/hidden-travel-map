// 우리 FastAPI 주소. 로컬 서버로 시험할 때는 페이지 주소 뒤에 ?api=http://127.0.0.1:8000 을 붙인다.
export const API = new URLSearchParams(location.search).get("api") || "https://hidden-travel-map-api.onrender.com";

// Render 무료 서버는 잠들어 있으면 첫 요청이 1분 가까이 걸린다. 3초가 넘으면 onSlow 로 알려 준다.
export async function getJSON(path, onSlow) {
  const slow = setTimeout(() => onSlow && onSlow(), 3000);
  try {
    const res = await fetch(API + path);
    if (!res.ok) throw new Error(`${path} 응답 오류 (HTTP ${res.status})`);
    return await res.json();
  } finally {
    clearTimeout(slow);
  }
}

// 1,234 / 3.1만 / 63만 처럼 읽기 쉬운 사람 수
export function people(n) {
  if (n >= 100000) return `${Math.round(n / 10000).toLocaleString("ko-KR")}만`;
  if (n >= 10000) return `${(n / 10000).toFixed(1).replace(/\.0$/, "")}만`;
  return Math.round(n).toLocaleString("ko-KR");
}
export const num = (n, d = 0) => Number(n).toLocaleString("ko-KR", { maximumFractionDigits: d, minimumFractionDigits: d });

// SVG 요소 만들기
const NS = "http://www.w3.org/2000/svg";
export function el(tag, attrs = {}, parent) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (parent) parent.appendChild(n);
  return n;
}
export function text(parent, x, y, str, attrs = {}) {
  const t = el("text", { x, y, ...attrs }, parent);
  t.textContent = str;
  return t;
}

// 툴팁 하나를 페이지 전체가 같이 쓴다. 내용은 textContent 로만 넣는다.
const tip = document.createElement("div");
tip.className = "tooltip";
tip.setAttribute("role", "status");
document.body.appendChild(tip);
export function showTip(evt, title, rows) {
  tip.textContent = "";
  const b = document.createElement("b");
  b.textContent = title;
  tip.appendChild(b);
  for (const [k, v] of rows) {
    const line = document.createElement("div");
    const key = document.createElement("span");
    key.className = "k";
    key.textContent = `${k} `;
    line.append(key, document.createTextNode(v));
    tip.appendChild(line);
  }
  const r = evt.target.getBoundingClientRect ? evt.target.getBoundingClientRect() : null;
  const x = evt.clientX ?? (r ? r.right : 0), y = evt.clientY ?? (r ? r.top : 0);
  tip.classList.add("on");
  const w = tip.offsetWidth, h = tip.offsetHeight;
  tip.style.left = `${Math.min(x + 14, innerWidth - w - 8)}px`;
  tip.style.top = `${Math.max(8, y - h - 12)}px`;
}
export function hideTip() { tip.classList.remove("on"); }

// 표 보기 (차트마다 같은 내용을 표로도 제공)
export function fillTable(details, headers, rows) {
  const table = details.querySelector("table");
  table.textContent = "";
  const thead = table.createTHead().insertRow();
  for (const h of headers) { const th = document.createElement("th"); th.textContent = h; thead.appendChild(th); }
  const tbody = table.createTBody();
  for (const r of rows) {
    const tr = tbody.insertRow();
    for (const c of r) tr.insertCell().textContent = c;
  }
}
