import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.model import extract_text_from_pdf, extract_key_terms, get_json, compare_rental_terms, detect_critical_terms, compare_rental_documents


class TestPDFExtraction(unittest.TestCase):
    
    @patch('fitz.open')
    def test_extract_text_from_pdf(self, mock_open):
        # Setup mock
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample text from PDF"
        mock_doc.__enter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        
        # Call function
        result = extract_text_from_pdf("dummy.pdf")
        
        # Assert
        self.assertEqual(result, "Sample text from PDF")
        mock_open.assert_called_once_with("dummy.pdf")


class TestOpenAIIntegration(unittest.TestCase):
    
    @patch('openai.OpenAI')
    def test_extract_key_terms(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content.strip.return_value = '```json{"Property Address": "123 Main St"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        # Call function
        result = extract_key_terms("Sample lease text")
        
        # Assert
        self.assertEqual(result, '```json{"Property Address": "123 Main St"}')
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('openai.OpenAI')
    def test_compare_rental_terms(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content.strip.return_value = "Comparison results"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Call function
        result = compare_rental_terms("Term 1", "Term 2")
        
        # Assert
        self.assertEqual(result, "Comparison results")
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('openai.OpenAI')
    def test_detect_critical_terms(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content.strip.return_value = "Critical terms detected"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Call function
        result = detect_critical_terms("Sample lease text")
        
        # Assert
        self.assertEqual(result, "Critical terms detected")
        mock_client.chat.completions.create.assert_called_once()


class TestJSONProcessing(unittest.TestCase):
    
    def test_get_json_valid(self):
        # Test with valid JSON
        text = '```json{"key": "value"}```'
        result = get_json(text)
        self.assertEqual(result, {"key": "value"})
    
    def test_get_json_invalid(self):
        # Test with invalid JSON
        text = 'No JSON here'
        result = get_json(text)
        self.assertIsNone(result)


class TestDocumentComparison(unittest.TestCase):
    
    @patch('app.model.extract_text_from_pdf')
    @patch('app.model.extract_key_terms')
    @patch('app.model.compare_rental_terms')
    @patch('app.model.get_json')
    @patch('pandas.DataFrame')
    def test_compare_rental_documents(self, mock_df, mock_get_json, mock_compare, mock_extract_terms, mock_extract_text):
        # Setup mocks
        mock_extract_text.side_effect = ["Text 1", "Text 2"]
        mock_extract_terms.side_effect = ["Terms 1", "Terms 2"]
        mock_compare.return_value = "Comparison"
        mock_get_json.side_effect = [
            {"Property Address": "123 Main St"}, 
            {"Property Address": "456 Oak Ave"},
            {"Property Address": "Different addresses; Inferences: Important"}
        ]
        
        # Mock DataFrame operations
        mock_df_instance = MagicMock()
        mock_df.return_value = mock_df_instance
        mock_df_instance.T = mock_df_instance
        mock_df_instance.to_dict.return_value = {"result": "data"}
        
        # Call function
        result = compare_rental_documents("doc1.pdf", "doc2.pdf")
        
        # Assert
        self.assertEqual(result, {"result": "data"})
        mock_extract_text.assert_any_call("doc1.pdf")
        mock_extract_text.assert_any_call("doc2.pdf")
        mock_extract_terms.assert_any_call("Text 1")
        mock_extract_terms.assert_any_call("Text 2")
        mock_compare.assert_called_once_with("Terms 1", "Terms 2")


if __name__ == '__main__':
    unittest.main()
