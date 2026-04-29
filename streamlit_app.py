import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time

st.set_page_config(
    page_title="GenCon Game Scout",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:       #0d0f14;
    --surface:  #161a23;
    --card:     #1c2130;
    --border:   #2a3045;
    --accent:   #f0a500;
    --accent2:  #e05c1a;
    --text:     #e8eaf0;
    --muted:    #7a839a;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
h1,h2,h3 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 2px; }

.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background-color: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #000 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 2px !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 2rem !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.game-card-outer {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 1rem 0.5rem 1rem;
    margin-bottom: 1rem;
    transition: border-color .2s, transform .15s;
}
.game-card-outer:hover { border-color: var(--accent); transform: translateY(-2px); }
.game-card-inner {
    display: flex;
    gap: 1.2rem;
    margin-bottom: 0.25rem;
}
/* Pull Streamlit expander flush inside the card */
.game-card-outer [data-testid="stExpander"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    margin-top: 0.25rem;
}
.game-card-outer [data-testid="stExpander"] summary {
    font-size: 0.75rem !important;
    color: var(--muted) !important;
    padding: 0.2rem 0 !important;
    border-top: 1px solid var(--border);
}
.game-card-outer [data-testid="stExpander"] summary:hover {
    color: var(--accent) !important;
}

.thumb-wrap {
    flex-shrink: 0;
    width: 90px; height: 90px;
    border-radius: 8px; overflow: hidden;
    background: var(--border);
    display: flex; align-items: center; justify-content: center;
}
.thumb-wrap img { width:100%; height:100%; object-fit:cover; }
.no-thumb { font-size: 2.5rem; }

.game-info { flex: 1; min-width: 0; }
.game-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.2rem; letter-spacing: 1px;
    color: var(--text); margin: 0 0 .3rem 0;
}
.game-meta { font-size: 0.78rem; color: var(--muted); margin-bottom: .5rem; }

.badge {
    display: inline-block; padding: 2px 8px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600; margin-right: 5px;
}
.badge-year {
    background: rgba(122,131,154,0.15); color: var(--muted);
    border: 1px solid rgba(122,131,154,0.3);
}
.badge-players {
    background: rgba(224,92,26,0.1); color: var(--accent2);
    border: 1px solid rgba(224,92,26,0.3);
}
.badge-expansion {
    background: rgba(138,43,226,0.12); color: #b88aff;
    border: 1px solid rgba(138,43,226,0.3);
}
.badge-publisher {
    background: rgba(62,140,207,0.1); color: #7ec8f7;
    border: 1px solid rgba(62,140,207,0.3);
}
.tags-row { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 0.4rem; }
.mech-tag {
    font-size: 0.65rem; font-weight: 600;
    padding: 2px 7px; border-radius: 20px;
    background: rgba(240,165,0,0.1);
    color: var(--accent);
    border: 1px solid rgba(240,165,0,0.22);
    white-space: nowrap;
}
.badge-map {
    background: rgba(62,207,142,0.1); color: #3ecf8e;
    border: 1px solid rgba(62,207,142,0.3);
    text-decoration: none !important;
    cursor: pointer;
}
.badge-map:hover {
    background: rgba(62,207,142,0.25);
}

.game-desc {
    font-size: 0.8rem; color: var(--muted); line-height: 1.6;
}

.stat-box {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: .75rem 1rem; text-align: center;
}
.stat-num { font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--accent); line-height:1; }
.stat-label { font-size:0.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:1px; }

