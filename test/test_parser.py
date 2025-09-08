
import unittest
import os
from curl_parser import parse_curl


class TestCurlParser(unittest.TestCase):
    """cURL 解析器测试用例"""

    def test_basic_get_request(self):
        """测试基本的 GET 请求"""
        curl_command = 'curl https://example.com'
        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'https://example.com')
        self.assertEqual(result.parsed_data.request, 'GET')
        self.assertEqual(result.parsed_data.headers, None)

    def test_post_request_with_data(self):
        """测试带数据的 POST 请求"""
        curl_command = 'curl -X POST -d "key=value" https://example.com'
        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'https://example.com')
        self.assertEqual(result.parsed_data.request, 'POST')
        self.assertEqual(result.parsed_data.data, {"key": "value"})

    def test_get_request_with_headers(self):
        """测试带请求头的 GET 请求"""
        curl_command = 'curl -H "Accept: application/json" -H "User-Agent: test" https://example.com'
        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'https://example.com')
        self.assertEqual(result.parsed_data.request, 'GET')
        expected_headers = {
            "Accept": "application/json",
            "User-Agent": "test"
        }
        self.assertEqual(result.parsed_data.headers, expected_headers)

    def test_request_with_cookies(self):
        """测试带 Cookie 的请求"""
        curl_command = 'curl -b "session=abc123; locale=zh-CN" https://example.com'
        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'https://example.com')
        expected_cookies = {
            "session": "abc123",
            "locale": "zh-CN"
        }
        self.assertEqual(result.parsed_data.cookies, expected_cookies)

    def test_url_with_query_parameters(self):
        """测试带查询参数的 URL"""
        curl_command = 'curl "https://example.com/api?name=test&id=123"'
        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'https://example.com/api')
        expected_params = {"name": "test", "id": "123"}
        self.assertEqual(result.parsed_data.params, expected_params)

    def test_post_with_form_data(self):
        """测试 POST 请求带表单数据"""
        curl_command = 'curl -d "username=admin&password=secret" https://example.com/login'
        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'https://example.com/login')
        self.assertEqual(result.parsed_data.request, 'POST')
        expected_data = {"username": "admin", "password": "secret"}
        self.assertEqual(result.parsed_data.data, expected_data)

    def test_complex_curl_command_from_file(self):
        """测试复杂的 cURL 命令（从文件读取）"""
        # 检查文件是否存在
        if not os.path.exists('test_curl.txt'):
            self.skipTest("test_curl.txt 文件不存在")

        with open('test_curl.txt', 'r', encoding='utf-8') as f:
            curl_command = f.read().strip()

        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'https://github.com/notifications/indicator')
        self.assertEqual(result.parsed_data.request, 'GET')

        # 检查是否包含一些关键的请求头
        self.assertIn('accept', result.parsed_data.headers)
        self.assertIn('user-agent', result.parsed_data.headers)

        # 检查 Cookie
        self.assertIsNone(result.parsed_data.cookies)

    def test_invalid_curl_command(self):
        """测试无效的 cURL 命令"""
        invalid_command = 'invalid command'

        with self.assertRaises(Exception):
            parse_curl(invalid_command)

    def test_empty_curl_command(self):
        """测试空的 cURL 命令"""
        empty_command = ''

        with self.assertRaises(Exception):
            parse_curl(empty_command)

    def test_curl_with_only_url(self):
        """测试只有 URL 的 cURL 命令"""
        curl_command = 'curl https://api.example.com'
        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'https://api.example.com')
        self.assertEqual(result.parsed_data.request, 'GET')
        self.assertEqual(result.parsed_data.headers, None)
        self.assertIsNone(result.parsed_data.data)

    def test_localhost_url(self):
        """测试本地地址"""
        curl_command = 'curl http://localhost:8080/api'
        result = parse_curl(curl_command)

        self.assertIsNotNone(result)
        self.assertEqual(result.parsed_data.url, 'http://localhost:8080/api')
        self.assertEqual(result.parsed_data.request, 'GET')

    def setUp(self):
        """每个测试用例运行前的设置"""
        pass

    def tearDown(self):
        """每个测试用例运行后的清理"""
        pass

    @classmethod
    def setUpClass(cls):
        """所有测试用例运行前的设置"""
        print("开始运行 cURL 解析器测试")

    @classmethod
    def tearDownClass(cls):
        """所有测试用例运行后的清理"""
        print("cURL 解析器测试完成")


if __name__ == '__main__':
    unittest.main()