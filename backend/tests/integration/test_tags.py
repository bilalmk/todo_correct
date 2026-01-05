"""Integration tests for Tag API endpoints (User Story 2)."""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestTagCRUDEndpoints:
    """Integration tests for 5 tag endpoints."""

    @pytest.mark.asyncio
    async def test_create_tag_201_with_color_normalization(
        self, client: AsyncClient, auth_headers: dict, user_id: str
    ):
        """Test POST /api/v1/{user_id}/tags returns 201 with color normalization."""
        response = await client.post(
            f"/api/v1/{user_id}/tags",
            json={"name": "work", "color": "#f5a"},  # Shorthand lowercase
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "work"
        assert data["color"] == "#FF55AA"  # Normalized to uppercase #RRGGBB
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_duplicate_tag_409_conflict(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test POST /api/v1/{user_id}/tags duplicate name returns 409 Conflict."""
        from backend.src.models.tag import Tag
        from uuid import UUID

        # Create a tag first
        tag = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        session.add(tag)
        await session.commit()

        # Try to create duplicate
        response = await client.post(
            f"/api/v1/{user_id}/tags",
            json={"name": "work", "color": "#00FF00"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "error" in data
        assert data["code"] == "TAG_NAME_CONFLICT"

    @pytest.mark.asyncio
    async def test_list_tags_200_ok(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test GET /api/v1/{user_id}/tags returns 200 OK with list."""
        from backend.src.models.tag import Tag
        from uuid import UUID

        # Create tags
        tag1 = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        tag2 = Tag(user_id=UUID(user_id), name="personal", color="#00FF00")
        session.add(tag1)
        session.add(tag2)
        await session.commit()

        response = await client.get(
            f"/api/v1/{user_id}/tags",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        names = {tag["name"] for tag in data}
        assert "work" in names
        assert "personal" in names

    @pytest.mark.asyncio
    async def test_get_single_tag_200_ok(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test GET /api/v1/{user_id}/tags/{id} returns 200 OK."""
        from backend.src.models.tag import Tag
        from uuid import UUID

        tag = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        session.add(tag)
        await session.commit()
        tag_id = tag.id

        response = await client.get(
            f"/api/v1/{user_id}/tags/{tag_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == tag_id
        assert data["name"] == "work"

    @pytest.mark.asyncio
    async def test_update_tag_200_ok(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test PUT /api/v1/{user_id}/tags/{id} returns 200 OK."""
        from backend.src.models.tag import Tag
        from uuid import UUID

        tag = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        session.add(tag)
        await session.commit()
        tag_id = tag.id

        response = await client.put(
            f"/api/v1/{user_id}/tags/{tag_id}",
            json={"name": "personal", "color": "#00FF00"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "personal"
        assert data["color"] == "#00FF00"

    @pytest.mark.asyncio
    async def test_delete_tag_204_no_content(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test DELETE /api/v1/{user_id}/tags/{id} returns 204 (soft delete)."""
        from backend.src.models.tag import Tag
        from uuid import UUID

        tag = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        session.add(tag)
        await session.commit()
        tag_id = tag.id

        response = await client.delete(
            f"/api/v1/{user_id}/tags/{tag_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify tag is soft-deleted
        get_response = await client.get(
            f"/api/v1/{user_id}/tags/{tag_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
