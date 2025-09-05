import re
import argparse
import shlex
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs, urlunparse
from dataclasses import dataclass

@dataclass
class ParsedCurlData:
    url: str
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    cookies: Optional[Dict[str, Any]] = None
    data: Optional[str] = str
    request: str = "GET"

@dataclass
class CurlParseResult:
    parsed_data: ParsedCurlData
    unresolved_data: Dict[str, Any]

"""
cURL 命令解析器
"""
sample_curl_command = ''' 
curl 'http://localhost:155/mpm-mix/create?_t=1757053091299_2DaOl' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'App-Name: MPM' \
  -H 'Authorization: 4da1519d-1db1-4aac-8c5b-37a0604270f2' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -b 'locale=zh-CN' \
  -H 'Origin: http://localhost:155' \
  -H 'Pragma: no-cache' \
  -H 'Referer: http://localhost:155/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Tenant-Id: 10000' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0' \
  -H 'User-Language: zh_cn' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'sec-ch-ua: "Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --data-raw '{"className":"erd.cloud.mpm.process.entity.MpmProcess","attrRawList":[{"attrName":"securityLabel","value":"PUBLIC"},{"attrName":"name","value":"1"},{"attrName":"parentVid","value":"VR:erd.cloud.mpm.process.entity.MpmProcess:1963795750197202944"}],"typeReference":"OR:erd.cloud.foundation.type.entity.TypeDefinition:1764838262922731521","folderRef":"OR:erd.cloud.foundation.core.folder.entity.Cabinet:1961628874755514369","containerRef":"OR:erd.cloud.foundation.core.container.entity.ScalableContainer:1961628874721959938"}'
  '''

URL_PATTERN = re.compile(
    r'^https?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)


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

def parse_curl(curl_command: str) -> Optional[CurlParseResult]:
    try:
        grouped_curl_options = group_curl_by_options(curl_command)
        if isinstance(grouped_curl_options, Exception):
            raise grouped_curl_options
        mixed_curl_options = mixin_curl_options(grouped_curl_options)  
        parse_result = fill_parse_data(mixed_curl_options)
        print(parse_result['parsed_data'])
        return CurlParseResult(parsed_data = parse_result['parsed_data'], unresolved_data = parse_result['unresolved_data'])
    except Exception as e:
        print(f"解析cURL 失败: {e}")
        return None
    
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
            next_index = current_index + 1
            while next_index < token_length:
                next_token = tokens[next_index]
                if next_token.startswith('-') and next_token == token or not next_token.startswith('-'):
                    next_index += 1
                else:
                    break
            grouped_options.append(list(set(tokens[current_index:next_index])))
            current_index = next_index
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
            parsed_data[key] = value[0] if value else None
        elif key == 'headers':
            parsed_data[key] = parse_common(value)
        else:
            if key not in curl_key_dict:
                unresolved_data[key] = value
            else:
                parsed_data[key] = True

    if "data" in parsed_data and "request" not in parsed_data:
        parsed_data['request'] = 'POST'
    else:
        parsed_data['request'] = 'GET'
    return {"parsed_data": parsed_data, "unresolved_data": unresolved_data}

def is_valid_url(url: str) -> bool:
    return bool(re.match(URL_PATTERN, url))



parse_curl(sample_curl_command)