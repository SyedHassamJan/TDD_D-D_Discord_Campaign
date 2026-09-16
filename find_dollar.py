import subprocess

try:
    out = subprocess.check_output(['git', 'log', '-G', r'(\$ =|function \$)', '-p', '-n', '2', 'gm.html'], text=True, errors='ignore')
    print("Found $ definition in gm.html git log:")
    print(out[:1000])
except Exception as e:
    print("Error:", e)

# Also check how $ is defined in earlier git commit of gm.html
try:
    head_rev = subprocess.check_output(['git', 'rev-parse', 'HEAD~1'], text=True).strip()
    content = subprocess.check_output(['git', 'show', f'{head_rev}:gm.html'], text=True, errors='ignore')
    for line in content.splitlines()[:150]:
        if '$' in line or 'getElementById' in line:
            print("Line:", line)
except Exception as e:
    print("Error 2:", e)
