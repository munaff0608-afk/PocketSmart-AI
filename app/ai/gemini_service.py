import json
import re
from typing import Optional
from google import genai
from google.genai import types
from ..config import get_settings
from .prompts import home_prompt, party_prompt, jewelry_prompt
from ..services.catalog import build_mock_catalog, enrich_links

def _clean_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
        raise

def _fallback(planner_type: str, data: dict, image_note: str = "") -> dict:
    budget = float(data["budget"])
    if planner_type == "home":
        allocation = {
            "furniture": round(budget * .40, 2),
            "lighting": round(budget * .20, 2),
            "decor": round(budget * .15, 2),
            "comfort": round(budget * .15, 2),
            "buffer": round(budget * .10, 2),
        }
        summary = f"A practical {data['style']} plan for your {data['room_type']} within ₹{budget:.0f}."
    elif planner_type == "party":
        allocation = {
            "food": round(budget * .45, 2),
            "venue": round(budget * .25, 2),
            "decoration": round(budget * .15, 2),
            "entertainment": round(budget * .10, 2),
            "buffer": round(budget * .05, 2),
        }
        summary = f"A balanced {data['event_type']} plan for {data['guests']} guests within ₹{budget:.0f}."
    else:
        allocation = {
            "necklace": round(budget * .40, 2),
            "earrings": round(budget * .20, 2),
            "bracelet": round(budget * .20, 2),
            "reserve": round(budget * .20, 2),
        }
        summary = f"A {data['style']} jewelry plan for {data['occasion']} within ₹{budget:.0f}."
        if image_note:
            summary += " The uploaded outfit was considered as optional visual context."

    catalog = enrich_links(build_mock_catalog(planner_type, budget))
    recommendations = []
    for item in catalog:
        recommendations.append({
            "name": item["name"],
            "category": planner_type,
            "estimated_price": item["price"],
            "platform": item["platform"],
            "reason": "Demo catalog option; verify live price, stock, delivery and suitability on the linked platform.",
            "url": item["url"],
        })
    return {
        "summary": summary,
        "budget": budget,
        "allocation": allocation,
        "recommendations": recommendations,
        "source": "fallback-demo-catalog",
        "image_analysis": image_note or None,
    }

def generate_recommendation(planner_type: str, data: dict, image_bytes: Optional[bytes] = None, mime_type: str = "image/jpeg") -> dict:
    settings = get_settings()
    image_note = ""
    prompt = {
        "home": home_prompt,
        "party": party_prompt,
        "jewelry": jewelry_prompt,
    }[planner_type](data, "") if planner_type == "jewelry" else {
        "home": home_prompt,
        "party": party_prompt,
    }[planner_type](data)

    if not settings.gemini_api_key:
        return _fallback(planner_type, data)

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        contents = [prompt]
        if image_bytes and planner_type == "jewelry":
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
            contents[0] = jewelry_prompt(data, "Analyze the uploaded outfit image for broad color/style coordination.")
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
            ),
        )
        parsed = _clean_json(response.text)
        parsed.setdefault("budget", float(data["budget"]))
        parsed.setdefault("allocation", {})
        parsed.setdefault("recommendations", [])
        parsed.setdefault("summary", "AI-generated budget recommendations.")
        parsed["source"] = f"gemini:{settings.gemini_model}"
        parsed["image_analysis"] = image_note or None

        # Add safe mock marketplace links to AI recommendations.
        for item in parsed["recommendations"]:
            platform = item.get("platform", "Amazon")
            query = item.get("name", "product")
            item["url"] = item.get("url") or enrich_links([{
                "name": query, "platform": platform, "price": item.get("estimated_price", 0), "query": query
            }])[0]["url"]
        return parsed
    except Exception:
        return _fallback(planner_type, data, image_note)
