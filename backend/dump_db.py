import sqlite3, json, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('wen-sheng-v2.sqlite3')
c = conn.cursor()
c.execute('SELECT id, character, payload FROM analysis_sessions ORDER BY id')
rows = c.fetchall()

seen_chars = set()

for row in rows:
    session_id, character, payload_str = row
    print(f'- ID: {session_id} | 汉字: 【{character}】')
    if character not in seen_chars:
        seen_chars.add(character)
        payload = json.loads(payload_str)
        analysis = payload.get('analysis', {})
        print(f'  > 来源: {payload.get("analysisProvider")} ({payload.get("analysisSource")})')
        print(f'  > 验证: {payload.get("validated")}')
        print(f'  > 数据结构包含字段:')
        for key, value in analysis.items():
            if isinstance(value, list):
                print(f'    - `{key}`: Array (长度 {len(value)})')
            elif isinstance(value, dict):
                print(f'    - `{key}`: Object (键: {list(value.keys())})')
            else:
                val_str = str(value).replace('\n', ' ')
                if len(val_str) > 30: val_str = val_str[:27] + '...'
                print(f'    - `{key}`: {type(value).__name__} = "{val_str}"')
    print('')
conn.close()
