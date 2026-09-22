with open('assets/codex_icons.js', 'r', encoding='utf-8') as f:
    text = f.read()

test_keys = [
    'gondor_gondor_sword_militia', 'gondor_aor_ringlovale_men_at_arms', 'gondor_aor_pelagir_marines', 'gondor_aor_ithilien_rangers',
    'mordor_mordor_orc_warband', 'mordor_nazgul', 'mordor_gothmog',
    'lostladen_tribes_aor_corsair_marines', 'lostladen_tribes_camel_riders', 'lostladen_tribes_aor_mahud_spearmen'
]

for k in test_keys:
    print(f"{k} in codex_icons: {k in text}")
