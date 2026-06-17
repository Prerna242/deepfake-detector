import asyncio
import base64
import copy
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from app.config import BASE_DIR, settings


DEFAULT_GEMINI_DETECTION_CONFIG: dict[str, Any] = {
    "role_prompt": "You are an expert forensic deepfake classifier for a single input image.",
    "focus_areas": [
        {
            "name": "facial_geometry_consistency",
            "weight": 0.2,
            "checks": [
                "eye symmetry and alignment",
                "ear shape continuity",
                "jawline contour coherence",
                "nose bridge and nostril consistency",
            ],
        },
        {
            "name": "skin_texture_and_blending",
            "weight": 0.2,
            "checks": [
                "waxy or oversmoothed skin patches",
                "edge blending around hairline and cheeks",
                "texture discontinuity across face regions",
            ],
        },
    ],
    "decision_policy": {
        "minimum_real_confidence": 88,
        "fallback_label_for_uncertain": "FAKE",
        "uncertain_confidence_threshold": 60,
    },
    "extra_instructions": [
        "Be conservative: if multiple suspicious cues appear, prefer FAKE.",
        "Do not use image aesthetics as evidence.",
        "Base confidence on forensic consistency, not style.",
    ],
    "generation_config": {
        "temperature": 0,
        "topP": 0.9,
        "topK": 40,
        "maxOutputTokens": 1024,
        "thinkingConfig": {"thinkingBudget": 0},
        "responseMimeType": "application/json",
    },
}


ALLOWED_GENERATION_CONFIG_KEYS = {
    "temperature",
    "topP",
    "topK",
    "maxOutputTokens",
    "candidateCount",
    "stopSequences",
    "responseMimeType",
    "thinkingConfig",
}


def _deep_merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def _get_detection_config_path() -> Path:
    config_path = Path(settings.GEMINI_DETECTION_CONFIG_PATH)
    if not config_path.is_absolute():
        config_path = BASE_DIR / config_path
    return config_path


def _load_detection_config() -> tuple[dict[str, Any], Path]:
    config_path = _get_detection_config_path()
    if not config_path.exists():
        print(
            f"[Gemini] WARNING: Detection config file not found at {config_path}. "
            "Using built-in defaults."
        )
        return copy.deepcopy(DEFAULT_GEMINI_DETECTION_CONFIG), config_path

    try:
        file_data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in Gemini detection config file: {config_path}"
        ) from exc

    if not isinstance(file_data, dict):
        raise RuntimeError(
            f"Gemini detection config must be a JSON object: {config_path}"
        )

    merged = _deep_merge_dict(DEFAULT_GEMINI_DETECTION_CONFIG, file_data)
    return merged, config_path


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_prompt(config: dict[str, Any]) -> str:
    role_prompt = str(
        config.get(
            "role_prompt",
            "You are an expert forensic deepfake classifier for a single input image.",
        )
    ).strip()

    focus_lines: list[str] = []
    focus_areas = config.get("focus_areas")
    if isinstance(focus_areas, list):
        for area in focus_areas:
            if not isinstance(area, dict):
                continue
            name = str(area.get("name", "unnamed_focus_area")).replace("_", " ").strip()
            weight_value = area.get("weight")
            weight_text = ""
            if weight_value is not None:
                weight_text = f" (weight={weight_value})"

            checks = area.get("checks")
            check_text = ""
            if isinstance(checks, list):
                clean_checks = [str(item).strip() for item in checks if str(item).strip()]
                if clean_checks:
                    check_text = "; ".join(clean_checks)

            if check_text:
                focus_lines.append(f"- {name}{weight_text}: {check_text}")
            else:
                focus_lines.append(f"- {name}{weight_text}")

    if not focus_lines:
        focus_lines = ["- facial consistency, texture coherence, lighting consistency"]

    policy = config.get("decision_policy") if isinstance(config.get("decision_policy"), dict) else {}
    min_real_confidence = _safe_float(policy.get("minimum_real_confidence", 88), 88.0)
    uncertain_threshold = _safe_float(policy.get("uncertain_confidence_threshold", 60), 60.0)
    fallback_label = str(policy.get("fallback_label_for_uncertain", "FAKE")).upper()
    if fallback_label not in {"REAL", "FAKE"}:
        fallback_label = "FAKE"

    extra_lines: list[str] = []
    extras = config.get("extra_instructions")
    if isinstance(extras, list):
        for item in extras:
            item_text = str(item).strip()
            if item_text:
                extra_lines.append(f"- {item_text}")

    extras_block = "\n".join(extra_lines) if extra_lines else "- No extra instructions"

    return (
        f"{role_prompt}\n\n"
        "Follow this forensic checklist:\n"
        + "\n".join(focus_lines)
        + "\n\n"
        "Decision policy:\n"
        f"- Label must be REAL or FAKE.\n"
        f"- Confidence is 0-100 for the selected label.\n"
        f"- Raw score is 0-1 where higher means more likely REAL.\n"
        f"- For uncertain cases, use fallback label.\n"
        f"- Real should only be selected with strong consistency.\n"
        f"- REAL requires at least {min_real_confidence:g}% confidence.\n"
        f"- If confidence is below {uncertain_threshold:g}%, use {fallback_label}.\n"
        "Extra instructions:\n"
        f"{extras_block}\n\n"
        "Return strictly JSON with keys: label, confidence, raw_score, reason, evidence. "
        "Do not include markdown or extra text."
    )


