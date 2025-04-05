#!/usr/bin/env python3
"""
Unit tests for NewsAPI tools.
"""
import unittest
import os
from unittest.mock import patch, MagicMock

from app.tools.news_api.service import NewsAPIService, get_service
from app.tools.news_api.tools import (
    news_top_headlines,
    news_search,
    news_sources
)


class TestNewsAPIService(unittest.TestCase):
    """Test the NewsAPI service class"""

    def setUp(self):
        """Set up test environment"""
        # Mock the NewsApiClient
        self.patcher = patch('newsapi.NewsApiClient')
        self.mock_client_class = self.patcher.start()
        self.mock_client = MagicMock()
        self.mock_client_class.return_value = self.mock_client

        # Set environment variable for testing
        os.environ['NEWS_API_KEY'] = 'test_api_key'

    def tearDown(self):
        """Clean up after tests"""
        self.patcher.stop()
        if 'NEWS_API_KEY' in os.environ:
            del os.environ['NEWS_API_KEY']

    def test_initialization(self):
        """Test service initialization"""
        service = NewsAPIService()
        result = service.initialize()

        self.assertTrue(result)
        self.assertTrue(service.initialized)
        self.mock_client_class.assert_called_once_with(api_key='test_api_key')

    def test_initialization_with_custom_key(self):
        """Test initialization with custom API key"""
        service = NewsAPIService(api_key='custom_key')
        result = service.initialize()

        self.assertTrue(result)
        self.assertEqual(service.api_key, 'custom_key')
        self.mock_client_class.assert_called_once_with(api_key='custom_key')

    def test_get_top_headlines(self):
        """Test getting top headlines"""
        service = NewsAPIService()
        service.initialize()

        # Mock response
        self.mock_client.get_top_headlines.return_value = {
            'status': 'ok',
            'totalResults': 2,
            'articles': [
                {
                    'source': {'id': 'test', 'name': 'Test Source'},
                    'title': 'Test Title 1',
                    'description': 'Test Description 1',
                    'url': 'http://test.com/1',
                    'publishedAt': '2023-01-01T12:00:00Z'
                },
                {
                    'source': {'id': 'test2', 'name': 'Test Source 2'},
                    'title': 'Test Title 2',
                    'description': 'Test Description 2',
                    'url': 'http://test.com/2',
                    'publishedAt': '2023-01-02T12:00:00Z'
                }
            ]
        }

        result = service.get_top_headlines(country='us')

        self.mock_client.get_top_headlines.assert_called_once_with(
            country='us')
        self.assertEqual(result['totalResults'], 2)
        self.assertEqual(len(result['articles']), 2)

    def test_get_everything(self):
        """Test searching for articles"""
        service = NewsAPIService()
        service.initialize()

        # Mock response
        self.mock_client.get_everything.return_value = {
            'status': 'ok',
            'totalResults': 1,
            'articles': [
                {
                    'source': {'id': 'test', 'name': 'Test Source'},
                    'title': 'Test Title 1',
                    'description': 'Test Description 1',
                    'url': 'http://test.com/1',
                    'publishedAt': '2023-01-01T12:00:00Z'
                }
            ]
        }

        result = service.get_everything(q='test')

        self.mock_client.get_everything.assert_called_once_with(q='test')
        self.assertEqual(result['totalResults'], 1)
        self.assertEqual(len(result['articles']), 1)

    def test_get_sources(self):
        """Test getting sources"""
        service = NewsAPIService()
        service.initialize()

        # Mock response
        self.mock_client.get_sources.return_value = {
            'status': 'ok',
            'sources': [
                {
                    'id': 'test',
                    'name': 'Test Source',
                    'description': 'Test Description',
                    'url': 'http://test.com',
                    'category': 'general',
                    'language': 'en',
                    'country': 'us'
                }
            ]
        }

        result = service.get_sources(category='general')

        self.mock_client.get_sources.assert_called_once_with(
            category='general')
        self.assertEqual(len(result['sources']), 1)

    def test_format_articles(self):
        """Test article formatting"""
        service = NewsAPIService()

        articles = [
            {
                'source': {'id': 'test', 'name': 'Test Source'},
                'title': 'Test Title',
                'description': 'Test Description',
                'url': 'http://test.com',
                'publishedAt': '2023-01-01T12:00:00Z'
            }
        ]

        formatted = service.format_articles(articles)

        self.assertIn('Source: Test Source', formatted)
        self.assertIn('Title: Test Title', formatted)
        self.assertIn('Description: Test Description', formatted)
        self.assertIn('URL: http://test.com', formatted)

    def test_error_handling(self):
        """Test error handling"""
        service = NewsAPIService()
        service.initialize()

        # Mock exception
        self.mock_client.get_top_headlines.side_effect = Exception(
            'Test error')

        result = service.get_top_headlines(country='us')

        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Test error')


