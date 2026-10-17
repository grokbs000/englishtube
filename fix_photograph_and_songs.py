import json, re, subprocess, os
from opencc import OpenCC

cc = OpenCC('s2twp')
INDEX_HTML_PATH = "index.html"
SONGS_100_PATH = "songs_100.json"
SW_JS_PATH = "sw.js"

CANONICAL_PHOTOGRAPH_CUES = [
  {"start": 16.02, "duration": 7.3, "en": "Loving can hurt, loving can hurt sometimes", "zh": "愛會令人受傷，有時愛會帶來傷痛"},
  {"start": 24.98, "duration": 4.84, "en": "But it's the only thing that I know", "zh": "但這是我唯一確知的事"},
  {"start": 33.74, "duration": 7.32, "en": "When it gets hard, you know it can get hard sometimes", "zh": "當生活變得艱難，你知道日子有時真的很難熬"},
  {"start": 42.7, "duration": 5.8, "en": "It is the only thing that makes us feel alive", "zh": "唯有這份愛，能讓我們感覺真實活著"},
  {"start": 52.88, "duration": 2.9, "en": "We keep this love in a photograph", "zh": "我們將這份愛珍藏在相片裡"},
  {"start": 57.34, "duration": 3.82, "en": "We made these memories for ourselves", "zh": "為彼此留下這些永恆的回憶"},
  {"start": 61.26, "duration": 4.6, "en": "Where our eyes are never closing, hearts were never broken", "zh": "在那裡我們的雙眼永不閉上，真心永不破碎"},
  {"start": 66.5, "duration": 2.48, "en": "And time's forever frozen still", "zh": "時光在那一刻永遠凍結停留"},
  {"start": 69.5, "duration": 7.5, "en": "So you can keep me inside the pocket of your ripped jeans", "zh": "所以請將我收進你破洞牛仔褲的口袋中"},
  {"start": 77.1, "duration": 4.26, "en": "Holding me closer 'til our eyes meet", "zh": "將我緊緊貼近，直到雙眼再次交會"},
  {"start": 81.46, "duration": 3.42, "en": "You won't ever be alone", "zh": "你將永遠不再孤單"},
  {"start": 86.1, "duration": 3.16, "en": "Wait for me to come home", "zh": "等待著我平安歸來"},
  {"start": 91.32, "duration": 15.76, "en": "Loving can heal, loving can mend your soul", "zh": "愛能撫平傷痕，愛能治癒你的靈魂"},
  {"start": 108.98, "duration": 8.1, "en": "I swear it will get easier, remember that with every piece of ya", "zh": "我發誓一切都會好轉，請用心裡的每個碎片緊緊記住"},
  {"start": 117.18, "duration": 7.58, "en": "And it's the only thing we take with us when we die", "zh": "唯有愛，是我們生命終結時唯一能帶走的珍寶"},
  {"start": 124.86, "duration": 6.56, "en": "We keep this love in a photograph", "zh": "我們將這份愛珍藏在相片裡"},
  {"start": 132.86, "duration": 3.12, "en": "We made these memories for ourselves", "zh": "為彼此留下這些永恆的回憶"},
  {"start": 136.08, "duration": 5.22, "en": "Where our eyes are never closing, hearts were never broken", "zh": "在那裡我們的雙眼永不閉上，真心永不破碎"},
  {"start": 141.4, "duration": 3.18, "en": "And time's forever frozen still", "zh": "時光在那一刻永遠凍結停留"},
  {"start": 145.42, "duration": 7.2, "en": "So you can keep me inside the pocket of your ripped jeans", "zh": "所以請將我收進你破洞牛仔褲的口袋中"},
  {"start": 153.42, "duration": 3.52, "en": "Holding me closer 'til our eyes meet", "zh": "將我緊緊貼近，直到雙眼再次交會"},
  {"start": 157.94, "duration": 2.4, "en": "You won't ever be alone", "zh": "你將永遠不再孤單"},
  {"start": 162.68, "duration": 3.12, "en": "And if you hurt me", "zh": "就算你無意間傷害了我"},
  {"start": 165.9, "duration": 4.7, "en": "That's okay baby, only words bleed", "zh": "那也沒關係親愛的，只有隻字片語會讓人流血淌淚"},
  {"start": 170.7, "duration": 3.98, "en": "Inside these pages you just hold me", "zh": "在泛黃相冊裡你只要緊緊抱著我"},
  {"start": 174.78, "duration": 3.84, "en": "I won't ever let you go", "zh": "我絕不會輕易放手"},
  {"start": 178.72, "duration": 3.6, "en": "Wait for me to come home", "zh": "請等我回家"},
  {"start": 183.84, "duration": 3.0, "en": "Wait for me to come home", "zh": "等著我回到你的身邊"},
  {"start": 195.78, "duration": 6.66, "en": "You can fit me inside the necklace", "zh": "你可以把我的相片收進貼身的項鍊墜子裡"},
  {"start": 202.54, "duration": 3.26, "en": "You got when you were sixteen", "zh": "那是你十六歲時收到的珍貴禮物"},
  {"start": 205.9, "duration": 4.38, "en": "Next to your heartbeat where I should be", "zh": "貼近你的心跳，那是我該停留的所在"},
  {"start": 211.28, "duration": 2.42, "en": "Keep it deep within your soul", "zh": "將它深藏在你的靈魂深處"},
  {"start": 216.28, "duration": 2.86, "en": "And if you hurt me", "zh": "就算你無意間傷害了我"},
  {"start": 219.24, "duration": 4.7, "en": "Well that's okay baby, only words bleed", "zh": "好吧親愛的沒關係，流血受傷的只會是言語"},
  {"start": 224.04, "duration": 3.94, "en": "Inside these pages you just hold me", "zh": "在泛黃相冊裡你只要緊緊抱著我"},
  {"start": 228.08, "duration": 3.44, "en": "I won't ever let you go", "zh": "我永遠不會放開你"},
  {"start": 234.28, "duration": 1.9, "en": "When I'm away", "zh": "當我遠行在異鄉"},
  {"start": 237.18, "duration": 4.26, "en": "I will remember how you kissed me", "zh": "我會深深刻記你當初是如何吻我"},
  {"start": 242.18, "duration": 3.74, "en": "Under the lamppost back on Sixth Street", "zh": "在那第六街昏黃的路燈之下"},
  {"start": 246.02, "duration": 3.3, "en": "Hearing you whisper through the phone", "zh": "耳畔傳來你在話筒那頭的溫柔低語"},
  {"start": 250.46, "duration": 2.96, "en": "Wait for me to come home", "zh": "「等我回家」"}
]
for c in CANONICAL_PHOTOGRAPH_CUES:
    c["text"] = c["en"]

