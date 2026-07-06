import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from repositories.entities import post_entity, get_entity


class TestPostEntityUpsert:
    """Test repositories/entities.py post_entity (MERGE/Upsert logic)"""

    @pytest.mark.asyncio
    async def test_post_entity_merge_existing(self):
        """Test MERGE logic when entity already exists in database"""
        # Mock the driver session
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_single = MagicMock()
        
        mock_single.return_value = {
            "node": {"id": "192.168.1.1"},
            "label": ["IP"]
        }
        
        mock_result.single.return_value = mock_single()
        mock_session.run.return_value = mock_result
        
        with patch("repositories.entities.driver.session") as mock_driver:
            mock_driver.return_value.__aenter__.return_value = mock_session
            
            result = await post_entity("phishing", "IP", "192.168.1.1")
            
            # Verify the MERGE query was executed
            assert mock_session.run.called
            # Check that MERGE keyword is in the query
            call_args = mock_session.run.call_args
            assert "MERGE" in call_args[0][0]


class TestGetEntityNotFound:
    """Test repositories/entities.py get_entity with non-existent entities"""

    @pytest.mark.asyncio
    async def test_get_entity_not_found(self):
        """Test lookup failure for non-existent entity"""
        # Mock the driver session returning None
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        
        # When entity not found, single() returns None
        mock_result.single.return_value = None
        mock_session.run.return_value = mock_result
        
        with patch("repositories.entities.driver.session") as mock_driver:
            mock_driver.return_value.__aenter__.return_value = mock_session
            
            result = await get_entity("phishing", "IP", "999.999.999.999")
            
            # Result should be None
            assert result is None

    @pytest.mark.asyncio
    async def test_get_entity_found_with_relationships(self):
        """Test successful lookup of existing entity with relationships"""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        
        mock_entity = {
            "entity": {"value": "192.168.1.1"},
            "label": ["IP"],
            "first_seen": "2024-01-01T00:00:00Z",
            "last_seen": "2024-01-31T23:59:59Z",
            "count": 5
        }
        
        mock_result.single.return_value = mock_entity
        mock_session.run.return_value = mock_result
        
        with patch("repositories.entities.driver.session") as mock_driver:
            mock_driver.return_value.__aenter__.return_value = mock_session
            
            result = await get_entity("phishing", "IP", "192.168.1.1")
            
            # Result should have the entity data
            assert result == mock_entity
