// ============================================================================
// 英文「手工策展」學術單字庫（2026-06-05）
//   - 給單字複習的「無限模式」與「生成主題單字組」用：預設主題直接插入策展單字，
//     不靠臨時 AI 生成 → 永遠有題、零延遲、品質穩定（B2+ 學術詞，宗教研究取向）。
//   - 自訂主題（不在此清單）才走 AI（NVIDIA 主→Gemini 備援）。
// 每筆：word / meaning(繁中) / example(英) / pos。reading 留空（英文不需音標欄）。
// 加詞：在對應主題 words 補一筆即可。主題 key 要對齊 review.vue 的 THEME_POOLS/PRESETS。
// ============================================================================

export interface CuratedWord {
  word: string;
  meaning: string;   // 繁中釋義
  example: string;   // 英文例句
  pos: string;       // 詞性
}

export const EN_VOCAB_THEMES: Record<string, CuratedWord[]> = {
  "AWL Sublist 1": [
    { word: "analyse", meaning: "分析；細究", example: "She analysed the manuscript's textual variants.", pos: "v." },
    { word: "concept", meaning: "概念；觀念", example: "The concept of grace is central to his theology.", pos: "n." },
    { word: "context", meaning: "脈絡；上下文", example: "The verse must be read in its historical context.", pos: "n." },
    { word: "derive", meaning: "源自；衍生", example: "The doctrine derives from earlier Jewish thought.", pos: "v." },
    { word: "interpret", meaning: "詮釋；解讀", example: "Scholars interpret the parable differently.", pos: "v." },
    { word: "method", meaning: "方法；方法論", example: "His method combines philology and history.", pos: "n." },
    { word: "principle", meaning: "原則；原理", example: "The principle of charity guides his reading.", pos: "n." },
    { word: "significant", meaning: "重要的；有意義的", example: "This is a significant addition to the corpus.", pos: "adj." },
    { word: "source", meaning: "來源；史料", example: "He cites only primary sources.", pos: "n." },
    { word: "theory", meaning: "理論；學說", example: "Her theory challenges the consensus.", pos: "n." },
    { word: "evident", meaning: "明顯的；顯而易見的", example: "The influence of Plato is evident throughout.", pos: "adj." },
    { word: "formula", meaning: "公式；定式表述", example: "The creed uses a fixed liturgical formula.", pos: "n." },
    { word: "structure", meaning: "結構；架構", example: "The structure of the argument is tightly logical.", pos: "n." },
    { word: "establish", meaning: "確立；建立", example: "The council established the canon.", pos: "v." },
    { word: "indicate", meaning: "顯示；指出", example: "The script indicates a fourth-century date.", pos: "v." },
  ],
  "GRE 高頻字": [
    { word: "ascetic", meaning: "苦行的；禁慾者", example: "The desert fathers led an ascetic life.", pos: "adj./n." },
    { word: "esoteric", meaning: "深奧的；僅少數人懂的", example: "Gnostic texts often convey esoteric knowledge.", pos: "adj." },
    { word: "orthodox", meaning: "正統的", example: "The bishop defended orthodox doctrine.", pos: "adj." },
    { word: "heretical", meaning: "異端的", example: "The teaching was condemned as heretical.", pos: "adj." },
    { word: "exegesis", meaning: "（經文）註釋；釋經", example: "His exegesis of Romans is widely cited.", pos: "n." },
    { word: "polemic", meaning: "論戰；駁斥性文章", example: "The treatise is a polemic against the Arians.", pos: "n." },
    { word: "canonical", meaning: "正典的；公認的", example: "Only canonical books were read in worship.", pos: "adj." },
    { word: "ineffable", meaning: "難以言喻的", example: "Mystics describe an ineffable union with God.", pos: "adj." },
    { word: "redaction", meaning: "編修；編輯", example: "The text shows signs of later redaction.", pos: "n." },
    { word: "venerate", meaning: "崇敬；敬奉", example: "Pilgrims venerated the relics.", pos: "v." },
    { word: "syncretic", meaning: "融合（不同信仰）的", example: "The cult was syncretic, blending several traditions.", pos: "adj." },
    { word: "eschatology", meaning: "末世論", example: "Early Christian eschatology expected an imminent end.", pos: "n." },
    { word: "apocryphal", meaning: "次經的；真偽存疑的", example: "The story is apocryphal, not found in the gospels.", pos: "adj." },
    { word: "dogma", meaning: "教條；信條", example: "The dogma was formally defined in 1854.", pos: "n." },
    { word: "schism", meaning: "（教會）分裂", example: "The schism of 1054 divided East and West.", pos: "n." },
  ],
  "哲學學術用語": [
    { word: "epistemology", meaning: "知識論", example: "His epistemology asks how we can know God.", pos: "n." },
    { word: "ontology", meaning: "本體論；存有論", example: "The debate concerns the ontology of universals.", pos: "n." },
    { word: "metaphysics", meaning: "形上學", example: "Aristotle's metaphysics shaped scholastic thought.", pos: "n." },
    { word: "teleology", meaning: "目的論", example: "A teleology sees nature as directed toward ends.", pos: "n." },
    { word: "immanent", meaning: "內在的（與超越相對）", example: "God is both immanent and transcendent.", pos: "adj." },
    { word: "transcendent", meaning: "超越的", example: "The divine is transcendent, beyond the world.", pos: "adj." },
    { word: "a priori", meaning: "先驗的", example: "He argues the principle is known a priori.", pos: "adj./adv." },
    { word: "dialectic", meaning: "辯證（法）", example: "Hegel's dialectic moves through contradiction.", pos: "n." },
    { word: "substance", meaning: "實體；本體", example: "The Father and Son share one substance.", pos: "n." },
    { word: "essence", meaning: "本質", example: "They debated the essence of the soul.", pos: "n." },
    { word: "contingent", meaning: "偶然的；依存的", example: "Created things are contingent, not necessary.", pos: "adj." },
    { word: "phenomenon", meaning: "現象", example: "Religious experience is a complex phenomenon.", pos: "n." },
    { word: "hermeneutics", meaning: "詮釋學", example: "Gadamer's hermeneutics stresses the reader's horizon.", pos: "n." },
    { word: "discourse", meaning: "論述；話語", example: "The discourse of natural theology shifted in the 18th century.", pos: "n." },
    { word: "premise", meaning: "前提", example: "The argument rests on a questionable premise.", pos: "n." },
  ],
  "歷史學術用語": [
    { word: "chronology", meaning: "年代學；先後次序", example: "The chronology of the councils is well documented.", pos: "n." },
    { word: "provenance", meaning: "出處；來歷", example: "The codex's provenance is uncertain.", pos: "n." },
    { word: "primary source", meaning: "第一手史料", example: "He prefers primary sources to later summaries.", pos: "n." },
    { word: "historiography", meaning: "史學史；史學編纂", example: "Reformation historiography has changed greatly.", pos: "n." },
    { word: "anachronism", meaning: "時代錯置", example: "Calling him a 'Protestant' is an anachronism.", pos: "n." },
    { word: "contemporary", meaning: "同時代的；當代的", example: "A contemporary chronicle records the event.", pos: "adj." },
    { word: "antiquity", meaning: "古代；古物", example: "The practice dates back to late antiquity.", pos: "n." },
    { word: "manuscript", meaning: "手稿；抄本", example: "The manuscript was copied in a monastery.", pos: "n." },
    { word: "archive", meaning: "檔案（館）", example: "He spent months in the Vatican archives.", pos: "n." },
    { word: "dynasty", meaning: "王朝", example: "The dynasty patronised the church for centuries.", pos: "n." },
    { word: "secular", meaning: "世俗的", example: "Secular and clerical authority often clashed.", pos: "adj." },
    { word: "annals", meaning: "編年史", example: "The annals note a famine that year.", pos: "n." },
    { word: "periodization", meaning: "歷史分期", example: "The periodization into 'medieval' is debated.", pos: "n." },
    { word: "corroborate", meaning: "佐證；證實", example: "Two independent sources corroborate the account.", pos: "v." },
    { word: "attest", meaning: "證實；（文獻）可證", example: "The name is attested in several inscriptions.", pos: "v." },
  ],
  "神學術語": [
    { word: "incarnation", meaning: "道成肉身", example: "The Incarnation is the Word becoming flesh.", pos: "n." },
    { word: "atonement", meaning: "贖罪", example: "Theories of the atonement vary widely.", pos: "n." },
    { word: "soteriology", meaning: "救恩論", example: "His soteriology stresses grace alone.", pos: "n." },
    { word: "Trinity", meaning: "三位一體", example: "The doctrine of the Trinity was refined at Constantinople.", pos: "n." },
    { word: "justification", meaning: "稱義", example: "Luther taught justification by faith.", pos: "n." },
    { word: "sanctification", meaning: "成聖", example: "Sanctification is the lifelong work of grace.", pos: "n." },
    { word: "eschatology", meaning: "末世論", example: "Pauline eschatology shapes his ethics.", pos: "n." },
    { word: "ecclesiology", meaning: "教會論", example: "Their ecclesiology defines the marks of the church.", pos: "n." },
    { word: "providence", meaning: "天意；護佑", example: "He saw the rescue as divine providence.", pos: "n." },
    { word: "covenant", meaning: "聖約；盟約", example: "The covenant binds God and his people.", pos: "n." },
    { word: "sacrament", meaning: "聖禮；聖事", example: "Baptism is a sacrament of initiation.", pos: "n." },
    { word: "grace", meaning: "恩典", example: "Salvation is a gift of grace.", pos: "n." },
    { word: "revelation", meaning: "啟示", example: "Scripture is held to be divine revelation.", pos: "n." },
    { word: "theodicy", meaning: "神義論（論惡之問題）", example: "His theodicy addresses the problem of evil.", pos: "n." },
    { word: "hypostasis", meaning: "位格", example: "Each hypostasis shares the one divine essence.", pos: "n." },
  ],
  "文學批評術語": [
    { word: "allegory", meaning: "寓言；託寓", example: "The Song of Songs was read as allegory.", pos: "n." },
    { word: "narrative", meaning: "敘事", example: "The gospel narrative builds toward the passion.", pos: "n." },
    { word: "trope", meaning: "比喻；修辭格", example: "The wilderness is a recurring trope.", pos: "n." },
    { word: "motif", meaning: "母題；主題意象", example: "Light is a central motif in John.", pos: "n." },
    { word: "intertextuality", meaning: "互文性", example: "The psalm's intertextuality with Exodus is striking.", pos: "n." },
    { word: "genre", meaning: "文類；體裁", example: "Apocalypse is a distinct literary genre.", pos: "n." },
    { word: "rhetoric", meaning: "修辭（學）", example: "Paul's rhetoric persuades as much as it argues.", pos: "n." },
    { word: "irony", meaning: "反諷", example: "The crucifixion is described with deep irony.", pos: "n." },
    { word: "canon", meaning: "（文學/經典）正典", example: "The literary canon shapes what is studied.", pos: "n." },
    { word: "hermeneutic", meaning: "詮釋（的）", example: "A feminist hermeneutic rereads the text.", pos: "adj./n." },
    { word: "polysemy", meaning: "多義性", example: "The word's polysemy invites multiple readings.", pos: "n." },
    { word: "typology", meaning: "預表論；類型", example: "Typology reads Adam as a figure of Christ.", pos: "n." },
    { word: "discourse", meaning: "話語；論述", example: "The text participates in apocalyptic discourse.", pos: "n." },
    { word: "metanarrative", meaning: "宏大敘事", example: "Salvation history is a sweeping metanarrative.", pos: "n." },
    { word: "subtext", meaning: "潛台詞；隱含義", example: "There is a polemical subtext to the letter.", pos: "n." },
  ],
  "學術寫作連接詞": [
    { word: "however", meaning: "然而（轉折）", example: "The dating is late; however, the tradition is early.", pos: "adv." },
    { word: "therefore", meaning: "因此（結果）", example: "The witnesses disagree; therefore, an eclectic text is needed.", pos: "adv." },
    { word: "moreover", meaning: "此外；而且（遞進）", example: "Moreover, the script confirms the date.", pos: "adv." },
    { word: "nevertheless", meaning: "儘管如此（讓步轉折）", example: "The evidence is thin; nevertheless, the case is plausible.", pos: "adv." },
    { word: "consequently", meaning: "因而；結果", example: "Consequently, the older reading was adopted.", pos: "adv." },
    { word: "furthermore", meaning: "再者（遞進）", example: "Furthermore, two manuscripts support this view.", pos: "adv." },
    { word: "whereas", meaning: "然而；反觀（對比）", example: "Mark is terse, whereas John is reflective.", pos: "conj." },
    { word: "nonetheless", meaning: "仍然；儘管如此", example: "It is fragmentary; nonetheless, it is invaluable.", pos: "adv." },
    { word: "thus", meaning: "因此；如此", example: "Thus the argument collapses.", pos: "adv." },
    { word: "in contrast", meaning: "相比之下", example: "In contrast, the later edition omits the passage.", pos: "phr." },
    { word: "notwithstanding", meaning: "儘管；雖然如此", example: "Notwithstanding these doubts, the attribution stands.", pos: "prep./adv." },
    { word: "hence", meaning: "因此；故", example: "Hence the need for a critical edition.", pos: "adv." },
    { word: "accordingly", meaning: "因此；相應地", example: "Accordingly, the editors revised the apparatus.", pos: "adv." },
    { word: "conversely", meaning: "反之；相反地", example: "Conversely, a late date would weaken the claim.", pos: "adv." },
    { word: "albeit", meaning: "雖然；儘管", example: "The text is complete, albeit damaged.", pos: "conj." },
  ],
};

// 主題是否有策展單字
export function hasCuratedTheme(theme: string): boolean {
  return !!EN_VOCAB_THEMES[theme?.trim()];
}

// 取某主題的策展單字（可選排除已有的字、限制數量、洗牌）
export function curatedWords(theme: string): CuratedWord[] {
  return EN_VOCAB_THEMES[theme?.trim()] || [];
}

export function curatedThemeKeys(): string[] {
  return Object.keys(EN_VOCAB_THEMES);
}
