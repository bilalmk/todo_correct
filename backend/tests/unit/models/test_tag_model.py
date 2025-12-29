"""Unit tests for Tag model."""
import pytest
from datetime import datetime, UTC
from sqlmodel import select

from src.models.tag import Tag


@pytest.mark.asyncio
async def test_create_tag(test_session, test_user):
    """Test creating a basic tag with required fields."""
    tag = Tag(
        user_id=test_user.id,
        name="work",
        color="#FF5733",
    )

    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    assert tag.id is not None
    assert tag.user_id == test_user.id
    assert tag.name == "work"
    assert tag.color == "#FF5733"
    assert tag.created_at is not None
    assert tag.deleted_at is None


@pytest.mark.asyncio
async def test_create_tag_without_color(test_session, test_user):
    """Test creating a tag without color (color is optional)."""
    tag = Tag(
        user_id=test_user.id,
        name="personal",
    )

    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    assert tag.id is not None
    assert tag.name == "personal"
    assert tag.color is None


@pytest.mark.asyncio
async def test_tag_name_required(test_session, test_user):
    """Test that tag name is required (NOT NULL constraint)."""
    tag = Tag(
        user_id=test_user.id,
        name=None,  # This should fail
    )

    with pytest.raises(Exception):  # Should raise validation or database error
        test_session.add(tag)
        await test_session.commit()


@pytest.mark.asyncio
async def test_tag_user_id_required(test_session, test_user):
    """Test that user_id is required (NOT NULL constraint)."""
    tag = Tag(
        user_id=None,  # This should fail
        name="test",
    )

    with pytest.raises(Exception):  # Should raise validation or database error
        test_session.add(tag)
        await test_session.commit()


@pytest.mark.asyncio
async def test_tag_name_max_length(test_session, test_user):
    """Test that tag name has max length of 50 characters."""
    long_name = "A" * 51  # 51 characters

    tag = Tag(
        user_id=test_user.id,
        name=long_name,  # Should fail max length constraint
    )

    with pytest.raises(Exception):  # Should raise validation or database error
        test_session.add(tag)
        await test_session.commit()


@pytest.mark.asyncio
async def test_tag_color_hex_format(test_session, test_user):
    """Test that tag color must be in hex format (#RRGGBB)."""
    tag = Tag(
        user_id=test_user.id,
        name="test",
        color="invalid",  # Should fail regex constraint
    )

    with pytest.raises(Exception):  # Should raise validation or database error
        test_session.add(tag)
        await test_session.commit()


@pytest.mark.asyncio
async def test_tag_unique_constraint_per_user(test_session, test_user):
    """Test that tag names are unique per user (user_id, name)."""
    # Create first tag
    tag1 = Tag(
        user_id=test_user.id,
        name="urgent",
        color="#FF0000",
    )
    test_session.add(tag1)
    await test_session.commit()

    # Try to create duplicate tag for same user
    tag2 = Tag(
        user_id=test_user.id,
        name="urgent",  # Same name, same user - should fail
        color="#00FF00",
    )

    with pytest.raises(Exception):  # Should raise unique constraint error
        test_session.add(tag2)
        await test_session.commit()


@pytest.mark.asyncio
async def test_tag_unique_constraint_across_users(test_session):
    """Test that tag names can be duplicated across different users."""
    from src.services.user import create_user
    from src.models.user import UserCreate

    # Create two users
    user1_data = UserCreate(email="taguser1@example.com", password="password123", name="Tag User 1")
    user2_data = UserCreate(email="taguser2@example.com", password="password123", name="Tag User 2")

    user1 = await create_user(test_session, user1_data)
    user2 = await create_user(test_session, user2_data)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    # Create same tag name for both users (should succeed)
    tag1 = Tag(user_id=user1.id, name="work", color="#FF0000")
    tag2 = Tag(user_id=user2.id, name="work", color="#00FF00")

    test_session.add_all([tag1, tag2])
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)

    # Both tags should exist
    assert tag1.id is not None
    assert tag2.id is not None
    assert tag1.name == tag2.name == "work"
    assert tag1.user_id != tag2.user_id


@pytest.mark.asyncio
async def test_tag_soft_delete(test_session, test_user):
    """Test soft delete functionality for tags."""
    tag = Tag(
        user_id=test_user.id,
        name="temporary",
        color="#AABBCC",
    )
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    # Soft delete the tag
    tag.deleted_at = datetime.now(UTC)
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    assert tag.deleted_at is not None


@pytest.mark.asyncio
async def test_tag_soft_delete_allows_name_reuse(test_session, test_user):
    """Test that soft-deleted tag names can be reused (partial unique constraint)."""
    # Create and soft-delete first tag
    tag1 = Tag(user_id=test_user.id, name="recycled", color="#111111")
    test_session.add(tag1)
    await test_session.commit()
    await test_session.refresh(tag1)

    tag1.deleted_at = datetime.now(UTC)
    test_session.add(tag1)
    await test_session.commit()

    # Create new tag with same name (should succeed because first is soft-deleted)
    tag2 = Tag(user_id=test_user.id, name="recycled", color="#222222")
    test_session.add(tag2)
    await test_session.commit()
    await test_session.refresh(tag2)

    assert tag2.id is not None
    assert tag2.name == "recycled"
    assert tag2.deleted_at is None


@pytest.mark.asyncio
async def test_tag_cascade_delete_on_user_deletion(test_session):
    """Test that deleting a user CASCADE deletes their tags."""
    from src.services.user import create_user
    from src.models.user import UserCreate

    # Create user
    user_data = UserCreate(email="tagcascade@example.com", password="password123", name="Tag Cascade")
    user = await create_user(test_session, user_data)
    await test_session.commit()
    await test_session.refresh(user)

    # Create tags for user
    tag1 = Tag(user_id=user.id, name="tag1")
    tag2 = Tag(user_id=user.id, name="tag2")
    test_session.add_all([tag1, tag2])
    await test_session.commit()

    # Verify tags exist
    statement = select(Tag).where(Tag.user_id == user.id)
    result = await test_session.execute(statement)
    tags_before = result.scalars().all()
    assert len(tags_before) == 2

    # Delete user (should CASCADE delete tags)
    await test_session.delete(user)
    await test_session.commit()

    # Verify tags are deleted
    statement = select(Tag).where(Tag.user_id == user.id)
    result = await test_session.execute(statement)
    tags_after = result.scalars().all()
    assert len(tags_after) == 0
