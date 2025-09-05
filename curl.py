import re
import argparse
import shlex
from typing import Dict, List, Any, Optional, Tuple, Union
from urllib.parse import urlparse, parse_qs, urlunparse

"""
cURL 命令解析器
"""
fetch_unresolved_issue_curl = ''' 
curl 'http://192.168.30.233:9000/api/issues/search?componentKeys=erdc-mpm&s=FILE_LINE&resolved=false&types=CODE_SMELL&ps=100&facets=owaspTop10%2CsansTop25%2Cseverities%2CsonarsourceSecurity%2Ctypes&additionalFields=_all&timeZone=Asia%2FShanghai' \
  -H 'Accept: application/json' \
  -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -b 'JSESSIONID.a00803dc=node01krvdwldm6r4gsknfwnl8ghte168.node0; OAUTHSTATE=c9d5187d93f46dbac9986247c8bc679b6ac74b6554aaf618e58c32ea65760311; XSRF-TOKEN=9fjvgao16g98t1ugmfjmuk1dk0; JSESSIONID.65b26541=node01sm1a1rwocuresbz8k0gnbpsh40.node0; JWT-SESSION=eyJhbGciOiJIUzI1NiJ9.eyJsYXN0UmVmcmVzaFRpbWUiOjE3NTY4ODA5NTA3NDksInhzcmZUb2tlbiI6IjlmanZnYW8xNmc5OHQxdWdtZmptdWsxZGswIiwianRpIjoiQVprTm9vTzNBcjNCNnZHQnRySDkiLCJzdWIiOiJBWlJLSndyRFdrQ0VSRWgtem5sTCIsImlhdCI6MTc1Njg3MDM3OCwiZXhwIjoxNzU3MTQwMTUwfQ.v1Cwkw0g-4XmmHpg27YNXc1F5Mrf_VLGZmANIgzqRCI' \
  -H 'Pragma: no-cache' \
  -H 'Referer: http://192.168.30.233:9000/project/issues?id=erdc-mpm&resolved=false&sinceLeakPeriod=false&types=CODE_SMELL' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0' \
  -H 'X-XSRF-TOKEN: 9fjvgao16g98t1ugmfjmuk1dk0' \
  --insecure
  '''

curl_options = {
    "request": ["--request", "-X"],
    "headers": ["--header", "-H"],
    "head": ["--head", "-l"],
    "data": ["--data", "-d", '--data-ascii', '--data-raw'],
    "form": ["--request", "-F"],
    "user": ["--user", "-u"],
    "location": ["--location", "-L"],
    "verify": ["--insecure", "-k"],
    "cookies": ["--cookie", "-b"],
    "cookie-jar": ["--cookie-jar", "-c"],
    "verbose": ["--verbose", "-v"],
    "output": ["--output", "-o"],
}
formatted_curl_options = {}
for key, value in curl_options.items():
    for v in value:
        formatted_curl_options[v] = key

def parse_curl(curl_command: str) -> bool:
    default_data = {
        "request": "GET",
        "url": None,
        "headers": None,
        "data": None,
        "files": None,
        "params": None,
        "cookies": None,
        "auth": None,
        "json_data": None,
        "verify": False,
        "timeout": None,
        "proxies": None,
        "allow_redirects": None
    }
    
    try:
        grouped_curl_options = group_curl_by_options(curl_command)
        if isinstance(grouped_curl_options, Exception):
            raise grouped_curl_options
        mixed_curl_options = mixin_curl_options(grouped_curl_options)  
        parsed_data = fill_parse_data(mixed_curl_options, default_data)
        print(parsed_data)
        return True
    except Exception as e:
        print(f"解析cURL 失败: {e}")
        return False
    
def parse_common(option_list:List) -> Dict[str, str]:
    options = {}
    for option in option_list:
        index = option.find(':')
        if index != -1:
            options[option[:index].strip()] = option[index+1:].strip()
    return options

def parse_cookie(cookie_list:List) -> Dict[str, str]:
    cookie = {}
    cookie_list = list(map(lambda x: x.split(';'), cookie_list))
    flatten_cookie_list = list(filter(lambda x: x != '', [item for sub_list in cookie_list for item in sub_list]))
    for c in flatten_cookie_list:
        index = c.find('=')
        cookie[c[:index].strip()] = c[index+1:].strip()
    return cookie

def parse_url(url: str) -> Dict[str, any]:
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

def group_curl_by_options(curl: str) -> Union[List[List[str]], Exception]:
    try:
        curl = curl.strip()
        if curl.startswith('curl'):
            curl = curl[4:].strip()
        tokens = shlex.split(curl)
        i = 0
        tokenLength = len(tokens)
        ret = []
        while(i < tokenLength):
            token = tokens[i]
            j = i + 1
            while(j < tokenLength):
                innerToken = tokens[j]
                if innerToken.startswith('-') and innerToken == token or not innerToken.startswith('-'):
                    j += 1
                else:
                    break
            ret.append(list(set(tokens[i:j])))
            i = j
        return ret
    except Exception as e:
        return e
def mixin_curl_options(curl_options:List[List[str]]) -> List[Tuple[str, List[str]]]:
    ret = {}
    for option in curl_options:
        if any(o.startswith('-') for o in option):
            key = None
            values = []
            for o in option:
                if o.startswith('-'):
                    key = formatted_curl_options[o]
                else:
                    values.append(o)
            if key in ret:
                ret[key].extend(values)
            else:
                ret[key] = values
        else:
            ret['url'] = option
    return ret
def fill_parse_data(mixin_options, default_data) -> Dict:
    parsed_data = {}
    unresolved_data = {}
    for key, value in mixin_options.items():
        if key == 'url':
            parsed_data.update(parse_url(value[0]))
        elif key == 'cookies':
            parsed_data['cookies'] = parse_cookie(value)
        elif len(value) > 0:
            parsed_data[key] = parse_common(value)
        else:
            parsed_data[key] = default_data.get(key, True)
            
    return {"parsed_data":{**default_data, **parsed_data}, "unresolved_data": unresolved_data}
parse_curl(fetch_unresolved_issue_curl)