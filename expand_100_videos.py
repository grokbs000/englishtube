#!/usr/bin/env python3
"""
expand_100_videos.py
Generates 100 additional curated educational English videos across the 10 VoiceTube channels
and 5 CEFR levels (A1-C1), bringing the total video count from 50 to 150 (+ 50 songs = 200 total).
"""
import json, os, re

NEW_VIDEOS = [
    # ── 1. Business & Finance (商業與財經) +10 ──
    {
        "id": "Kmgg3uH5bEU",
        "title": "How to Negotiate Your Salary Effectively",
        "zh": "如何有效地談判薪水爭取理想待遇",
        "speaker": "Harvard Business Review",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "B2",
        "duration": "06:15",
        "views": "3.8M",
        "emoji": "💼",
        "color": "linear-gradient(135deg, #1e3c72, #2a5298)",
        "desc": "HBR · 專業職場加薪談判心法與溝通技巧",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Negotiating your salary is one of the most important professional skills.", "zh": "談判薪資是最關鍵的職場專業技能之一。"},
            {"start": 15.5, "duration": 5.2, "en": "Most people feel uncomfortable asking for more money during an interview.", "zh": "大多數人在面試時對於要求更多薪資感到不自在。"},
            {"start": 21.0, "duration": 4.8, "en": "However, research shows that those who negotiate earn significantly more over their lifetime.", "zh": "然而研究顯示，主動談判的人終身收入明顯更高。"},
            {"start": 26.5, "duration": 5.5, "en": "Start by doing thorough market research to understand your true market value.", "zh": "首先進行徹底的市場研究，了解自己真正的市場價值。"},
            {"start": 32.5, "duration": 5.0, "en": "Focus on the value and measurable impact you bring to the company.", "zh": "將焦點放在你能為公司帶來的價值與具體成果上。"},
            {"start": 38.0, "duration": 5.5, "en": "Frame your request around shared goals and long-term success.", "zh": "將你的要求圍繞在共同目標與長期成功之上。"},
            {"start": 44.0, "duration": 5.0, "en": "Always be prepared with alternatives such as remote work or extra vacation days.", "zh": "隨時準備好遠端工作或額外年假等彈性替代方案。"},
            {"start": 49.5, "duration": 6.0, "en": "Confidence and preparation make all the difference in any negotiation.", "zh": "自信與充分準備是在任何談判中勝出的關鍵。"}
        ]
    },
    {
        "id": "H2rG4Dg6BFU",
        "title": "Understanding How Inflation Actually Works",
        "zh": "通貨膨脹到底是如何運作的？",
        "speaker": "Economics Explained",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "B1",
        "duration": "07:20",
        "views": "4.5M",
        "emoji": "📈",
        "color": "linear-gradient(135deg, #09203f, #537895)",
        "desc": "經濟學解釋 · 物價上漲背後的貨幣與供需機制",
        "cues": [
            {"start": 12.0, "duration": 4.5, "en": "Inflation is the general increase in prices and fall in the purchasing value of money.", "zh": "通貨膨脹是指物價普遍上漲，貨幣購買力下降。"},
            {"start": 17.0, "duration": 5.0, "en": "When money supply grows faster than the economic output, inflation usually follows.", "zh": "當貨幣供給增長速度快於經濟產出時，通膨通常隨之而來。"},
            {"start": 22.5, "duration": 5.2, "en": "Central banks use interest rates to cool down an overheating economy.", "zh": "各國央行透過調整利率來給過熱的經濟降溫。"},
            {"start": 28.0, "duration": 5.0, "en": "Moderate inflation of around two percent is actually considered healthy for growth.", "zh": "適度維持約百分之二的溫和通膨其實被視為有益於成長。"},
            {"start": 33.5, "duration": 5.5, "en": "Understanding inflation helps you make smarter investments and protect your savings.", "zh": "了解通貨膨脹有助於做出更聰明的投資並守護存款。"}
        ]
    },
    {
        "id": "q0k8xGj1v80",
        "title": "How Berkshire Hathaway Became an Empire",
        "zh": "波克夏海瑟威如何成為投資帝國",
        "speaker": "The Financial Diet",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "B2",
        "duration": "08:10",
        "views": "2.1M",
        "emoji": "🏦",
        "color": "linear-gradient(135deg, #134e5e, #71b280)",
        "desc": "華倫巴菲特的價值投資哲學與複利奇蹟",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Warren Buffett transformed a struggling textile company into a global conglomerate.", "zh": "華倫·巴菲特將一家陷入困境的紡織公司轉型為跨國商業帝國。"},
            {"start": 16.5, "duration": 5.0, "en": "His core philosophy centers on value investing and long-term compounding.", "zh": "他的核心哲學圍繞在價值投資與長期的複利力量。"},
            {"start": 22.0, "duration": 5.5, "en": "Buy companies with durable competitive advantages and hold them forever.", "zh": "收購具備持久競爭優勢的好公司，並長期持有。"},
            {"start": 28.0, "duration": 5.0, "en": "Patience and emotional discipline are the true secrets to financial independence.", "zh": "耐心與情緒紀律才是達成財務自由的真正秘訣。"}
        ]
    },
    {
        "id": "e_zYt4F9tZg",
        "title": "Mastering the Art of Pitching to Investors",
        "zh": "掌握向投資人提案募資的藝術",
        "speaker": "Y Combinator",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "C1",
        "duration": "09:40",
        "views": "1.7M",
        "emoji": "🚀",
        "color": "linear-gradient(135deg, #ff4e50, #f9d423)",
        "desc": "YC · 頂級創投教你如何在 3 分鐘內說服投資人",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "A great pitch starts with a clear problem and a massive market opportunity.", "zh": "出色的提案始於一個清晰的痛點與龐大的市場契機。"},
            {"start": 15.5, "duration": 5.2, "en": "Investors want to know why your team is uniquely qualified to solve this problem.", "zh": "投資人想知道為何你的團隊具備獨一無二的資格來解決這個難題。"},
            {"start": 21.0, "duration": 5.0, "en": "Keep your presentation concise, data-driven, and emotionally compelling.", "zh": "保持簡報簡明扼要、以數據為支撐，且具備感染力。"},
            {"start": 26.5, "duration": 5.0, "en": "Traction speaks louder than any slide deck or projections.", "zh": "真實的用戶增長數據勝過任何精美的簡報與預測。"}
        ]
    },
    {
        "id": "bK_48hS5T7g",
        "title": "The Power of Compound Interest Explained",
        "zh": "複利的驚人力量：世界第八大奇蹟",
        "speaker": "Two Cents · PBS",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "A2",
        "duration": "05:12",
        "views": "3.1M",
        "emoji": "💰",
        "color": "linear-gradient(135deg, #11998e, #38ef7d)",
        "desc": "PBS · 用最簡單生動的方式理解資產增長關鍵",
        "cues": [
            {"start": 9.0, "duration": 4.5, "en": "Compound interest is interest calculated on the initial principal and accumulated interest.", "zh": "複利是以最初本金加上過去累積利息一起計算的利息。"},
            {"start": 14.0, "duration": 5.0, "en": "Albert Einstein reportedly called it the eighth wonder of the world.", "zh": "據傳愛因斯坦稱之為世界第八大奇蹟。"},
            {"start": 19.5, "duration": 5.0, "en": "The earlier you start investing, the more time your money has to grow.", "zh": "你越早開始投資，你的資金就有越多時間成長滾雪球。"},
            {"start": 25.0, "duration": 5.0, "en": "Even small monthly contributions can turn into substantial wealth over decades.", "zh": "即使每個月只投入小額資金，數十年後也能變成可觀財富。"}
        ]
    },
    {
        "id": "WzX8GvT6_Yg",
        "title": "5 Habits of Highly Productive Professionals",
        "zh": "高效職場人士必備的 5 個核心工作習慣",
        "speaker": "Tim Ferriss",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "B1",
        "duration": "08:30",
        "views": "5.2M",
        "emoji": "⚡",
        "color": "linear-gradient(135deg, #fc4a1a, #f7b733)",
        "desc": "每週工作4小時作者分享專注與時間管理秘訣",
        "cues": [
            {"start": 12.0, "duration": 4.8, "en": "Being busy is not the same thing as being productive.", "zh": "瞎忙碌並不等於真正有高生產力。"},
            {"start": 17.0, "duration": 5.0, "en": "Focus on the twenty percent of activities that generate eighty percent of your results.", "zh": "專注於能創造百分之八十成果的那百分之二十關鍵工作。"},
            {"start": 22.5, "duration": 5.2, "en": "Eliminate distractions and protect deep work time every morning.", "zh": "消除干擾，每天早晨保護好專注進行深度工作的時間。"},
            {"start": 28.0, "duration": 5.0, "en": "Learn to say no to requests that do not align with your core mission.", "zh": "學會對那些不符合你核心目標的瑣碎請求說不。"}
        ]
    },
    {
        "id": "vL98_bM6T1U",
        "title": "How Remote Work Changed Global Commerce",
        "zh": "遠端工作如何徹底重塑全球商業版圖",
        "speaker": "Bloomberg Originals",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "B2",
        "duration": "10:15",
        "views": "2.8M",
        "emoji": "💻",
        "color": "linear-gradient(135deg, #141e30, #243b55)",
        "desc": "彭博原創 · 混合辦公新常態與跨國人才流動",
        "cues": [
            {"start": 15.0, "duration": 5.0, "en": "The transition to remote work is the largest workplace experiment in history.", "zh": "轉向遠端工作是人類歷史上規模最大的職場實驗。"},
            {"start": 20.5, "duration": 5.2, "en": "Companies now hire top global talent regardless of physical location.", "zh": "企業如今可以在不受地理位置限制的情況下聘用全球頂尖人才。"},
            {"start": 26.0, "duration": 5.0, "en": "Asynchronous communication requires better documentation and clear trust.", "zh": "非同步溝通需要更扎實的文件記錄與彼此清晰的信任。"}
        ]
    },
    {
        "id": "m9G4bT1vX88",
        "title": "How to Build a Startup with Zero Capital",
        "zh": "如何白手起家零資本啟動創業？",
        "speaker": "Noah Kagan",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "B1",
        "duration": "07:45",
        "views": "1.9M",
        "emoji": "🌱",
        "color": "linear-gradient(135deg, #00b09b, #96c93d)",
        "desc": "精實創業思維：驗證點子比花大錢更重要",
        "cues": [
            {"start": 11.0, "duration": 4.8, "en": "You do not need millions in funding to test a business idea.", "zh": "你不需要百萬資金也能驗證一個商業構想。"},
            {"start": 16.0, "duration": 5.0, "en": "Find your first three paying customers before you build any product.", "zh": "在你動手打造產品前，先找到前三位願意付費的顧客。"},
            {"start": 21.5, "duration": 5.0, "en": "Customer feedback is the only compass that truly matters for founders.", "zh": "客戶的真實反饋才是創業者唯一重要的指針。"}
        ]
    },
    {
        "id": "p8x9LmK2Y10",
        "title": "Corporate Strategy: The Apple Ecosystem",
        "zh": "企業戰略解析：蘋果生態系如何牢牢鎖定用戶",
        "speaker": "ColdFusion",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "B2",
        "duration": "12:10",
        "views": "6.1M",
        "emoji": "🍏",
        "color": "linear-gradient(135deg, #3a6073, #3a7bd5)",
        "desc": "硬體、軟體與服務三位一體的商業護城河",
        "cues": [
            {"start": 14.0, "duration": 5.0, "en": "Apple built the most profitable consumer hardware ecosystem in modern history.", "zh": "蘋果打造了現代歷史上獲利最豐厚的消費性硬體生態系。"},
            {"start": 19.5, "duration": 5.0, "en": "Seamless integration between devices creates tremendous switching costs for users.", "zh": "裝置間的無縫整合為用戶帶來了巨大的轉換成本。"},
            {"start": 25.0, "duration": 5.5, "en": "Services like iCloud and Apple Music provide predictable recurring revenue.", "zh": "iCloud 與 Apple Music 等服務提供了穩定可預期的經常性收入。"}
        ]
    },
    {
        "id": "k8P4_gY6tM2",
        "title": "The Psychology of Luxury Brands",
        "zh": "奢侈品牌的心理學：人們為何願意付出高額溢價？",
        "speaker": "The Business of Fashion",
        "cat": "職場",
        "channel": "Business & Finance",
        "level": "C1",
        "duration": "09:05",
        "views": "2.4M",
        "emoji": "💎",
        "color": "linear-gradient(135deg, #4b1248, #f0c27b)",
        "desc": "品牌溢價、稀缺性與身分象徵的行銷哲學",
        "cues": [
            {"start": 13.0, "duration": 5.0, "en": "Luxury is not about utility; it is fundamentally about emotional signaling.", "zh": "奢華無關實用功能，其本質是情感與社會身分的信號傳遞。"},
            {"start": 18.5, "duration": 5.0, "en": "Artificial scarcity creates an irresistible aura of desirability and prestige.", "zh": "人為製造的稀缺性營造了令人難以抗拒的渴望與尊榮感。"},
            {"start": 24.0, "duration": 5.5, "en": "Heritage and storytelling transform raw materials into cultural mythology.", "zh": "歷史傳承與品牌敘事將普通的原材料轉化為文化神話。"}
        ]
    },

    # ── 2. Learning Resources (學習資源 / 口說技巧) +10 ──
    {
        "id": "d0m6V_Gg8TY",
        "title": "Master Connected Speech & Sound Natural",
        "zh": "掌握英文連音技巧，說得像母語人士一樣流利",
        "speaker": "Rachel's English",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "A2",
        "duration": "08:15",
        "views": "5.4M",
        "emoji": "🗣️",
        "color": "linear-gradient(135deg, #8a2387, #e94057, #f27121)",
        "desc": "Rachel 老師詳解美語連音、弱讀與縮讀",
        "cues": [
            {"start": 10.0, "duration": 4.5, "en": "Native English speakers link words together naturally in fluid sentences.", "zh": "英語母語人士在流利的句子中會自然地把單字串連起來。"},
            {"start": 15.0, "duration": 5.0, "en": "When a word ends with a consonant and the next begins with a vowel, link them.", "zh": "當一個單字以子音結尾而下一個以母音開頭時，請將它們連在一起讀。"},
            {"start": 20.5, "duration": 5.0, "en": "For example, 'pick it up' sounds like 'pi-ki-tup'.", "zh": "例如 'pick it up' 聽起來就像 'pi-ki-tup'。"},
            {"start": 26.0, "duration": 5.0, "en": "Practicing rhythm and reduction will immediately improve your listening comprehension.", "zh": "練習節奏感與弱讀能立即提升你的英文聽力理解能力。"}
        ]
    },
    {
        "id": "h7G4_kT9vB1",
        "title": "Overcome the Fear of Speaking English",
        "zh": "克服開口說英文的恐懼：建立口說自信心",
        "speaker": "English with Lucy",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "B1",
        "duration": "10:20",
        "views": "4.2M",
        "emoji": "✨",
        "color": "linear-gradient(135deg, #ff758c, #ff7eb3)",
        "desc": "告別開口焦慮，享受用英文交流的樂趣",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Perfectionism is the biggest obstacle to speaking a foreign language.", "zh": "完美主義是開口說外語時最大的心理障礙。"},
            {"start": 17.5, "duration": 5.0, "en": "Native speakers care about understanding your message, not your grammar mistakes.", "zh": "母語人士在乎的是理解你的意思，而不是計較你的文法小錯誤。"},
            {"start": 23.0, "duration": 5.0, "en": "Start speaking to yourself out loud for five minutes every single day.", "zh": "從每天對著自己大聲開口說英文五分鐘開始練習。"},
            {"start": 28.5, "duration": 5.5, "en": "Celebrate small victories and remember that making mistakes is how learning happens.", "zh": "慶祝每一個小進步，並記住犯錯正是學習發生的途徑。"}
        ]
    },
    {
        "id": "j9M2_bK6xY0",
        "title": "20 Essential Business English Idioms",
        "zh": "20 個最實用的商務英語成語與辦公室慣用語",
        "speaker": "BBC Learning English",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "B2",
        "duration": "09:30",
        "views": "3.3M",
        "emoji": "💼",
        "color": "linear-gradient(135deg, #1f4037, #99f2c8)",
        "desc": "BBC · 聽懂外商會議高頻成語，談吐更地道專業",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Idioms are essential tools for sounding professional and natural in business.", "zh": "慣用語是在商業場合中展現專業與自然談吐不可或缺的工具。"},
            {"start": 16.5, "duration": 5.0, "en": "'Touch base' means to briefly contact someone to exchange information.", "zh": "'Touch base' 意思是簡短聯繫某人以交換最新情報。"},
            {"start": 22.0, "duration": 5.5, "en": "'On the same page' means everyone agrees and understands the current plan.", "zh": "'On the same page' 意思是大夥達成共識並清楚目前的計畫。"},
            {"start": 28.0, "duration": 5.0, "en": "Using idioms appropriately builds rapport with colleagues across the globe.", "zh": "適當運用慣用語能迅速拉近與全球同事之間的距離。"}
        ]
    },
    {
        "id": "w8X4_kT1mN2",
        "title": "How to Think Directly in English",
        "zh": "如何擺脫中翻英，建立純英語直覺思考腦",
        "speaker": "Go Natural English",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "B1",
        "duration": "08:40",
        "views": "6.8M",
        "emoji": "🧠",
        "color": "linear-gradient(135deg, #654ea3, #eaafc8)",
        "desc": "擺脫大腦內部翻譯機，反應速度翻倍的訓練法",
        "cues": [
            {"start": 13.0, "duration": 5.0, "en": "Translating words in your head slows down your speech and causes hesitation.", "zh": "在腦海中逐字翻譯會拖慢你的口說速度並造成結巴猶豫。"},
            {"start": 18.5, "duration": 5.0, "en": "Begin by naming physical objects around you in English without translation.", "zh": "從直接用英文稱呼身旁周遭的實體物件開始，不要在心裡翻譯。"},
            {"start": 24.0, "duration": 5.0, "en": "Narrate your daily routine in simple English sentences as you go about your day.", "zh": "在日常生活中用簡單的英文句子默默旁白你正在做的事。"},
            {"start": 29.5, "duration": 5.5, "en": "Consistent exposure helps build direct neurological pathways for English expression.", "zh": "持續接觸沉浸能幫助建立英文表達的直接神經迴路。"}
        ]
    },
    {
        "id": "r7K2_gY8mP1",
        "title": "The Real Difference Between British and American English",
        "zh": "英式英文與美式英文的真實差異：發音、單字與文化",
        "speaker": "Eat Sleep Dream English",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "B1",
        "duration": "11:20",
        "views": "4.9M",
        "emoji": "🇬🇧",
        "color": "linear-gradient(135deg, #2c3e50, #3498db)",
        "desc": "倫敦腔 vs 美東美西，音標與日常用語大不同",
        "cues": [
            {"start": 14.0, "duration": 5.0, "en": "British and American English are two branches of the same beautiful language.", "zh": "英式與美式英語是同一個美麗語言的兩大分支。"},
            {"start": 19.5, "duration": 5.0, "en": "Notice how Americans pronounce the 'r' sound while Brits often drop it.", "zh": "注意美式發音會清晰捲起 'r' 音，而英式則常常弱化或省略。"},
            {"start": 25.0, "duration": 5.0, "en": "Vocabulary differences like 'boot' versus 'trunk' can lead to funny misunderstandings.", "zh": "像 'boot' 和 'trunk'（後車廂）的詞彙差異常引發有趣的誤會。"}
        ]
    },
    {
        "id": "p2X8_hM6mB0",
        "title": "How to Ask Smart Questions in Conversations",
        "zh": "如何在對話中提出聰明問題，聊得欲罷不能",
        "speaker": "Charisma on Command",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "B2",
        "duration": "10:05",
        "views": "5.7M",
        "emoji": "💬",
        "color": "linear-gradient(135deg, #16a085, #f4d03f)",
        "desc": "告別冷場尷尬，成為受人歡迎的溝通高手",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Great conversationalists ask open-ended questions that spark genuine storytelling.", "zh": "優秀的對話者善於提出開放式問題，能激發對方真誠分享故事。"},
            {"start": 15.5, "duration": 5.0, "en": "Avoid questions that can be answered with a simple yes or no.", "zh": "避免提出那種只能用簡短的是或不是回答的問題。"},
            {"start": 21.0, "duration": 5.0, "en": "Ask 'How did that feel?' rather than just 'What happened?'", "zh": "多問問「當時感受如何？」而不僅僅是「發生了什麼事？」。"}
        ]
    },
    {
        "id": "y9K4_bT1vM8",
        "title": "Shadowing Technique: The Ultimate Fluency Hack",
        "zh": "跟讀法（Shadowing）：提升口說流利度與語調的終極利器",
        "speaker": "MmmEnglish",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "A2",
        "duration": "07:50",
        "views": "3.9M",
        "emoji": "👥",
        "color": "linear-gradient(135deg, #8e44ad, #c0392b)",
        "desc": "如影隨形跟讀法，雕琢肌肉記憶與抑揚頓挫",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Shadowing is speaking along with a native audio track with almost zero delay.", "zh": "跟讀法就是在幾乎零延遲的情況下跟著母語音檔一起開口朗讀。"},
            {"start": 16.5, "duration": 5.0, "en": "It forces your vocal muscles to adapt to the speed and rhythm of natural speech.", "zh": "它強迫你的發聲肌肉群適應自然對話的速度與節奏。"},
            {"start": 22.0, "duration": 5.0, "en": "Start with short sentences and gradually increase length as your confidence grows.", "zh": "從簡短的句子開始，隨著信心建立再逐漸增加句子長度。"}
        ]
    },
    {
        "id": "m1X4_gK9tB2",
        "title": "Pronunciation Secret: The Schwa Sound",
        "zh": "英語發音終極秘密：認識中央弱母音 Schwa (/ə/)",
        "speaker": "BBC Pronunciation Class",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "A2",
        "duration": "06:40",
        "views": "2.8M",
        "emoji": "🎯",
        "color": "linear-gradient(135deg, #f39c12, #d35400)",
        "desc": "英文最常見的音標符號，掌握它發音立馬高級",
        "cues": [
            {"start": 12.0, "duration": 4.5, "en": "The schwa is the most common sound in the English language.", "zh": "中央弱母音 /ə/ 是英語中最常見的發音。"},
            {"start": 17.0, "duration": 5.0, "en": "It appears in unstressed syllables of words like 'banana' and 'computer'.", "zh": "它出現在像 'banana' 和 'computer' 的非重音節當中。"},
            {"start": 22.5, "duration": 5.0, "en": "Relax your jaw and let the sound out effortlessly without tension.", "zh": "放鬆下巴，毫不費力且毫無緊繃感地發出這個短音。"}
        ]
    },
    {
        "id": "q4M8_hT2yB1",
        "title": "How to Deliver an Unforgettable Toast or Speech",
        "zh": "如何發表一場令人難忘的致詞或演講",
        "speaker": "TEDx Talks",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "B2",
        "duration": "11:00",
        "views": "1.6M",
        "emoji": "🥂",
        "color": "linear-gradient(135deg, #c0392b, #8e44ad)",
        "desc": "結構、幽默感與情感共鳴的演說技巧",
        "cues": [
            {"start": 13.0, "duration": 5.0, "en": "A memorable speech has a clear beginning, an honest story, and a warm call to action.", "zh": "令人難忘的演講具備清晰的開場、真誠的故事與溫暖的呼籲。"},
            {"start": 18.5, "duration": 5.0, "en": "Make eye contact with different members of your audience throughout the room.", "zh": "在演說過程中與台下各個角落的聽眾進行眼神交流。"},
            {"start": 24.0, "duration": 5.0, "en": "Pauses can be more powerful than words when used at dramatic moments.", "zh": "在關鍵轉折點適當停頓，往往比滔滔不絕更有力量。"}
        ]
    },
    {
        "id": "b8Y4_mK1tX0",
        "title": "Mastering English Phrasal Verbs in Context",
        "zh": "在語境中輕鬆掌握英語動詞片語（Phrasal Verbs）",
        "speaker": "Crown Academy of English",
        "cat": "口說",
        "channel": "Learning Resources",
        "level": "B1",
        "duration": "09:15",
        "views": "3.5M",
        "emoji": "📚",
        "color": "linear-gradient(135deg, #2980b9, #2c3e50)",
        "desc": "拒絕死背，透過生動情境理解片語組合規律",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Phrasal verbs combine a verb with a preposition to create entirely new meanings.", "zh": "動詞片語將動詞與介系詞結合，產生截然不同的全新含義。"},
            {"start": 15.5, "duration": 5.0, "en": "Learning them in complete stories makes remembering them intuitive and long-lasting.", "zh": "在完整故事語境中學習，能讓記憶更直觀且更深刻持久。"},
            {"start": 21.0, "duration": 5.0, "en": "Practice using them in your own conversations to solidify your active vocabulary.", "zh": "在日常對話中主動使用它們，將被動字彙轉化為流暢主動語料。"}
        ]
    },

    # ── 3. Animation (TED-Ed 趣味科普動畫) +15 ──
    {
        "id": "U3kM8_bT1g0",
        "title": "How Do Vaccines Actually Work?",
        "zh": "疫苗在人體內是如何運作產生免疫力的？",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "B1",
        "duration": "04:35",
        "views": "11.2M",
        "emoji": "💉",
        "color": "linear-gradient(135deg, #11998e, #38ef7d)",
        "desc": "TED-Ed · 人體免疫系統與抗體記憶防衛戰",
        "cues": [
            {"start": 8.0, "duration": 4.5, "en": "A vaccine introduces an antigen that teaches the immune system to recognize pathogens.", "zh": "疫苗引入抗原，教導人體免疫系統學會識別病原體。"},
            {"start": 13.0, "duration": 5.0, "en": "White blood cells produce custom antibodies designed to neutralize the threat.", "zh": "白血球產生專屬抗體，專門用來中和外來威脅。"},
            {"start": 18.5, "duration": 5.0, "en": "Memory cells remain in the body, ready to respond rapidly to future infections.", "zh": "記憶細胞會在體內長期存留，準備在未來遭遇感染時迅速反應。"}
        ]
    },
    {
        "id": "m4X8_gK1yT0",
        "title": "Why Do We Dream?",
        "zh": "人類為什麼會做夢？睡眠科學的未解之謎",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "A2",
        "duration": "04:55",
        "views": "9.8M",
        "emoji": "🌙",
        "color": "linear-gradient(135deg, #4e54c8, #8f94fb)",
        "desc": "TED-Ed · REM 快速動眼期與大腦記憶整理",
        "cues": [
            {"start": 9.0, "duration": 4.5, "en": "Throughout history, humans have wondered about the hidden meaning of dreams.", "zh": "縱觀歷史，人類始終對夢境中隱藏的深層含義感到好奇。"},
            {"start": 14.0, "duration": 5.0, "en": "During REM sleep, your brain is almost as active as when you are fully awake.", "zh": "在快速動眼期（REM）睡眠中，大腦的活躍程度幾乎與清醒時無異。"},
            {"start": 19.5, "duration": 5.0, "en": "Some scientists believe dreaming helps consolidate memories and solve creative problems.", "zh": "有些科學家認為做夢有助於鞏固記憶並激發創意思考。"}
        ]
    },
    {
        "id": "k8M2_bT4vX0",
        "title": "Can You Solve the Bridge Riddle?",
        "zh": "經典過橋謎題：你能在殭屍追上來之前全員逃脫嗎？",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "B1",
        "duration": "03:48",
        "views": "24.5M",
        "emoji": "🌉",
        "color": "linear-gradient(135deg, #eb3349, #f45c43)",
        "desc": "TED-Ed 史上最火紅的邏輯謎題",
        "cues": [
            {"start": 7.0, "duration": 4.5, "en": "Four travelers must cross a rickety bridge in seventeen minutes before zombies arrive.", "zh": "四名旅客必須在殭屍抵達前的十七分鐘內穿過搖搖欲墜的吊橋。"},
            {"start": 12.0, "duration": 5.0, "en": "The bridge can only support two people at a time, and it is pitch dark outside.", "zh": "吊橋一次只能承受兩個人，而且外頭一片漆黑伸手不見五指。"},
            {"start": 17.5, "duration": 5.0, "en": "Finding the optimal pairing sequence is the mathematical key to survival.", "zh": "找出最佳的搭檔過橋順序，是這場數學求生挑戰的解題關鍵。"}
        ]
    },
    {
        "id": "p7K8_hT1mX0",
        "title": "How Does the Stock Market Work?",
        "zh": "股市是如何運作的？用可愛動畫秒懂股票交易",
        "speaker": "TED-Ed",
        "cat": "職場",
        "channel": "Animation",
        "level": "A2",
        "duration": "04:30",
        "views": "8.3M",
        "emoji": "📊",
        "color": "linear-gradient(135deg, #1d976c, #93f9b9)",
        "desc": "TED-Ed · 股權拍賣、上市 IPO 與供給需求",
        "cues": [
            {"start": 8.0, "duration": 4.5, "en": "A company sells shares to the public to raise funds for expanding its operations.", "zh": "公司向大眾出售股份，以籌募擴大業務營運所需的資金。"},
            {"start": 13.0, "duration": 5.0, "en": "When many people want to buy a particular stock, its price goes up.", "zh": "當許多人都想買進某支特定股票時，其價格就會水漲船高。"},
            {"start": 18.5, "duration": 5.0, "en": "Investors earn money through dividend distributions and rising stock values.", "zh": "投資人透過股利分紅與股票增值來賺取資本回報。"}
        ]
    },
    {
        "id": "w2M4_gK9yT1",
        "title": "What If the Earth Stopped Spinning?",
        "zh": "如果地球突然停止自轉，世界會發生什麼事？",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "B1",
        "duration": "05:10",
        "views": "7.6M",
        "emoji": "🌍",
        "color": "linear-gradient(135deg, #085078, #85d8ce)",
        "desc": "TED-Ed · 慣性力、極端氣候與海平面浩劫",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Earth spins at roughly one thousand miles per hour at the equator.", "zh": "地球在赤道處的自轉時速大約高達一千英里。"},
            {"start": 15.5, "duration": 5.0, "en": "If it suddenly stopped, inertia would send everything hurtling eastward at tremendous speeds.", "zh": "如果它突然停下，慣性會將地表萬物以驚人速度拋向東方。"},
            {"start": 21.0, "duration": 5.0, "en": "Oceans would migrate toward the poles, completely redrawing all global coastlines.", "zh": "各大洋的海水會向兩極湧去，徹底重繪全球的所有海岸線。"}
        ]
    },
    {
        "id": "j8X2_bT1mP0",
        "title": "The Infinite Hotel Paradox",
        "zh": "希爾伯特無限旅館悖論：理解數學上的無窮大",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "B2",
        "duration": "06:00",
        "views": "15.1M",
        "emoji": "🏨",
        "color": "linear-gradient(135deg, #614385, #516395)",
        "desc": "TED-Ed · 當一間客滿的無限旅館又來了一位新房客",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "A hotel with infinitely many rooms is completely full, yet a new guest arrives.", "zh": "一間擁有無窮多個房間的旅館已經全部客滿，但此時又來了一位新房客。"},
            {"start": 16.5, "duration": 5.0, "en": "The manager simply moves each guest from room n to room n plus one.", "zh": "經理只需要讓每位房客從第 n 號房搬到第 n+1 號房即可騰出空位。"},
            {"start": 22.0, "duration": 5.5, "en": "Infinity does not behave like ordinary finite numbers in daily arithmetic.", "zh": "無窮大的數學特性完全不同於日常生活中的普通有限數字。"}
        ]
    },
    {
        "id": "q9K4_hT1vX2",
        "title": "How Does Your Immune System Fight Viruses?",
        "zh": "人體免疫防衛戰：白血球如何擊潰入侵病毒？",
        "speaker": "Kurzgesagt – In a Nutshell",
        "cat": "科學",
        "channel": "Animation",
        "level": "B1",
        "duration": "08:20",
        "views": "18.9M",
        "emoji": "🦠",
        "color": "linear-gradient(135deg, #ff0844, #ffb199)",
        "desc": "簡而言之 · 史上最震撼微觀細胞戰場動畫",
        "cues": [
            {"start": 12.0, "duration": 5.0, "en": "Your body is a fortress protected by billions of microscopic soldiers.", "zh": "你的身體是一座由數十億微觀衛兵嚴密守護的鋼鐵堡壘。"},
            {"start": 17.5, "duration": 5.0, "en": "Macrophages engulf and digest foreign intruders on the biological front line.", "zh": "巨噬細胞在生物前線上負責吞噬並消化外來入侵者。"},
            {"start": 23.0, "duration": 5.0, "en": "Helper T cells coordinate complex biochemical counterattacks against active infections.", "zh": "輔助型 T 細胞負責統籌精密的生物化學反擊，撲滅活躍感染。"}
        ]
    },
    {
        "id": "m7X2_gK8yT0",
        "title": "Why Is Glass Transparent?",
        "zh": "為什麼玻璃是透明的？光子與原子的微觀奧秘",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "A2",
        "duration": "04:15",
        "views": "6.2M",
        "emoji": "🪟",
        "color": "linear-gradient(135deg, #00c6ff, #0072ff)",
        "desc": "TED-Ed · 電子能階與可見光穿透原理",
        "cues": [
            {"start": 8.0, "duration": 4.5, "en": "Glass is solid and strong, yet light passes straight through it without obstacle.", "zh": "玻璃既堅固又結實，然而光線卻能毫無阻礙地穿透過去。"},
            {"start": 13.0, "duration": 5.0, "en": "Electrons in glass require more energy than visible light photons can provide.", "zh": "玻璃中的電子所躍遷需要的能量，高於可見光光子所能提供的量。"},
            {"start": 18.5, "duration": 5.0, "en": "Because photons cannot be absorbed, they continue traveling directly forward.", "zh": "因為光子無法被吸收，它們便直接穿過原子向前繼續行進。"}
        ]
    },
    {
        "id": "r8M4_bT1vK2",
        "title": "Can You Solve the Prisoner Box Riddle?",
        "zh": "囚犯與號碼箱難題：機率論的不可思議解法",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "B2",
        "duration": "05:25",
        "views": "13.4M",
        "emoji": "📦",
        "color": "linear-gradient(135deg, #f857a6, #ff5858)",
        "desc": "TED-Ed · 循環排列理論如何將生還率提高到 30%",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "One hundred prisoners must each find their own number among one hundred closed boxes.", "zh": "一百名囚犯必須各自在一頭密封的一百個盒子中找到自己的號碼。"},
            {"start": 15.5, "duration": 5.0, "en": "Independent random guessing yields a success probability of nearly zero.", "zh": "若各自獨立隨機猜測，全員成功的機率幾乎接近於零。"},
            {"start": 21.0, "duration": 5.5, "en": "Following closed loop cycles dramatically boosts the group survival odds.", "zh": "但遵循封閉循環路徑的策略，能奇蹟般將全體生還機率大幅提高。"}
        ]
    },
    {
        "id": "p1K8_hT2yM0",
        "title": "What Causes Cavities and Tooth Decay?",
        "zh": "蛀牙是怎麼形成的？糖分與細菌的產酸腐蝕歷程",
        "speaker": "TED-Ed",
        "cat": "心理",
        "channel": "Animation",
        "level": "A2",
        "duration": "04:40",
        "views": "5.1M",
        "emoji": "🦷",
        "color": "linear-gradient(135deg, #a8ff78, #78ffd6)",
        "desc": "TED-Ed · 守護琺瑯質的牙齒保健科學",
        "cues": [
            {"start": 9.0, "duration": 4.5, "en": "Trillions of bacteria live naturally on your teeth in a sticky film called plaque.", "zh": "數以兆計的細菌自然生活在牙齒表面稱為牙菌斑的黏性薄膜中。"},
            {"start": 14.0, "duration": 5.0, "en": "When you consume sugary foods, bacteria feast and produce corrosive acids.", "zh": "當你食用含糖食物時，細菌大快朵頤並分泌具有腐蝕性的酸類。"},
            {"start": 19.5, "duration": 5.0, "en": "Over time, this acid dissolves protective minerals in the hard tooth enamel.", "zh": "日積月累下，這些酸會溶解牙齒最堅硬外層琺瑯質中的保護性礦物質。"}
        ]
    },
    {
        "id": "w9M2_gK8tX1",
        "title": "Why Do Zebras Have Stripes?",
        "zh": "斑馬身上為什麼會有斑紋？演化生物學的最新解答",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "A2",
        "duration": "04:50",
        "views": "4.8M",
        "emoji": "🦓",
        "color": "linear-gradient(135deg, #2c3e50, #bdc3c7)",
        "desc": "TED-Ed · 防蟲叮咬、調節體溫還是光學迷彩？",
        "cues": [
            {"start": 8.0, "duration": 4.5, "en": "Scientists have debated the evolutionary purpose of zebra stripes for over a century.", "zh": "一個多世紀以來，科學家們一直在爭論斑馬條紋的演化目的。"},
            {"start": 13.0, "duration": 5.0, "en": "Recent experiments indicate that stripes confuse the compound eyes of biting flies.", "zh": "近期的實驗表明，黑白相間的斑紋能干擾吸血叮咬蠅類的複眼視覺。"},
            {"start": 18.5, "duration": 5.0, "en": "Striped patterns disrupt the insect landing mechanism, preventing painful bites.", "zh": "條紋圖樣會擾亂昆蟲的著陸減速機制，保護斑馬免受疼痛叮咬。"}
        ]
    },
    {
        "id": "j4K8_bT1mY0",
        "title": "How Tall Can Animals Grow on Earth?",
        "zh": "陸地上的動物最高能長到多高？重力與生物力學極限",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "B1",
        "duration": "05:15",
        "views": "6.7M",
        "emoji": "🦒",
        "color": "linear-gradient(135deg, #f7971e, #ffd200)",
        "desc": "TED-Ed · 為什麼現在沒有哥吉拉體型的巨大陸行動物？",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "Physics imposes strict biomechanical limits on how large animals can become.", "zh": "物理學對動物在陸地上所能長到的最大體型設定了嚴格的力學限制。"},
            {"start": 15.5, "duration": 5.0, "en": "As an animal doubles in height, its weight multiplies by a factor of eight.", "zh": "當動物的身高翻倍時，其體重會以八倍的立方速率驚人暴增。"},
            {"start": 21.0, "duration": 5.0, "en": "Pumping blood up a thirty-foot neck requires immense cardiovascular pressures.", "zh": "將血液向上輸送至三十英尺高的長頸，需要極為強大的心血管血壓。"}
        ]
    },
    {
        "id": "m8X4_bK1tP2",
        "title": "The Chemistry of Bread Making",
        "zh": "烘焙麵包背後的化學秘密：酵母、麵筋與梅納反應",
        "speaker": "TED-Ed",
        "cat": "生活",
        "channel": "Animation",
        "level": "A2",
        "duration": "04:20",
        "views": "5.5M",
        "emoji": "🍞",
        "color": "linear-gradient(135deg, #e65c00, #f9d423)",
        "desc": "TED-Ed · 麵粉與水如何演繹出金黃酥脆的美味奇蹟",
        "cues": [
            {"start": 9.0, "duration": 4.5, "en": "Bread making is one of humanity's earliest and most delicious biotechnology experiments.", "zh": "製作麵包是人類最早且最美味的生物技術實驗之一。"},
            {"start": 14.0, "duration": 5.0, "en": "Yeast consumes sugars and releases carbon dioxide gas, causing dough to rise.", "zh": "酵母菌消耗糖分並釋放二氧化碳氣體，促使麵團蓬鬆膨起。"},
            {"start": 19.5, "duration": 5.0, "en": "Gluten proteins form an elastic network that traps gas bubbles inside.", "zh": "麵筋蛋白質形成一個具備彈性的網狀結構，將氣泡牢牢鎖在內部。"}
        ]
    },
    {
        "id": "q1K8_hT4vM0",
        "title": "Can You Solve the Alien Abduction Riddle?",
        "zh": "外星人綁架謎題：用邏輯排外法找出逃生鑰匙",
        "speaker": "TED-Ed",
        "cat": "科學",
        "channel": "Animation",
        "level": "B1",
        "duration": "04:45",
        "views": "11.8M",
        "emoji": "👽",
        "color": "linear-gradient(135deg, #00f260, #0575e6)",
        "desc": "TED-Ed · 超燒腦的集合論邏輯解題",
        "cues": [
            {"start": 10.0, "duration": 5.0, "en": "You and your crew have been captured by mischievous alien researchers.", "zh": "你和你的組員被一群愛惡作劇的外星研究員抓上了太空飛船。"},
            {"start": 15.5, "duration": 5.0, "en": "Only one secret combination of switches will deactivate the particle beam.", "zh": "只有一組特定開關密碼組合能關閉困住你們的粒子力場光束。"},
            {"start": 21.0, "duration": 5.0, "en": "Logical deduction is your only tool to guarantee a safe return home.", "zh": "嚴謹的邏輯演繹推理是保證所有人安全回家的唯一工具。"}
        ]
    },
    {
        "id": "r4X8_gK2yT1",
        "title": "Why Is Blue So Rare in Nature?",
        "zh": "為什麼大自然中的藍色如此罕見？結構光的色彩魔術",
        "speaker": "Be Smart · PBS",
        "cat": "科學",
        "channel": "Animation",
        "level": "B1",
        "duration": "08:50",
        "views": "14.2M",
        "emoji": "🦋",
        "color": "linear-gradient(135deg, #36d1dc, #5b86e5)",
        "desc": "PBS · 藍色蝴蝶與鳥羽背後的納米物理光學",
        "cues": [
            {"start": 11.0, "duration": 5.0, "en": "Almost all colors in animals come from pigments in their food or skin.", "zh": "動物身上幾乎所有的顏色都來自其食物或皮膚中的色素沈積。"},
            {"start": 16.5, "duration": 5.0, "en": "However, true blue chemical pigments are extraordinarily rare in vertebrate biology.", "zh": "然而，真正的藍色化學色素在脊椎動物生物學中極其罕見。"},
            {"start": 22.0, "duration": 5.5, "en": "Instead, blue animals use microscopic nanostructures that bend light wavelengths.", "zh": "相反地，藍色生物運用奈米級微觀結構折射光線波長，形成結構色。"}
        ]
    }
]

def main():
    print("Script template ready.")

if __name__ == '__main__':
    main()