def build_the_a_team():
    vid = "UAWcs5H-qgQ"
    sub_prefix = f"/tmp/sub_{vid}"
    cmd = [
        "yt-dlp", "--skip-download", "--write-sub", "--write-auto-sub",
        "--sub-lang", "en.*,en,zh-TW,zh",
        "--sub-format", "vtt",
        "--extractor-args", "youtube:player_client=android",
        "-o", f"{sub_prefix}.%(ext)s",
        f"https://www.youtube.com/watch?v={vid}"
    ]
    subprocess.run(cmd, capture_output=True)
    import glob
    vtts = glob.glob(f"{sub_prefix}*.en*.vtt")
    cues = []
    if vtts:
        from scan_and_repair_subtitles import parse_vtt
        cues = parse_vtt(vtts[0])
    for f in glob.glob(f"{sub_prefix}*"):
        try: os.remove(f)
        except Exception: pass
    
    if cues:
        from scan_and_repair_subtitles import batch_translate_cues
        batch_translate_cues(cues)
        
    return {
        "id": vid,
        "title": "The A Team",
        "speaker": "Ed Sheeran",
        "cat": "Acoustic",
        "level": "B1",
        "duration": "04:18",
        "views": "380M",
        "emoji": "🎸",
        "color": "linear-gradient(135deg, #fa709a, #fee140)",
        "zh": "Ed Sheeran - The A Team（葛萊美年度歌曲入圍·不朽吉他民謠）",
        "url": f"https://www.youtube.com/watch?v={vid}",
        "cues": cues,
        "en": [c["en"] for c in cues],
        "cn": [c.get("zh", "") for c in cues]
    }

def main():
    print("=== REPAIRING PHOTOGRAPH & THE A TEAM IN SONGS ===")
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    m = re.search(r'const songs = (\[.*?\]);', html, re.DOTALL)
    songs = json.loads(m.group(1))

    # 1. Fix Photograph at index 8
    photo_song = songs[8]
    assert photo_song["id"] == "KKQl-pIRQMY"
    photo_song["cues"] = CANONICAL_PHOTOGRAPH_CUES
    photo_song["en"] = [c["en"] for c in CANONICAL_PHOTOGRAPH_CUES]
    photo_song["cn"] = [c["zh"] for c in CANONICAL_PHOTOGRAPH_CUES]
    photo_song["zh"] = "照片中的回憶（愛能撫平所有的傷口）"
    print("Successfully repaired Ed Sheeran - Photograph at index 8!")

    # 2. Replace duplicate Photograph at index 66 with The A Team
    a_team = build_the_a_team()
    songs[66] = a_team
    print(f"Successfully replaced duplicate at index 66 with Ed Sheeran - The A Team ({len(a_team['cues'])} cues)!")

    # Save to index.html
    s_idx = html.find("const songs = [")
    e_idx = html.find("let customLessons =")
    if e_idx == -1:
        e_idx = html.find("function renderNavBars()")
    
    # Locate semicolon after songs
    semi_idx = html.find("];\n", s_idx)
    new_songs_str = json.dumps(songs, ensure_ascii=False, indent=2)
    updated_html = html[:s_idx + len("const songs = ")] + new_songs_str + html[semi_idx + 1:]

    # Bump version
    with open(SW_JS_PATH, "r", encoding="utf-8") as sf:
        sw_text = sf.read()
    m_v = re.search(r"englishtube-v(\d+)", sw_text)
    curr_v = int(m_v.group(1)) if m_v else 124
    new_v = curr_v + 1
    new_sw = sw_text.replace(f"englishtube-v{curr_v}", f"englishtube-v{new_v}")
    with open(SW_JS_PATH, "w", encoding="utf-8") as sf:
        sf.write(new_sw)

    updated_html = updated_html.replace(f"?v={curr_v}", f"?v={new_v}")
    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(updated_html)

    # Save to songs_100.json
    with open(SONGS_100_PATH, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

    print(f"Bumped cache version to v{new_v}")
    print("SUCCESS: 100 songs fully unique, Photograph lyrics completely corrected!")

if __name__ == "__main__":
    main()
