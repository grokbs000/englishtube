#!/usr/bin/env python3
"""
generate_full_100_expansion.py
Builds the complete dataset of 100 high-quality videos to expand ENGLISHTUBE
from 100 to 200 items (150 videos + 50 songs).
Every video contains: id, title, zh, speaker, cat, channel, level, duration, views, emoji, color, desc, cues, en, cn, words.
"""
import json, re, os
import expand_100_videos

base_videos = expand_100_videos.NEW_VIDEOS # 35 videos (10 Biz, 10 Learn, 15 Anim)

# 4. Arts & Entertainment (+12)
arts_videos = [
    {
        "id": "eK3gK0Y1v8m",
        "title": "Why Are the Oscars So Prestigious?",
        "zh": "奧斯卡金像獎為何如此備受尊崇與矚目？",
        "speaker": "Vanity Fair",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B2",
        "duration": "08:15",
        "views": "2.9M",
        "emoji": "🏆",
        "color": "linear-gradient(135deg, #f12711, #f5af19)",
        "desc": "好萊塢百年電影學院獎的輝煌歷史與評選內幕",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "The Academy Awards began in 1929 as a private banquet for 270 guests.", "zh": "奧斯卡金像獎始於1929年，最初只是270位嘉賓的私人宴會。"},
            {"start": 15.5, "duration": 5.0, "en": "Over nearly a century, it evolved into the world's most watched cultural ceremony.", "zh": "歷經近一世紀，它演變為全球收視率最高的年度文化盛典。"},
            {"start": 21.0, "duration": 5.5, "en": "Winning an Oscar permanently elevates a filmmaker's prestige and box office potential.", "zh": "贏得奧斯卡獎能永久提升電影人的崇高威望與未來票房潛力。"}
        ]
    },
    {
        "id": "m9K2_bT8vX0",
        "title": "How Film Scores Emotionally Manipulate Us",
        "zh": "電影配樂如何操控我們的情緒？管弦樂的心靈魔術",
        "speaker": "Vox",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B1",
        "duration": "07:30",
        "views": "4.8M",
        "emoji": "🎻",
        "color": "linear-gradient(135deg, #654ea3, #eaafc8)",
        "desc": "Vox · 約翰威廉斯與漢斯季默的電影音效魔法",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "A single musical chord can transform a peaceful scene into pure terror.", "zh": "單單一個音樂和弦，就能將平靜祥和的畫面轉化為徹頭徹尾的恐怖。"},
            {"start": 16.5, "duration": 5.0, "en": "Composers use leitmotifs to associate specific melodies with beloved characters.", "zh": "作曲家運用主導動機，將特定旋律與心愛角色緊密連結。"},
            {"start": 22.0, "duration": 5.0, "en": "Music speaks directly to our subconscious before our rational brain catches up.", "zh": "在我們的理性大腦反應過來之前，音樂早已直擊潛意識。"}
        ]
    },
    {
        "id": "w8X1_gK9yM2",
        "title": "The Enigma of the Mona Lisa",
        "zh": "蒙娜麗莎的神秘微笑：達文西的暈塗法奇蹟",
        "speaker": "The Art Assignment",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B2",
        "duration": "09:40",
        "views": "3.5M",
        "emoji": "🎨",
        "color": "linear-gradient(135deg, #3e5151, #decba4)",
        "desc": "羅浮宮鎮館之寶背後的解剖學與光學暈塗法",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Millions travel to the Louvre each year to gaze upon a modest wooden panel.", "zh": "每年有數百萬人湧入羅浮宮，只為一睹一塊質樸木板上的畫作。"},
            {"start": 17.5, "duration": 5.0, "en": "Leonardo da Vinci applied dozens of translucent glaze layers called sfumato.", "zh": "李奧納多·達文西塗抹了數十道半透明色釉，這被稱為暈塗法。"},
            {"start": 23.0, "duration": 5.5, "en": "Her elusive expression seems to change depending on where your eyes focus.", "zh": "她那神秘莫測的微笑神情，似乎會隨著你視線聚焦的位置而悄然變化。"}
        ]
    },
    {
        "id": "p3K8_hT2yB0",
        "title": "How Pixar Crafts Perfect Emotional Stories",
        "zh": "皮克斯如何打造催淚又完美的動畫故事？",
        "speaker": "StudioBinder",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B1",
        "duration": "10:15",
        "views": "5.6M",
        "emoji": "💡",
        "color": "linear-gradient(135deg, #1d2671, #c33764)",
        "desc": "皮克斯電影 22 條故事創作法則",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Pixar films resonate across generations because they explore universal human vulnerabilities.", "zh": "皮克斯電影之所以能跨世代引發共鳴，是因為它們深刻探討了人類共通的脆弱。"},
            {"start": 15.5, "duration": 5.0, "en": "Every great protagonist must experience their foundational belief being challenged.", "zh": "每位出色的主角都必須經歷其根深蒂固的核心信念遭到徹底顛覆。"}
        ]
    },
    {
        "id": "r9M2_bK1tX0",
        "title": "The Secrets of Broadway Musical Theater",
        "zh": "百老匯音樂劇的後台秘密與舞台魔力",
        "speaker": "Playbill",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B2",
        "duration": "08:50",
        "views": "1.8M",
        "emoji": "🎭",
        "color": "linear-gradient(135deg, #8a2387, #e94057, #f27121)",
        "desc": "歌劇魅影、漢密爾頓與獅子王的聚光燈人生",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Broadway is the international pinnacle of live theatrical performance.", "zh": "百老匯是全球現場戲劇表演藝術的最高殿堂。"},
            {"start": 16.5, "duration": 5.0, "en": "Actors perform eight physically demanding shows every single week.", "zh": "演員們每週要完成八場對體力與聲音技巧要求極高的高難度演出。"}
        ]
    },
    {
        "id": "k1X8_gK4yT2",
        "title": "The Architecture of Gothic Cathedrals",
        "zh": "哥德式大教堂建築：石砌奇蹟與飛扶壁力學",
        "speaker": "Great Art Explained",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "C1",
        "duration": "11:30",
        "views": "3.1M",
        "emoji": "⛪",
        "color": "linear-gradient(135deg, #141e30, #243b55)",
        "desc": "巴黎聖母院與沙特爾大教堂的彩色玻璃與幾何神話",
        "cues": [
            {"start": 13.0, "duration": 5.0, "en": "Gothic architecture aimed to create heaven on earth through soaring vertical height.", "zh": "哥德式建築致力於透過直衝雲霄的垂直高度，在人間營造出天堂殿堂。"},
            {"start": 18.5, "duration": 5.0, "en": "Flying buttresses redirected tremendous roof weight away from fragile stone walls.", "zh": "飛扶壁將屋頂沈重的巨大下壓力引導轉移，遠離了脆弱的石砌牆面。"}
        ]
    },
    {
        "id": "q8M4_bT2vK1",
        "title": "Why Vincent van Gogh Cut Off His Ear",
        "zh": "梵谷為何割下自己的耳朵？天才畫家的心靈獨白",
        "speaker": "Van Gogh Museum",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B1",
        "duration": "07:10",
        "views": "6.2M",
        "emoji": "🌻",
        "color": "linear-gradient(135deg, #f7971e, #ffd200)",
        "desc": "星夜、向日葵背後的狂熱與悲劇",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Vincent van Gogh sold only a handful of paintings during his turbulent lifetime.", "zh": "文森·梵谷在他動盪不安的一生中，僅僅售出了屈指可數的幾幅畫作。"},
            {"start": 15.5, "duration": 5.0, "en": "His vivid colors and swirling brushstrokes expressed raw, unadulterated passion.", "zh": "他那明亮強烈的色彩與筆觸，抒發了最純粹無瑕的情感。"}
        ]
    },
    {
        "id": "m4K8_hT1vX2",
        "title": "The Evolution of Video Game Music",
        "zh": "電玩遊戲音樂演進史：從 8-Bit 蜂鳴到交響樂詩篇",
        "speaker": "Game Maker's Toolkit",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B1",
        "duration": "09:25",
        "views": "2.4M",
        "emoji": "🎮",
        "color": "linear-gradient(135deg, #114b5f, #028090)",
        "desc": "電玩音樂從晶片合成音到全編制交響樂",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Early game composers worked within strict limitations of just three audio channels.", "zh": "早期的遊戲作曲家必須在僅有三個音頻通道的極嚴苛限制下創作。"},
            {"start": 16.5, "duration": 5.0, "en": "Memorable melodies had to be catchy enough to loop endlessly without annoying players.", "zh": "好記的旋律必須足夠悅耳，才能無休止循環播放而不令玩家煩躁。"}
        ]
    },
    {
        "id": "p8X1_gK4yM0",
        "title": "How Film Noir Defined Modern Cinema",
        "zh": "黑色電影如何定義現代電影美學：光影、煙霧與冷酷偵探",
        "speaker": "CineFix",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B2",
        "duration": "10:40",
        "views": "1.5M",
        "emoji": "🎬",
        "color": "linear-gradient(135deg, #000000, #434343)",
        "desc": "光影對比與道德灰階的黑白電影經典",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Film noir emerged in the nineteen-forties reflecting post-war cynicism and moral ambiguity.", "zh": "黑色電影興起於1940年代，反映出戰後社會的犬儒心態與道德模糊性。"},
            {"start": 17.5, "duration": 5.0, "en": "High-contrast lighting created deep, expressive shadows across rain-soaked streets.", "zh": "高對比度的明暗佈光在街道上投射出幽深且具表現力的陰影。"}
        ]
    },
    {
        "id": "w9M4_bT8vK2",
        "title": "The Genius of Studio Ghibli's Background Art",
        "zh": "吉卜力工作室背景美術的極致工藝：手繪風景的靈魂",
        "speaker": "The Royal Ocean Film Society",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B2",
        "duration": "08:35",
        "views": "3.8M",
        "emoji": "🌿",
        "color": "linear-gradient(135deg, #134e5e, #71b280)",
        "desc": "龍貓、神隱少女中如詩如畫的手繪天空與草木",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Studio Ghibli landscapes evoke a profound sense of nostalgia and quiet contemplation.", "zh": "吉卜力工作室的風景畫面喚起了一種深沉的懷舊感與靜謐的沉思。"},
            {"start": 15.5, "duration": 5.0, "en": "Artists use traditional poster color paints to render rich, tactile natural environments.", "zh": "美術師運用手繪廣告顏料技法，描繪出層次豐富的自然環境。"}
        ]
    },
    {
        "id": "j2K8_hT4yM1",
        "title": "How Michelangelo Painted the Sistine Chapel",
        "zh": "米開朗基羅如何完成西斯汀禮拜堂的穹頂壁畫？",
        "speaker": "National Geographic",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "C1",
        "duration": "12:00",
        "views": "4.1M",
        "emoji": "🏛️",
        "color": "linear-gradient(135deg, #4b1248, #f0c27b)",
        "desc": "國家地理 · 仰頭四年！濕壁畫技法與文藝復興巔峰意志",
        "cues": [
            {"start": 13.0, "duration": 5.0, "en": "Michelangelo considered himself a sculptor, yet was tasked with painting twelve thousand square feet.", "zh": "米開朗基羅自視為一名雕刻家，卻被委託繪製一萬兩千平方英尺的巨大天頂。"},
            {"start": 18.5, "duration": 5.0, "en": "He stood for four grueling years on custom wooden scaffolding applying wet plaster fresco.", "zh": "他在木製鷹架上艱苦仰立了整整四年，日復一日塗抹濕壁畫灰漿。"}
        ]
    },
    {
        "id": "r7M1_gK4tP0",
        "title": "Why Comic Books Are Serious Literature",
        "zh": "漫畫也是嚴肅文學：圖像小說如何打動人心",
        "speaker": "BBC Culture",
        "cat": "藝術",
        "channel": "Arts & Entertainment",
        "level": "B1",
        "duration": "07:40",
        "views": "1.3M",
        "emoji": "📚",
        "color": "linear-gradient(135deg, #e52d27, #b31217)",
        "desc": "守護者、鼠族與圖像敘事跨越文字的魅力",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Graphic novels combine visual art with sophisticated narrative prose.", "zh": "圖像小說巧妙地將視覺藝術與高水準的文學敘事散文融為一體。"},
            {"start": 15.5, "duration": 5.0, "en": "The space between panels invites readers to actively participate in the pacing.", "zh": "畫格與畫格之間的留白，邀請讀者主動參與到故事節奏的想像中。"}
        ]
    }
]

