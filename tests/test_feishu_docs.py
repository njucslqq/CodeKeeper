"""Tests for Feishu docs system integration."""

import pytest
from unittest.mock import Mock, patch
from git_deep_analyzer.integrations.docs.feishu import FeishuDocs


class TestFeishuDocs:
    """Test FeishuDocs class."""

    @pytest.fixture
    def feishu_config(self):
        """Sample Feishu configuration."""
        return {
            "api_base": "https://open.feishu.cn/open-apis",
            "user_access_token": "test-token",
            "app_id": "test-app"
        }

    @pytest.fixture
    def feishu_docs(self, feishu_config):
        """Create FeishuDocs instance."""
        return FeishuDocs(feishu_config)

    def test_init_with_config(self, feishu_docs):
        """Given: Feishu config
        When: FeishuDocs is created
        Then: Config is stored correctly
        """
        assert feishu_docs.api_base == "https://open.feishu.cn/open-apis"
        assert feishu_docs.user_access_token == "test-token"

    @patch('requests.Session')
    def test_connect_success(self, mock_session, feishu_config):
        """Given: Feishu config
        When: connect() is called with valid token
        Then: Returns True
        """
        # Given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response

        docs = FeishuDocs(feishu_config)

        # When
        result = docs.connect()

        # Then
        assert result is True

    @patch('requests.Session')
    def test_fetch_documents(self, mock_session, feishu_docs):
        """Given: Feishu docs instance
        When: fetch_documents() is called
        Then: Returns list of documents
        """
        # Given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "has_more": False,
                "items": [
                    {
                        "node_token": "token1",
                        "title": "Test Document",
                        "create_time": 1704067200000,
                        "update_time": 1704153600000,
                        "creator": {"open_id": "ou_123"},
                        "type": "doc"
                    }
                ]
            }
        }
        mock_session.return_value.post.return_value = mock_response

        # When
        docs = feishu_docs.fetch_documents(space_id="space123")

        # Then
        assert len(docs) == 1
        assert docs[0].title == "Test Document"

    @patch('requests.Session')
    def test_fetch_document_detail(self, mock_session, feishu_docs):
        """Given: Document token
        When: fetch_document_detail() is called
        Then: Returns document with content blocks
        """
        # Given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "node_token": "token1",
                "title": "Test Document",
                "document": {
                    "blocks": [
                        {
                            "block_id": 1,
                            "block_type": 1,
                            "text": {
                                "elements": [
                                    {
                                        "text_run": {
                                            "content": "Test content"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        mock_session.return_value.post.return_value = mock_response

        # When
        doc = feishu_docs.fetch_document_detail("token1")

        # Then
        assert doc.title == "Test Document"
        assert doc.content is not None

    @patch('requests.Session')
    def test_fetch_documents_by_type(self, mock_session, feishu_docs):
        """Given: Feishu docs instance
        When: fetch_documents() is called with type filter
        Then: Returns documents of specified type only
        """
        # Given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "has_more": False,
                "items": [
                    {
                        "node_token": "token1",
                        "title": "Test Doc",
                        "type": "doc"
                    },
                    {
                        "node_token": "token2",
                        "title": "Test Sheet",
                        "type": "sheet"
                    }
                ]
            }
        }
        mock_session.return_value.post.return_value = mock_response

        # When
        docs = feishu_docs.fetch_documents(space_id="space123", doc_type="doc")

        # Then
        assert len(docs) == 1
        assert docs[0].type == "doc"
