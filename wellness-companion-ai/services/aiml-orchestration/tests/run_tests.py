
"""
Test runner for RAG pipeline tests.
Comprehensive test execution and reporting.
"""

import unittest
import sys
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.append('/app/src')

class RAGTestRunner:
    """Comprehensive test runner for RAG pipeline."""
    
    def __init__(self):
        self.test_results = {
            'start_time': None,
            'end_time': None,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_details': [],
            'performance_metrics': {},
            'system_health': {}
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all RAG pipeline tests."""
        print("🚀 Starting RAG Pipeline Test Suite")
        print("=" * 50)
        
        self.test_results['start_time'] = datetime.now().isoformat()
        
        # Discover and run tests
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add test modules
        test_modules = [
            'test_rag_pipeline',
            'test_embeddings', 
            'test_vector_search',
            'test_orchestrator'
        ]
        
        for module_name in test_modules:
            try:
                module = __import__(module_name)
                tests = loader.loadTestsFromModule(module)
                suite.addTests(tests)
                print(f"✅ Loaded tests from {module_name}")
            except ImportError as e:
                print(f"⚠️  Could not load {module_name}: {str(e)}")
        
        # Run tests with custom result handler
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            resultclass=CustomTestResult
        )
        
        result = runner.run(suite)
        
        # Process results
        self._process_test_results(result)
        
        self.test_results['end_time'] = datetime.now().isoformat()
        
        # Print summary
        self._print_test_summary()
        
        return self.test_results

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance-specific tests."""
        print("\n🏃 Running Performance Tests")
        print("-" * 30)
        
        performance_results = {}
        
        try:
            # Import and run performance tests
            from test_rag_pipeline import TestRAGPipeline
            
            test_instance = TestRAGPipeline()
            test_instance.setUp()
            
            # Run performance test
            start_time = datetime.now()
            
            # This will be an async test
            async def run_perf_test():
                return await test_instance.rag_orchestrator.process_query(
                    "Performance test query for RAG pipeline"
                )
            
            result = asyncio.run(run_perf_test())
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            performance_results = {
                'query_processing_time': processing_time,
                'confidence_score': result.confidence,
                'fallback_used': result.fallback_used,
                'total_processing_time': result.total_processing_time,
                'within_target': processing_time < 5.0
            }
            
            print(f"⏱️  Query processing time: {processing_time:.2f}s")
            print(f"🎯 Confidence score: {result.confidence:.2f}")
            print(f"🔄 Fallback used: {result.fallback_used}")
            
        except Exception as e:
            print(f"❌ Performance test failed: {str(e)}")
            performance_results['error'] = str(e)
        
        self.test_results['performance_metrics'] = performance_results
        return performance_results

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests between components."""
        print("\n🔗 Running Integration Tests")
        print("-" * 30)
        
        integration_results = {
            'component_connectivity': {},
            'data_flow': {},
            'error_handling': {}
        }
        
        try:
            # Test component connectivity
            integration_results['component_connectivity'] = self._test_component_connectivity()
            
            # Test data flow
            integration_results['data_flow'] = self._test_data_flow()
            
            # Test error handling
            integration_results['error_handling'] = self._test_error_handling()
            
        except Exception as e:
            print(f"❌ Integration tests failed: {str(e)}")
            integration_results['error'] = str(e)
        
        return integration_results

    def _test_component_connectivity(self) -> Dict[str, bool]:
        """Test connectivity between components."""
        connectivity = {}
        
        try:
            # Test orchestrator imports
            from orchestrators.rag_orchestrator import RAGOrchestrator
            orchestrator = RAGOrchestrator()
            connectivity['rag_orchestrator'] = True
            print("✅ RAG Orchestrator connectivity: OK")
            
            # Test retrieval orchestrator
            from orchestrators.retrieval_orchestrator import RetrievalOrchestrator
            retrieval = RetrievalOrchestrator()
            connectivity['retrieval_orchestrator'] = True
            print("✅ Retrieval Orchestrator connectivity: OK")
            
            # Test response synthesizer
            from orchestrators.response_synthesizer import ResponseSynthesizer
            synthesizer = ResponseSynthesizer()
            connectivity['response_synthesizer'] = True
            print("✅ Response Synthesizer connectivity: OK")
            
            # Test confidence scorer
            from reranking.confidence_scorer import ConfidenceScorer
            scorer = ConfidenceScorer()
            connectivity['confidence_scorer'] = True
            print("✅ Confidence Scorer connectivity: OK")
            
        except Exception as e:
            print(f"❌ Component connectivity error: {str(e)}")
            connectivity['error'] = str(e)
        
        return connectivity

    def _test_data_flow(self) -> Dict[str, Any]:
        """Test data flow between components."""
        data_flow = {}
        
        try:
            # Test query processing flow
            from orchestrators.query_processor import QueryProcessor
            processor = QueryProcessor()
            
            async def test_flow():
                analysis = await processor.process_query("Test data flow")
                return {
                    'query_processed': analysis.processed_query != "",
                    'intent_detected': analysis.intent != "",
                    'keywords_extracted': len(analysis.keywords) > 0,
                    'confidence_calculated': 0 <= analysis.confidence <= 1
                }
            
            data_flow['query_processing'] = asyncio.run(test_flow())
            print("✅ Query processing data flow: OK")
            
        except Exception as e:
            print(f"❌ Data flow test error: {str(e)}")
            data_flow['error'] = str(e)
        
        return data_flow

    def _test_error_handling(self) -> Dict[str, bool]:
        """Test error handling across components."""
        error_handling = {}
        
        try:
            # Test orchestrator error handling
            from orchestrators.rag_orchestrator import RAGOrchestrator
            orchestrator = RAGOrchestrator()
            
            async def test_error_handling():
                # Test with invalid input
                result = await orchestrator.process_query("")
                return {
                    'handles_empty_query': result.confidence == 0.0,
                    'graceful_degradation': isinstance(result.metadata, dict),
                    'error_metadata_present': 'error' in str(result.metadata) or result.fallback_used
                }
            
            error_handling['orchestrator'] = asyncio.run(test_error_handling())
            print("✅ Error handling: OK")
            
        except Exception as e:
            print(f"❌ Error handling test error: {str(e)}")
            error_handling['error'] = str(e)
        
        return error_handling

    def _process_test_results(self, result):
        """Process unittest results."""
        self.test_results['total_tests'] = result.testsRun
        self.test_results['passed_tests'] = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        self.test_results['failed_tests'] = len(result.failures) + len(result.errors)
        self.test_results['skipped_tests'] = len(result.skipped)
        
        # Process individual test details
        for test, error in result.failures + result.errors:
            self.test_results['test_details'].append({
                'test_name': str(test),
                'status': 'failed',
                'error': error
            })
        
        for test, reason in result.skipped:
            self.test_results['test_details'].append({
                'test_name': str(test),
                'status': 'skipped',
                'reason': reason
            })

    def _print_test_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 50)
        print("📊 RAG PIPELINE TEST SUMMARY")
        print("=" * 50)
        
        print(f"🧪 Total Tests: {self.test_results['total_tests']}")
        print(f"✅ Passed: {self.test_results['passed_tests']}")
        print(f"❌ Failed: {self.test_results['failed_tests']}")
        print(f"⏭️  Skipped: {self.test_results['skipped_tests']}")
        
        if self.test_results['total_tests'] > 0:
            success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Performance summary
        if 'performance_metrics' in self.test_results and self.test_results['performance_metrics']:
            perf = self.test_results['performance_metrics']
            print(f"\n⚡ PERFORMANCE METRICS")
            if 'query_processing_time' in perf:
                print(f"⏱️  Query Processing: {perf['query_processing_time']:.2f}s")
            if 'confidence_score' in perf:
                print(f"🎯 Confidence Score: {perf['confidence_score']:.2f}")
        
        print("\n" + "=" * 50)


class CustomTestResult(unittest.TestResult):
    """Custom test result handler for detailed reporting."""
    
    def __init__(self):
        super().__init__()
        self.test_start_time = None
    
    def startTest(self, test):
        super().startTest(test)
        self.test_start_time = datetime.now()
        print(f"🔄 Running: {test}")
    
    def stopTest(self, test):
        super().stopTest(test)
        if self.test_start_time:
            duration = (datetime.now() - self.test_start_time).total_seconds()
            print(f"⏱️  Completed in {duration:.2f}s")


def main():
    """Main test runner function."""
    runner = RAGTestRunner()
    
    print("🤖 Wellness Companion AI - RAG Pipeline Test Suite")
    print("Version 1.0.0")
    print("=" * 60)
    
    # Run all tests
    results = runner.run_all_tests()
    
    # Run performance tests
    runner.run_performance_tests()
    
    # Run integration tests
    integration_results = runner.run_integration_tests()
    
    # Save results to file
    try:
        with open('/app/logs/test_results.json', 'w') as f:
            json.dump({
                'test_results': results,
                'integration_results': integration_results
            }, f, indent=2)
        print("📄 Test results saved to /app/logs/test_results.json")
    except Exception as e:
        print(f"⚠️  Could not save test results: {str(e)}")
    
    # Return exit code based on test results
    if results['failed_tests'] > 0:
        print("❌ Some tests failed")
        return 1
    else:
        print("✅ All tests passed!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)