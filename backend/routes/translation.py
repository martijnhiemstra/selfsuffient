"""Translation routes for blog, library, and diary entries."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone

from config import db
from services import get_current_user, verify_project_access
from services.translation import translate_content, SUPPORTED_LANGUAGES
from routes.openai_settings import decrypt_api_key

router = APIRouter()


class TranslateRequest(BaseModel):
    target_language: str


class TranslationUpdateRequest(BaseModel):
    title: str
    content: str


async def get_user_openai_credentials(user_id: str):
    """Get user's decrypted OpenAI key and model."""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user or not user.get("openai_api_key"):
        raise HTTPException(status_code=400, detail="No OpenAI API key configured. Go to Settings to add one.")
    try:
        api_key = decrypt_api_key(user["openai_api_key"])
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decrypt API key. Please re-save it in Settings.")
    model = user.get("openai_model", "gpt-4o-mini")
    return api_key, model


@router.get("/languages")
async def get_supported_languages():
    """Return all supported languages."""
    return {"languages": [{"code": k, "name": v} for k, v in SUPPORTED_LANGUAGES.items()]}


# --- Blog translations ---

@router.post("/projects/{project_id}/blog/{entry_id}/translate")
async def translate_blog_entry(
    project_id: str,
    entry_id: str,
    data: TranslateRequest,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if data.target_language not in project.get("languages", ["en"]):
        raise HTTPException(status_code=400, detail="Target language not enabled for this project")

    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")

    api_key, model = await get_user_openai_credentials(current_user["id"])
    primary = project.get("primary_language", "en")

    try:
        result = await translate_content(api_key, model, entry["title"], entry["description"], primary, data.target_language)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    translations = entry.get("translations", {})
    translations[data.target_language] = {"title": result["title"], "description": result["content"]}

    await db.blog_entries.update_one(
        {"id": entry_id},
        {"$set": {"translations": translations, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"message": "Translation saved", "translation": translations[data.target_language]}


@router.put("/projects/{project_id}/blog/{entry_id}/translate/{lang}")
async def update_blog_translation(
    project_id: str,
    entry_id: str,
    lang: str,
    data: TranslationUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    entry = await db.blog_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Blog entry not found")

    translations = entry.get("translations", {})
    translations[lang] = {"title": data.title, "description": data.content}

    await db.blog_entries.update_one(
        {"id": entry_id},
        {"$set": {"translations": translations, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"message": "Translation updated"}


@router.delete("/projects/{project_id}/blog/{entry_id}/translate/{lang}")
async def delete_blog_translation(
    project_id: str,
    entry_id: str,
    lang: str,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    await db.blog_entries.update_one({"id": entry_id}, {"$unset": {f"translations.{lang}": ""}})
    return {"message": "Translation deleted"}


# --- Library translations ---

@router.post("/projects/{project_id}/library/entries/{entry_id}/translate")
async def translate_library_entry(
    project_id: str,
    entry_id: str,
    data: TranslateRequest,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if data.target_language not in project.get("languages", ["en"]):
        raise HTTPException(status_code=400, detail="Target language not enabled for this project")

    entry = await db.library_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Library entry not found")

    api_key, model = await get_user_openai_credentials(current_user["id"])
    primary = project.get("primary_language", "en")

    try:
        result = await translate_content(api_key, model, entry["title"], entry["description"], primary, data.target_language)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    translations = entry.get("translations", {})
    translations[data.target_language] = {"title": result["title"], "description": result["content"]}

    await db.library_entries.update_one(
        {"id": entry_id},
        {"$set": {"translations": translations, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"message": "Translation saved", "translation": translations[data.target_language]}


@router.put("/projects/{project_id}/library/entries/{entry_id}/translate/{lang}")
async def update_library_translation(
    project_id: str,
    entry_id: str,
    lang: str,
    data: TranslationUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    entry = await db.library_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Library entry not found")

    translations = entry.get("translations", {})
    translations[lang] = {"title": data.title, "description": data.content}

    await db.library_entries.update_one(
        {"id": entry_id},
        {"$set": {"translations": translations, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"message": "Translation updated"}


@router.delete("/projects/{project_id}/library/entries/{entry_id}/translate/{lang}")
async def delete_library_translation(
    project_id: str,
    entry_id: str,
    lang: str,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    await db.library_entries.update_one({"id": entry_id}, {"$unset": {f"translations.{lang}": ""}})
    return {"message": "Translation deleted"}


# --- Diary translations ---

@router.post("/projects/{project_id}/diary/{entry_id}/translate")
async def translate_diary_entry(
    project_id: str,
    entry_id: str,
    data: TranslateRequest,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if data.target_language not in project.get("languages", ["en"]):
        raise HTTPException(status_code=400, detail="Target language not enabled for this project")

    entry = await db.diary_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")

    api_key, model = await get_user_openai_credentials(current_user["id"])
    primary = project.get("primary_language", "en")

    try:
        result = await translate_content(api_key, model, entry["title"], entry["story"], primary, data.target_language)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    translations = entry.get("translations", {})
    translations[data.target_language] = {"title": result["title"], "story": result["content"]}

    await db.diary_entries.update_one(
        {"id": entry_id},
        {"$set": {"translations": translations, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"message": "Translation saved", "translation": translations[data.target_language]}


@router.put("/projects/{project_id}/diary/{entry_id}/translate/{lang}")
async def update_diary_translation(
    project_id: str,
    entry_id: str,
    lang: str,
    data: TranslationUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    entry = await db.diary_entries.find_one({"id": entry_id, "project_id": project_id}, {"_id": 0})
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")

    translations = entry.get("translations", {})
    translations[lang] = {"title": data.title, "story": data.content}

    await db.diary_entries.update_one(
        {"id": entry_id},
        {"$set": {"translations": translations, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"message": "Translation updated"}


@router.delete("/projects/{project_id}/diary/{entry_id}/translate/{lang}")
async def delete_diary_translation(
    project_id: str,
    entry_id: str,
    lang: str,
    current_user: dict = Depends(get_current_user),
):
    await verify_project_access(project_id, current_user["id"])
    await db.diary_entries.update_one({"id": entry_id}, {"$unset": {f"translations.{lang}": ""}})
    return {"message": "Translation deleted"}
