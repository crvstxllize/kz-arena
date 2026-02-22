import gzip
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from typing import Optional, Dict, Any

def fetch_json(url: str, params: Optional[Dict[str, Any]] = None, user_agent: str = "KZArenaData/1.0"):
    target = url
    if params:
        target = f"{url}?{urlencode(params)}"

    request = Request(
        target,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        },
    )
    with urlopen(request, timeout=20) as response:
        raw = response.read()
        if response.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))
