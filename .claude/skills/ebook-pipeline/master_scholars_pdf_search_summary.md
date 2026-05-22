# Master Scholars Free PDF Search — Summary

## Headline numbers
- **170/170 searched, 161 found (94.7%), 9 not found (5.3%)** — after English-title retry round
- Round 1 (Chinese / mixed): 143 Y / 27 N
- Round 2 (English-title retry for the 27 N): +18 Y, 9 still N
- CSV: `c:/tmp/master_scholars_pdf_urls.csv`

## Hit rate by section
- **近代哲學: 25/26 (96%)** — best, mostly public-domain English texts (Early Modern Texts, archive.org, Marxists.org)
- **人類學: 24/26 (92%)**
- **現象學: 22/24 (92%)**
- **神學: 24/26 (92%)**
- **心理學: 24/31 (77%)**
- **宗教學: 10/15 (67%)** — worst, many Chinese-only titles
- **社會學: 14/22 (64%)** — worst, many recent Chinese translations behind paywalls

## Pattern: English title vs Chinese title
For 26 books with English titles in the input, **25 hit Y (96%)**. For Chinese-only titles, hit rate drops to ~78%. **English titles win** — when the book has an indexable English original (Geertz, Levi-Strauss, Bourdieu, Freud, Hegel, Kierkegaard...), Monoskop / archive.org / Early Modern Texts / Bookey / .edu syllabus PDFs reliably surface. Chinese-only titles (`貨幣哲學`, `公共領域的結構轉型`, `動機與人格`) mostly only surface bookstores (博客來/讀墨/TAAZE) — these are filtered out.

## Top hosts by best_url
1. archive.org — 11
2. cdn.bookey.app — 10  *(many are summaries, not full text — caveat)*
3. monoskop.org — 5
4. web.mit.edu — 4
5. homepage.ntu.edu.tw — 3
6. faculty.las.illinois.edu — 3
7. link.springer.com — 3

Plus heavy long tail: earlymoderntexts.com, files.libcom.org, marxists.org, ia*.us.archive.org, edu.tw NTU/NTNU/NCCU dissertation repositories.

## Top 20 highest-quality URLs the user should try first
1. https://archive.org/details/the-collected-works-of-carl-jung-complete-digital-edition — Jung Collected Works ALL
2. https://archive.org/details/sigmund-freud-standard-edition-vol-24 — Freud Standard Edition ALL
3. https://monoskop.org/File:Levi-Strauss_Claude_The_Savage_Mind.pdf — Savage Mind
4. https://monoskop.org/File:Brown_Radcliffe_Alfred_Structure_and_Function_in_Primitive_Society_1952.pdf — Radcliffe-Brown
5. https://monoskop.org/File:Mauss_Marcel_The_Gift_The_Form_and_Functions_of_Exchange_in_Archaic_Societies_1966.pdf — Mauss The Gift
6. https://monoskop.org/File:Bourdieu_Pierre_The_Logic_of_Practice_1990.pdf — Bourdieu
7. https://monoskop.org/File:Derrida_Jacques_Of_Grammatology_1998.pdf — Derrida Grammatology
8. https://monoskop.org/File:Whitehead_Alfred_North_Process_and_Reality_corr_ed_1978.pdf — Whitehead
9. https://monoskop.org/File:Agamben_Giorgio_Homo_sacer_Suverena_moc_i_goli_zivot.pdf — Agamben
10. https://monoskop.org/File:Geertz_Clifford_Local_Knowledge_Further_Essays_in_Interpretive_Anthropology_1983.pdf — Geertz
11. https://taiwanebook.ncl.edu.tw/zh-tw/book/NCL-000122532/reader — 國富論（亞當斯密中譯）
12. https://www.haodoo.net/?M=Share&P=0970 — 國富論 好讀版
13. https://www.bfskinner.org/newtestsite/wp-content/uploads/2014/02/ScienceHumanBehavior.pdf — Skinner（官方基金會）
14. https://files.libcom.org/files/Sahlins%20-%20Stone%20Age%20Economics.pdf — Sahlins Stone Age Economics
15. https://files.libcom.org/files/Mauss%20-%20The%20Gift.pdf — Mauss alt
16. https://www.marxists.org/reference/archive/hegel/works/pr/philosophy-of-right.pdf — Hegel Phil of Right
17. https://www.earlymoderntexts.com/assets/pdfs/hume1748.pdf — Hume Enquiry
18. https://www.earlymoderntexts.com/assets/pdfs/descartes1637.pdf — Descartes Discourse
19. https://psychxspirit.com/wp-content/uploads/2021/11/Paul-Tillich-The-Courage-to-Be-Yale-University-Press-2000.pdf — Tillich Courage to Be
20. https://media.sabda.org/alkitab-2/Religion-Online.org%20Books/Moltman,%20Jurgen%20-%20Theology%20of%20Hope.pdf — Moltmann