def _build_generation_config(config: dict[str, Any], model_name: str) -> dict[str, Any]:
    generation_config: dict[str, Any] = {
        "temperature": 0,
        "maxOutputTokens": 1024,
        "responseMimeType": "application/json",
    }

    candidate = config.get("generation_config")
    if isinstance(candidate, dict):
        for key, value in candidate.items():
            if key in ALLOWED_GENERATION_CONFIG_KEYS:
                generation_config[key] = value

    if not model_name.startswith("gemini-2.5"):
        generation_config.pop("thinkingConfig", None)

    generation_config["responseMimeType"] = "application/json"
    return generation_config


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _to_float(value: Any) -> float:
    if isinstance(value, str):
        value = value.strip().replace("%", "")
    return float(value)


def _extract_text_from_response(response_payload: dict[str, Any]) -> str:
    candidates = response_payload.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []

    texts = []
    for part in parts:
        if isinstance(part, dict) and part.get("text"):
            texts.append(part["text"])

    if not texts:
        raise RuntimeError("Gemini response did not contain text output.")

    return "\n".join(texts).strip()


def _extract_json_text(raw_text: str) -> str:
    cleaned = raw_text.strip()

    if "```" in cleaned:
        chunks = cleaned.split("```")
        for chunk in chunks:
            candidate = chunk.strip()
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return candidate

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]

    return cleaned


def _normalize_prediction(payload: dict[str, Any]) -> dict[str, float | str]:
    label = str(payload.get("label", "")).strip().upper()
    if label not in {"REAL", "FAKE"}:
        verdict = str(payload.get("verdict", "")).strip().upper()
        label = verdict

    if label not in {"REAL", "FAKE"}:
        raise RuntimeError("Gemini response did not provide a valid label (REAL/FAKE).")

    confidence = None
    for key in ("confidence", "confidence_percent", "probability"):
        if key in payload and payload[key] is not None:
            confidence = _to_float(payload[key])
            if confidence <= 1:
                confidence *= 100
            confidence = _clamp(confidence, 0.0, 100.0)
            break

    raw_score = None
    for key in ("raw_score", "real_probability", "probability_real", "score"):
        if key in payload and payload[key] is not None:
            raw_score = _to_float(payload[key])
            if raw_score > 1:
                raw_score /= 100
            raw_score = _clamp(raw_score, 0.0, 1.0)
            break

    if raw_score is None and confidence is not None:
        if label == "REAL":
            raw_score = confidence / 100.0
        else:
            raw_score = 1.0 - (confidence / 100.0)

    if confidence is None and raw_score is not None:
        if label == "REAL":
            confidence = raw_score * 100.0
        else:
            confidence = (1.0 - raw_score) * 100.0

    if confidence is None or raw_score is None:
        confidence = 50.0
        raw_score = 0.5

    return {
        "label": label,
        "confidence": round(confidence, 2),
        "raw_score": round(raw_score, 4),
    }


def _extract_partial_payload_from_text(text: str) -> dict[str, Any] | None:
    label_match = re.search(r'"label"\s*:\s*"?(REAL|FAKE)"?', text, flags=re.IGNORECASE)
    if not label_match:
        return None

    payload: dict[str, Any] = {
        "label": label_match.group(1).upper(),
    }

    confidence_match = re.search(
        r'"confidence"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
        text,
        flags=re.IGNORECASE,
    )
    if confidence_match:
        payload["confidence"] = float(confidence_match.group(1))

    raw_score_match = re.search(
        r'"raw_score"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
        text,
        flags=re.IGNORECASE,
    )
    if raw_score_match:
        payload["raw_score"] = float(raw_score_match.group(1))

    return payload


