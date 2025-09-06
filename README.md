# cURL 命令解析器

一个用于解析cURL命令行并将其转换为结构化数据的Python库。

## 特性

- 🔄 **命令解析**: 解析标准的 cURL 命令并提取关键信息
- 📊 **结构化输出**: 将解析结果转换为结构化的数据格式
- 🌐 **多种输入**: 支持命令行直接输入、文件读取和管道输入
- 📋 **全面支持**: 支持 HTTP 方法、请求头、Cookie、请求体等常见选项
- 🔍 **参数提取**: 自动解析 URL 查询参数和表单数据
- 🛠️ **CLI 工具**: 提供命令行工具，支持 JSON 和文本格式输出

## 支持的 cURL 选项

- `-X, --request`: HTTP 请求方法 (GET, POST, PUT, DELETE 等)
- `-H, --header`: 请求头设置
- `-d, --data`: 请求体数据
- `-b, --cookie`: Cookie 设置
- `-F, --form`: 表单数据
- `-u, --user`: 用户认证
- `-L, --location`: 跟随重定向
- `-k, --insecure`: 忽略 SSL 证书验证
- `-v, --verbose`: 详细输出
- `-o, --output`: 输出到文件


## 安装

```bash
pip install easy-curl-parser
```

## 使用方法

### 命令行工具

```bash
# 直接解析 cURL 命令
python -m curl_parser.cli 'curl -H "Accept: application/json" https://api.example.com'

# 从文件读取 cURL 命令
python -m curl_parser.cli -f curl_command.txt

# 通过管道输入
echo 'curl https://example.com' | python -m curl_parser.cli

# JSON 格式输出
python -m curl_parser.cli -j 'curl https://example.com'

# 输出到文件
python -m curl_parser.cli -o result.txt 'curl https://example.com'
```

### Python API

```python
from curl_parser import parse_curl

# 解析cURL命令
curl_command = "curl 'http://example.com' -H 'Accept: application/json'"
result = parse_curl(curl_command)

# 获取解析后的数据
print(result.parsed_data.url)  # http://example.com
print(result.parsed_data.headers)  # {'Accept': 'application/json'}
```

## 数据结构

`parse_curl` 函数返回 `CurlParseResult` 对象，包含：

- `parsed_data`: 解析后的数据，类型为 `ParsedCurlData`
- `unresolved_data`: 未被解析的数据

`ParsedCurlData` 包含以下字段：

- `url`: 请求URL
- `params`: URL查询参数
- `headers`: 请求头
- `cookies`: Cookie
- `data`: 请求体数据
- `request`: 请求方法 (默认为 "GET")

## 示例

```python
from curl_parser import parse_curl

curl_command = '''
curl 'http://localhost:155/common/sso/login?_t=1757126032510_JG9BY' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8' \
  -b 'locale=und' \
  --data-raw 'username=erdcadmin&password=GaSkDZ2dZOmracDMTMoRy9uqMnxa46FK3OHnE1ppGbuz9clTDWb+nZDVdFqoatPL'
'''

result = parse_curl(curl_command)
print(result.parsed_data.url)  # http://localhost:155/common/sso/login
print(result.parsed_data.params)  # {'_t': '1757126032510_JG9BY'}
print(result.parsed_data.request)  # POST
```

## 开发

### 安装开发依赖

```bash
git clone https://github.com/RosApr/curl-parser.git
cd curl-parser
pip install -e .
```

### 运行测试

```bash
python ./test/test_parser.py
```

## 许可证

MIT

## 贡献

欢迎提交问题和Pull Request！