#!/usr/bin/env python3
import sys
import json
import argparse
from .utils import extract_curl_commands
try:
    from .parser import parse_curl, format_parser_result_to_str
except ImportError:
    from parser import parse_curl, format_parser_result_to_str

def main():
    parser = argparse.ArgumentParser(description="解析cURL命令并输出结构化数据")
    parser.add_argument('curl_command', nargs="?", help="要解析的cURL命令")
    parser.add_argument('-f', '--file', help="包含cURL命令的文件路径")
    parser.add_argument('-o', '--output', help="输出结果的文件路径")
    parser.add_argument('-j', '--json', action='store_true', help="以JSON格式输出结果")

    args = parser.parse_args()

    curl_command = None

    if args.curl_command:
        curl_command = args.curl_command
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                curl_command = extract_curl_commands(f.read().encode('utf-8').decode('unicode_escape').strip())
        except Exception as e:
            print(f"读取文件失败: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        curl_command = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)
    if isinstance(curl_command, list):
        parse_result = list(map(lambda x : parse_curl(x), curl_command))
    else:
        parse_result = list(parse_curl(curl_command))

    if not parse_result:
        print("解析cURL命令失败", file=sys.stderr)
        sys.exit(1)
    output_dict = list(map(lambda x : x.to_dict(), parse_result))
    if args.json:
        output = json.dumps(output_dict, ensure_ascii=False, indent=2)
    else:
        output = list(map(lambda x : format_parser_result_to_str(x), output_dict))

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8')as f:
                f.write(output)
        except Exception as e:
            print(f"文件写入失败: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

if __name__ == '__main__':
    main()