def _apply_decision_policy(
    prediction: dict[str, float | str],
    config: dict[str, Any],
) -> dict[str, float | str]:
    policy = config.get("decision_policy") if isinstance(config.get("decision_policy"), dict) else {}

    min_real_confidence = _safe_float(policy.get("minimum_real_confidence", 88), 88.0)
    fallback_label = str(policy.get("fallback_label_for_uncertain", "FAKE")).upper()
    uncertain_confidence_threshold = _safe_float(
        policy.get("uncertain_confidence_threshold", 60),
        60.0,
    )

    if fallback_label not in {"REAL", "FAKE"}:
        fallback_label = "FAKE"

    label = str(prediction.get("label", "")).upper()
    confidence = _safe_float(prediction.get("confidence", 0), 0.0)

    if label == "REAL" and confidence < min_real_confidence:
        prediction["label"] = fallback_label
        if fallback_label == "FAKE":
            fake_confidence = max(100.0 - confidence, uncertain_confidence_threshold)
            fake_confidence = _clamp(fake_confidence, 0.0, 100.0)
            prediction["confidence"] = round(fake_confidence, 2)
            prediction["raw_score"] = round(1.0 - (fake_confidence / 100.0), 4)

    return prediction


def _call_gemini(file_bytes: bytes, mime_type: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured in backend/.env.")

    config, config_path = _load_detection_config()

    model_name = (settings.GEMINI_MODEL or "gemini-2.5-flash").strip()
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        f"?key={settings.GEMINI_API_KEY}"
    )

    prompt = _build_prompt(config)
    generation_config = _build_generation_config(config, model_name)

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64.b64encode(file_bytes).decode("utf-8"),
                        }
                    },
                ],
            }
        ],
        "generationConfig": generation_config,
    }

    print(
        f"[Gemini] Request configured from {config_path}. "
        f"Model={model_name}, MIME={mime_type}, Bytes={len(file_bytes)}"
    )
    print(f"[Gemini] Request generationConfig: {json.dumps(generation_config, ensure_ascii=True)}")

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=settings.GEMINI_TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(
            f"Gemini API request failed ({exc.code}). Response: {error_body[:300]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Unable to reach Gemini API: {exc.reason}") from exc

    try:
        response_payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini API returned invalid JSON response.") from exc

    if response_payload.get("error"):
        error_message = response_payload["error"].get("message", "Unknown Gemini API error.")
        raise RuntimeError(f"Gemini API error: {error_message}")

    finish_reason = None
    candidates = response_payload.get("candidates") or []
    if candidates and isinstance(candidates[0], dict):
        finish_reason = candidates[0].get("finishReason")
    if finish_reason:
        print(f"[Gemini] finishReason: {finish_reason}")

    print(f"[Gemini] Raw API response: {json.dumps(response_payload, ensure_ascii=True)}")

    return response_payload, config


async def predict_with_gemini(file_bytes: bytes, mime_type: str) -> dict[str, float | str]:
    response_payload, config = await asyncio.to_thread(_call_gemini, file_bytes, mime_type)
    text_output = _extract_text_from_response(response_payload)
    print(f"[Gemini] Extracted candidate text: {text_output}")

    try:
        parsed_payload = json.loads(_extract_json_text(text_output))
    except json.JSONDecodeError as exc:
        partial_payload = _extract_partial_payload_from_text(text_output)
        if partial_payload is None:
            raise RuntimeError(
                "Gemini response could not be parsed as JSON. "
                f"Raw output: {text_output[:300]}"
            ) from exc
        parsed_payload = partial_payload
        print(
            "[Gemini] WARNING: Response JSON was incomplete; "
            "using partial payload extraction."
        )

    print(f"[Gemini] Parsed JSON payload: {json.dumps(parsed_payload, ensure_ascii=True)}")

    normalized_prediction = _normalize_prediction(parsed_payload)
    normalized_prediction = _apply_decision_policy(normalized_prediction, config)

    print(
        "[Gemini] Final normalized prediction: "
        f"{json.dumps(normalized_prediction, ensure_ascii=True)}"
    )

    return normalized_prediction