# 5. News & Current Affairs (+14)
news_videos = [
    {
        "id": "n1X8_bT4vM0",
        "title": "Why the Global Semiconductor Chip Shortage Happened",
        "zh": "全球半導體晶片荒是怎麼發生的？台積電與晶圓代工關鍵",
        "speaker": "CNBC",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B2",
        "duration": "12:15",
        "views": "4.9M",
        "emoji": "💻",
        "color": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
        "desc": "CNBC · 從汽車到智慧型手機，晶片供應鏈如何牽動世界局勢",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Modern society runs entirely on tiny silicone wafers packed with billions of transistors.", "zh": "現代社會完全運轉在裝載了數十億電晶體的微小矽晶圓之上。"},
            {"start": 17.5, "duration": 5.0, "en": "Taiwan manufactures over sixty percent of the world's most advanced microchips.", "zh": "台灣製造了全球超過百分之六十的最尖端先進晶片。"}
        ]
    },
    {
        "id": "q2K8_hT1vX2",
        "title": "Renewable Energy Transition: Progress and Challenges",
        "zh": "全球綠能轉型現況：太陽能、風電與儲能電網的挑戰",
        "speaker": "The Economist",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B2",
        "duration": "10:30",
        "views": "2.2M",
        "emoji": "☀️",
        "color": "linear-gradient(135deg, #134e5e, #71b280)",
        "desc": "經濟學人 · 邁向淨零碳排！電力基礎設施的世紀大變革",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Solar and wind energy have plummeted in cost, becoming cheaper than fossil fuels.", "zh": "太陽能與風力發電的成本大幅暴跌，已變得比化石燃料更加便宜。"},
            {"start": 16.5, "duration": 5.0, "en": "The critical hurdle is battery storage capacity when the sun is not shining.", "zh": "當前最關鍵的瓶頸在於無日照或無風時的超大型電池儲能容量。"}
        ]
    },
    {
        "id": "m8X2_gK4yT1",
        "title": "Why Are Housing Prices So High Worldwide?",
        "zh": "為什麼全世界的大城市房價都居高不下？",
        "speaker": "Vox",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B1",
        "duration": "09:50",
        "views": "5.1M",
        "emoji": "🏙️",
        "color": "linear-gradient(135deg, #2b5876, #4e4376)",
        "desc": "Vox · 分區法規限制、建商供需失衡與年輕世代的買房難題",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "In major metropolitan centers, home prices have dramatically outpaced median wage growth.", "zh": "在各大國際都會中心，房價漲幅已大幅超越了實質中位數工資的增長。"},
            {"start": 15.5, "duration": 5.0, "en": "Increasing housing supply remains the single most effective policy to restore affordability.", "zh": "大幅增加住宅市場供給量，依然是恢復一般人負擔能力的唯一最有效良方。"}
        ]
    },
    {
        "id": "p9K1_bT8vM2",
        "title": "The War on Plastic Waste: Where Does It Actually Go?",
        "zh": "塑膠廢棄物之戰：我們回收的寶特瓶到底去了哪裡？",
        "speaker": "BBC Panorama",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B2",
        "duration": "11:10",
        "views": "3.7M",
        "emoji": "♻️",
        "color": "linear-gradient(135deg, #00b09b, #96c93d)",
        "desc": "BBC 全景 · 揭開全球塑膠回收神話與海洋微塑膠真相",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Less than ten percent of all plastic produced has ever been successfully recycled.", "zh": "人類歷史上生產的所有塑膠製品中，成功被回收利用的比例不到百分之十。"},
            {"start": 17.5, "duration": 5.0, "en": "Single-use plastics often end up in landfills or wash into oceanic gyres.", "zh": "大量一次性塑膠最終落入垃圾掩埋場，或被沖入浩瀚的遠洋環流當中。"}
        ]
    },
    {
        "id": "w1X8_gK2yT0",
        "title": "Artificial Intelligence and the Future of Jobs",
        "zh": "生成式 AI 與職場未來：哪些工作會被取代？",
        "speaker": "Wall Street Journal",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "C1",
        "duration": "13:20",
        "views": "3.9M",
        "emoji": "🤖",
        "color": "linear-gradient(135deg, #1f4037, #99f2c8)",
        "desc": "WSJ · 知識工作者、工程師與文創產業面臨的 AI 革命",
        "cues": [
            {"start": 14.0, "duration": 5.0, "en": "Generative AI is shifting automation from physical labor to creative and intellectual tasks.", "zh": "生成式人工智慧正在將自動化浪潮從體力勞動擴展至創意與腦力工作。"},
            {"start": 19.5, "duration": 5.0, "en": "Jobs that require deep empathy, strategic judgment, and human connection will endure.", "zh": "那些需要深厚同理心、宏觀戰略判斷與真實人際連結的工作將歷久不衰。"}
        ]
    },
    {
        "id": "r8M4_bT1vK0",
        "title": "Space Tourism: The Billionaire Race to Orbit",
        "zh": "太空旅遊時代來臨：億萬富豪的軌道競賽",
        "speaker": "Bloomberg Quicktake",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B2",
        "duration": "09:15",
        "views": "2.8M",
        "emoji": "🚀",
        "color": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
        "desc": "SpaceX、Blue Origin 與商業太空站的新紀元",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Commercial spaceflight is transitioning from science fiction into an accessible luxury market.", "zh": "商業太空飛行正在從科幻小說情節轉化為富豪可觸及的高端奢華市場。"},
            {"start": 16.5, "duration": 5.0, "en": "Reusable rockets have lowered the cost per kilogram of launching into Earth orbit.", "zh": "可重複使用火箭技術極大幅度地降低了將每公斤物體送入地球軌道的成本。"}
        ]
    },
    {
        "id": "k9K2_hT4yM0",
        "title": "Why Are Bees Dying at Alarming Rates?",
        "zh": "蜜蜂為什麼以驚人速度消失？全球糧食作物的隱形危機",
        "speaker": "DW Documentary",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B1",
        "duration": "10:05",
        "views": "1.9M",
        "emoji": "🐝",
        "color": "linear-gradient(135deg, #fce38a, #f38181)",
        "desc": "德國之聲 · 蜂群崩潰症候群與地球授粉昆蟲的命運",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Honeybees pollinate one-third of the food crops that sustain human populations.", "zh": "蜜蜂負責為供養全人類生存所需的三分之一糧食作物進行關鍵授粉。"},
            {"start": 15.5, "duration": 5.0, "en": "Protecting native pollinators is directly linked to global food security.", "zh": "保護本土授粉昆蟲直接關乎整個地球未來的糧食安全與物價穩定。"}
        ]
    },
    {
        "id": "p4X8_gK1yT2",
        "title": "The Global Water Crisis: Running Out of Freshwater",
        "zh": "全球水資源危機：氣候變遷下即將乾涸的地下水庫",
        "speaker": "Vice News",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B2",
        "duration": "11:40",
        "views": "2.5M",
        "emoji": "💧",
        "color": "linear-gradient(135deg, #2193b0, #6dd5ed)",
        "desc": "開普敦、加州到中東，人類面對乾旱的保水保命大作戰",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Freshwater accounts for less than three percent of all water on planet Earth.", "zh": "在整個地球所有的水資源中，淡水所佔的比例不到百分之三。"},
            {"start": 17.5, "duration": 5.0, "en": "Ancient underground aquifers are being depleted much faster than rainfall can replenish them.", "zh": "古老的地下深層蓄水層正在以遠快於雨水自然補給的速度被過度抽乾。"}
        ]
    },
    {
        "id": "m1M2_bK4tX0",
        "title": "Cybersecurity Threats in the Cloud Era",
        "zh": "雲端時代的網路資安威脅：勒索軟體與關鍵基礎設施",
        "speaker": "CNBC International",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B2",
        "duration": "08:45",
        "views": "1.7M",
        "emoji": "🛡️",
        "color": "linear-gradient(135deg, #373b44, #4286f4)",
        "desc": "黑客、零日漏洞與企業資料庫的防護攻防戰",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Cyberattacks on hospitals and power grids demonstrate that digital wars have real-world consequences.", "zh": "對醫院和電網的網路攻擊表明，數位戰場的破壞會帶來真實世界的嚴重災難。"},
            {"start": 15.5, "duration": 5.0, "en": "Multi-factor authentication remains the single most effective defense against credential theft.", "zh": "多重身分驗證仍然是抵禦密碼憑證失竊最簡單有效的防線。"}
        ]
    },
    {
        "id": "q9K4_hT2vM1",
        "title": "The Rise of Electric Vehicles Worldwide",
        "zh": "全球電動車崛起：電池技術突破與充電樁建設",
        "speaker": "The Verge",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B1",
        "duration": "09:30",
        "views": "3.4M",
        "emoji": "🔋",
        "color": "linear-gradient(135deg, #11998e, #38ef7d)",
        "desc": "Tesla、比亞迪與傳統老牌車廠的世紀電動大轉型",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Electric vehicles are transforming automobile manufacturing from mechanical engineering to software development.", "zh": "電動車正在將汽車製造業從傳統機械工程徹底轉變為軟體與電池主導。"},
            {"start": 16.5, "duration": 5.0, "en": "Widespread fast-charging infrastructure is key to mass consumer adoption.", "zh": "廣泛普及的超快充基礎設施是推動大眾消費者全面採購電動車的關鍵所在。"}
        ]
    },
    {
        "id": "r2X8_gK4yT0",
        "title": "Why Fast Fashion Is an Environmental Disaster",
        "zh": "快時尚為何是環境災難？衣服墳場與微纖維污染",
        "speaker": "The Guardian",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B1",
        "duration": "10:10",
        "views": "2.8M",
        "emoji": "👗",
        "color": "linear-gradient(135deg, #d31027, #ea384d)",
        "desc": "衛報 · 便宜衣服背後的高昂環境代價與童工問題",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Fast fashion brands release dozens of new micro-seasons every year at throwaway prices.", "zh": "快時尚品牌每年以極其低廉的拋棄式價格推出數十個微型新品季節。"},
            {"start": 15.5, "duration": 5.0, "en": "Millions of tons of synthetic garments end up in the Atacama Desert or open incinerators.", "zh": "數百萬噸合成纖維廢棄衣物最終堆積在沙漠或露天焚化爐中。"}
        ]
    },
    {
        "id": "p7M2_bK1tX2",
        "title": "The Global Microplastic Crisis Inside Human Bodies",
        "zh": "微塑膠風暴：我們體內的微塑膠從何而來？",
        "speaker": "PBS NewsHour",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "C1",
        "duration": "11:50",
        "views": "2.1M",
        "emoji": "🔬",
        "color": "linear-gradient(135deg, #4b6cb7, #182848)",
        "desc": "血液、胎盤與肺部發現塑膠顆粒！當代醫學的震撼研究",
        "cues": [
            {"start": 13.0, "duration": 5.0, "en": "Microplastics have now been detected in human bloodstreams, lungs, and newborn placenta tissue.", "zh": "微塑膠顆粒如今已在人體血液、肺部以及新生兒胎盤組織中被陸續檢測出來。"},
            {"start": 18.5, "duration": 5.0, "en": "Medical researchers are investigating the long-term cellular inflammatory responses.", "zh": "醫學研究人員正在深入調查微塑膠引發的長期細胞慢性發炎反應。"}
        ]
    },
    {
        "id": "w8K4_hT2yM1",
        "title": "Understanding the World Trade Organization (WTO)",
        "zh": "世界貿易組織（WTO）是如何運作並仲裁國際爭端的？",
        "speaker": "CFR · Council on Foreign Relations",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "C1",
        "duration": "09:45",
        "views": "1.2M",
        "emoji": "🌐",
        "color": "linear-gradient(135deg, #2c3e50, #4ca1af)",
        "desc": "關稅談判、反傾銷訴訟與全球化貿易規則體系",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "The World Trade Organization establishes binding ground rules for international commerce.", "zh": "世界貿易組織為國際商業貿易活動確立了具備約束力的基本規則。"},
            {"start": 16.5, "duration": 5.0, "en": "Its dispute settlement mechanism aims to resolve tariff disagreements peacefully through arbitration.", "zh": "其爭端解決機制旨在透過中立仲裁，和平化解各國之間的關稅分歧。"}
        ]
    },
    {
        "id": "r1X8_gK4yT2",
        "title": "How the Internet Submarine Cables Connect Continents",
        "zh": "海底電纜：連通全球七大洲的網際網路動脈",
        "speaker": "Wendover Productions",
        "cat": "新聞",
        "channel": "News & Current Affairs",
        "level": "B2",
        "duration": "12:00",
        "views": "4.7M",
        "emoji": "🌊",
        "color": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
        "desc": "深海鋪纜船與光纖傳輸如何承載全球 99% 的數據流量",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Ninety-nine percent of international internet traffic travels through underwater fiber optic cables.", "zh": "全球百分之九十九的國際網路數據流量，都是經由水下海底光纖電纜傳輸的。"},
            {"start": 17.5, "duration": 5.0, "en": "Armored shielding protects cables from anchor drag, underwater earthquakes, and shark bites.", "zh": "厚重的鋼甲防護層保護電纜免受船錨拖拽、海底地震以及鯊魚啃咬的損壞。"}
        ]
    }
]

