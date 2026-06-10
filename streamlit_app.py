import streamlit as st
import requests
import xml.etree.ElementTree as ET
import time
import hashlib, json, os, re, io
from streamlit_gsheets import GSheetsConnection

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
.game-card-inner { display: flex; gap: 1.2rem; margin-bottom: 0.25rem; }
.game-card-outer [data-testid="stExpander"] {
    border: none !important; background: transparent !important;
    box-shadow: none !important; margin-top: 0.25rem;
}
.game-card-outer [data-testid="stExpander"] summary {
    font-size: 0.75rem !important; color: var(--muted) !important;
    padding: 0.2rem 0 !important; border-top: 1px solid var(--border);
}
.game-card-outer [data-testid="stExpander"] summary:hover { color: var(--accent) !important; }

.thumb-wrap {
    flex-shrink: 0; width: 90px; height: 90px;
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
.badge-year      { background: rgba(122,131,154,0.15); color: var(--muted);   border: 1px solid rgba(122,131,154,0.3); }
.badge-players   { background: rgba(224,92,26,0.1);    color: var(--accent2); border: 1px solid rgba(224,92,26,0.3); }
.badge-expansion { background: rgba(138,43,226,0.12);  color: #b88aff;        border: 1px solid rgba(138,43,226,0.3); }
.badge-publisher { background: rgba(62,140,207,0.1);   color: #7ec8f7;        border: 1px solid rgba(62,140,207,0.3); }
.badge-map {
    background: rgba(62,207,142,0.1); color: #3ecf8e;
    border: 1px solid rgba(62,207,142,0.3);
    text-decoration: none !important; cursor: pointer;
}
.badge-map:hover { background: rgba(62,207,142,0.25); }

.tags-row { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 0.4rem; }
.mech-tag {
    font-size: 0.65rem; font-weight: 600; padding: 2px 7px; border-radius: 20px;
    background: rgba(240,165,0,0.1); color: var(--accent);
    border: 1px solid rgba(240,165,0,0.22); white-space: nowrap;
}

.game-desc { font-size: 0.8rem; color: var(--muted); line-height: 1.6; }

.stat-box {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: .75rem 1rem; text-align: center;
}
.stat-num   { font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--accent); line-height:1; }
.stat-label { font-size:0.72rem; color:var(--muted); text-transform:uppercase; letter-spacing:1px; }

.hero-title {
    font-family: 'Bebas Neue', sans-serif; font-size: 3.5rem; letter-spacing: 5px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1; margin: 0;
}
.hero-sub { color:var(--muted); font-size:0.9rem; letter-spacing:2px; text-transform:uppercase; margin-top:.3rem; }
.divider   { border:none; border-top:1px solid var(--border); margin:1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Auth helpers ──────────────────────────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), b"gencon-scout-salt", 260_000).hex()

def check_credentials(username: str, password: str) -> bool:
    users = st.secrets.get("users", {})
    stored = users.get(username)
    return bool(stored and _hash(password) == stored)

# ── Favorites helpers (Google Sheets backend) ────────────────────────────────
def _get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

def load_favorites(force: bool = False) -> dict:
    """Read all rows from the Favorites sheet and return as {username: {gid: {...}}}.
    Results are cached in session_state so the UI stays snappy; pass force=True to re-read."""
    if not force and st.session_state.get("favorites_cache") is not None:
        return st.session_state.favorites_cache
    try:
        conn = _get_conn()
        df   = conn.read(worksheet="Favorites", ttl=0)
        favs = {}
        for _, row in df.iterrows():
            user = str(row.get("username","")).strip()
            gid  = str(row.get("game_id","")).strip()
            if not user or not gid:
                continue
            if user not in favs:
                favs[user] = {}
            try:
                mechanics = json.loads(row.get("mechanics","[]") or "[]")
            except Exception:
                mechanics = []
            favs[user][gid] = {
                "id":          gid,
                "name":        str(row.get("name","")),
                "thumbnail":   str(row.get("thumbnail","")),
                "year":        str(row.get("year","?")),
                "players":     str(row.get("players","")),
                "publisher":   str(row.get("publisher","")),
                "mechanics":   mechanics,
                "description": str(row.get("description","")),
            }
        st.session_state.favorites_cache = favs
        # Seed the instant set ONCE per session; never overwrite it afterwards
        # (toggle_favorite is the only thing allowed to mutate it after seeding)
        if not st.session_state.get("fav_ids_seeded", False):
            user = st.session_state.get("username", "")
            st.session_state.fav_ids_local = set(favs.get(user, {}).keys())
            st.session_state.fav_ids_seeded = True
        return favs
    except Exception:
        st.session_state.favorites_cache = {}
        return {}

def save_favorites(favs: dict):
    """Write entire favorites dict back to the sheet."""
    rows = []
    for username, games in favs.items():
        for gid, g in games.items():
            rows.append({
                "username":    username,
                "game_id":     gid,
                "name":        g.get("name",""),
                "thumbnail":   g.get("thumbnail",""),
                "year":        g.get("year","?"),
                "players":     g.get("players",""),
                "publisher":   g.get("publisher",""),
                "mechanics":   json.dumps(g.get("mechanics",[])),
                "description": g.get("description",""),
            })
    import pandas as pd
    df   = pd.DataFrame(rows, columns=["username","game_id","name","thumbnail","year","players","publisher","mechanics","description"])
    conn = _get_conn()
    conn.update(worksheet="Favorites", data=df)
    # NOTE: we deliberately do NOT bust favorites_cache here — toggle_favorite
    # already updated it in session state, and re-reading from Sheets immediately
    # after a write can return stale data and clobber the user's action.

def toggle_favorite(username: str, game: dict):
    favs      = load_favorites()
    user_favs = favs.get(username, {})
    gid       = game["id"]
    if gid in user_favs:
        del user_favs[gid]
    else:
        user_favs[gid] = {
            "id":          gid,
            "name":        game.get("name",""),
            "thumbnail":   game.get("thumbnail",""),
            "year":        game.get("year","?"),
            "players":     game.get("players",""),
            "publisher":   game.get("publisher",""),
            "mechanics":   game.get("mechanics",[]),
            "description": game.get("description",""),
        }
    favs[username] = user_favs
    # Update session state BEFORE the slow Sheets write so rerun sees correct state
    st.session_state.favorites_cache = favs
    if gid in st.session_state.fav_ids_local:
        st.session_state.fav_ids_local.discard(gid)
    else:
        st.session_state.fav_ids_local.add(gid)
    save_favorites(favs)  # slow Sheets write happens after state is already updated

def get_user_favorites(username: str) -> dict:
    return load_favorites().get(username, {})

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
            players   = f"{mn}–{mx}" if mn != mx else mn
            mechanics = [l.get("value","") for l in item.findall("link[@type='boardgamemechanic']") if l.get("value")]
            pubs      = [l.get("value","") for l in item.findall("link[@type='boardgamepublisher']") if l.get("value")]
            games[gid] = {
                "id": gid, "name": name, "thumbnail": thumb,
                "description": desc, "year": year, "players": players,
                "mechanics": mechanics, "publisher": pubs[0] if pubs else "",
            }
    return games

def parse_list_id(raw: str):
    raw = raw.strip()
    m = re.search(r'/(?:geeklist|geekpreview)/(\d+)', raw)
    if m:
        return int(m.group(1))
    return int(raw) if raw.isdigit() else None

def load_games_from_ids(ids: list, title: str, api_key: str):
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

def render_game_card(g, fav_ids, expansion_map, location_map, show_star=True, show_remove=False):
    thumb_html = (
        f'<img src="{g["thumbnail"]}" alt="{g["name"]}" loading="lazy">'
        if g.get("thumbnail") else '<span class="no-thumb">🎲</span>'
    )
    year_badge      = f'<span class="badge badge-year">{g["year"]}</span>'               if g.get("year","?") != "?" else ""
    players_badge   = f'<span class="badge badge-players">👥 {g["players"]}</span>'     if g.get("players") else ""
    pub_badge       = f'<span class="badge badge-publisher">🏢 {g["publisher"]}</span>' if g.get("publisher") else ""
    expansion_badge = '<span class="badge badge-expansion">Expansion</span>'              if expansion_map.get(g["id"]) else ""
    booth = location_map.get(g["id"])
    map_link = (
        f'<a href="https://www.gencon.com/map?lt=7.27529233637217&lg=25.55419921875&z=4&f=1&c=26&s={booth}" '
        f'target="_blank" class="badge badge-map">📍 Booth {booth}</a>'
    ) if booth else ""
    mech_tags_html = ""
    if g.get("mechanics"):
        tags = "".join(f'<span class="mech-tag">{m}</span>' for m in g["mechanics"])
        mech_tags_html = f'<div class="tags-row">{tags}</div>'
    desc = g.get("description", "").replace("<", "&lt;").replace(">", "&gt;")

    st.markdown('<div class="game-card-outer">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="game-card-inner">
        <div class="thumb-wrap">{thumb_html}</div>
        <div class="game-info">
            <p class="game-title">{g['name']}</p>
            <div class="game-meta">{year_badge}{players_badge}{pub_badge}{expansion_badge}{map_link}</div>
            {mech_tags_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if show_star:
        # Always read directly from session_state so label is instant
        is_fav = g["id"] in st.session_state.fav_ids_local
        label  = "★ Favorited" if is_fav else "☆ Add to Favorites"
        if st.button(label, key=f"fav_{g['id']}"):
            toggle_favorite(st.session_state.username, g)
            st.rerun()

    if show_remove:
        if st.button("★ Remove from Favorites", key=f"unfav_{g['id']}"):
            toggle_favorite(st.session_state.username, g)
            st.rerun()

    if desc:
        with st.expander("📖 Description"):
            st.markdown(f'<p class="game-desc">{desc}</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "authenticated"    not in st.session_state: st.session_state.authenticated    = False
if "username"         not in st.session_state: st.session_state.username         = ""
if "games"            not in st.session_state: st.session_state.games            = []
if "list_title"       not in st.session_state: st.session_state.list_title       = ""
if "all_mechanics"    not in st.session_state: st.session_state.all_mechanics    = []
if "location_map"     not in st.session_state: st.session_state.location_map     = {}
if "expansion_map"    not in st.session_state: st.session_state.expansion_map    = {}
if "availability_map"  not in st.session_state: st.session_state.availability_map = {}
if "favorites_cache"   not in st.session_state: st.session_state.favorites_cache  = {}
if "fav_ids_local"     not in st.session_state: st.session_state.fav_ids_local    = set()
if "fav_ids_seeded"    not in st.session_state: st.session_state.fav_ids_seeded   = False

# ── Login gate ────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    st.markdown("""
    <style>
    .login-wrap  { max-width:380px; margin:6rem auto; text-align:center; }
    .login-title { font-family:'Bebas Neue',sans-serif; font-size:3rem; letter-spacing:4px;
        background:linear-gradient(135deg,#f0a500,#e05c1a);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .login-sub   { color:#7a839a; font-size:0.85rem; letter-spacing:2px; text-transform:uppercase; margin-bottom:2rem; }
    </style>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
        st.markdown('<p class="login-title">🎲 SCOUT</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-sub">GenCon Game Explorer</p>', unsafe_allow_html=True)
        uname = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
        pw    = st.text_input("Password", placeholder="Password", type="password",
                              label_visibility="collapsed", autocomplete="off")
        if st.button("LOG IN", use_container_width=True):
            if check_credentials(uname.strip(), pw):
                st.session_state.authenticated = True
                st.session_state.username      = uname.strip()
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

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
    st.markdown(
        f'<p style="color:#3ecf8e;font-size:0.75rem;margin-top:-0.3rem;">👤 {st.session_state.username}</p>',
        unsafe_allow_html=True,
    )
    if st.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # BGG API key from secrets — never shown to users
    api_key = st.secrets.get("BGG_API_KEY", "")

    sb_gl, sb_csv = st.tabs(["📋 GeekList", "📂 GeekPreview CSV"])

    with sb_gl:
        list_input = st.text_input(
            "GeekList ID or URL",
            placeholder="e.g. 338062 or boardgamegeek.com/geeklist/338062/...",
        )
        fetch_btn = st.button("🎯  FETCH LIST", use_container_width=True)

    with sb_csv:
        csv_exists = os.path.exists("Gencon.csv")
        if csv_exists:
            st.markdown(
                '<p style="color:#3ecf8e;font-size:0.72rem;line-height:1.6;">✅ <strong>Gencon.csv</strong> found in repo.</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<p style="color:#e05c1a;font-size:0.72rem;line-height:1.6;">⚠️ <strong>Gencon.csv</strong> not found. Add it to the root of your GitHub repo.</p>',
                unsafe_allow_html=True,
            )
        fetch_csv_btn = st.button("🎯  LOAD GENCON.CSV", use_container_width=True, disabled=not csv_exists)

# ── Main panel ────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">GENCON<br>GAME SCOUT</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Browse Games from Any BGG GeekList</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Tabs are defined here — before any content is rendered into them
tab_browse, tab_favs = st.tabs(["🎲 Browse", "⭐ My Favorites"])

# ── Browse tab ────────────────────────────────────────────────────────────────
with tab_browse:

    # Handle GeekList fetch
    if fetch_btn:
        list_id = parse_list_id(list_input or "")
        if not list_id:
            st.error("Please enter a valid GeekList ID or BGG URL.")
        else:
            with st.spinner("Fetching GeekList from BGG…"):
                try:
                    gl = fetch_geeklist(int(list_id), api_key=api_key)
                    st.session_state.location_map     = {}
                    st.session_state.expansion_map    = {}
                    st.session_state.availability_map = {}
                    load_games_from_ids(gl["item_ids"], gl["title"], api_key)
                except Exception as e:
                    st.error(f"Error: {e}")

    # Handle CSV fetch
    if fetch_csv_btn:
        try:
            import pandas as pd
            df     = pd.read_csv("Gencon.csv")
            id_col = next((c for c in ["BGGId","objectid","objectID","bggid","ID","id"] if c in df.columns), None)
            if id_col is None:
                st.error(f"Couldn't find a game ID column. Columns: {list(df.columns)}")
            else:
                df               = df.drop_duplicates(subset=[id_col])
                expansion_map    = {}
                availability_map = {}
                location_map     = {}
                for _, row in df.iterrows():
                    gid = str(int(row[id_col])) if pd.notna(row[id_col]) else None
                    if not gid:
                        continue
                    if "Type" in df.columns:
                        expansion_map[gid] = str(row.get("Type","")).strip().lower() == "expansion"
                    if "Availability" in df.columns:
                        avail = str(row.get("Availability","")).strip()
                        if avail and avail.lower() != "nan":
                            availability_map[gid] = avail
                    if "Location" in df.columns:
                        loc = str(row.get("Location","")) if pd.notna(row.get("Location")) else ""
                        m = re.search(r'(\d+)', loc)
                        if m:
                            location_map[gid] = m.group(1)
                st.session_state.expansion_map    = expansion_map
                st.session_state.availability_map = availability_map
                st.session_state.location_map     = location_map
                ids   = [str(int(v)) for v in pd.to_numeric(df[id_col], errors="coerce").dropna()]
                title = "GenCon 2026 Preview"
                load_games_from_ids(ids, title, api_key)
        except Exception as e:
            st.error(f"Error reading Gencon.csv: {e}")

    # Display games
    if st.session_state.games:
        games = list(st.session_state.games)

        # Filters
        with st.container():
            st.markdown(
                '<p style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;'
                'letter-spacing:2px;color:var(--muted);margin-bottom:0.5rem;">🔍 SEARCH &amp; FILTER</p>',
                unsafe_allow_html=True,
            )

            # Row 1: Search + Sort + Favorites only
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Search</p>', unsafe_allow_html=True)
                search = st.text_input("Search", placeholder="Game name…", label_visibility="collapsed")
            with c2:
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Sort by</p>', unsafe_allow_html=True)
                sort_by = st.selectbox("Sort by", ["Name (A–Z)","Name (Z–A)","Year (Newest)","Year (Oldest)"], label_visibility="collapsed")
            with c3:
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Favorites</p>', unsafe_allow_html=True)
                show_favs_only = st.checkbox("⭐ Only", value=False, help="Show only your starred games")

            # Row 2: Availability + Hide expansions (CSV data only)
            avail_options   = sorted(set(st.session_state.availability_map.values()))
            has_csv_filters = bool(avail_options or st.session_state.expansion_map)
            if has_csv_filters:
                c4, c5 = st.columns([3, 1])
                with c4:
                    st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Availability</p>', unsafe_allow_html=True)
                    avail_filter = st.multiselect("Availability", options=avail_options, placeholder="All…", label_visibility="collapsed") if avail_options else []
                with c5:
                    st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Type</p>', unsafe_allow_html=True)
                    hide_expansions = st.checkbox("Hide expansions", value=False) if st.session_state.expansion_map else False
            else:
                avail_filter    = []
                hide_expansions = False

            # Row 3: Publisher
            all_publishers = sorted(set(g["publisher"] for g in st.session_state.games if g.get("publisher")))
            if all_publishers:
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Publisher</p>', unsafe_allow_html=True)
                pub_filter = st.multiselect("Publisher", options=all_publishers, placeholder="Search publishers…", label_visibility="collapsed")
            else:
                pub_filter = []

            # Row 4: Mechanics + match mode
            if st.session_state.all_mechanics:
                c6, c7 = st.columns([3, 1])
                with c6:
                    st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Mechanics</p>', unsafe_allow_html=True)
                    mech_filter = st.multiselect("Mechanics", options=sorted(st.session_state.all_mechanics), placeholder="Any mechanic…", label_visibility="collapsed")
                with c7:
                    st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Match mode</p>', unsafe_allow_html=True)
                    match_all = st.toggle("Require ALL", value=False)
            else:
                mech_filter = []
                match_all   = False

            # Row 5: Player count slider
            all_mins, all_maxs = [], []
            for g in st.session_state.games:
                parts = str(g.get("players","")).replace("–","-").split("-")
                try:
                    all_mins.append(int(parts[0]))
                    all_maxs.append(int(parts[-1]))
                except (ValueError, IndexError):
                    pass
            if all_mins and all_maxs:
                global_min = min(all_mins)
                global_max = min(max(all_maxs), 10)
                st.markdown('<p style="font-size:0.72rem;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px;">Player Count</p>', unsafe_allow_html=True)
                player_filter = st.slider("Player count", min_value=global_min, max_value=global_max,
                                          value=(global_min, global_max), label_visibility="collapsed")
            else:
                player_filter = None

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Trigger initial favorites load (seeds fav_ids_local once via load_favorites)
        get_user_favorites(st.session_state.username)
        fav_ids = st.session_state.fav_ids_local


        if search:
            games = [g for g in games if search.lower() in g["name"].lower()]
        if show_favs_only:
            games = [g for g in games if g["id"] in fav_ids]
        if hide_expansions:
            games = [g for g in games if not st.session_state.expansion_map.get(g["id"], False)]
        if avail_filter:
            games = [g for g in games if st.session_state.availability_map.get(g["id"]) in avail_filter]
        if pub_filter:
            games = [g for g in games if g.get("publisher") in pub_filter]
        if player_filter:
            pmin, pmax = player_filter
            def player_ok(g):
                parts = str(g.get("players","")).replace("–","-").split("-")
                try:    return int(parts[-1]) >= pmin and int(parts[0]) <= pmax
                except: return True
            games = [g for g in games if player_ok(g)]
        if mech_filter:
            if match_all:
                games = [g for g in games if all(m in g["mechanics"] for m in mech_filter)]
            else:
                games = [g for g in games if any(m in g["mechanics"] for m in mech_filter)]

        def safe_year(g):
            try:    return int(g["year"])
            except: return 0

        if sort_by == "Name (A–Z)":      games = sorted(games, key=lambda g: g["name"].lower())
        elif sort_by == "Name (Z–A)":    games = sorted(games, key=lambda g: g["name"].lower(), reverse=True)
        elif sort_by == "Year (Newest)": games = sorted(games, key=safe_year, reverse=True)
        elif sort_by == "Year (Oldest)": games = sorted(games, key=safe_year)

        # Stats row
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{len(st.session_state.games)}</div><div class="stat-label">Total Games</div></div>', unsafe_allow_html=True)
        with sc2:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{len(games)}</div><div class="stat-label">Showing</div></div>', unsafe_allow_html=True)

        st.markdown(f"### {st.session_state.list_title}")
        st.markdown(f"<p style='color:var(--muted);font-size:0.82rem;'>{len(games)} game{'s' if len(games)!=1 else ''} shown</p>", unsafe_allow_html=True)

        if not games:
            st.info("No games match your current filters.")
        else:
            for g in games:
                render_game_card(g, fav_ids, st.session_state.expansion_map, st.session_state.location_map, show_star=True)

    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:var(--muted);">
            <div style="font-size:5rem;margin-bottom:1rem;">🎲</div>
            <p style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:3px;color:#e8eaf0;">READY TO SCOUT</p>
            <p style="font-size:0.9rem;">Enter a BGG GeekList ID in the sidebar and hit <strong style="color:#f0a500">FETCH LIST</strong>.</p>
            <p style="font-size:0.78rem;margin-top:1rem;">💡 Find a GenCon GeekList on <a href="https://boardgamegeek.com" target="_blank" style="color:#f0a500">boardgamegeek.com</a> and grab the ID from the URL.</p>
        </div>
        """, unsafe_allow_html=True)

# ── Favorites tab ─────────────────────────────────────────────────────────────
with tab_favs:
    user_favs = get_user_favorites(st.session_state.username)
    # Filter to only games still in the live local set (reflects instant removes)
    fav_ids   = st.session_state.fav_ids_local
    fav_items = [(gid, g) for gid, g in user_favs.items() if gid in fav_ids]
    if not fav_items:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:var(--muted);">
            <div style="font-size:4rem;margin-bottom:1rem;">⭐</div>
            <p style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:3px;color:#e8eaf0;">NO FAVORITES YET</p>
            <p style="font-size:0.9rem;">Star games in the Browse tab to save them here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            f"### ⭐ {st.session_state.username}'s Favorites &nbsp;"
            f"<span style='color:var(--muted);font-size:0.9rem;font-family:DM Sans,sans-serif;font-weight:400;'>"
            f"{len(fav_items)} games</span>",
            unsafe_allow_html=True,
        )
        for gid, g in fav_items:
            render_game_card(g, fav_ids, {}, {}, show_star=False, show_remove=True)
