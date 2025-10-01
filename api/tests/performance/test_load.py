"""
Performance and load testing for MouseAlerts API
"""
import asyncio
import aiohttp
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List, Dict, Any

class LoadTester:
    """Load testing utility for MouseAlerts API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Make a single API request and measure performance"""
        start_time = time.time()
        
        try:
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    await response.text()
                    status_code = response.status
            elif method == "POST":
                async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                    await response.text()
                    status_code = response.status
            elif method == "PATCH":
                async with session.patch(f"{self.base_url}{endpoint}", json=data) as response:
                    await response.text()
                    status_code = response.status
            elif method == "DELETE":
                async with session.delete(f"{self.base_url}{endpoint}") as response:
                    await response.text()
                    status_code = response.status
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time": response_time,
                "success": 200 <= status_code < 300,
                "timestamp": start_time
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e),
                "timestamp": start_time
            }
    
    async def run_concurrent_requests(self, endpoint: str, method: str = "GET", data: Dict = None, num_requests: int = 100, concurrency: int = 10) -> List[Dict[str, Any]]:
        """Run concurrent requests to test load"""
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(concurrency)
            
            async def limited_request():
                async with semaphore:
                    return await self.make_request(session, endpoint, method, data)
            
            tasks = [limited_request() for _ in range(num_requests)]
            results = await asyncio.gather(*tasks)
            return results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance test results"""
        if not results:
            return {}
        
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        error_count = len(results) - success_count
        
        return {
            "total_requests": len(results),
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": (success_count / len(results)) * 100,
            "avg_response_time": statistics.mean(response_times),
            "median_response_time": statistics.median(response_times),
            "p95_response_time": sorted(response_times)[int(len(response_times) * 0.95)],
            "p99_response_time": sorted(response_times)[int(len(response_times) * 0.99)],
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "requests_per_second": len(results) / max(response_times) if response_times else 0
        }

class TestHealthEndpoint:
    """Test health endpoint performance"""
    
    def test_health_endpoint_load(self):
        """Test health endpoint under load"""
        tester = LoadTester()
        
        async def run_test():
            results = await tester.run_concurrent_requests(
                endpoint="/health",
                method="GET",
                num_requests=1000,
                concurrency=50
            )
            return tester.analyze_results(results)
        
        results = asyncio.run(run_test())
        
        # Assertions
        assert results["success_rate"] >= 99.0, f"Success rate too low: {results['success_rate']}%"
        assert results["avg_response_time"] < 0.1, f"Average response time too high: {results['avg_response_time']}s"
        assert results["p95_response_time"] < 0.2, f"P95 response time too high: {results['p95_response_time']}s"
        
        print(f"Health endpoint load test results: {results}")

class TestAuthEndpoint:
    """Test authentication endpoint performance"""
    
    def test_magic_link_endpoint_load(self):
        """Test magic link endpoint under load"""
        tester = LoadTester()
        
        async def run_test():
            results = await tester.run_concurrent_requests(
                endpoint="/api/auth/magic-link",
                method="POST",
                data={"phone": "+15551234567"},
                num_requests=100,
                concurrency=10
            )
            return tester.analyze_results(results)
        
        results = asyncio.run(run_test())
        
        # Assertions
        assert results["success_rate"] >= 95.0, f"Success rate too low: {results['success_rate']}%"
        assert results["avg_response_time"] < 1.0, f"Average response time too high: {results['avg_response_time']}s"
        
        print(f"Magic link endpoint load test results: {results}")

class TestAlertsEndpoint:
    """Test alerts endpoint performance"""
    
    def test_alerts_endpoint_load(self):
        """Test alerts endpoint under load"""
        tester = LoadTester()
        
        async def run_test():
            results = await tester.run_concurrent_requests(
                endpoint="/api/alerts",
                method="GET",
                num_requests=500,
                concurrency=25
            )
            return tester.analyze_results(results)
        
        results = asyncio.run(run_test())
        
        # Assertions
        assert results["success_rate"] >= 95.0, f"Success rate too low: {results['success_rate']}%"
        assert results["avg_response_time"] < 0.5, f"Average response time too high: {results['avg_response_time']}s"
        
        print(f"Alerts endpoint load test results: {results}")

class TestDatabasePerformance:
    """Test database performance under load"""
    
    def test_database_concurrent_access(self):
        """Test database performance with concurrent access"""
        tester = LoadTester()
        
        async def run_test():
            # Test multiple endpoints that hit the database
            endpoints = [
                "/api/alerts",
                "/api/me",
                "/api/admin/users",
                "/api/admin/analytics/dashboard"
            ]
            
            all_results = []
            for endpoint in endpoints:
                results = await tester.run_concurrent_requests(
                    endpoint=endpoint,
                    method="GET",
                    num_requests=50,
                    concurrency=10
                )
                all_results.extend(results)
            
            return tester.analyze_results(all_results)
        
        results = asyncio.run(run_test())
        
        # Assertions
        assert results["success_rate"] >= 90.0, f"Success rate too low: {results['success_rate']}%"
        assert results["avg_response_time"] < 1.0, f"Average response time too high: {results['avg_response_time']}s"
        
        print(f"Database performance test results: {results}")

class TestMemoryUsage:
    """Test memory usage under load"""
    
    def test_memory_usage_under_load(self):
        """Test memory usage with sustained load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        tester = LoadTester()
        
        async def run_sustained_load():
            # Run sustained load for 60 seconds
            start_time = time.time()
            results = []
            
            while time.time() - start_time < 60:  # 60 seconds
                batch_results = await tester.run_concurrent_requests(
                    endpoint="/health",
                    method="GET",
                    num_requests=100,
                    concurrency=20
                )
                results.extend(batch_results)
                
                # Check memory usage
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                if memory_increase > 100:  # 100MB increase
                    print(f"Warning: Memory usage increased by {memory_increase:.2f}MB")
                
                await asyncio.sleep(1)  # Wait 1 second between batches
            
            return results
        
        results = asyncio.run(run_sustained_load())
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Assertions
        assert memory_increase < 200, f"Memory usage increased too much: {memory_increase:.2f}MB"
        
        print(f"Memory usage test results: {memory_increase:.2f}MB increase")