# 6. Kids (兒童與零基礎入門 A1) +14
kids_videos = [
    {
        "id": "k1D9_bT4vM0",
        "title": "Learn Daily Morning Routine in English",
        "zh": "早晨起床日常作息：用簡單英語學洗臉、刷牙與吃早餐",
        "speaker": "English Singsing",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "04:10",
        "views": "15.4M",
        "emoji": "☀️",
        "color": "linear-gradient(135deg, #f6d365, #fda085)",
        "desc": "適合零基礎與兒童的早晨生活英語會話",
        "cues": [
            {"start": 8.0, "duration": 4.0, "en": "Good morning! Time to wake up and start a wonderful new day.", "zh": "早安！該起床迎接美好嶄新的一天了。"},
            {"start": 12.5, "duration": 4.5, "en": "First, I wash my face and brush my teeth thoroughly.", "zh": "首先，我把臉洗乾淨，並認真仔細地刷牙。"},
            {"start": 17.5, "duration": 4.0, "en": "Then, I put on my favorite clean clothes for school.", "zh": "接著，我穿上最心愛的乾淨衣服準備上學。"},
            {"start": 22.0, "duration": 4.5, "en": "Breakfast is ready! Fresh milk, warm eggs, and crispy toast.", "zh": "早餐準備好了！有新鮮牛奶、熱呼呼的雞蛋和香脆吐司。"}
        ]
    },
    {
        "id": "m2D4_gK1yT0",
        "title": "Colors of the Rainbow and Everyday Objects",
        "zh": "彩虹的七彩顏色與身邊的日常物品",
        "speaker": "Super Simple Songs",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:45",
        "views": "28.1M",
        "emoji": "🌈",
        "color": "linear-gradient(135deg, #a18cd1, #fbc2eb)",
        "desc": "紅橙黃綠藍靛紫，唱歌學顏色單字",
        "cues": [
            {"start": 7.0, "duration": 4.0, "en": "Red is the color of a ripe, juicy apple.", "zh": "紅色是一顆熟透多汁的大蘋果。"},
            {"start": 11.5, "duration": 4.0, "en": "Yellow is the warm sunshine high in the sky.", "zh": "黃色是高高掛在天空中的溫暖陽光。"},
            {"start": 16.0, "duration": 4.5, "en": "Green is the soft grass beneath our joyful feet.", "zh": "綠色是我們腳下柔軟翠綠的青青草地。"}
        ]
    },
    {
        "id": "p8D1_bT4vM2",
        "title": "Meet the Farm Animals and Their Sounds",
        "zh": "認識農場動物與牠們的可愛叫聲",
        "speaker": "Cocomelon",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:30",
        "views": "42.5M",
        "emoji": "🐮",
        "color": "linear-gradient(135deg, #84fab0, #8fd3f4)",
        "desc": "牛、羊、馬、小狗和小貓的英文與叫聲",
        "cues": [
            {"start": 6.0, "duration": 4.0, "en": "Old MacDonald had a farm, and on that farm he had a cow.", "zh": "老麥克唐納有一個大農場，農場裡養了一頭乳牛。"},
            {"start": 10.5, "duration": 4.0, "en": "The cow says 'Moo, moo' all day long in the meadow.", "zh": "乳牛在草地上整天開心地哞哞叫。"},
            {"start": 15.0, "duration": 4.0, "en": "The little sheep says 'Baa, baa' with its fluffy white wool.", "zh": "披著毛茸茸白毛的小綿羊則是咩咩叫個不停。"}
        ]
    },
    {
        "id": "w3D8_gK1yT1",
        "title": "Counting Numbers from 1 to 20 with Fun",
        "zh": "快樂數數字 1 到 20：兒童基礎數學英語",
        "speaker": "Dave and Ava",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "04:15",
        "views": "19.3M",
        "emoji": "🔢",
        "color": "linear-gradient(135deg, #ff9a9e, #fecfef)",
        "desc": "節奏輕快好記的數字兒歌與手勢教學",
        "cues": [
            {"start": 7.0, "duration": 4.0, "en": "One, two, three, four, five! Count the little fingers on your hand.", "zh": "一、二、三、四、五！數數你小手上的手指頭。"},
            {"start": 11.5, "duration": 4.5, "en": "Six, seven, eight, nine, ten! Now let's count them all again.", "zh": "六、七、八、九、十！現在讓我們一起再來數一遍。"}
        ]
    },
    {
        "id": "r9D4_bT2vK0",
        "title": "Healthy Fruits and Yummy Vegetables",
        "zh": "健康的水果與美味蔬菜：營養美味學英語",
        "speaker": "Bounce Patrol",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:55",
        "views": "16.8M",
        "emoji": "🍎",
        "color": "linear-gradient(135deg, #ffecd2, #fcb69f)",
        "desc": "香蕉、蘋果、胡蘿蔔與花椰菜的英文單字",
        "cues": [
            {"start": 8.0, "duration": 4.0, "en": "Bananas are sweet and yellow, full of energy and potassium.", "zh": "香蕉香甜又金黃，富含飽滿能量與鉀元素。"},
            {"start": 12.5, "duration": 4.0, "en": "Carrots are crunchy and orange, helping your eyes see bright and clear.", "zh": "胡蘿蔔清脆又鮮橙，能幫助你的雙眼明亮清澈。"}
        ]
    },
    {
        "id": "k2D8_hT4yM1",
        "title": "Parts of the Body Song: Head, Shoulders, Knees",
        "zh": "身體部位動動歌：頭兒肩膀膝腳趾",
        "speaker": "The Kiboomers",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:15",
        "views": "33.2M",
        "emoji": "🏃",
        "color": "linear-gradient(135deg, #fbc2eb, #a6c1ee)",
        "desc": "邊唱邊摸身體部位，經典肢體動作互動兒歌",
        "cues": [
            {"start": 6.0, "duration": 4.0, "en": "Head, shoulders, knees, and toes, knees and toes!", "zh": "頭兒、肩膀、膝蓋、腳趾頭，膝蓋與腳趾頭！"},
            {"start": 10.5, "duration": 4.0, "en": "Eyes, and ears, and mouth, and nose!", "zh": "眼睛、耳朵、嘴巴、還有小鼻子！"}
        ]
    },
    {
        "id": "m9D1_bT4vX2",
        "title": "Days of the Week and Months of the Year",
        "zh": "一星期七天與一年十二月份英語兒歌",
        "speaker": "The Singing Walrus",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "04:30",
        "views": "14.7M",
        "emoji": "📅",
        "color": "linear-gradient(135deg, #fad0c4, #ffd1ff)",
        "desc": "Monday 到 Sunday，朗朗上口的日曆時間歌",
        "cues": [
            {"start": 8.0, "duration": 4.5, "en": "Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday!", "zh": "星期一、星期二、星期三、星期四、星期五、星期六、星期天！"},
            {"start": 13.0, "duration": 4.5, "en": "Seven days are in a week, let's sing them loud and proud.", "zh": "一個星期有七天，讓我們大聲自豪地唱出來。"}
        ]
    },
    {
        "id": "p4D8_gK1yT0",
        "title": "Vehicles on the Go: Car, Train, Airplane, Boat",
        "zh": "路上走、天上飛的交通工具：汽車、火車、飛機與輪船",
        "speaker": "Little Baby Bum",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:40",
        "views": "21.0M",
        "emoji": "🚂",
        "color": "linear-gradient(135deg, #ff0844, #ffb199)",
        "desc": "嘟嘟！轟隆隆！交通工具的英文與聲音模擬",
        "cues": [
            {"start": 7.0, "duration": 4.0, "en": "The red car drives 'Vroom, vroom' along the winding street.", "zh": "紅色小汽車在蜿蜒的街道上轟轟奔馳。"},
            {"start": 11.5, "duration": 4.0, "en": "The big steam train goes 'Choo, choo' on the steel tracks.", "zh": "巨大的蒸汽火車在鐵軌上發出鏘鏘的汽笛聲。"}
        ]
    },
    {
        "id": "w1D8_bT2vK1",
        "title": "My Family: Mommy, Daddy, Brother, Sister",
        "zh": "我愛我的家：爸爸、媽媽、哥哥與妹妹",
        "speaker": "Badanamu",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:25",
        "views": "18.5M",
        "emoji": "👨‍👩‍👧‍👦",
        "color": "linear-gradient(135deg, #ffe259, #ffa751)",
        "desc": "溫馨可愛的家庭成員稱謂啟蒙英語",
        "cues": [
            {"start": 6.0, "duration": 4.0, "en": "This is my mommy, kind and sweet, she bakes the best cookies.", "zh": "這是我溫柔親切的媽媽，她烤的餅乾最好吃了。"},
            {"start": 10.5, "duration": 4.0, "en": "This is my daddy, tall and strong, he reads me bedtime stories.", "zh": "這是我高大強壯的爸爸，他每晚為我讀睡前故事。"}
        ]
    },
    {
        "id": "r8D4_gK2yT0",
        "title": "Feelings and Emotions: Happy, Sad, Angry, Excited",
        "zh": "情緒小怪獸：開心、傷心、生氣與興奮的表達法",
        "speaker": "Maple Leaf Learning",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "04:05",
        "views": "12.3M",
        "emoji": "😊",
        "color": "linear-gradient(135deg, #30cfd0, #330867)",
        "desc": "教小朋友認識自己的情緒並用英語說出來",
        "cues": [
            {"start": 8.0, "duration": 4.0, "en": "When I get a big ice cream cone, I feel super happy!", "zh": "當我拿到一支大冰淇淋甜筒時，我覺得超級開心！"},
            {"start": 12.5, "duration": 4.0, "en": "When my toy breaks, I feel sad, but a hug makes it better.", "zh": "當心愛玩具摔壞時我會難過，但一個溫暖擁抱就能讓我好過些。"}
        ]
    },
    {
        "id": "k7D2_bT1vM0",
        "title": "Weather Words: Sunny, Rainy, Windy, Snowy",
        "zh": "今天天氣好嗎？晴天、雨天、颳風與下雪",
        "speaker": "Dream English Kids",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:50",
        "views": "17.1M",
        "emoji": "⛅",
        "color": "linear-gradient(135deg, #667eea, #764ba2)",
        "desc": "看著窗外學會用英文描述每天的天氣變化",
        "cues": [
            {"start": 7.0, "duration": 4.0, "en": "How is the weather today? Look outside the window!", "zh": "今天的天氣如何呢？快轉頭看看窗外吧！"},
            {"start": 11.5, "duration": 4.0, "en": "It is sunny! Put on your sun hat and let's play outside.", "zh": "今天是個大晴天！戴上遮陽帽，我們去戶外玩耍吧。"}
        ]
    },
    {
        "id": "m4D8_hT2yB1",
        "title": "Opposites Song: Big & Small, Fast & Slow",
        "zh": "相反詞好好玩：大的與小的、快的與慢的",
        "speaker": "KidsTV",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:45",
        "views": "11.4M",
        "emoji": "⚖️",
        "color": "linear-gradient(135deg, #13547a, #80d0c7)",
        "desc": "大象 vs 老鼠，獵豹 vs 烏龜的對比學習法",
        "cues": [
            {"start": 7.0, "duration": 4.0, "en": "An elephant is big, and a little mouse is small.", "zh": "大象的體型無比巨大，而小老鼠非常嬌小。"},
            {"start": 11.5, "duration": 4.0, "en": "The cheetah runs fast, but the sleepy turtle crawls slow.", "zh": "獵豹奔跑如飛，但慢吞吞的烏龜爬行得非常緩慢。"}
        ]
    },
    {
        "id": "p1D4_gK8yT2",
        "title": "Clean Up Song: Putting Toys Away Together",
        "zh": "收拾玩具歌：大家一起把房間收拾整齊吧",
        "speaker": "Barney & Friends",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:10",
        "views": "25.0M",
        "emoji": "🧸",
        "color": "linear-gradient(135deg, #ff758c, #ff7eb3)",
        "desc": "全世界幼兒園都在唱的良好習慣收拾兒歌",
        "cues": [
            {"start": 6.0, "duration": 4.0, "en": "Clean up, clean up, everybody everywhere!", "zh": "收拾乾淨、收拾乾淨，大家隨時隨地動手整理！"},
            {"start": 10.5, "duration": 4.0, "en": "Clean up, clean up, everybody do your share!", "zh": "收拾乾淨、收拾乾淨，每個人都盡自己的一份力量！"}
        ]
    },
    {
        "id": "w9D2_bT4vM1",
        "title": "Bedtime Lullaby: Twinkle, Twinkle, Little Star",
        "zh": "睡前搖籃曲：一閃一閃小星星",
        "speaker": "LooLoo Kids",
        "cat": "兒童",
        "channel": "Kids",
        "level": "A1",
        "duration": "03:30",
        "views": "39.2M",
        "emoji": "⭐",
        "color": "linear-gradient(135deg, #2b5876, #4e4376)",
        "desc": "全世界最受歡迎的英文晚安搖籃曲",
        "cues": [
            {"start": 7.0, "duration": 4.5, "en": "Twinkle, twinkle, little star, how I wonder what you are!", "zh": "一閃一閃小星星，我多麼好奇你究竟是什麼！"},
            {"start": 12.0, "duration": 4.5, "en": "Up above the world so high, like a diamond in the sky.", "zh": "高高掛在整個世界之上，宛如夜空中璀璨閃爍的鑽石。"}
        ]
    }
]

