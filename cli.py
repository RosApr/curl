#!/usr/bin/env python3
import sys
import json
import argparse
from curl_parser import parse_curl


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='解析cURL命令并输出结构化数据')
    parser.add_argument('curl_command', nargs='?', help='要解析的cURL命令')
    parser.add_argument('-f', '--file', help='包含cURL命令的文件路径')
    parser.add_argument('-o', '--output', help='输出结果的文件路径')
    parser.add_argument('-j', '--json', action='store_true', help='以JSON格式输出结果')

    args = parser.parse_args()

    # 获取cURL命令
    curl_command = None

    if args.curl_command:
        curl_command = args.curl_command
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                curl_command = f.read().strip()
        except Exception as e:
            print(f"读取文件出错: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():  # 检查是否有管道输入
        curl_command = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    result = parse_curl(curl_command)

    if not result:
        print("解析cURL命令失败", file=sys.stderr)
        sys.exit(1)

    if args.json:
        # 将结果转换为可序列化的字典
        output_dict = {
            'parsed_data': {
                'url': result.parsed_data.url,
                'request': result.parsed_data.request
            },
            'unresolved_data': result.unresolved_data
        }

        # 添加可选字段
        if result.parsed_data.params:
            output_dict['parsed_data']['params'] = result.parsed_data.params
        if result.parsed_data.headers:
            output_dict['parsed_data']['headers'] = result.parsed_data.headers
        if result.parsed_data.cookies:
            output_dict['parsed_data']['cookies'] = result.parsed_data.cookies
        if result.parsed_data.data:
            output_dict['parsed_data']['data'] = result.parsed_data.data

        output = json.dumps(output_dict, ensure_ascii=False, indent=2)
    else:
        output = f"URL: {result.parsed_data.url}\n"
        output += f"请求方法: {result.parsed_data.request}\n"

        if result.parsed_data.params:
            output += "\n查询参数:\n"
            for key, value in result.parsed_data.params.items():
                output += f"  {key}: {value}\n"

        if result.parsed_data.headers:
            output += "\n请求头:\n"
            for key, value in result.parsed_data.headers.items():
                output += f"  {key}: {value}\n"

        if result.parsed_data.cookies:
            output += "\nCookies:\n"
            for key, value in result.parsed_data.cookies.items():
                output += f"  {key}: {value}\n"

        if result.parsed_data.data:
            output += f"\n请求数据:\n{result.parsed_data.data}\n"

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        except Exception as e:
            print(f"写入文件出错: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

if __name__ == "__main__":
    main()