class TestStressTest:
    """Stress testing for MouseAlerts API"""
    
    def test_stress_test(self):
        """Run stress test with high concurrency"""
        tester = LoadTester()
        
        async def run_stress_test():
            # Test with very high concurrency
            results = await tester.run_concurrent_requests(
                endpoint="/health",
                method="GET",
                num_requests=1000,
                concurrency=100  # Very high concurrency
            )
            return tester.analyze_results(results)
        
        results = asyncio.run(run_stress_test())
        
        # Assertions for stress test
        assert results["success_rate"] >= 80.0, f"Success rate too low under stress: {results['success_rate']}%"
        assert results["avg_response_time"] < 2.0, f"Average response time too high under stress: {results['avg_response_time']}s"
        
        print(f"Stress test results: {results}")

class TestPerformanceRegression:
    """Test for performance regressions"""
    
    def test_performance_baseline(self):
        """Test performance against baseline metrics"""
        tester = LoadTester()
        
        async def run_baseline_test():
            results = await tester.run_concurrent_requests(
                endpoint="/health",
                method="GET",
                num_requests=100,
                concurrency=10
            )
            return tester.analyze_results(results)
        
        results = asyncio.run(run_baseline_test())
        
        # Baseline performance expectations
        baseline_metrics = {
            "success_rate": 99.0,
            "avg_response_time": 0.05,
            "p95_response_time": 0.1
        }
        
        # Check against baseline
        assert results["success_rate"] >= baseline_metrics["success_rate"], \
            f"Success rate below baseline: {results['success_rate']}% < {baseline_metrics['success_rate']}%"
        
        assert results["avg_response_time"] <= baseline_metrics["avg_response_time"] * 2, \
            f"Average response time above baseline: {results['avg_response_time']}s > {baseline_metrics['avg_response_time'] * 2}s"
        
        assert results["p95_response_time"] <= baseline_metrics["p95_response_time"] * 2, \
            f"P95 response time above baseline: {results['p95_response_time']}s > {baseline_metrics['p95_response_time'] * 2}s"
        
        print(f"Performance baseline test results: {results}")

if __name__ == "__main__":
    """Run all performance tests"""
    print("Running MouseAlerts API performance tests...")
    
    # Run all tests
    TestHealthEndpoint().test_health_endpoint_load()
    TestAuthEndpoint().test_magic_link_endpoint_load()
    TestAlertsEndpoint().test_alerts_endpoint_load()
    TestDatabasePerformance().test_database_concurrent_access()
    TestMemoryUsage().test_memory_usage_under_load()
    TestStressTest().test_stress_test()
    TestPerformanceRegression().test_performance_baseline()
    
    print("All performance tests completed!")