class TestNewsAPITools(unittest.TestCase):
    """Test the NewsAPI tool functions"""

    def setUp(self):
        """Set up test environment"""
        # Mock the get_service function
        self.patcher = patch('app.tools.news_api.tools.get_service')
        self.mock_get_service = self.patcher.start()
        self.mock_service = MagicMock()
        self.mock_get_service.return_value = self.mock_service

    def tearDown(self):
        """Clean up after tests"""
        self.patcher.stop()

    async def test_news_top_headlines(self):
        """Test news_top_headlines tool"""
        # Mock service response
        self.mock_service.get_top_headlines.return_value = {
            'totalResults': 1,
            'articles': [
                {
                    'source': {'id': 'test', 'name': 'Test Source'},
                    'title': 'Test Title',
                    'description': 'Test Description',
                    'url': 'http://test.com',
                    'publishedAt': '2023-01-01T12:00:00Z'
                }
            ]
        }

        # Mock format_articles
        self.mock_service.format_articles.return_value = "Formatted articles"

        result = await news_top_headlines(country='us')

        self.mock_service.get_top_headlines.assert_called_once_with(
            country='us', page=1, page_size=5)
        self.mock_service.format_articles.assert_called_once()
        self.assertIn('Found 1 articles', result)
        self.assertIn('Formatted articles', result)

    async def test_news_search(self):
        """Test news_search tool"""
        # Mock service response
        self.mock_service.get_everything.return_value = {
            'totalResults': 2,
            'articles': [
                {
                    'source': {'id': 'test', 'name': 'Test Source'},
                    'title': 'Test Title 1',
                    'description': 'Test Description 1',
                    'url': 'http://test.com/1',
                    'publishedAt': '2023-01-01T12:00:00Z'
                },
                {
                    'source': {'id': 'test2', 'name': 'Test Source 2'},
                    'title': 'Test Title 2',
                    'description': 'Test Description 2',
                    'url': 'http://test.com/2',
                    'publishedAt': '2023-01-02T12:00:00Z'
                }
            ]
        }

        # Mock format_articles
        self.mock_service.format_articles.return_value = "Formatted articles"

        result = await news_search(q='test')

        self.mock_service.get_everything.assert_called_once()
        self.mock_service.format_articles.assert_called_once()
        self.assertIn('Found 2 articles', result)
        self.assertIn('Formatted articles', result)

    async def test_news_sources(self):
        """Test news_sources tool"""
        # Mock service response
        self.mock_service.get_sources.return_value = {
            'sources': [
                {
                    'id': 'test',
                    'name': 'Test Source',
                    'description': 'Test Description',
                    'url': 'http://test.com',
                    'category': 'general',
                    'language': 'en',
                    'country': 'us'
                }
            ]
        }

        result = await news_sources(category='general')

        self.mock_service.get_sources.assert_called_once_with(
            category='general')
        self.assertIn('Found 1 sources', result)
        self.assertIn('ID: test', result)
        self.assertIn('Name: Test Source', result)


if __name__ == '__main__':
    unittest.main()
