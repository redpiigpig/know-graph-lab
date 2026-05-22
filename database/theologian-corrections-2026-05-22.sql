-- 使用者譯名校正 2026-05-22（52 條 + 刪 1 dup）
-- 套用方法：scripts via Management API

-- 刪 dup（T. F. Torrance 跟 Thomas F. Torrance 同人）
DELETE FROM theologians WHERE name_english = 'T. F. Torrance';

-- 統一更新 ★建議譯名（並複製到對應的傳統欄，讓「建議」跟該傳統欄一致）
UPDATE theologians SET name_recommended = '安提阿的依納爵', name_catholic_sgs = '安提阿的依納爵' WHERE name_english = 'Ignatius of Antioch';
UPDATE theologians SET name_recommended = '羅馬的黑馬'    WHERE name_english = 'Hermas';
UPDATE theologians SET name_recommended = '雅典那哥拉'    WHERE name_english = 'Athenagoras of Athens';
UPDATE theologians SET name_recommended = '他提安'        WHERE name_english = 'Tatian the Assyrian';
UPDATE theologians SET name_recommended = '俄利根'        WHERE name_english = 'Origen';
UPDATE theologians SET name_recommended = '潘代諾'        WHERE name_english = 'Pantaenus';
UPDATE theologians SET name_recommended = '諾窪天'        WHERE name_english = 'Novatian';
UPDATE theologians SET name_recommended = '亞歷山卓的狄奧尼修' WHERE name_english = 'Dionysius of Alexandria';

-- 大公教父 — 思高傳統
UPDATE theologians SET name_recommended = '大巴西略'                     WHERE name_english = 'Basil the Great';
UPDATE theologians SET name_recommended = '拿先斯的格列高理'             WHERE name_english = 'Gregory of Nazianzus';
UPDATE theologians SET name_recommended = '尼撒的格列高理'               WHERE name_english = 'Gregory of Nyssa';
UPDATE theologians SET name_recommended = '敘利亞的艾弗冷'               WHERE name_english = 'Ephrem the Syrian';
UPDATE theologians SET name_recommended = '亞波里那留'                   WHERE name_english = 'Apollinaris of Laodicea';
UPDATE theologians SET name_recommended = '摩普綏提亞的狄奧多若'         WHERE name_english = 'Theodore of Mopsuestia';
UPDATE theologians SET name_recommended = '若望‧格西安'                  WHERE name_english = 'John Cassian';
UPDATE theologians SET name_recommended = '勒蘭的文生'                   WHERE name_english = 'Vincent of Lerins';
UPDATE theologians SET name_recommended = '凱撒略'                       WHERE name_english = 'Caesarius of Arles';
UPDATE theologians SET name_recommended = '偽狄奧尼修斯'                 WHERE name_english = 'Pseudo-Dionysius the Areopagite';
UPDATE theologians SET name_recommended = '大良'                         WHERE name_english = 'Leo the Great';
UPDATE theologians SET name_recommended = '大額我略'                     WHERE name_english = 'Gregory the Great';
UPDATE theologians SET name_recommended = '依西多祿'                     WHERE name_english = 'Isidore of Seville';
UPDATE theologians SET name_recommended = '可敬者比德'                   WHERE name_english = 'Bede the Venerable';
UPDATE theologians SET name_recommended = '認信者馬克西姆'               WHERE name_english = 'Maximus the Confessor';
UPDATE theologians SET name_recommended = '大馬士革的若望'               WHERE name_english = 'John of Damascus';

-- 中世紀東方
UPDATE theologians SET name_recommended = '君士坦丁堡的佛提烏'           WHERE name_english = 'Photius of Constantinople';
UPDATE theologians SET name_recommended = '新神學家西蒙'                 WHERE name_english = 'Symeon the New Theologian';
UPDATE theologians SET name_recommended = '帕拉馬的格列高理'             WHERE name_english = 'Gregory Palamas';

