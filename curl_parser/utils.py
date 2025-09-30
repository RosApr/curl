from typing import List

def extract_curl_commands(file_content: str) -> List[str]:
    """从文件内容中提取所有cURL命令"""
    commands = []
    current_cmd = []
    for line in file_content.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            if current_cmd:
                commands.append(' '.join(current_cmd))
                current_cmd = []
            continue
        if stripped_line.startswith('curl'):
            if current_cmd:
                commands.append(' '.join(current_cmd))
            current_cmd = [stripped_line]
        else:
            current_cmd.append(stripped_line)
    if current_cmd:
        commands.append(' '.join(current_cmd))
    return commands

if __name__ == '__main__':
    with open('./test/test_curl.txt', 'r', encoding='utf-8') as curlFile, \
        open('./test/ret.txt', 'w', encoding='utf-8') as targetFile:
        ret = extract_curl_commands(curlFile.read())
        for cmd in ret:
            targetFile.write(cmd + '\n\n')