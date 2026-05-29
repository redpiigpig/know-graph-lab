-- ============================================================================
-- Apocrypha — add `genre` column + backfill per 黃根春《基督教典外文獻》
-- 10-volume taxonomy. Each doc gets a fine-grained genre slug.
--
-- OT genres:
--   apocalyptic     默示文學       (1-3 Enoch / Sibylline / *-apoc / Baruchs / Ezras)
--   testaments      族長遺訓       (Testaments)
--   legends         重述聖經/傳奇  (Jubilees / Aristeas / Joseph & Aseneth / Adam & Eve / ...)
--   wisdom          智慧文獻       (Wisdom of Solomon / Sirach / Ahiqar / Pseudo-Phocylides)
--   deutero         隱藏經卷/第二正典 (Tobit / Judith / Esther+ / Baruch / Macc / Manasseh / 1 Esdras / Ps 151)
--   hymns           詩歌頌詞       (Psalms of Solomon / Odes / Prayer of Joseph)
--   fragments       希臘化猶太斷片 (Aristobulus / Artapanus / Demetrius / Eupolemus / etc.)
--   qumran          昆蘭古卷       (1QS)
--
-- NT genres:
--   gospels         福音書         (Thomas / Mary / Peter / Egyptians / Hebrews / Nazarenes / Ebionites
--                                   / Philip / Truth / Judas / Bartholomew / Nicodemus / Secret Mark / ...)
--   papyri          蒲草紙殘片     (P.Oxy 840 / Egerton 2 / Merton 51 / Berlin 11710 / 16388 / Strasbourg / Fayyum)
--   acts            行傳           (Paul / Peter / Andrew / John / Thomas / Philip / Pseudo-Clementines / Abgar)
--   epistles        書信           (3 Corinthians / Laodicea / Seneca-Paul / Pseudo-Titus / Pilate Letters / Peter-Philip)
--   apocalypses     默示錄         (Apoc Peter / Paul / Thomas / James I & II / Isaiah Ascension)
--   dialogues       對話錄         (Sophia / Apocryphon of John / Pistis Sophia / Dialogue of Savior / Epistula Apost.)
--   misc            其他           (Didache / Joseph of Arimathea / Seventy / Life of JBap / Vindicta / Mani)
-- ============================================================================

ALTER TABLE apocrypha_documents ADD COLUMN IF NOT EXISTS genre VARCHAR(40);
CREATE INDEX IF NOT EXISTS apocrypha_documents_genre ON apocrypha_documents (testament, genre);

-- ── OT: Apocalyptic 默示文學 ──────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'apocalyptic' WHERE slug IN (
  '1-enoch','2-enoch','3-enoch',
  'sibylline-oracles','christian-sibyl',
  '4-ezra','5-6-ezra','greek-ezra-apoc','vision-ezra','questions-ezra',
  'sedrach-apoc','abraham-apoc','adam-apoc','elijah-apoc','daniel-apoc',
  'zephaniah-apoc','shem-treatise','ezekiel-apoc',
  '2-baruch','3-baruch','4-baruch'
);

-- ── OT: Testaments 族長遺訓 ─────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'testaments' WHERE slug IN (
  'test-12-patriarchs','test-job','test-3-patriarchs',
  'test-moses','test-solomon','test-adam'
);

-- ── OT: Legends / Rewritten Bible 重述聖經/傳奇 ─────────────────────────
UPDATE apocrypha_documents SET genre = 'legends' WHERE slug IN (
  'jubilees','aristeas','joseph-aseneth','life-adam-eve',
  'pseudo-philo','lives-prophets','rechab-history',
  'jacob-ladder','jannes-jambres','joseph-history'
);

-- ── OT: Wisdom 智慧文獻 ────────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'wisdom' WHERE slug IN (
  'wisdom-solomon','sirach','ahiqar','phocylides','menander-syr'
);

-- ── OT: Deuterocanon 隱藏經卷/第二正典 ─────────────────────────────────
UPDATE apocrypha_documents SET genre = 'deutero' WHERE slug IN (
  'tobit','judith','esther-additions',
  'baruch','letter-jeremiah',
  '1-maccabees','2-maccabees','3-maccabees','4-maccabees',
  '1-esdras','prayer-manasseh','psalm-151'
);

-- ── OT: Hymns 詩歌頌詞 ─────────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'hymns' WHERE slug IN (
  'psalms-solomon','odes-solomon','joseph-prayer'
);

-- ── OT: Hellenistic-Jewish Fragments 希臘化猶太斷片 ────────────────────
UPDATE apocrypha_documents SET genre = 'fragments' WHERE slug IN (
  'aristobulus','artapanus','demetrius-chron','eupolemus',
  'orphica','philo-poet','theodotus','hecataeus'
);

-- ── OT: Qumran 昆蘭古卷 ───────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'qumran' WHERE slug IN ('1qs');

-- ── NT: Gospels 福音書 ────────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'gospels' WHERE slug IN (
  'gthom','infancy-thomas','protoevangelium-james',
  'infancy-arabic','infancy-latin','joseph-carpenter','birth-mary',
  'gpet','gmary','ghebrews','gnazarenes','gebionites','gegyptians',
  'gphilip','gtruth','gjudas','gbart','gnicodemus',
  'q-secret-mark','gmatthias','logia-unknown','q-mani'
);

-- ── NT: Papyrus fragments 蒲草紙殘片 ───────────────────────────────────
UPDATE apocrypha_documents SET genre = 'papyri' WHERE slug IN (
  'p-oxy-840','p-egerton-2','p-merton-51',
  'p-berlin-11710','p-berlin-16388','p-strasbourg','faiyum'
);

-- ── NT: Acts 行傳 ─────────────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'acts' WHERE slug IN (
  'acts-paul','acts-peter','acts-andrew','acts-john','acts-thomas','acts-philip',
  'clement-romance','abgar'
);

-- ── NT: Epistles 書信 ─────────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'epistles' WHERE slug IN (
  '3-cor','q-laodicea','seneca-paul','pseudo-titus',
  'pilate-claudius','pilate-tiberius','pilate-herod',
  'peter-philip','q-peter-preaching'
);

-- ── NT: Apocalypses 默示錄 ────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'apocalypses' WHERE slug IN (
  'apoc-peter','apoc-peter-cop','apoc-paul','apoc-paul-cop','apoc-thomas',
  'apoc-james-1','apoc-james-2','isaiah-ascension'
);

-- ── NT: Dialogues / Gnostic discourses 對話錄 ─────────────────────────
UPDATE apocrypha_documents SET genre = 'dialogues' WHERE slug IN (
  'soph-jesus','john-apocryphon','pistis-sophia','dialogue-savior',
  'epistula-apostolorum','memoria-apostolorum','two-books-jeu'
);

-- ── NT: Misc 其他 ──────────────────────────────────────────────────────
UPDATE apocrypha_documents SET genre = 'misc' WHERE slug IN (
  'didache','joseph-arimathea','seventy-elders','john-baptist-life','vengeance-savior'
);

-- Update isaiah-ascension testament to OT side (it's classified mixed but
-- in 黃根春's organization it sits with NT 默示錄 vol).
UPDATE apocrypha_documents SET testament = 'nt' WHERE slug = 'isaiah-ascension';

-- Fall-back: anything still NULL gets 'misc' (we can refine later)
UPDATE apocrypha_documents SET genre = 'misc' WHERE genre IS NULL;