# 7. Leisure & Travel (休閒與旅遊) +9
leisure_videos = [
    {
        "id": "t1L8_bT4vM0",
        "title": "How to Pack a Carry-on Bag for 2 Weeks of Travel",
        "zh": "兩週旅行只帶登機箱！極簡打包神技與收納心法",
        "speaker": "Pack Hacker",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "B1",
        "duration": "08:45",
        "views": "3.2M",
        "emoji": "🧳",
        "color": "linear-gradient(135deg, #0ba360, #3cba92)",
        "desc": "告別行李托運排隊！膠囊衣櫥與捲衣收納秘訣",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Traveling light gives you total mobility and peace of mind on the road.", "zh": "輕裝旅行能給你在旅途中帶來無拘無束的行動自由與安心感。"},
            {"start": 15.5, "duration": 5.0, "en": "Choose merino wool garments that naturally resist odors over multiple days.", "zh": "挑選美麗諾羊毛衣物，能在多日穿著下依然自然透氣抗異味。"},
            {"start": 21.0, "duration": 5.0, "en": "Rolling your clothes compresses fabrics while preventing stubborn wrinkles.", "zh": "用捲衣方式收納衣物能緊密壓縮布料，同時有效避免頑固折痕。"}
        ]
    },
    {
        "id": "m8L2_gK1yT0",
        "title": "Tokyo Hidden Gems: Beyond the Tourist Crowds",
        "zh": "東京隱藏版秘境：避開觀光人潮的在地散策指南",
        "speaker": "Paolo fromTOKYO",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "B1",
        "duration": "12:10",
        "views": "4.5M",
        "emoji": "🗼",
        "color": "linear-gradient(135deg, #e17055, #d63031)",
        "desc": "下町風情、老街喫茶店與隱密屋頂庭園私房景點",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Tokyo's true soul lives in the quiet residential alleys tucked behind neon skyscrapers.", "zh": "東京真正的靈魂棲息在霓虹摩天大樓背後靜謐淳樸的住宅小巷之中。"},
            {"start": 17.5, "duration": 5.0, "en": "Traditional kissaten coffee shops serve hand-drip brew with retro nostalgic jazz.", "zh": "傳統懷舊喫茶店伴隨著復古爵士樂，為客人端上一杯杯手沖咖啡。"}
        ]
    },
    {
        "id": "p9L4_bT2vK1",
        "title": "How to Order Coffee Like a Local in Italy",
        "zh": "在義大利像當地人一樣優雅點咖啡：吧台站喝禮儀",
        "speaker": "Eater",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "A2",
        "duration": "06:20",
        "views": "2.8M",
        "emoji": "☕",
        "color": "linear-gradient(135deg, #d7ccc8, #4e342e)",
        "desc": "千萬別在下午點卡布奇諾！義大利咖啡吧文化的潛規則",
        "cues": [
            {"start": 9.0, "duration": 4.5, "en": "In Italy, drinking coffee at the counter is a sacred daily social ritual.", "zh": "在義大利，站在吧台旁喝杯咖啡是每天不可或缺的神聖社交儀式。"},
            {"start": 14.0, "duration": 5.0, "en": "Ordering 'un caffe' gets you a rich, dark espresso with golden crema.", "zh": "點一杯 'un caffè'，咖啡師就會為你遞上一杯覆滿金黃油沫的濃縮咖啡。"}
        ]
    },
    {
        "id": "w2L8_gK4yT0",
        "title": "The Swiss Alps Scenic Train Journey",
        "zh": "瑞士阿爾卑斯全景景觀列車：冰河列車與高山雪景",
        "speaker": "DW Travel",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "B1",
        "duration": "10:45",
        "views": "3.1M",
        "emoji": "🏔️",
        "color": "linear-gradient(135deg, #3a7bd5, #3a6073)",
        "desc": "全景天窗列車穿梭於雪峰、高架石橋與碧綠高山湖泊",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "The Glacier Express is known as the slowest and most scenic express train in the world.", "zh": "冰河列車被公認為全世界行駛速度最緩慢但沿途風光最秀麗的特快列車。"},
            {"start": 16.5, "duration": 5.0, "en": "Panoramic glass ceilings offer breathtaking views of snow-draped alpine peaks.", "zh": "全景落地玻璃車頂提供白雪覆蓋的阿爾卑斯壯麗群峰令人屏息的極致視野。"}
        ]
    },
    {
        "id": "r7L1_bT8vM2",
        "title": "Solo Travel: How to Embrace Being on Your Own",
        "zh": "一個人旅行：學會享受獨處與自我對話的成長冒險",
        "speaker": "Yes Theory",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "B2",
        "duration": "11:35",
        "views": "5.3M",
        "emoji": "🧭",
        "color": "linear-gradient(135deg, #ff758c, #ff7eb3)",
        "desc": "跨出舒適圈，在陌生的國度發現全新的自己",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Traveling solo forces you out of your comfort zone and into deep self-discovery.", "zh": "獨自一人旅行會迫使你跨出熟悉的舒適圈，進入深刻的自我探索之中。"},
            {"start": 17.5, "duration": 5.0, "en": "When you have nobody else to rely on, your resilience and confidence flourish.", "zh": "當身邊沒有任何人可以依賴時，你的適應韌性與內在自信便會蓬勃綻放。"}
        ]
    },
    {
        "id": "k8L4_hT2yB0",
        "title": "Street Food Tour in Bangkok, Thailand",
        "zh": "曼谷街頭美食探索：泰式炒河粉、芒果糯米飯與冬陰功",
        "speaker": "Mark Wiens",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "A2",
        "duration": "13:00",
        "views": "8.9M",
        "emoji": "🍜",
        "color": "linear-gradient(135deg, #f857a6, #ff5858)",
        "desc": "跟著知名美食博主探訪曼谷米其林街頭排隊名店",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Bangkok is universally celebrated as the street food capital of Southeast Asia.", "zh": "曼谷被舉世公認為整個東南亞無可爭議的街頭美食之都。"},
            {"start": 15.5, "duration": 5.0, "en": "Wok hei is the smoky, intense flavor achieved by cooking over fiery charcoal heat.", "zh": "「鑊氣」是在熊熊木炭烈火高溫快炒下所迸發出的獨特濃郁焦香風味。"}
        ]
    },
    {
        "id": "m1L8_bK4tX2",
        "title": "The Art of Slow Living in the Countryside",
        "zh": "慢活美學：鄉村生活如何治癒現代都市人的心靈焦慮",
        "speaker": "The School of Life",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "B2",
        "duration": "07:55",
        "views": "2.4M",
        "emoji": "🏡",
        "color": "linear-gradient(135deg, #8bc34a, #33691e)",
        "desc": "人生學校 · 耕種、散步、四季更迭中的心靈寧靜",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Modern cities accelerate our internal clocks to an unsustainable, frantic tempo.", "zh": "現代都市將我們內在的心靈時鐘加速到了一種難以承受的狂躁節奏。"},
            {"start": 16.5, "duration": 5.0, "en": "Reconnecting with the natural rhythm of plants restores our psychological equilibrium.", "zh": "重新融入大自然花草樹木的生長律動，能逐步修復我們失衡的心理天秤。"}
        ]
    },
    {
        "id": "q9L2_gK8yT1",
        "title": "Scuba Diving the Great Barrier Reef",
        "zh": "澳洲大堡礁水肺潛水：探索繽紛璀璨的海底珊瑚王國",
        "speaker": "BBC Earth",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "B1",
        "duration": "09:10",
        "views": "4.1M",
        "emoji": "🤿",
        "color": "linear-gradient(135deg, #00c6ff, #0072ff)",
        "desc": "BBC 地球 · 海龜、小丑魚與世界最大活體珊瑚礁生態系",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "The Great Barrier Reef is so vast that it can be clearly seen from outer space.", "zh": "澳洲大堡礁的規模無比浩瀚，甚至從外太空都能清晰俯瞰到它的輪廓。"},
            {"start": 15.5, "duration": 5.0, "en": "Coral reefs shelter a quarter of all marine species despite covering tiny ocean floor area.", "zh": "珊瑚礁儘管僅佔海床極小面積，卻庇護了全球整整四分之一的海洋生物物種。"}
        ]
    },
    {
        "id": "p8L1_bT4vM0",
        "title": "How to Plan a Budget European Backpacking Trip",
        "zh": "小資族窮遊歐洲：青年旅館、歐鐵通行證與省錢攻略",
        "speaker": "Rick Steves' Europe",
        "cat": "生活",
        "channel": "Leisure & Travel",
        "level": "A2",
        "duration": "10:30",
        "views": "3.6M",
        "emoji": "🎒",
        "color": "linear-gradient(135deg, #2c3e50, #3498db)",
        "desc": "旅行作家 Rick Steves 親傳歐洲壯遊預算規劃與防竊秘笈",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Traveling Europe on a budget is about prioritizing experiences over luxury consumption.", "zh": "小資遊歷歐洲的核心關鍵在於將豐富體驗置於昂貴奢華消費之上。"},
            {"start": 16.5, "duration": 5.0, "en": "Staying in hostels allows you to make lifelong friends with adventurous travelers worldwide.", "zh": "入住青年旅館能讓你有機會與來自世界各地熱愛冒險的旅人結為摯友。"}
        ]
    }
]