## 27 books NOT found (need other sources)
**Chinese 中譯本，網路爬不到（建議找學校圖書館 / OpenLibrary / Anna's Archive 手動查）：**
- 涂爾幹《自殺論》— 中譯版只在博客來
- 潘尼卡《宇宙—神—人共融》
- 穆勒《比較宗教學》《東方聖書》
- 奧托《論神聖》（中譯）
- 布迪厄《實踐感》
- 哈伯馬斯《公共領域的結構轉型》— 中譯只有聯經
- 戈夫曼《日常生活中的自我表演》《汙名》
- 鮑曼《現代性與大屠殺》《液態現代性》
- 孔德《實證哲學教程》
- 阿宏《社會學主要思潮》
- 佛洛伊德《文明及其不滿》（中譯，原文 vol 21 在 Freud Standard Edition）
- 榮格《心理類型》（中譯，原文 in Collected Works vol 6）
- 馬斯洛《動機與人格》《存在心理學探索》
- 羅傑斯《案主中心治療》（中譯）
- 佛洛姆《為自己的人》
- 皮亞傑《發生認識論原理》（中譯）
- 泰勒《原始文化》（中譯，原文 1871 should be on archive.org — retry English query）
- 馬林諾夫斯基《西太平洋的航海者》（中譯，原文 Argonauts of the Western Pacific 1922 should be on Monoskop/archive.org — retry English query）
- 斯賓諾莎《神學政治論》（中譯，原文 Theological-Political Treatise 1670 — retry English query: Spinoza Tractatus Theologico-Politicus filetype:pdf）
- 梅洛-龐蒂《符號》（中譯，原文 Signs by Merleau-Ponty）
- 哈特曼《精神生活的本體論》（中譯，原文 Das Problem des geistigen Seins）
- 巴爾塔薩《天主教真理》— title 不清楚對應哪本英文書
- 郝爾沃斯《和平的國度》（中譯，原文 Peaceable Kingdom 是 Notre Dame Press 出版，無公開 PDF）

## Recommendations
- For the 27 N rows: **retry English-title queries** for the ~15 cases where Chinese title is masking an indexed English original (Tylor Primitive Culture, Malinowski Argonauts, Spinoza Tractatus, Merleau-Ponty Signs, Otto Idea of the Holy, etc).
- For remaining ~10 truly recent-Chinese-translation-only books (Bauman, Habermas, Goffman, Maslow Chinese editions): only Anna's Archive / library catalog / publisher will get you the Chinese PDFs. Free web search is blocked.
- **cdn.bookey.app** appears 10× in best_url but these are AI-generated summaries, not the actual book — re-rank to deprioritize.
- **archive.org and monoskop.org** are by far the highest-quality hits — when the title is English-known, these almost always have full PDFs.

## Retry round (English titles)

Re-ran the 27 N rows with their English-original titles. Result: **+18 new Y, 9 still N. Total now 161/170 (94.7%).**

### Confirmed full-text PDFs added (18)