-- 中世紀西方
UPDATE theologians SET name_recommended = '聖維克多的修格'               WHERE name_english = 'Hugh of Saint Victor';
UPDATE theologians SET name_recommended = '文德'                         WHERE name_english = 'Bonaventure';
UPDATE theologians SET name_recommended = '大亞爾伯特'                   WHERE name_english = 'Albertus Magnus';
UPDATE theologians SET name_recommended = '董‧思高'                      WHERE name_english = 'Duns Scotus';
UPDATE theologians SET name_recommended = '奧坎的威廉'                   WHERE name_english = 'William of Ockham';
UPDATE theologians SET name_recommended = '多瑪斯‧肯皮斯'                WHERE name_english = 'Thomas à Kempis';
UPDATE theologians SET name_recommended = '若望‧思高‧愛留根納'          WHERE name_english = 'John Scotus Eriugena';
UPDATE theologians SET name_recommended = '蘭的安塞姆'                   WHERE name_english = 'Anselm of Laon';
UPDATE theologians SET name_recommended = '伯多祿‧亞伯拉'                WHERE name_english = 'Peter Abelard';
UPDATE theologians SET name_recommended = '西奈的聖若望'                 WHERE name_english = 'John Climacus';
UPDATE theologians SET name_recommended = '西奈的格列高理'               WHERE name_english = 'Gregory of Sinai';
UPDATE theologians SET name_recommended = '揚‧胡斯'                      WHERE name_english = 'Jan Hus';

-- 宗教改革／近代
UPDATE theologians SET name_recommended = '腓力‧莫蘭頓'                  WHERE name_english = 'Philip Melanchthon';
UPDATE theologians SET name_recommended = '烏利希‧慈運理'                WHERE name_english = 'Huldrych Zwingli';
UPDATE theologians SET name_recommended = '門諾‧西門'                    WHERE name_english = 'Menno Simons';
UPDATE theologians SET name_recommended = '湯瑪斯‧克蘭麥'                WHERE name_english = 'Thomas Cranmer';
UPDATE theologians SET name_recommended = '聖方濟各‧沙雷氏'              WHERE name_english = 'Francis de Sales';
UPDATE theologians SET name_recommended = '尼古拉‧欽虔多夫'              WHERE name_english = 'Nikolaus von Zinzendorf';

-- 現代／當代
UPDATE theologians SET name_recommended = '索倫‧祈克果'                  WHERE name_english = 'Søren Kierkegaard';
UPDATE theologians SET name_recommended = '保囉‧田立克'                  WHERE name_english = 'Paul Tillich';
UPDATE theologians SET name_recommended = '于爾根‧莫特曼'                WHERE name_english = 'Jürgen Moltmann';
UPDATE theologians SET name_recommended = '沃夫哈特‧潘能伯格'            WHERE name_english = 'Wolfhart Pannenberg';
UPDATE theologians SET name_recommended = '漢斯‧昆'                      WHERE name_english = 'Hans Küng';

-- 全庫「亞歷山大」→「亞歷山卓」（人名地名）— 多欄一起改
UPDATE theologians SET
  name_recommended       = REPLACE(name_recommended, '亞歷山大', '亞歷山卓'),
  name_protestant        = REPLACE(name_protestant, '亞歷山大', '亞歷山卓'),
  name_catholic_sgs      = REPLACE(name_catholic_sgs, '亞歷山大', '亞歷山卓'),
  name_orthodox          = REPLACE(name_orthodox, '亞歷山大', '亞歷山卓'),
  name_hk                = REPLACE(name_hk, '亞歷山大', '亞歷山卓'),
  name_tw                = REPLACE(name_tw, '亞歷山大', '亞歷山卓'),
  name_china_academic    = REPLACE(name_china_academic, '亞歷山大', '亞歷山卓'),
  nationality            = REPLACE(nationality, '亞歷山大', '亞歷山卓')
WHERE
  name_recommended    LIKE '%亞歷山大%' OR
  name_protestant     LIKE '%亞歷山大%' OR
  name_catholic_sgs   LIKE '%亞歷山大%' OR
  name_orthodox       LIKE '%亞歷山大%' OR
  name_hk             LIKE '%亞歷山大%' OR
  name_tw             LIKE '%亞歷山大%' OR
  name_china_academic LIKE '%亞歷山大%' OR
  nationality         LIKE '%亞歷山大%';

-- 但 Alexander the Great（亞歷山大大帝）等如有需保留 — 目前 master 沒這人，不擔心
-- 也要避開「亞歷山大三世」「亞歷山大六世」等教宗名 — 目前 master 沒這些

UPDATE theologians SET updated_at = now() WHERE updated_at < now();