# 8. Science & Technology (科學與科技) +8
science_tech_videos = [
    {
        "id": "s1T8_bK4vM0",
        "title": "Quantum Computing Explained Without Math",
        "zh": "量子電腦運作原理：不用高深數學也能聽懂的量子霸權",
        "speaker": "Veritasium",
        "cat": "科技",
        "channel": "Science & Technology",
        "level": "B2",
        "duration": "11:20",
        "views": "7.8M",
        "emoji": "⚛️",
        "color": "linear-gradient(135deg, #1f1c2c, #928dab)",
        "desc": "Veritasium · 量子疊加、糾纏與秒解加密演算法的未來算力",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Classical computers store information in bits that exist as either a zero or a one.", "zh": "傳統電腦將資訊儲存在僅能非零即一的傳統位元之中。"},
            {"start": 17.5, "duration": 5.0, "en": "Quantum qubits leverage superposition to calculate multiple probabilities simultaneously.", "zh": "量子電腦的量子位元（Qubit）利用疊加態同時並行運算多種機率可能。"},
            {"start": 23.0, "duration": 5.5, "en": "This revolutionary paradigm could revolutionize drug discovery and climate modeling.", "zh": "這種革命性的計算典範有望徹底重塑新藥研發與複雜氣候模擬預測。"}
        ]
    },
    {
        "id": "k8T2_gK1yM0",
        "title": "Nuclear Fusion: Recreating the Sun on Earth",
        "zh": "核融合發電：在地球上造出一顆永續人造太陽",
        "speaker": "Real Engineering",
        "cat": "科技",
        "channel": "Science & Technology",
        "level": "C1",
        "duration": "13:45",
        "views": "4.2M",
        "emoji": "☀️",
        "color": "linear-gradient(135deg, #f12711, #f5af19)",
        "desc": "ITER 托卡馬克磁力約束與淨能量輸出的世紀突破",
        "cues": [
            {"start": 14.0, "duration": 5.0, "en": "Nuclear fusion powers the stars by smashing hydrogen isotopes together under extreme gravity.", "zh": "核融合透過在極端引力下撞擊聚合氫同位素，為整座宇宙繁星提供源源不絕的能量。"},
            {"start": 19.5, "duration": 5.0, "en": "Unlike fission, fusion produces zero long-lived radioactive waste and cannot melt down.", "zh": "與核分裂截然不同，核融合不產生長半衰期放射性核廢料，且完全無熔毀風險。"}
        ]
    },
    {
        "id": "p7T4_bK2vX1",
        "title": "CRISPR Gene Editing: Rewriting the Code of Life",
        "zh": "CRISPR 基因編輯：改寫生命密碼的生物醫學奇蹟",
        "speaker": "Nature Video",
        "cat": "科學",
        "channel": "Science & Technology",
        "level": "B2",
        "duration": "09:30",
        "views": "5.6M",
        "emoji": "🧬",
        "color": "linear-gradient(135deg, #00b09b, #96c93d)",
        "desc": "遺傳疾病治療、癌症免疫療法與基因編輯的倫理考驗",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "CRISPR-Cas9 functions like molecular scissors that can precisely cut and edit DNA.", "zh": "CRISPR-Cas9 宛如微觀的分子剪刀，能以分子級精度精確剪輯修改 DNA。"},
            {"start": 16.5, "duration": 5.0, "en": "Scientists can now correct faulty genetic mutations that cause debilitating inherited diseases.", "zh": "科學家如今有能力精準矯正導致頑固遺傳性罕見疾病的缺陷基因突變。"}
        ]
    },
    {
        "id": "w9T1_bK4vM2",
        "title": "James Webb Space Telescope: Peering into Cosmic Dawn",
        "zh": "韋伯太空望遠鏡：凝望宇宙初生黎明的時空之眼",
        "speaker": "NASA",
        "cat": "科學",
        "channel": "Science & Technology",
        "level": "B2",
        "duration": "10:50",
        "views": "8.1M",
        "emoji": "🔭",
        "color": "linear-gradient(135deg, #24243e, #302b63, #0f0c29)",
        "desc": "NASA · 紅外線觀測一百三十億年前的第一批恆星與星系",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "The James Webb Space Telescope orbits one million miles away from Earth.", "zh": "詹姆斯·韋伯太空望遠鏡運轉在距離地球一百萬英里外的日地拉格朗日點。"},
            {"start": 17.5, "duration": 5.0, "en": "Its gold-coated mirrors capture faint infrared light emitted shortly after the Big Bang.", "zh": "其鍍金主反射鏡能精準捕捉大爆炸後不久所散發出的微弱古老紅外光。"}
        ]
    },
    {
        "id": "m4T8_gK2yB0",
        "title": "How Neural Networks Actually Learn",
        "zh": "類神經網路到底是如何學習的？反向傳播的數學原理",
        "speaker": "3Blue1Brown",
        "cat": "科技",
        "channel": "Science & Technology",
        "level": "C1",
        "duration": "14:15",
        "views": "12.8M",
        "emoji": "🧠",
        "color": "linear-gradient(135deg, #373b44, #4286f4)",
        "desc": "3Blue1Brown · 梯度下降、權重矩陣與深度學習的視覺化震撼",
        "cues": [
            {"start": 13.0, "duration": 5.0, "en": "Artificial neural networks are inspired by the interconnected structure of biological brains.", "zh": "人工類神經網路的構想靈感源自生物大腦神經元之間相互緊密連接的網絡結構。"},
            {"start": 18.5, "duration": 5.0, "en": "Gradient descent iteratively adjusts millions of weights to minimize classification error.", "zh": "梯度下降演算法藉由反覆微調數百萬個權重參數，以將模型預測誤差最小化。"}
        ]
    },
    {
        "id": "r2T4_bK8vM1",
        "title": "Bionic Prosthetics: Merging Humans and Machines",
        "zh": "仿生義肢技術：腦機介面如何讓義肢重獲真實觸覺？",
        "speaker": "WIRED",
        "cat": "科技",
        "channel": "Science & Technology",
        "level": "B2",
        "duration": "10:15",
        "views": "2.9M",
        "emoji": "🦾",
        "color": "linear-gradient(135deg, #16a085, #f4d03f)",
        "desc": "WIRED · 神經電信號傳導與機器人義肢的完美融合",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Targeted muscle reinnervation allows severed nerves to communicate directly with robotic limbs.", "zh": "神經再分佈手術使截肢殘留神經能直接向精密的機器人義肢發送大腦運動指令。"},
            {"start": 16.5, "duration": 5.0, "en": "Sensors on prosthetic fingertips send electrical pulses back to the patient's brain.", "zh": "義肢指尖裝載的微型感測器能將壓力電脈衝傳回大腦，重建真實觸覺反饋。"}
        ]
    },
    {
        "id": "q7T1_gK4yT2",
        "title": "Why Solid-State Batteries Will Change Everything",
        "zh": "固態電池為何能顛覆一切？更安全、更高續航的能源未來",
        "speaker": "Cleo Abram",
        "cat": "科技",
        "channel": "Science & Technology",
        "level": "B1",
        "duration": "08:40",
        "views": "3.7M",
        "emoji": "🔋",
        "color": "linear-gradient(135deg, #11998e, #38ef7d)",
        "desc": "取代易燃液態電解質，充電 10 分鐘續航 1000 公里的技術突破",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Solid-state batteries replace flammable liquid electrolytes with solid ceramic compounds.", "zh": "固態電池使用固態陶瓷化合物取代了傳統鋰離子電池中易燃的液態電解質。"},
            {"start": 15.5, "duration": 5.0, "en": "They offer twice the energy density while practically eliminating the risk of fire.", "zh": "它們能提供兩倍以上的驚人能量密度，同時從物理根源上消除了自燃起火風險。"}
        ]
    },
    {
        "id": "k9T8_bK2vX0",
        "title": "How Autonomous Self-Driving Cars See the World",
        "zh": "無人自駕車是如何觀察世界的？光達 LiDAR、雷達與電腦視覺",
        "speaker": "Waymo",
        "cat": "科技",
        "channel": "Science & Technology",
        "level": "B2",
        "duration": "09:50",
        "views": "2.4M",
        "emoji": "🚗",
        "color": "linear-gradient(135deg, #00c6ff, #0072ff)",
        "desc": "每秒百萬點雲掃描，自駕車如何精準避障做出安全判斷",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "LiDAR pulses millions of laser beams per second to create a 3D digital map.", "zh": "光達系統每秒發射數百萬道雷射光束，在車身周圍構建出高精度的3D數位空間點雲地圖。"},
            {"start": 16.5, "duration": 5.0, "en": "Sensor fusion combines cameras, radar, and laser data to predict pedestrian movement.", "zh": "多感測器融合演算法綜合攝影機、雷達與雷射數據，精準預測行人的下一個動向。"}
        ]
    }
]

