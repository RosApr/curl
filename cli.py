#!/usr/bin/env python3
import sys
import json
import argparse
from dataclasses import asdict
from curl_parser import parse_curl, CN_MAPPING

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
                curl_command = f.read().encode('utf-8').decode('unicode_escape').strip()
        except Exception as e:
            print(f"读取文件失败: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        curl_command = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    parse_result = parse_curl(curl_command)

    if not parse_result:
        print("解析cURL命令失败", file=sys.stderr)
        sys.exit(1)
    output = ''
    output_dict = {
        'parsed_data': asdict(parse_result.parsed_data),
        'unresolved_data': parse_result.unresolved_data
    }

    if args.json:
        output = json.dumps(output_dict, ensure_ascii=False, indent=2)
    else:
        for key, value in output_dict['parsed_data'].items():
            label = CN_MAPPING[key]
            output += f"{label}:\n"
            if isinstance(value, dict):
                for k, v in value.items():
                    output += f"  {k}: {v}\n"
            else:
                output += f"  {value}\n"
        for key, value in output_dict['unresolved_data'].items():
            output += f"{key}:\n"
            if isinstance(value, dict):
                for k, v in value.items():
                    output += f"  {k}: {v}\n"
            else:
                output += f"  {value}\n"

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
