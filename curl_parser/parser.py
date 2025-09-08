#!/usr/bin/env python3

import re
import shlex
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs, urlunparse
from dataclasses import dataclass, asdict

@dataclass
class ParsedCurlData:
    url: str
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    cookies: Optional[Dict[str, Any]] = None
    data: Optional[str] = None
    request: str = "GET"

    def to_dict(self, exclude_none = True) -> Dict[str, Any]:
        d = asdict(self)
        if exclude_none:
            return {k: v for k, v in d.items() if v is not None}
        return d


@dataclass
class CurlParseResult:
    parsed_data: ParsedCurlData
    unresolved_data: Dict[str, Any]
    def to_dict(self, exclude_none = True) -> Dict[str, Any]:
        return {
            "parsed_data": self.parsed_data.to_dict(exclude_none),
            "unresolved_data": self.unresolved_data if not exclude_none else {k: v for k, v in self.unresolved_data.items() if v is not None}
        }

"""
cURL 命令解析器
"""

URL_PATTERN = re.compile(
    r'^https?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)

CN_MAPPING = {
    "request": "请求方法",
    "headers": "请求头",
    "head": "仅返回头信息",
    "data": "请求体数据",
    "form": "表单数据",
    "user": "用户名和密码",
    "location": "自动重定向",
    "verify": "忽略SSL证书验证",
    "cookies": "请求cookie",
    "cookie-jar": "保存响应cookie",
    "verbose": "显示详细信息",
    "output": "输出文件",
    "url": "请求地址",
    "params": "请求参数"
}

resolve_curl_options = {
    "request": ["--request", "-X"],
    "headers": ["--header", "-H"],
    "head": ["--head", "-l"],
    "data": ["--data", "-d", '--data-ascii', '--data-raw'],
    "form": ["--form", "-F"],
    "user": ["--user", "-u"],
    "location": ["--location", "-L"],
    "verify": ["--insecure", "-k"],
    "cookies": ["--cookie", "-b"],
    "cookie-jar": ["--cookie-jar", "-c"],
    "verbose": ["--verbose", "-v"],
    "output": ["--output", "-o"],
}

def parse_curl(curl_command: str) -> Optional[CurlParseResult]:
    try:
        grouped_curl_options = group_curl_by_options(curl_command)
        if isinstance(grouped_curl_options, Exception):
            raise grouped_curl_options
        mixed_curl_options = mixin_curl_options(grouped_curl_options)
        parse_result = fill_parse_data(mixed_curl_options)
        return CurlParseResult(parsed_data = ParsedCurlData(**parse_result['parsed_data']), unresolved_data = parse_result['unresolved_data'])
    except Exception:
        raise Exception


def format_curl_options(options: Dict[str, List[str]]) -> Dict[str, str]:
    """
    格式化cURL 选项
    """
    key_dict = {}
    for key, value in options.items():
        for v in value:
            key_dict[v] = key
    return key_dict

curl_key_dict = format_curl_options(resolve_curl_options)

def parse_common(option_list: List[str]) -> Dict[str, str]:
    options = {}
    for option in option_list:
        index = option.find(':')
        if index != -1:
            options[option[:index].strip()] = option[index+1:].strip()
    return options

def parse_cookie(cookie_list:List[str]) -> Dict[str, str]:
    cookie_dict = {}
    cookie_list = list(map(lambda x: x.split(';'), cookie_list))
    flattened_cookie_list = list(filter(lambda x: x != '', [item for sub_list in cookie_list for item in sub_list]))
    for cookie_item in flattened_cookie_list:
        separator_index = cookie_item.find('=')
        cookie_dict[cookie_item[:separator_index].strip()] = cookie_item[separator_index+1:].strip()
    return cookie_dict

def parse_url(url: str) -> Dict[str, str]:
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query) if parsed_url.query else None
    if params:
        for key, value in params.items():
            if len(value) == 1:
                params[key] = value[0]
    url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return {
        "url": url,
        "params": params
    }

def group_curl_by_options(curl_command: str) -> Optional[List[List[str]]]:
    try:
        curl_command = curl_command.strip()
        if curl_command.startswith('curl'):
            curl_command = curl_command[4:].strip()
        tokens = shlex.split(curl_command)
        current_index = 0
        grouped_options = []
        token_length = len(tokens)
        while current_index < token_length:
            token = tokens[current_index]
            if token.startswith('-'):
                grouped_options.append(tokens[current_index:current_index+2])
                current_index += 2
            else:
                grouped_options.append(tokens[current_index:current_index+1])
                current_index += 1
        return grouped_options
    except Exception:
        raise Exception
def mixin_curl_options(curl_options:List[List[str]]) -> Dict[str, List[str]]:
    mixed_options = {}
    for option in curl_options:
        if any(o.startswith('-') for o in option):
            key = None
            values = []
            for o in option:
                if o.startswith('-'):
                    key = curl_key_dict[o]
                else:
                    values.append(o)
            if key in mixed_options:
                mixed_options[key].extend(values)
            else:
                mixed_options[key] = values
        elif is_valid_url(option[0]):
            mixed_options['url'] = option
        else:
            mixed_options[option[0]] = option
    return mixed_options
def fill_parse_data(mixin_options: Dict[str, List[str]]) -> Dict:
    parsed_data = {}
    unresolved_data = {}
    for key, value in mixin_options.items():
        if key == 'url':
            parsed_data.update(parse_url(value[0]))
        elif key == 'cookies':
            parsed_data['cookies'] = parse_cookie(value)
        elif key == 'data':
            parsed_data[key] = {k: v[0] for k, v in parse_qs(value[0]).items()} if value else None
        elif key == 'headers':
            parsed_data[key] = parse_common(value)
        elif key == 'request' and value:
            parsed_data['request'] = value[0]
        else:
            if key not in curl_key_dict:
                unresolved_data[key] = value
            else:
                parsed_data[key] = True
    if "data" in parsed_data and "request" not in parsed_data:
        parsed_data['request'] = 'POST'
    elif "request" not in parsed_data:
        parsed_data['request'] = 'GET'
    return {"parsed_data": parsed_data, "unresolved_data": unresolved_data}

def is_valid_url(url: str) -> bool:
    return bool(re.match(URL_PATTERN, url))

def format_parser_result_to_str(parsed_result: Dict[str, Any]):
    output = ''
    for key, value in parsed_result['parsed_data'].items():
        label = CN_MAPPING[key]
        output += f"{label}:\n"
        if isinstance(value, dict):
            for k, v in value.items():
                output += f"  {k}: {v}\n"
        else:
            output += f"  {value}\n"
    for key, value in parsed_result['unresolved_data'].items():
        output += f"{key}:\n"
        if isinstance(value, dict):
            for k, v in value.items():
                output += f"  {k}: {v}\n"
        else:
            output += f"  {value}\n"
    return output

if __name__ == "__main__":
    sample_curl_command = '''
  curl http://demo.rospar.com"'
    '''
    result = parse_curl(sample_curl_command)
    if result:
        print(f"{format_parser_result_to_str(result.to_dict())}")