.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem; letter-spacing: 5px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1; margin: 0;
}
.hero-sub { color:var(--muted); font-size:0.9rem; letter-spacing:2px; text-transform:uppercase; margin-top:.3rem; }
.divider { border:none; border-top:1px solid var(--border); margin:1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "games"         not in st.session_state: st.session_state.games         = []
if "list_title"    not in st.session_state: st.session_state.list_title    = ""
if "all_mechanics"  not in st.session_state: st.session_state.all_mechanics  = []
if "location_map"   not in st.session_state: st.session_state.location_map   = {}
if "expansion_map"  not in st.session_state: st.session_state.expansion_map  = {}
if "availability_map" not in st.session_state: st.session_state.availability_map = {}

# ── BGG API helpers ───────────────────────────────────────────────────────────

def bgg_get(url: str, api_key: str = "", retries: int = 6, delay: int = 3) -> ET.Element:
    headers = {"Authorization": f"Bearer {api_key.strip()}"} if api_key.strip() else {}
    for _ in range(retries):
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 401:
            raise RuntimeError("401 Unauthorized — check your BGG Bearer token at boardgamegeek.com/applications")
        if resp.status_code == 202:
            st.toast("BGG is queuing the request, retrying…", icon="⏳")
            time.sleep(delay)
            continue
        resp.raise_for_status()
        return ET.fromstring(resp.content)
    raise RuntimeError("BGG kept returning 202 — please try again shortly.")


def fetch_geeklist(list_id: int, api_key: str = "") -> dict:
    root  = bgg_get(f"https://boardgamegeek.com/xmlapi2/geeklist/{list_id}?comments=0", api_key=api_key)
    title = root.findtext("title") or f"GeekList #{list_id}"
    ids   = [
        item.get("objectid")
        for item in root.findall("item")
        if item.get("objectid") and "boardgame" in item.get("subtype", "").lower()
    ]
    return {"title": title, "item_ids": ids}


def fetch_game_details(game_ids: list, api_key: str = "") -> dict:
    games = {}
    for i in range(0, len(game_ids), 20):
        chunk = game_ids[i : i + 20]
        root  = bgg_get(f"https://boardgamegeek.com/xmlapi2/thing?id={','.join(chunk)}&stats=1", api_key=api_key)
        for item in root.findall("item"):
            gid     = item.get("id")
            name_el = item.find(".//name[@type='primary']")
            name    = name_el.get("value", "Unknown") if name_el is not None else "Unknown"
            thumb   = item.findtext("thumbnail") or ""
            desc    = item.findtext("description") or ""
            year_el = item.find("yearpublished")
            year    = year_el.get("value", "?") if year_el is not None else "?"
            minp    = item.find("minplayers")
            maxp    = item.find("maxplayers")
            mn      = minp.get("value", "?") if minp is not None else "?"
            mx      = maxp.get("value", "?") if maxp is not None else "?"
            players = f"{mn}–{mx}" if mn != mx else mn
            mechanics = [
                lnk.get("value", "")
                for lnk in item.findall("link[@type='boardgamemechanic']")
                if lnk.get("value")
            ]
            publishers = [
                lnk.get("value", "")
                for lnk in item.findall("link[@type='boardgamepublisher']")
                if lnk.get("value")
            ]
            publisher = publishers[0] if publishers else ""
            games[gid] = {
                "id": gid, "name": name, "thumbnail": thumb,
                "description": desc, "year": year,
                "players": players, "mechanics": mechanics,
                "publisher": publisher,
            }
    return games


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;letter-spacing:3px;'
        'background:linear-gradient(135deg,#f0a500,#e05c1a);-webkit-background-clip:text;'
        '-webkit-text-fill-color:transparent;">🎲 SCOUT</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#7a839a;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;margin-top:-0.8rem;">'
        'GenCon Game Explorer</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("### 🔑 BGG API Token")
    api_key = st.text_input(
        "Bearer Token",
        type="password",
        placeholder="Paste token — cleared when tab closes",
        help="Your token is never saved anywhere. It only exists in memory for this browser session and is gone the moment you close the tab.",
        key=None,
        autocomplete="off",
    )
    st.markdown(
        '<p style="color:#7a839a;font-size:0.68rem;line-height:1.5;margin-top:-0.5rem;">'
        '🔒 Not saved — paste each session</p>',
        unsafe_allow_html=True,
    )
    tab_gl, tab_csv = st.tabs(["📋 GeekList", "📂 GeekPreview CSV"])

    with tab_gl:
        list_input = st.text_input(
            "GeekList ID or URL",
            placeholder="e.g. 338062 or boardgamegeek.com/geeklist/338062/...",
            help="Paste a GeekList ID, a full GeekList URL, or a GeekPreview URL.",
        )
        fetch_btn = st.button("🎯  FETCH LIST", use_container_width=True)

    with tab_csv:
        st.markdown(
            '<p style="color:#7a839a;font-size:0.72rem;line-height:1.6;">'
            'On BGG, open your GeekPreview, scroll to the bottom and click '
            '<strong style="color:#e8eaf0">Download as CSV</strong>, '
            'then upload it here.</p>',
            unsafe_allow_html=True,
        )
        csv_file   = st.file_uploader("Upload GeekPreview CSV", type=["csv"])
        csv_title  = st.text_input("Preview title (optional)", placeholder="e.g. GenCon 2025 Preview")
        fetch_csv_btn = st.button("🎯  LOAD CSV", use_container_width=True)

    search          = ""
    sort_by         = "Name (A–Z)"
    hide_expansions = False
    avail_filter    = []
    pub_filter      = []
    player_filter   = None

# ── Main panel ────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">GENCON<br>GAME SCOUT</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Browse Games from Any BGG GeekList</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
import re, io

def parse_list_id(raw: str):
    raw = raw.strip()
    m = re.search(r'/(?:geeklist|geekpreview)/(\d+)', raw)
    if m:
        return int(m.group(1))
    if raw.isdigit():
        return int(raw)
    return None

def load_games_from_ids(ids: list, title: str):
    """Shared pipeline: fetch details for a list of BGG object IDs."""
    st.session_state.list_title = title
    if not ids:
        st.warning("No board game IDs found.")
        st.session_state.games         = []
        st.session_state.all_mechanics = []
        return
    with st.spinner(f"Loading details for {len(ids)} games…"):
        details = fetch_game_details(ids, api_key=api_key)
    st.session_state.games = [details[i] for i in ids if i in details]
    all_m = set()
    for g in st.session_state.games:
        all_m.update(g["mechanics"])
    st.session_state.all_mechanics = sorted(all_m)
    st.toast(f"Loaded {len(st.session_state.games)} games!", icon="✅")

# ── Fetch: GeekList ───────────────────────────────────────────────────────────
if fetch_btn:
    list_id = parse_list_id(list_input or "")
    if not list_id:
        st.error("Please enter a valid GeekList ID or BGG URL.")
    else:
        with st.spinner("Fetching GeekList from BGG…"):
            try:
                gl  = fetch_geeklist(int(list_id), api_key=api_key)
                st.session_state.location_map    = {}
                st.session_state.expansion_map   = {}
                st.session_state.availability_map = {}
                load_games_from_ids(gl["item_ids"], gl["title"])
            except Exception as e:
                st.error(f"Error: {e}")

# ── Fetch: GeekPreview CSV ────────────────────────────────────────────────────
if fetch_csv_btn:
    if not csv_file:
        st.error("Please upload a GeekPreview CSV file first.")
    else:
        try:
            import pandas as pd
            df = pd.read_csv(io.StringIO(csv_file.read().decode("utf-8", errors="replace")))

            # Locate the BGG ID column — GeekPreview exports use 'BGGId'
            id_col = None
            for candidate in ["BGGId", "objectid", "objectID", "bggid", "ID", "id"]:
                if candidate in df.columns:
                    id_col = candidate
                    break

            if id_col is None:
                st.error(f"Couldn't find a game ID column. Columns found: {list(df.columns)}")
            else:
                # Deduplicate by BGGId, keep first occurrence
                df = df.drop_duplicates(subset=[id_col])

                # Store expansion flags and availability: BGGId -> value
                expansion_map    = {}
                availability_map = {}
                if "Type" in df.columns:
                    for _, row in df.iterrows():
                        gid = str(int(row[id_col])) if pd.notna(row[id_col]) else None
                        if gid:
                            expansion_map[gid] = str(row.get("Type", "")).strip().lower() == "expansion"
                            avail = str(row.get("Availability", "")).strip()
                            if avail and avail.lower() != "nan":
                                availability_map[gid] = avail
                st.session_state.expansion_map    = expansion_map
                st.session_state.availability_map = availability_map

                # Build location lookup: BGGId -> first numeric booth number from Location
                location_map = {}
                if "Location" in df.columns:
                    for _, row in df.iterrows():
                        gid = str(int(row[id_col])) if pd.notna(row[id_col]) else None
                        loc = str(row.get("Location", "")) if pd.notna(row.get("Location")) else ""
                        # Extract first run of digits from the location string
                        booth_match = re.search(r'(\d+)', loc)
                        if gid and booth_match:
                            location_map[gid] = booth_match.group(1)
                st.session_state.location_map = location_map

                ids = [str(int(v)) for v in pd.to_numeric(df[id_col], errors="coerce").dropna()]
                title = csv_title.strip() or csv_file.name.replace(".csv", "").replace("_", " ").replace("-", " ")
                load_games_from_ids(ids, title)
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# ── Display ───────────────────────────────────────────────────────────────────
if st.session_state.games:
    games = list(st.session_state.games)

    # ── All filters in main panel ────────────────────────────────────────────
    with st.container():
        st.markdown(
            '<p style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;'
            'letter-spacing:2px;color:var(--muted);margin-bottom:0.5rem;">🔍 SEARCH &amp; FILTER</p>',
            unsafe_allow_html=True,
        )

        # Row 1: Search + Sort — always shown
        c_search, c_sort = st.columns([3, 1])
        with c_search:
            st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Search</p>', unsafe_allow_html=True)
            search = st.text_input("Search", placeholder="Game name…", label_visibility="collapsed")
        with c_sort:
            st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Sort by</p>', unsafe_allow_html=True)
            sort_by = st.selectbox("Sort by", ["Name (A–Z)", "Name (Z–A)", "Year (Newest)", "Year (Oldest)"], label_visibility="collapsed")

        # Row 2: Availability + Hide expansions — only when CSV data present
        avail_options = sorted(set(st.session_state.availability_map.values()))
        has_csv_filters = bool(avail_options or st.session_state.expansion_map)
        if has_csv_filters:
            c_avail, c_exp = st.columns([3, 1])
            with c_avail:
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Availability</p>', unsafe_allow_html=True)
                if avail_options:
                    avail_filter = st.multiselect("Availability", options=avail_options, placeholder="All…", label_visibility="collapsed")
                else:
                    avail_filter = []
                    st.markdown('<p style="color:var(--muted);font-size:0.8rem;padding-top:0.4rem;">—</p>', unsafe_allow_html=True)
            with c_exp:
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Type</p>', unsafe_allow_html=True)
                if st.session_state.expansion_map:
                    hide_expansions = st.checkbox("Hide expansions", value=False)
                else:
                    hide_expansions = False
        else:
            avail_filter    = []

        # Row 3: Mechanics — only when data present
        if st.session_state.all_mechanics:
            c_mech, c_toggle = st.columns([3, 1])
            with c_mech:
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Mechanics</p>', unsafe_allow_html=True)
                mech_filter = st.multiselect("Mechanics", options=sorted(st.session_state.all_mechanics), placeholder="Any mechanic…", label_visibility="collapsed")
            with c_toggle:
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Match mode</p>', unsafe_allow_html=True)
                match_all = st.toggle("Require ALL", value=False, help="ON = game must have every selected mechanic. OFF = any one.")
        else:
            mech_filter = []
            match_all   = False

        # Row 4: Publisher filter — only when publisher data exists
        all_publishers = sorted(set(g["publisher"] for g in st.session_state.games if g.get("publisher")))
        if all_publishers:
            st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Publisher</p>', unsafe_allow_html=True)
            pub_filter = st.multiselect("Publisher", options=all_publishers, placeholder="Search publishers…", label_visibility="collapsed")
        else:
            pub_filter = []

        # Row 5: Player count slider — only when player data exists
        all_mins = []
        all_maxs = []
        for g in st.session_state.games:
            p = g.get("players", "")
            parts = str(p).replace("–", "-").split("-")
            try:
                all_mins.append(int(parts[0]))
                all_maxs.append(int(parts[-1]))
            except (ValueError, IndexError):
                pass
        if all_mins and all_maxs:
            global_min = min(all_mins)
            global_max = min(max(all_maxs), 10)  # cap at 10 for usability
            st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Player Count</p>', unsafe_allow_html=True)
            player_filter = st.slider(
                "Player count",
                min_value=global_min,
                max_value=global_max,
                value=(global_min, global_max),
                label_visibility="collapsed",
            )
        else:
            player_filter = None

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if search:
        games = [g for g in games if search.lower() in g["name"].lower()]
    if hide_expansions and st.session_state.expansion_map:
        games = [g for g in games if not st.session_state.expansion_map.get(g["id"], False)]
    if avail_filter and st.session_state.availability_map:
        games = [g for g in games if st.session_state.availability_map.get(g["id"]) in avail_filter]
    if pub_filter:
        games = [g for g in games if g.get("publisher") in pub_filter]
    if player_filter:
        pmin, pmax = player_filter
        def player_matches(g):
            parts = str(g.get("players","")).replace("–","-").split("-")
            try:
                gmin = int(parts[0])
                gmax = int(parts[-1])
                return gmax >= pmin and gmin <= pmax
            except (ValueError, IndexError):
                return True
        games = [g for g in games if player_matches(g)]
    if mech_filter:
        if match_all:
            games = [g for g in games if all(m in g["mechanics"] for m in mech_filter)]
        else:
            games = [g for g in games if any(m in g["mechanics"] for m in mech_filter)]

    def safe_year(g):
        try: return int(g["year"])
        except: return 0

    if sort_by == "Name (A–Z)":
        games = sorted(games, key=lambda g: g["name"].lower())
    elif sort_by == "Name (Z–A)":
        games = sorted(games, key=lambda g: g["name"].lower(), reverse=True)
    elif sort_by == "Year (Newest)":
        games = sorted(games, key=safe_year, reverse=True)
    elif sort_by == "Year (Oldest)":
        games = sorted(games, key=safe_year)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(st.session_state.games)}</div><div class="stat-label">Total Games</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(games)}</div><div class="stat-label">Showing</div></div>', unsafe_allow_html=True)

    st.markdown(f"### {st.session_state.list_title}")
    st.markdown(f"<p style='color:var(--muted);font-size:0.82rem;'>{len(games)} game{'s' if len(games)!=1 else ''} shown</p>", unsafe_allow_html=True)

    if not games:
        st.info("No games match your current filters.")
    else:
        for g in games:
            thumb_html = (
                f'<img src="{g["thumbnail"]}" alt="{g["name"]}" loading="lazy">'
                if g["thumbnail"] else '<span class="no-thumb">🎲</span>'
            )
            year_badge      = f'<span class="badge badge-year">{g["year"]}</span>'           if g["year"] != "?" else ""
            players_badge   = f'<span class="badge badge-players">👥 {g["players"]}</span>' if g["players"] else ""
            expansion_badge = '<span class="badge badge-expansion">Expansion</span>' if st.session_state.expansion_map.get(g["id"]) else ""
            publisher_badge = f'<span class="badge badge-publisher">🏢 {g["publisher"]}</span>' if g.get("publisher") else ""
            desc = g["description"].replace("<","&lt;").replace(">","&gt;")

            booth = st.session_state.location_map.get(g["id"])
            map_url = f"https://www.gencon.com/map?lt=7.27529233637217&lg=25.55419921875&z=4&f=1&c=26&s={booth}" if booth else None
            map_link = (f'<a href="{map_url}" target="_blank" class="badge badge-map">📍 Booth {booth}</a>') if map_url else ""

            mech_tags_html = ""
            if g.get("mechanics"):
                tags = "".join(f'<span class="mech-tag">{m}</span>' for m in g["mechanics"])
                mech_tags_html = f'<div class="tags-row">{tags}</div>'

            # Outer card border wraps both the header row and the expander
            st.markdown('<div class="game-card-outer">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="game-card-inner">
                <div class="thumb-wrap">{thumb_html}</div>
                <div class="game-info">
                    <p class="game-title">{g['name']}</p>
                    <div class="game-meta">{year_badge}{players_badge}{publisher_badge}{expansion_badge}{map_link}</div>
                    {mech_tags_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if desc:
                with st.expander("📖 Description"):
                    st.markdown(f'<p class="game-desc">{desc}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:var(--muted);">
        <div style="font-size:5rem;margin-bottom:1rem;">🎲</div>
        <p style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:3px;color:#e8eaf0;">READY TO SCOUT</p>
        <p style="font-size:0.9rem;">Enter a BGG GeekList ID in the sidebar and hit <strong style="color:#f0a500">FETCH LIST</strong>.</p>
        <p style="font-size:0.78rem;margin-top:1rem;">💡 Find a GenCon GeekList on <a href="https://boardgamegeek.com" target="_blank" style="color:#f0a500">boardgamegeek.com</a> and grab the ID from the URL.</p>
    </div>
    """, unsafe_allow_html=True)