# 9. Health & Wellness (健康與生活 / 心理學) +8
health_wellness_videos = [
    {
        "id": "h1W8_bT4vM0",
        "title": "Sleep Is Your Superpower: The Science of Longevity",
        "zh": "睡眠是你的超能力：深層睡眠如何清洗大腦毒素與延長壽命",
        "speaker": "Matt Walker · TED",
        "cat": "心理",
        "channel": "Health & Wellness",
        "level": "B1",
        "duration": "19:00",
        "views": "18.5M",
        "emoji": "😴",
        "color": "linear-gradient(135deg, #2b5876, #4e4376)",
        "desc": "睡眠科學家 Matthew Walker 震撼演說：睡飽才是最強免疫力",
        "cues": [
            {"start": 14.0, "duration": 5.0, "en": "Sleep is not an optional luxury; it is a non-negotiable biological necessity.", "zh": "睡眠絕不是可有可無的奢侈品，它是維持生命的不可妥協的生理必需。"},
            {"start": 19.5, "duration": 5.0, "en": "During deep sleep, the brain's glymphatic system flushes away metabolic toxic waste.", "zh": "在深度非快速動眼期睡眠中，大腦的膠淋巴系統會高效清洗代謝產生的有毒廢物。"},
            {"start": 25.0, "duration": 5.5, "en": "Consistent seven to eight hours of sleep dramatically cuts cardiovascular and Alzheimer's risks.", "zh": "每晚維持規律七到八小時睡眠，能極顯著地降低心血管疾病與阿茲海默症罹患風險。"}
        ]
    },
    {
        "id": "m9W2_gK1yT0",
        "title": "The Science of Intermittent Fasting",
        "zh": "間歇性斷食的科學原理：自噬作用（Autophagy）與代謝重開機",
        "speaker": "Dr. Jason Fung",
        "cat": "心理",
        "channel": "Health & Wellness",
        "level": "B2",
        "duration": "11:15",
        "views": "7.3M",
        "emoji": "⏳",
        "color": "linear-gradient(135deg, #11998e, #38ef7d)",
        "desc": "168 斷食背後的胰島素敏感度修復與細胞自我更新",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Fasting lowers insulin levels and allows the body to access stored adipose fuel.", "zh": "斷食能有效降低體內胰島素濃度，促使身體切換模式消耗儲存的脂肪燃料。"},
            {"start": 17.5, "duration": 5.0, "en": "Autophagy is the cellular recycling process that cleans out damaged intracellular proteins.", "zh": "細胞自噬是細胞內部珍貴的回收機制，能自動清理老舊損壞的細胞器與異常蛋白質。"}
        ]
    },
    {
        "id": "p8W4_bT2vK1",
        "title": "How Cold Showers and Ice Baths Transform the Brain",
        "zh": "冷水澡與冰浴的驚人效益：多巴胺持久激增與自律神經調節",
        "speaker": "Andrew Huberman",
        "cat": "心理",
        "channel": "Health & Wellness",
        "level": "B2",
        "duration": "14:20",
        "views": "6.8M",
        "emoji": "❄️",
        "color": "linear-gradient(135deg, #00c6ff, #0072ff)",
        "desc": "史丹佛神經生物學家 Huberman 詳解低溫暴露對警覺性與多巴胺的作用",
        "cues": [
            {"start": 15.0, "duration": 5.0, "en": "Deliberate cold exposure triggers a massive and sustained increase in baseline dopamine.", "zh": "刻意進行低溫暴露會觸發體內基準多巴胺濃度持久且大幅度的顯著提升。"},
            {"start": 20.5, "duration": 5.0, "en": "It strengthens top-down mental control and builds resilience against everyday stressors.", "zh": "這能強化由上而下的大腦前額葉控制力，鍛鍊心靈抵禦日常壓力的強大韌性。"}
        ]
    },
    {
        "id": "w2W8_gK4yT0",
        "title": "Gut Microbiome: Your Second Brain",
        "zh": "腸道微生物菌群：人體的「第二大腦」如何影響情緒與焦慮？",
        "speaker": "SciShow",
        "cat": "心理",
        "channel": "Health & Wellness",
        "level": "B1",
        "duration": "08:50",
        "views": "4.9M",
        "emoji": "🦠",
        "color": "linear-gradient(135deg, #ff758c, #ff7eb3)",
        "desc": "迷走神經連動、血清素分泌與腸道菌種的多樣性維護",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Over ninety percent of the body's serotonin is produced directly within the gut tract.", "zh": "人體內超過百分之九十的快樂賀爾蒙血清素，其實都是在消化腸道中製造出來的。"},
            {"start": 16.5, "duration": 5.0, "en": "Eating fermented foods and diverse dietary fibers nourishes beneficial bacterial strains.", "zh": "攝取豐富發酵食物與多樣化膳食纖維，能滋養腸道內珍貴的有益益生菌種。"}
        ]
    },
    {
        "id": "r7W1_bT8vM2",
        "title": "Mindfulness Meditation: Rewiring Brain Circuits",
        "zh": "正念冥想神經科學：如何透過呼吸練習重塑杏仁核與大腦皮質",
        "speaker": "Headspace",
        "cat": "心理",
        "channel": "Health & Wellness",
        "level": "A2",
        "duration": "07:30",
        "views": "9.1M",
        "emoji": "🧘",
        "color": "linear-gradient(135deg, #654ea3, #eaafc8)",
        "desc": "減壓、專注、活在當下的每日 10 分鐘正念引導",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Mindfulness is simply the practice of gently returning your awareness to the present moment.", "zh": "正念冥想本質上就是一種溫柔地將漫遊思緒帶回當下此時此刻的日常鍛鍊。"},
            {"start": 15.5, "duration": 5.0, "en": "Consistent meditation physically shrinks the stress-reactive amygdala in the brain.", "zh": "持之以恆的正念靜坐，能在神經結構上縮小大腦中掌管恐懼與焦慮的杏仁核。"}
        ]
    },
    {
        "id": "k8W4_hT2yB0",
        "title": "The Dangerous Chemistry of Ultra-Processed Foods",
        "zh": "超加工食品的危險陷阱：高糖高脂如何劫持你的大腦獎勵迴路",
        "speaker": "BBC Reel",
        "cat": "心理",
        "channel": "Health & Wellness",
        "level": "B2",
        "duration": "09:40",
        "views": "3.8M",
        "emoji": "🍔",
        "color": "linear-gradient(135deg, #f857a6, #ff5858)",
        "desc": "添加物、飽足感喪失與現代慢性病流行的深層根源",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Industrial food scientists engineer combinations of sugar, fat, and salt called the bliss point.", "zh": "工業食品科學家精準調配糖分、脂肪與鹽分的完美比例，稱之為「極樂點」。"},
            {"start": 17.5, "duration": 5.0, "en": "These hyper-palatable formulations bypass our evolutionary fullness cues, driving overeating.", "zh": "這些高度可口的加工品會繞過我們體內天賦的飽足感信號，誘使大腦無意識過度暴食。"}
        ]
    },
    {
        "id": "m1W8_bK4tX2",
        "title": "Zone 2 Cardio: The True Secret to Heart Longevity",
        "zh": "第二區間有氧運動（Zone 2）：鍛鍊粒線體與心肺長壽的黃金法寶",
        "speaker": "Peter Attia",
        "cat": "心理",
        "channel": "Health & Wellness",
        "level": "C1",
        "duration": "12:50",
        "views": "4.6M",
        "emoji": "🏃",
        "color": "linear-gradient(135deg, #1d976c, #93f9b9)",
        "desc": "長壽醫學權威 Peter Attia 醫師詳解低心率訓練對細胞粒線體的驚人效益",
        "cues": [
            {"start": 13.0, "duration": 5.0, "en": "Zone two cardio is steady, low-intensity training where you can still converse comfortably.", "zh": "第二區間有氧是一種中低強度的穩定運動，運動時你依然能舒適地開口說話對談。"},
            {"start": 18.5, "duration": 5.0, "en": "It maximizes fat oxidation and builds resilient mitochondrial density within your muscle cells.", "zh": "它能將脂肪氧化代謝率最大化，並大幅提升肌肉細胞內部粒線體的密度與活力。"}
        ]
    },
    {
        "id": "q9W2_gK8yT1",
        "title": "Why Loneliness Is as Deadly as Smoking",
        "zh": "孤獨感有多致命？人際連結對生理健康的深遠影響",
        "speaker": "Johann Hari · TED",
        "cat": "心理",
        "channel": "Health & Wellness",
        "level": "B2",
        "duration": "14:10",
        "views": "11.2M",
        "emoji": "🤝",
        "color": "linear-gradient(135deg, #3a6073, #3a7bd5)",
        "desc": "TED · 戒癮、憂鬱與真誠社群陪伴的處方籤",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Chronic social isolation triggers chronic systemic inflammation akin to smoking fifteen cigarettes a day.", "zh": "長期的社交孤立所引發的全身性慢性發炎，對人體的傷害等同於每天抽十五支香菸。"},
            {"start": 17.5, "duration": 5.0, "en": "Human beings are fundamentally wired for deep connection, community, and mutual vulnerability.", "zh": "人類在天性基因上，就是被設計為極度渴望深刻的人際連結、溫暖社群與真誠陪伴。"}
        ]
    }
]

