#!/usr/bin/env python3
"""
Test Script for Task 32: Web Search Processing
Location: services/aiml-orchestration/tests/test_task32_web_processing.py

Complete test suite for all Task 32 components:
- WebResultProcessor
- ResultParser  
- ContentExtractor
- ResultValidator
- MetadataEnricher
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import Task 32 components
from src.search.web_result_processor import WebResultProcessor, ProcessedWebResult
from src.search.result_parser import ResultParser
from src.search.content_extractor import ContentExtractor
from src.search.result_validator import ResultValidator
from src.search.metadata_enricher import MetadataEnricher

class Task32TestSuite:
    """Complete test suite for Task 32 web search processing components"""
    
    def __init__(self):
        self.test_results = []
        self.mock_tavily_response = self._create_mock_tavily_response()
        self.test_query = "machine learning algorithms"
    
    def _create_mock_tavily_response(self) -> Dict[str, Any]:
        """Create mock Tavily API response for testing"""
        return {
            "results": [
                {
                    "title": "Introduction to Machine Learning Algorithms",
                    "url": "https://en.wikipedia.org/wiki/Machine_learning",
                    "content": "Machine learning (ML) is a type of artificial intelligence (AI) that allows software applications to become more accurate at predicting outcomes without being explicitly programmed to do so. Machine learning algorithms use historical data as input to predict new output values. The three main types of machine learning are supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled datasets to train algorithms that classify data or predict outcomes accurately. Common supervised learning algorithms include linear regression, logistic regression, decision trees, and neural networks. Unsupervised learning finds hidden patterns or intrinsic structures in input data without labeled examples. Popular unsupervised learning techniques include clustering algorithms like k-means and hierarchical clustering, as well as dimensionality reduction techniques like principal component analysis (PCA). Reinforcement learning is an area of machine learning where an agent learns to make decisions by performing actions in an environment to maximize cumulative reward.",
                    "snippet": "Machine learning algorithms use historical data as input to predict new output values...",
                    "published_date": "2024-01-15",
                    "score": 0.89
                },
                {
                    "title": "Top 10 Machine Learning Algorithms Every Data Scientist Should Know",
                    "url": "https://towardsdatascience.com/top-10-algorithms",
                    "content": "Data science is rapidly evolving, and machine learning algorithms are at the heart of this transformation. Whether you're a beginner or an experienced practitioner, understanding these fundamental algorithms is crucial for success in data science. Here are the top 10 machine learning algorithms: 1. Linear Regression - Used for predicting continuous values. 2. Logistic Regression - Perfect for binary classification problems. 3. Decision Trees - Easy to understand and interpret. 4. Random Forest - An ensemble method that combines multiple decision trees. 5. Support Vector Machines (SVM) - Effective for both classification and regression. 6. K-Means Clustering - Popular unsupervised learning algorithm. 7. Neural Networks - The foundation of deep learning. 8. Naive Bayes - Simple yet powerful probabilistic classifier. 9. K-Nearest Neighbors (KNN) - Instance-based learning algorithm. 10. Gradient Boosting - Another powerful ensemble method. Each algorithm has its strengths and is suitable for different types of problems.",
                    "snippet": "Here are the top 10 machine learning algorithms every data scientist should know...",
                    "published_date": "2024-02-01",
                    "score": 0.85
                },
                {
                    "title": "Machine Learning Algorithm Performance Comparison",
                    "url": "https://example-spam.com/click-here-now",
                    "content": "Click here for amazing deals! Buy now! Limited time offer! Get your free trial today! Download now and save money! Subscribe for exclusive offers!",
                    "snippet": "Click here for amazing deals...",
                    "score": 0.3
                },
                {
                    "title": "Understanding Deep Learning Algorithms",
                    "url": "https://arxiv.org/abs/1234.5678",
                    "content": "Deep learning represents a significant advancement in machine learning, utilizing artificial neural networks with multiple layers to model and understand complex patterns in data. This paper provides a comprehensive overview of deep learning algorithms, including convolutional neural networks (CNNs), recurrent neural networks (RNNs), and transformer architectures. CNNs have revolutionized computer vision tasks by automatically learning spatial hierarchies of features through convolutional layers, pooling layers, and fully connected layers. RNNs, including Long Short-Term Memory (LSTM) and Gated Recurrent Unit (GRU) variants, excel at processing sequential data by maintaining hidden states that capture temporal dependencies. Transformer models, introduced in the seminal 'Attention Is All You Need' paper, have transformed natural language processing through self-attention mechanisms that allow parallel processing of sequences. The training of deep learning models typically involves backpropagation and gradient descent optimization, with techniques like dropout, batch normalization, and regularization used to prevent overfitting and improve generalization.",
                    "snippet": "Deep learning represents a significant advancement in machine learning...",
                    "published_date": "2024-01-20",
                    "score": 0.92
                }
            ],
            "query": "machine learning algorithms",
            "response_time": 0.45
        }
    
    async def run_all_tests(self):
        """Run complete test suite for all Task 32 components"""
        print("🧪 STARTING TASK 32 WEB SEARCH PROCESSING TEST SUITE")
        print("=" * 60)
        
        # Test individual components
        await self.test_result_parser()
        await self.test_content_extractor()
        await self.test_result_validator()
        await self.test_metadata_enricher()
        
        # Test main processor (integration test)
        await self.test_web_result_processor()
        
        # Print summary
        self.print_test_summary()
    
    async def test_result_parser(self):
        """Test ResultParser component"""
        print("\n📋 Testing ResultParser...")
        
        try:
            parser = ResultParser()
            
            # Test parsing Tavily response
            parsed_results = await parser.parse_tavily_response(self.mock_tavily_response)
            
            # Validate results
            assert len(parsed_results) > 0, "No results parsed from Tavily response"
            assert all('title' in result for result in parsed_results), "Missing titles in parsed results"
            assert all('content' in result for result in parsed_results), "Missing content in parsed results"
            assert all('url' in result for result in parsed_results), "Missing URLs in parsed results"
            
            # Test metadata parsing
            metadata = await parser.parse_metadata(parsed_results)
            assert 'total_results' in metadata, "Missing total_results in metadata"
            assert metadata['total_results'] == len(parsed_results), "Incorrect total_results count"
            
            self._log_test_result("ResultParser", True, f"Parsed {len(parsed_results)} results successfully")
            
            # Print sample parsed result
            if parsed_results:
                sample = parsed_results[0]
                print(f"   📄 Sample parsed result:")
                print(f"      Title: {sample.get('title', 'N/A')[:50]}...")
                print(f"      URL: {sample.get('url', 'N/A')}")
                print(f"      Content length: {len(sample.get('content', ''))}")
                print(f"      Score: {sample.get('score', 'N/A')}")
        
        except Exception as e:
            self._log_test_result("ResultParser", False, f"Error: {str(e)}")
    
    async def test_content_extractor(self):
        """Test ContentExtractor component"""
        print("\n🔧 Testing ContentExtractor...")
        
        try:
            extractor = ContentExtractor()
            parser = ResultParser()
            
            # Get parsed results first
            parsed_results = await parser.parse_tavily_response(self.mock_tavily_response)
            
            # Test content extraction
            extracted_results = []
            for result in parsed_results:
                extracted = await extractor.extract_relevant_content(result, self.test_query)
                if extracted:
                    extracted_results.append(extracted)
            
            # Validate extraction
            assert len(extracted_results) > 0, "No content extracted from results"
            
            for result in extracted_results:
                assert 'content' in result, "Missing cleaned content"
                assert 'chunks' in result, "Missing content chunks"
                assert len(result['chunks']) > 0, "No chunks created"
                assert 'extraction_stats' in result, "Missing extraction statistics"
            
            self._log_test_result("ContentExtractor", True, f"Extracted content from {len(extracted_results)} results")
            
            # Print sample extraction stats
            if extracted_results:
                sample = extracted_results[0]
                stats = sample.get('extraction_stats', {})
                print(f"   📊 Sample extraction stats:")
                print(f"      Original length: {stats.get('original_length', 'N/A')}")
                print(f"      Final length: {stats.get('final_length', 'N/A')}")
                print(f"      Chunks created: {sample.get('chunk_count', 'N/A')}")
                print(f"      Reduction ratio: {stats.get('reduction_ratio', 'N/A'):.2%}")
        
        except Exception as e:
            self._log_test_result("ContentExtractor", False, f"Error: {str(e)}")
    
    async def test_result_validator(self):
        """Test ResultValidator component"""
        print("\n✅ Testing ResultValidator...")
        
        try:
            validator = ResultValidator()
            parser = ResultParser()
            extractor = ContentExtractor()
            
            # Get extracted results first
            parsed_results = await parser.parse_tavily_response(self.mock_tavily_response)
            extracted_results = []
            for result in parsed_results:
                extracted = await extractor.extract_relevant_content(result, self.test_query)
                if extracted:
                    extracted_results.append(extracted)
            
            # Test validation
            validated_results = await validator.validate_results(extracted_results, self.test_query)
            
            # Should filter out spam result
            spam_urls = [r.get('url', '') for r in validated_results if 'spam' in r.get('url', '')]
            assert len(spam_urls) == 0, "Spam results not filtered out"
            
            # All remaining results should have validation scores
            for result in validated_results:
                assert 'validation_score' in result, "Missing validation score"
                assert 'final_score' in result, "Missing final score"
            
            self._log_test_result("ResultValidator", True, f"Validated {len(validated_results)} results (filtered {len(extracted_results) - len(validated_results)} low-quality)")
            
            # Print validation stats
            if validated_results:
                avg_validation = sum(r.get('validation_score', 0) for r in validated_results) / len(validated_results)
                avg_final = sum(r.get('final_score', 0) for r in validated_results) / len(validated_results)
                print(f"   📈 Validation stats:")
                print(f"      Average validation score: {avg_validation:.3f}")
                print(f"      Average final score: {avg_final:.3f}")
                print(f"      Results filtered: {len(extracted_results) - len(validated_results)}")
        
        except Exception as e:
            self._log_test_result("ResultValidator", False, f"Error: {str(e)}")
    
    async def test_metadata_enricher(self):
        """Test MetadataEnricher component"""
        print("\n🏷️ Testing MetadataEnricher...")
        
        try:
            enricher = MetadataEnricher()
            parser = ResultParser()
            extractor = ContentExtractor()
            validator = ResultValidator()
            
            # Get validated results first
            parsed_results = await parser.parse_tavily_response(self.mock_tavily_response)
            extracted_results = []
            for result in parsed_results:
                extracted = await extractor.extract_relevant_content(result, self.test_query)
                if extracted:
                    extracted_results.append(extracted)
            
            validated_results = await validator.validate_results(extracted_results, self.test_query)
            
            # Test enrichment
            enriched_results = []
            for result in validated_results:
                enriched = await enricher.enrich_with_metadata(result, self.test_query)
                enriched_results.append(enriched)
            
            # Validate enrichment
            for result in enriched_results:
                assert 'confidence_score' in result, "Missing confidence score"
                assert 'domain_info' in result, "Missing domain info"
                assert 'citations' in result, "Missing citations"
                assert 'source_attribution' in result, "Missing source attribution"
                assert 'metadata' in result, "Missing enhanced metadata"
            
            self._log_test_result("MetadataEnricher", True, f"Enriched {len(enriched_results)} results with metadata")
            
            # Print sample enrichment data
            if enriched_results:
                sample = enriched_results[0]
                print(f"   🔍 Sample enrichment data:")
                print(f"      Confidence score: {sample.get('confidence_score', 'N/A'):.3f}")
                print(f"      Domain authority: {sample.get('domain_info', {}).get('authority_score', 'N/A'):.3f}")
                print(f"      Source type: {sample.get('source_attribution', {}).get('source_type', 'N/A')}")
                print(f"      Content type: {sample.get('source_attribution', {}).get('content_type', 'N/A')}")
                
                # Print citation example
                citations = sample.get('citations', {}).get('formats', {})
                if 'simple' in citations:
                    print(f"      Citation: {citations['simple'][:80]}...")
        
        except Exception as e:
            self._log_test_result("MetadataEnricher", False, f"Error: {str(e)}")
    
    async def test_web_result_processor(self):
        """Test main WebResultProcessor (integration test)"""
        print("\n🔄 Testing WebResultProcessor (Integration Test)...")
        
        try:
            processor = WebResultProcessor()
            
            # Test complete processing pipeline
            processed_results = await processor.process_web_results(
                self.mock_tavily_response, 
                self.test_query
            )
            
            # Validate processed results
            assert len(processed_results) > 0, "No results from complete processing pipeline"
            
            for result in processed_results:
                assert isinstance(result, ProcessedWebResult), "Result not converted to ProcessedWebResult"
                assert result.content, "Missing content in processed result"
                assert result.title, "Missing title in processed result"
                assert result.url, "Missing URL in processed result"
                assert result.confidence_score >= 0, "Invalid confidence score"
                assert len(result.chunks) > 0, "No chunks in processed result"
            
            # Test RAG formatting
            rag_formatted = await processor.format_for_rag(processed_results, self.test_query)
            
            assert 'results' in rag_formatted, "Missing results in RAG format"
            assert 'total_results' in rag_formatted, "Missing total_results in RAG format"
            assert 'avg_confidence' in rag_formatted, "Missing avg_confidence in RAG format"
            assert 'sources' in rag_formatted, "Missing sources in RAG format"
            
            # Test processing stats
            stats = await processor.get_processing_stats(processed_results)
            assert 'total_results' in stats, "Missing total_results in stats"
            assert 'avg_confidence' in stats, "Missing avg_confidence in stats"
            
            self._log_test_result("WebResultProcessor", True, f"Processed {len(processed_results)} results end-to-end")
            
            # Print processing summary
            print(f"   📊 Processing summary:")
            print(f"      Total processed: {len(processed_results)}")
            print(f"      Average confidence: {rag_formatted.get('avg_confidence', 0):.3f}")
            print(f"      Unique sources: {len(rag_formatted.get('sources', []))}")
            print(f"      Total chunks: {sum(len(r.chunks) for r in processed_results)}")
            
            # Print sample ProcessedWebResult
            if processed_results:
                sample = processed_results[0]
                print(f"   📋 Sample ProcessedWebResult:")
                print(f"      Title: {sample.title[:50]}...")
                print(f"      Confidence: {sample.confidence_score:.3f}")
                print(f"      Relevance: {sample.relevance_score:.3f}")
                print(f"      Source type: {sample.source_type}")
                print(f"      Chunks: {len(sample.chunks)}")
        
        except Exception as e:
            self._log_test_result("WebResultProcessor", False, f"Error: {str(e)}")
    
    def _log_test_result(self, component: str, success: bool, message: str):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'component': component,
            'success': success,
            'message': message
        })
        print(f"   {status}: {message}")
    
    def print_test_summary(self):
        """Print complete test summary"""
        print("\n" + "=" * 60)
        print("🏁 TASK 32 TEST SUITE SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['component']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   - {result['component']}: {result['message']}")
        
        print("\n🎯 TASK 32 STATUS:", "✅ ALL TESTS PASSED" if failed_tests == 0 else "❌ SOME TESTS FAILED")

async def main():
    """Main test execution"""
    print("🚀 Starting Task 32 Web Search Processing Test Suite...")
    
    test_suite = Task32TestSuite()
    await test_suite.run_all_tests()
    
    print("\n🏁 Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main())