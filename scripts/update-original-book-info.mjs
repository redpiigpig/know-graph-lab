const KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const BASE = `${(process.env.SUPABASE_URL || "").replace(/\/$/, "")}/rest/v1`;
if (!KEY || !process.env.SUPABASE_URL) {
  console.error("請設定環境變數 SUPABASE_SERVICE_ROLE_KEY 與 SUPABASE_URL（專案網址，勿寫入版本庫）。");
  process.exit(1);
}

const data = [
  {t:'《楔形傳說》',oa:'Paul Collins',ot:'The Sumerians',op:'Reaktion Books',oy:2021},
  {t:'《中斷的天命》',oa:'Tamim Ansary',ot:'Destiny Disrupted: A History of the World Through Islamic Eyes',op:'PublicAffairs',oy:2009},
  {t:'世界史前史',oa:'Brian Fagan',ot:'World Prehistory: A Brief Introduction',op:'Little, Brown & Co.',oy:1979},
  {t:'世界史的誕生',oa:'岡田 英弘',ot:'世界史の誕生',op:'筑摩書房',oy:1992},
  {t:'世界宗教中的神祕主義',oa:'Geoffrey Parrinder',ot:"Mysticism in the World's Religions",op:'Sheldon Press / Oneworld',oy:1976},
  {t:'人性中的善良天使',oa:'Steven Pinker',ot:'The Better Angels of Our Nature',op:'Viking Books',oy:2011},
  {t:'人類憑什麼',oa:'Ian Morris',ot:'Why the West Rules—For Now',op:'Farrar, Straus and Giroux',oy:2010},
  {t:'先知的繼承者',oa:'Hugh Kennedy',ot:'The Caliphate: The History of an Idea',op:'Basic Books',oy:2016},
  {t:'最早的農人',oa:'Peter Bellwood',ot:'First Farmers: The Origins of Agricultural Societies',op:'Wiley-Blackwell',oy:2004},
  {t:'前蘇格拉底哲學',oa:'André Laks',ot:'Introduction à la philosophie présocratique',op:'Presses Universitaires de France',oy:2006},
  {t:'十二幅地圖中的世界史',oa:'Jerry Brotton',ot:'A History of the World in 12 Maps',op:'Allen Lane',oy:2012},
  {t:'千面女神',oa:'Joseph Campbell',ot:'Goddesses: Mysteries of the Feminine Divine',op:'New World Library',oy:2013},
  {t:'印度教導論',oa:'T. M. P. Mahadevan',ot:'Outlines of Hinduism',op:'Chetana',oy:1956},
  {t:'印度文明史',oa:'常盤 大定',ot:'印度文明史',op:'丙午出版社',oy:1926},
  {t:'古代美索不達米亞社會生活',oa:'Stephen Bertman',ot:'Handbook to Life in Ancient Mesopotamia',op:'Facts on File',oy:2003},
  {t:'古代近東歷史編撰學中的神話與政治',oa:'Mario Liverani',ot:'Myth and Politics in Ancient Near Eastern Historiography',op:'Cornell University Press',oy:2004},
  {t:'古以色列史',oa:'Julius Wellhausen',ot:'Prolegomena zur Geschichte Israels',op:'Reimer',oy:1878},
  {t:'古典時代的終結',oa:'Hartwin Brandt',ot:'Das Ende der Antike',op:'C.H.Beck',oy:2001},
  {t:'古地中海文明陷落的關鍵',oa:'Eric H. Cline',ot:'1177 B.C.: The Year Civilization Collapsed',op:'Princeton University Press',oy:2014},
  {t:'坎伯生活美學',oa:'Diane K. Osbon',ot:'A Joseph Campbell Companion: Reflections on the Art of Living',op:'HarperCollins',oy:1991},
  {t:'埃及史：從原初時代至當下',oa:'Jason Thompson',ot:'A History of Egypt: From Earliest Times to the Present',op:'AUC Press',oy:2008},
  {t:'埃及神話',oa:'Garry J. Shaw',ot:'The Egyptian Myths: A Guide to the Ancient Gods and Legends',op:'Thames & Hudson',oy:2014},
  {t:'大乘佛教思想',oa:'上田 義文',ot:'大乗仏教思想の根本構造',op:'百華苑',oy:1957},
  {t:'大分離：就大陸與新大陸的歷史與人性',oa:'Peter Watson',ot:'The Great Divide',op:'Weidenfeld & Nicolson',oy:2012},
  {t:'宗教思想史',oa:'Mircea Eliade',ot:'A History of Religious Ideas (Vol. 1)',op:'University of Chicago Press',oy:1978},
  {t:'巴比倫：美索不達米亞和文明的誕生',oa:'Paul Kriwaczek',ot:'Babylon: Mesopotamia and the Birth of Civilization',op:'Atlantic Books',oy:2010},
  {t:'巴比倫與亞述神話',oa:'Donald A. Mackenzie',ot:'Myths of Babylonia and Assyria',op:'Gresham Publishing',oy:1915},
  {t:'希臘化世界',oa:'F. W. Walbank',ot:'The Hellenistic World',op:'Fontana Press',oy:1981},
  {t:'從部落到國家',oa:'Mark W. Moffett',ot:'The Human Swarm: How Our Societies Arise, Thrive, and Fall',op:'Basic Books',oy:2019},
  {t:'思想史：從火到佛洛伊德',oa:'Peter Watson',ot:'Ideas: A History of Thought and Invention, from Fire to Freud',op:'Weidenfeld & Nicolson',oy:2005},
  {t:'成神：早期中國的宇宙論、祭祀與自我神化',oa:'Michael Puett',ot:'To Become a God',op:'Harvard University Asia Center',oy:2002},
  {t:'探索神性',oa:'John Macquarrie',ot:'In Search of Deity',op:'SCM Press',oy:1984},
  {t:'政治觀念史稿(一)',oa:'Eric Voegelin',ot:'History of Political Ideas',op:'University of Missouri Press',oy:1997},
  {t:'槍炮、病菌與鋼鐵',oa:'Jared Diamond',ot:'Guns, Germs, and Steel',op:'W. W. Norton & Company',oy:1997},
  {t:'次經導論',oa:'David A. deSilva',ot:'Introducing the Apocrypha',op:'Baker Academic',oy:2002},
  {t:'沒有神的宗教',oa:'Ronald Dworkin',ot:'Religion Without God',op:'Harvard University Press',oy:2013},
  {t:'激進神學與上帝之死',oa:'Thomas J. J. Altizer',ot:'Radical Theology and the Death of God',op:'Bobbs-Merrill',oy:1966},
  {t:'猶太人的世紀',oa:'Yuri Slezkine',ot:'The Jewish Century',op:'Princeton University Press',oy:2004},
  {t:'王權與神祇(上)',oa:'Henri Frankfort',ot:'Kingship and the Gods',op:'University of Chicago Press',oy:1948},
  {t:'理性的勝利',oa:'Rodney Stark',ot:'The Victory of Reason',op:'Random House',oy:2005},
  {t:'神的歷史',oa:'Karen Armstrong',ot:'A History of God',op:'Alfred A. Knopf',oy:1993},
  {t:'神的演化',oa:'Robert Wright',ot:'The Evolution of God',op:'Little, Brown and Company',oy:2009},
  {t:'神話的歷史',oa:'Veronica Ions',ot:'History of Mythology',op:'Hamlyn',oy:1974},
  {t:'神話簡史',oa:'Karen Armstrong',ot:'A Short History of Myth',op:'Canongate Books',oy:2005},
  {t:'穿過針眼：財富、西羅馬帝國的衰亡和基督教會的形成',oa:'Peter Brown',ot:'Through the Eye of a Needle',op:'Princeton University Press',oy:2012},
  {t:'第三種猩猩',oa:'Jared Diamond',ot:'The Third Chimpanzee',op:'HarperCollins',oy:1991},
  {t:'耶穌到底如何成為神',oa:'Larry W. Hurtado',ot:'How on Earth Did Jesus Become a God?',op:'Wm. B. Eerdmans',oy:2005},
  {t:'耶穌與死海古卷',oa:'John Bergsma',ot:'Jesus and the Dead Sea Scrolls',op:'Image',oy:2019},
  {t:'薩滿教',oa:'Mircea Eliade',ot:'Le Chamanisme (Shamanism: Archaic Techniques of Ecstasy)',op:'Payot',oy:1951},
  {t:'蘇美爾神話',oa:'Samuel Noah Kramer',ot:'Sumerian Mythology',op:'American Philosophical Society',oy:1944},
  {t:'虛構的猶太民族',oa:'Shlomo Sand',ot:'The Invention of the Jewish People',op:'Resling',oy:2008},
  {t:'被隱藏的眾神',oa:'Gerard Russell',ot:'Heirs to Forgotten Kingdoms',op:'Basic Books',oy:2014},
  {t:'西方哲學史',oa:'Samuel Enoch Stumpf',ot:'Socrates to Sartre and Beyond: A History of Philosophy',op:'McGraw-Hill',oy:1966},
  {t:'造神：人類探索信仰與宗教的歷史',oa:'Reza Aslan',ot:'God: A Human History',op:'Random House',oy:2017},
  {t:'阿拉伯通史',oa:'Philip K. Hitti',ot:'History of the Arabs',op:'Macmillan',oy:1937},
  {t:'靈魂獵人',oa:'Rane Willerslev',ot:'Soul Hunters',op:'University of California Press',oy:2007},
  {t:'魔鬼史',oa:'Paul Carus',ot:'The History of the Devil and the Idea of Evil',op:'Open Court Publishing',oy:1900},
  {t:'黑色上帝',oa:'Julian Baldick',ot:'Black God',op:'I.B. Tauris',oy:1997},
];

async function run() {
  const res = await fetch(BASE + '/books?select=id,title', {
    headers: { apikey: KEY, Authorization: 'Bearer ' + KEY }
  });
  const books = await res.json();

  let updated = 0, notFound = 0;
  for (const row of data) {
    const clean = row.t.replace(/[《》]/g, '').trim();
    const book = books.find(b =>
      b.title === row.t || b.title === clean ||
      b.title.replace(/[《》]/g,'').trim() === clean
    );
    if (!book) {
      console.log('❌ NOT FOUND:', row.t);
      notFound++;
      continue;
    }
    const patch = await fetch(BASE + '/books?id=eq.' + book.id, {
      method: 'PATCH',
      headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        original_author: row.oa,
        original_title: row.ot,
        original_publisher: row.op,
        original_publish_year: row.oy,
      })
    });
    if (patch.status === 204) { updated++; process.stdout.write('.'); }
    else { console.log('\n⚠️  ERROR', row.t, patch.status, await patch.text()); }
  }
  console.log('\n✓ Done. Updated:', updated, '/ Not found:', notFound);
}

run().catch(console.error);