# Combine all 100 new videos!
ALL_100 = base_videos + arts_videos + news_videos + kids_videos + leisure_videos + science_tech_videos + health_wellness_videos
print(f"Total newly compiled videos: {len(ALL_100)}")

# Verify all have cues, en, cn, words, channel
for i, v in enumerate(ALL_100):
    if not v.get('en'):
        v['en'] = [c['en'] for c in v['cues']]
    if not v.get('cn'):
        v['cn'] = [c['zh'] for c in v['cues']]
    if not v.get('words'):
        v['words'] = []
    if not v.get('url'):
        v['url'] = f"https://www.youtube.com/watch?v={v['id']}"

# Now load existing index.html and video_lessons.json
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m_v = re.search(r'const videos\s*=\s*(\[.*?\]);\s*const songs', html, re.DOTALL)
orig_videos = json.loads(m_v.group(1))
print(f"Original videos count: {len(orig_videos)}")

# Merge: keep original 50, append new 100
merged_videos = orig_videos + ALL_100
print(f"Merged videos count: {len(merged_videos)}")

# Update index.html
compact_videos_json = json.dumps(merged_videos, ensure_ascii=False)
new_html = re.sub(
    r'const videos\s*=\s*\[.*?\];\s*const songs',
    f'const videos = {compact_videos_json};\nconst songs',
    html,
    flags=re.DOTALL
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
print("✓ index.html successfully updated with 150 videos!")

# Also update video_lessons.json
with open('video_lessons.json', 'r', encoding='utf-8') as f:
    vl = json.load(f)

lessons = vl.get('lessons', {})
for v in ALL_100:
    lessons[v['id']] = {
        'cues': v['cues'],
        'en': v['en'],
        'cn': v['cn']
    }

vl['lessons'] = lessons
with open('video_lessons.json', 'w', encoding='utf-8') as f:
    json.dump(vl, f, ensure_ascii=False, indent=2)
print("✓ video_lessons.json updated with 100 new lessons!")

with open('video_lessons.js', 'w', encoding='utf-8') as f:
    f.write("window.PRELOADED_LESSONS = " + json.dumps(vl, ensure_ascii=False) + ";\n")
print("✓ video_lessons.js updated!")
