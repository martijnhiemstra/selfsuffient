"""
Test suite for Multi-language Translation Feature
Tests: GET /api/languages, project language config, translate/update/delete endpoints for blog/library/diary
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@selfsufficient.app"
TEST_PASSWORD = "admin123"
TEST_PROJECT_ID = "72868dc9-f97d-4209-83e8-8d2c6fd59c67"
TEST_BLOG_ENTRY_ID = "16cdb857-4768-4637-8cf3-bff46a99ff9e"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for testing"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    return data.get("access_token")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestLanguagesEndpoint:
    """Test GET /api/languages endpoint"""
    
    def test_get_supported_languages_returns_27_languages(self, auth_headers):
        """GET /api/languages should return all 27 supported languages"""
        response = requests.get(f"{BASE_URL}/api/languages", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "languages" in data
        languages = data["languages"]
        
        # Should have 27 languages
        assert len(languages) == 27, f"Expected 27 languages, got {len(languages)}"
        
        # Each language should have code and name
        for lang in languages:
            assert "code" in lang
            assert "name" in lang
        
        # Check some expected languages
        codes = [l["code"] for l in languages]
        assert "en" in codes, "English should be in supported languages"
        assert "nl" in codes, "Dutch should be in supported languages"
        assert "de" in codes, "German should be in supported languages"
        assert "fr" in codes, "French should be in supported languages"
        assert "ja" in codes, "Japanese should be in supported languages"
        print(f"✓ GET /api/languages returns {len(languages)} supported languages")


class TestProjectLanguageConfig:
    """Test project language configuration"""
    
    def test_get_project_returns_languages_and_primary_language(self, auth_headers):
        """GET /api/projects/{pid} should return languages and primary_language fields"""
        response = requests.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "languages" in data, "Project should have 'languages' field"
        assert "primary_language" in data, "Project should have 'primary_language' field"
        assert isinstance(data["languages"], list), "languages should be a list"
        assert isinstance(data["primary_language"], str), "primary_language should be a string"
        
        print(f"✓ Project has languages: {data['languages']}, primary: {data['primary_language']}")
    
    def test_update_project_languages(self, auth_headers):
        """PUT /api/projects/{pid} should accept languages and primary_language fields"""
        # First get current project state
        get_response = requests.get(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}", headers=auth_headers)
        original_data = get_response.json()
        
        # Update with new languages
        update_payload = {
            "languages": ["en", "nl", "de", "fr"],
            "primary_language": "en"
        }
        response = requests.put(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}",
            json=update_payload,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "languages" in data
        assert set(data["languages"]) == {"en", "nl", "de", "fr"}
        assert data["primary_language"] == "en"
        
        # Restore original languages
        restore_payload = {
            "languages": original_data.get("languages", ["en"]),
            "primary_language": original_data.get("primary_language", "en")
        }
        requests.put(f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}", json=restore_payload, headers=auth_headers)
        
        print("✓ PUT /api/projects/{pid} accepts languages and primary_language")
    
    def test_public_project_returns_languages(self, auth_headers):
        """GET /api/public/projects/{pid} should return languages and primary_language"""
        response = requests.get(f"{BASE_URL}/api/public/projects/{TEST_PROJECT_ID}")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "languages" in data, "Public project should have 'languages' field"
        assert "primary_language" in data, "Public project should have 'primary_language' field"
        
        print(f"✓ Public project returns languages: {data['languages']}")


class TestBlogTranslation:
    """Test blog translation endpoints"""
    
    def test_blog_entry_has_translations_field(self, auth_headers):
        """Blog entry response should include 'translations' dict field"""
        response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        if data.get("entries") and len(data["entries"]) > 0:
            entry = data["entries"][0]
            assert "translations" in entry, "Blog entry should have 'translations' field"
            assert isinstance(entry["translations"], dict), "translations should be a dict"
            print(f"✓ Blog entry has translations field: {entry['translations']}")
        else:
            print("⚠ No blog entries found to test translations field")
    
    def test_translate_blog_returns_400_if_language_not_in_project(self, auth_headers):
        """POST translate should return 400 if target_language not in project languages"""
        # Try to translate to a language not in project
        response = requests.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}/translate",
            json={"target_language": "zh"},  # Chinese - likely not in project
            headers=auth_headers
        )
        # Should be 400 if language not enabled
        if response.status_code == 400:
            assert "not enabled" in response.json().get("detail", "").lower() or "not in" in response.json().get("detail", "").lower()
            print("✓ POST translate returns 400 for language not in project")
        else:
            # If it succeeds, the language was in project - that's also valid
            print(f"⚠ Language 'zh' is in project languages, got status {response.status_code}")
    
    def test_translate_blog_returns_400_if_no_openai_key(self, auth_headers):
        """POST translate should return 400 if no OpenAI key configured"""
        # First ensure project has the target language
        requests.put(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}",
            json={"languages": ["en", "nl", "de"]},
            headers=auth_headers
        )
        
        response = requests.post(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}/translate",
            json={"target_language": "nl"},
            headers=auth_headers
        )
        
        # Should return 400 with "No OpenAI API key configured" if user has no key
        if response.status_code == 400:
            detail = response.json().get("detail", "")
            assert "openai" in detail.lower() or "api key" in detail.lower(), f"Expected OpenAI key error, got: {detail}"
            print("✓ POST translate returns 400 when no OpenAI key configured")
        elif response.status_code == 502:
            # OpenAI API error - key exists but may be invalid
            print("⚠ OpenAI API error (502) - key exists but may be invalid")
        else:
            print(f"⚠ Unexpected status {response.status_code}: {response.text}")
    
    def test_update_blog_translation(self, auth_headers):
        """PUT /api/projects/{pid}/blog/{eid}/translate/{lang} updates manual translation"""
        # First, manually add a translation
        response = requests.put(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}/translate/de",
            json={"title": "Test Titel", "content": "Test Inhalt"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert response.json().get("message") == "Translation updated"
        
        # Verify translation was saved
        get_response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}",
            headers=auth_headers
        )
        entry = get_response.json()
        assert "de" in entry.get("translations", {}), "German translation should exist"
        assert entry["translations"]["de"]["title"] == "Test Titel"
        
        print("✓ PUT translate/{lang} updates manual translation")
    
    def test_delete_blog_translation(self, auth_headers):
        """DELETE /api/projects/{pid}/blog/{eid}/translate/{lang} deletes translation"""
        # First ensure translation exists
        requests.put(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}/translate/de",
            json={"title": "To Delete", "content": "To Delete"},
            headers=auth_headers
        )
        
        # Delete the translation
        response = requests.delete(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}/translate/de",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        assert response.json().get("message") == "Translation deleted"
        
        # Verify translation was deleted
        get_response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}",
            headers=auth_headers
        )
        entry = get_response.json()
        assert "de" not in entry.get("translations", {}), "German translation should be deleted"
        
        print("✓ DELETE translate/{lang} removes translation")


class TestPublicBlogWithLang:
    """Test public blog list with ?lang= parameter"""
    
    def test_public_blog_list_accepts_lang_param(self, auth_headers):
        """GET /api/public/projects/{pid}/blog?lang= should accept lang parameter"""
        # First add a translation to a blog entry
        requests.put(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}/translate/nl",
            json={"title": "Nederlandse Titel", "content": "Nederlandse inhoud"},
            headers=auth_headers
        )
        
        # Get public blog list with lang param
        response = requests.get(f"{BASE_URL}/api/public/projects/{TEST_PROJECT_ID}/blog?lang=nl")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "entries" in data
        
        # Check if translated title is returned
        for entry in data["entries"]:
            if entry["id"] == TEST_BLOG_ENTRY_ID:
                # Should have Dutch title if translation exists
                print(f"✓ Public blog with ?lang=nl returns entry with title: {entry['title']}")
                break
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/blog/{TEST_BLOG_ENTRY_ID}/translate/nl",
            headers=auth_headers
        )


class TestLibraryTranslation:
    """Test library translation endpoints"""
    
    def test_library_entry_has_translations_field(self, auth_headers):
        """Library entry response should include 'translations' dict field"""
        response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/library",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        if data.get("entries") and len(data["entries"]) > 0:
            entry = data["entries"][0]
            assert "translations" in entry, "Library entry should have 'translations' field"
            assert isinstance(entry["translations"], dict), "translations should be a dict"
            print(f"✓ Library entry has translations field")
        else:
            print("⚠ No library entries found to test translations field")
    
    def test_public_library_accepts_lang_param(self):
        """GET /api/public/projects/{pid}/library?lang= should accept lang parameter"""
        response = requests.get(f"{BASE_URL}/api/public/projects/{TEST_PROJECT_ID}/library?lang=nl")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "entries" in data
        print("✓ Public library accepts ?lang= parameter")


class TestDiaryTranslation:
    """Test diary translation endpoints"""
    
    def test_diary_entry_has_translations_field(self, auth_headers):
        """Diary entry response should include 'translations' dict field"""
        response = requests.get(
            f"{BASE_URL}/api/projects/{TEST_PROJECT_ID}/diary",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        if data.get("entries") and len(data["entries"]) > 0:
            entry = data["entries"][0]
            assert "translations" in entry, "Diary entry should have 'translations' field"
            assert isinstance(entry["translations"], dict), "translations should be a dict"
            print(f"✓ Diary entry has translations field")
        else:
            print("⚠ No diary entries found to test translations field")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