| # | Book | New best_url |
|---|---|---|
| Durkheim 自殺論 | Suicide: A Study in Sociology | https://dn720006.ca.archive.org/0/items/english-collections-k-z/Suicide_%20A%20Study%20in%20Sociology%20-%20Emile%20Durkheim.pdf |
| Müller 比較宗教學 | Intro to the Science of Religion | https://upload.wikimedia.org/wikipedia/commons/0/09/Introduction_To_The_Science_Of_Religion_(IA_IntroductionToTheScienceOfReligion).pdf |
| Müller 東方聖書 | Sacred Books of the East | https://ia801403.us.archive.org/11/items/in.ernet.dli.2015.177585/2015.177585.The-Sacred-Books-Of-The-East-Vol-I.pdf |
| Otto 論神聖 | The Idea of the Holy | https://upload.wikimedia.org/wikipedia/commons/4/4b/Rudolf_Otto_(translated_by_Harvey)_-_The_Idea_of_the_Holy_...pdf |
| Bourdieu 實踐感 | The Logic of Practice | https://monoskop.org/images/8/88/Bourdieu_Pierre_The_Logic_of_Practice_1990.pdf |
| Habermas 公共領域的結構轉型 | Public Sphere | https://allen-webb-wmu.github.io/website/habermas.pdf |
| Goffman 自我表演 | Presentation of Self in Everyday Life | https://archive.org/download/goffmanthepresentationofselfineverydaylife/Goffman%20the%20presentation%20of%20self%20in%20everyday%20life.pdf |
| Goffman 汙名 | Stigma | https://ia601503.us.archive.org/22/items/in.ernet.dli.2015.264015/2015.264015.Stigma.pdf |
| Bauman 液態現代性 | Liquid Modernity | https://giuseppecapograssi.wordpress.com/wp-content/uploads/2014/01/bauman-liquid-modernity.pdf |
| Comte 實證哲學教程 | Positive Philosophy | https://ia902902.us.archive.org/10/items/positivephilosop01comt/positivephilosop01comt.pdf |
| Freud 文明及其不滿 | Civilization and Its Discontents | https://ia801503.us.archive.org/20/items/in.ernet.dli.2015.218475/2015.218475.Civilization-And_text.pdf |
| Jung 心理類型 | Psychological Types (CW Vol 6) | https://www.jungiananalysts.org.uk/wp-content/uploads/2018/07/C.-G.-Jung-Collected-Works-Volume-6_-Psychological-Types.pdf |
| Maslow 動機與人格 | Motivation and Personality | https://www.sciencetheearth.com/uploads/2/4/6/5/24658156/1954_maslow_motivation_and_personality.pdf |
| Maslow 存在心理學探索 | Toward a Psychology of Being | https://psycnet.apa.org/fulltext/2005-06675-000-FRM.pdf |
| Piaget 發生認識論 | Principles of Genetic Epistemology | https://rexresearch1.com/PiagetChildPsychologyLibrary/GeneticEpistemology.pdf |
| Tylor 原始文化 | Primitive Culture | https://archive.org/download/primitiveculture1tylouoft/primitiveculture1tylouoft.pdf |
| Malinowski 西太平洋的航海者 | Argonauts of the Western Pacific | https://monoskop.org/images/4/41/Malinowski_Bronislaw_Argonauts_of_the_Western_Pacific_2002.pdf |
| Spinoza 神學政治論 | Tractatus Theologico-Politicus | https://www.earlymoderntexts.com/assets/pdfs/spinoza1669.pdf |

### Still N after retry (9)
Only secondary-source PDFs / bookstore-only / publisher-locked even under English query:
- Panikkar 《宇宙—神—人共融》 The Cosmotheandric Experience — only Gerard Hall secondary essays
- Bauman 《現代性與大屠殺》 Modernity and the Holocaust — Cornell UP locked; only summaries
- Aron 《社會學主要思潮》 Main Currents in Sociological Thought — Taylor & Francis preview only
- Rogers 《案主中心治療》 Client Centered Therapy — only summaries/secondary
- Fromm 《為自己的人》 Man for Himself — only summaries/Fromm Society bibliography
- Merleau-Ponty 《符號》 Signs — SEO-spam redirect PDFs, no legit copy
- Hartmann 《精神生活的本體論》 Das Problem des geistigen Seins — De Gruyter preview only
- Balthasar 《天主教真理》 Catholicism — English title mapping unclear (likely *In the Fullness of Faith* or *Theo-Drama*); only secondary
- Hauerwas 《和平的國度》 The Peaceable Kingdom — Notre Dame UP locked

For these 9, only Anna's Archive / library catalog / publisher will resolve.
