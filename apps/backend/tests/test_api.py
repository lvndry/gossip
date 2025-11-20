"""Tests for FastAPI endpoints."""


class TestProcessArticlesEndpoint:
    """Test the /process-articles endpoint."""

    def test_process_articles_success(self, test_client, mocker):
        """Test successful article processing."""
        # Mock the process_all_articles function
        mock_articles = [
            mocker.MagicMock(
                title="Test Article",
                url="https://example.com/article",
                source="example.com",
            )
        ]
        mocker.patch("main.process_all_articles", return_value=mock_articles)

        response = test_client.post("/process-articles")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "articles" in data

    def test_process_articles_error(self, test_client, mocker):
        """Test error handling in article processing."""
        mocker.patch("main.process_all_articles", side_effect=Exception("Processing error"))

        response = test_client.post("/process-articles")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "message" in data


class TestGetArticlesEndpoint:
    """Test the /articles endpoint."""

    def test_get_articles_success(self, test_client, mocker):
        """Test successful article retrieval."""
        mock_articles = [
            {
                "title": "Test Article",
                "url": "https://example.com/article",
                "source": "example.com",
                "description": "Test description",
            }
        ]
        mocker.patch("main.get_recent_articles", return_value=mock_articles)

        response = test_client.get("/articles")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["articles"]) == 1
        assert data["articles"][0]["title"] == "Test Article"

    def test_get_articles_with_limit(self, test_client, mocker):
        """Test article retrieval with custom limit."""
        mock_get_recent = mocker.patch("main.get_recent_articles", return_value=[])

        response = test_client.get("/articles?limit=50")

        assert response.status_code == 200
        mock_get_recent.assert_called_once_with(limit=50)

    def test_get_articles_default_limit(self, test_client, mocker):
        """Test article retrieval with default limit."""
        mock_get_recent = mocker.patch("main.get_recent_articles", return_value=[])

        response = test_client.get("/articles")

        assert response.status_code == 200
        mock_get_recent.assert_called_once_with(limit=100)

    def test_get_articles_error(self, test_client, mocker):
        """Test error handling in article retrieval."""
        mocker.patch("main.get_recent_articles", side_effect=Exception("Database error"))

        response = test_client.get("/articles")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["articles"] == []


class TestQueryEndpoint:
    """Test the /query endpoint."""

    def test_query_success(self, test_client, mocker):
        """Test successful query."""
        mock_answer = "This is the answer to your query."
        mocker.patch("main.answer_query", return_value=mock_answer)

        response = test_client.post(
            "/query", json={"query": "What is the latest gossip?", "top_k": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == mock_answer

    def test_query_default_top_k(self, test_client, mocker):
        """Test query with default top_k value."""
        mock_answer_query = mocker.patch("main.answer_query", return_value="Answer")

        response = test_client.post("/query", json={"query": "Test query"})

        assert response.status_code == 200
        mock_answer_query.assert_called_once_with("Test query", top_k=8)

    def test_query_custom_top_k(self, test_client, mocker):
        """Test query with custom top_k value."""
        mock_answer_query = mocker.patch("main.answer_query", return_value="Answer")

        response = test_client.post("/query", json={"query": "Test query", "top_k": 15})

        assert response.status_code == 200
        mock_answer_query.assert_called_once_with("Test query", top_k=15)

    def test_query_missing_query_field(self, test_client, mocker):
        """Test query with missing query field."""
        response = test_client.post("/query", json={"top_k": 5})

        # Should return validation error
        assert response.status_code == 422

    def test_query_invalid_top_k_type(self, test_client, mocker):
        """Test query with invalid top_k type."""
        response = test_client.post("/query", json={"query": "Test", "top_k": "invalid"})

        # Should return validation error
        assert response.status_code == 422

    def test_query_error(self, test_client, mocker):
        """Test error handling in query."""
        mocker.patch("main.answer_query", side_effect=Exception("Query error"))

        response = test_client.post("/query", json={"query": "Test query"})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "message" in data

    def test_query_empty_string(self, test_client, mocker):
        """Test query with empty string."""
        mock_answer_query = mocker.patch("main.answer_query", return_value="Answer")

        response = test_client.post("/query", json={"query": ""})

        # Empty string is valid, should process
        assert response.status_code == 200
        mock_answer_query.assert_called_once()


class TestHealthCheck:
    """Test basic API health."""

    def test_api_starts(self, test_client):
        """Test that the API starts successfully."""
        # If we can create a test client, the API is healthy
        assert test_client is not None

    def test_api_accepts_requests(self, test_client, mocker):
        """Test that the API accepts and processes requests."""
        mocker.patch("main.get_recent_articles", return_value=[])

        response = test_client.get("/articles")

        # Should get a valid response
        assert response.status_code == 200
        assert response.json() is not None
