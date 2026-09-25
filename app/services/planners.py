from .catalog import enrich_links, build_mock_catalog

def normalize_items(items: dict) -> dict:
    return {str(k): max(0, int(v)) for k, v in items.items() if str(k).strip()}

def validate_home(data: dict) -> dict:
    data = dict(data)
    data["items"] = normalize_items(data.get("items", {}))
    return data

def validate_party(data: dict) -> dict:
    data = dict(data)
    data["guests"] = int(data["guests"])
    return data

def validate_jewelry(data: dict) -> dict:
    return dict(data)
