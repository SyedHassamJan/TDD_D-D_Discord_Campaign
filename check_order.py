import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all script openings and first 60 chars of each
matches = list(re.finditer(r'<script([^>]*)>(.*?)</script>', html, re.DOTALL))
print(f"Total scripts: {len(matches)}")
for i, m in enumerate(matches):
    attrs = m.group(1).strip()
    body = m.group(2).strip()[:60].replace('\n', ' ')
    print(f"Script #{i+1}: <script {attrs}> -> {body}...")
