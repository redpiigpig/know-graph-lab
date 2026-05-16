/** Rome popes batch 4: #151-#200 (AD 1055-1334). Note: church='天主教' (post-1054 schism) */
import fs from "node:fs";
const env = Object.fromEntries(
  fs.readFileSync("c:/Users/user/Desktop/know-graph-lab/.env", "utf8").split(/\r?\n/).filter(l => l && !l.startsWith("#")).map(l => {
    const i = l.indexOf("="); return [l.slice(0, i), l.slice(i+1).trim().replace(/^["']|["']$/g, "")];
  })
);
const ref = env.SUPABASE_URL.replace("https://", "").split(".")[0];
const endpoint = `https://api.supabase.com/v1/projects/${ref}/database/query`;
async function q(sql) {
  const res = await fetch(endpoint, { method: "POST", headers: { Authorization: `Bearer ${env.SUPABASE_ACCESS_TOKEN}`, "Content-Type": "application/json" }, body: JSON.stringify({ query: sql }) });
  const txt = await res.text(); if (!res.ok) { console.error("FAIL:", txt); process.exit(1); } return JSON.parse(txt);
}

const popes = [
  [151, '維克多二世',         'Pope Victor II',         1055, 1057, '逝世', null],
  [152, '斯德望九世',         'Pope Stephen IX',        1057, 1058, '逝世', null],
  [153, '尼古拉二世',         'Pope Nicholas II',       1059, 1061, '逝世', '訂立樞機團教宗選舉法'],
  [154, '亞歷山大二世',       'Pope Alexander II',      1061, 1073, '逝世', null],
  [155, '聖額我略七世',       'Pope Gregory VII',       1073, 1085, '流亡逝世', '克呂尼改革；卡諾莎之辱'],
  [156, '真福維克多三世',     'Pope Victor III',        1086, 1087, '逝世', null],
  [157, '真福烏爾班二世',     'Pope Urban II',          1088, 1099, '逝世', '召開第一次十字軍東征'],
  [158, '巴斯加二世',         'Pope Paschal II',        1099, 1118, '逝世', null],
  [159, '吉拉削二世',         'Pope Gelasius II',       1118, 1119, '逝世', null],
  [160, '加里斯都二世',       'Pope Callixtus II',      1119, 1124, '逝世', '訂立沃爾姆斯協約解決敘任權之爭'],
  [161, '何挪略二世',         'Pope Honorius II',       1124, 1130, '逝世', null],
  [162, '依諾增爵二世',       'Pope Innocent II',       1130, 1143, '逝世', null],
  [163, '塞肋斯定二世',       'Pope Celestine II',      1143, 1144, '逝世', null],
  [164, '路修二世',           'Pope Lucius II',         1144, 1145, '逝世', null],
  [165, '真福恩仁三世',       'Pope Eugene III',        1145, 1153, '逝世', '召開第二次十字軍東征'],
  [166, '亞納大削四世',       'Pope Anastasius IV',     1153, 1154, '逝世', null],
  [167, '哈德良四世',         'Pope Adrian IV',         1154, 1159, '逝世', '唯一英格蘭裔教宗'],
  [168, '亞歷山大三世',       'Pope Alexander III',     1159, 1181, '逝世', '對抗腓特烈一世巴巴羅薩'],
  [169, '路修三世',           'Pope Lucius III',        1181, 1185, '逝世', null],
  [170, '烏爾班三世',         'Pope Urban III',         1185, 1187, '逝世', null],
  [171, '額我略八世',         'Pope Gregory VIII',      1187, 1187, '逝世', null],
  [172, '克勉三世',           'Pope Clement III',       1187, 1191, '逝世', '召開第三次十字軍東征'],
  [173, '塞肋斯定三世',       'Pope Celestine III',     1191, 1198, '逝世', null],
  [174, '依諾增爵三世',       'Pope Innocent III',      1198, 1216, '逝世', '中世紀教權頂峰；第四次拉特朗大公會議'],
  [175, '何挪略三世',         'Pope Honorius III',      1216, 1227, '逝世', '批准方濟會、道明會'],
  [176, '額我略九世',         'Pope Gregory IX',        1227, 1241, '逝世', '建立宗教裁判所'],
  [177, '塞肋斯定四世',       'Pope Celestine IV',      1241, 1241, '逝世', null],
  [178, '依諾增爵四世',       'Pope Innocent IV',       1243, 1254, '逝世', '第一次里昂大公會議'],
  [179, '亞歷山大四世',       'Pope Alexander IV',      1254, 1261, '逝世', null],
  [180, '烏爾班四世',         'Pope Urban IV',          1261, 1264, '逝世', '訂立基督聖體節'],
  [181, '克勉四世',           'Pope Clement IV',        1265, 1268, '逝世', null],
  [182, '真福額我略十世',     'Pope Gregory X',         1271, 1276, '逝世', '第二次里昂大公會議'],
  [183, '真福依諾增爵五世',   'Pope Innocent V',        1276, 1276, '逝世', null],
  [184, '哈德良五世',         'Pope Adrian V',          1276, 1276, '逝世', null],
  [185, '若望二十一世',       'Pope John XXI',          1276, 1277, '意外逝世', null],
  [186, '尼古拉三世',         'Pope Nicholas III',      1277, 1280, '逝世', null],
  [187, '瑪爾定四世',         'Pope Martin IV',         1281, 1285, '逝世', null],
  [188, '何挪略四世',         'Pope Honorius IV',       1285, 1287, '逝世', null],
  [189, '尼古拉四世',         'Pope Nicholas IV',       1288, 1292, '逝世', '首位方濟會教宗'],
  [190, '聖塞肋斯定五世',     'Pope Celestine V',       1294, 1294, '退位', '主動退位後被囚'],
  [191, '博尼法八世',         'Pope Boniface VIII',     1294, 1303, '逝世', '阿那格尼之辱；對抗法王腓力四世'],
  [192, '真福本篤十一世',     'Pope Benedict XI',       1303, 1304, '逝世', null],
  [193, '克勉五世',           'Pope Clement V',         1305, 1314, '逝世', '亞維儂時期開始；解散聖殿騎士團'],
  [194, '若望二十二世',       'Pope John XXII',         1316, 1334, '逝世', '亞維儂教廷'],
  [195, '本篤十二世',         'Pope Benedict XII',      1334, 1342, '逝世', '亞維儂教廷'],
  [196, '克勉六世',           'Pope Clement VI',        1342, 1352, '逝世', '亞維儂教廷'],
  [197, '依諾增爵六世',       'Pope Innocent VI',       1352, 1362, '逝世', '亞維儂教廷'],
  [198, '真福烏爾班五世',     'Pope Urban V',           1362, 1370, '逝世', '亞維儂教廷'],
  [199, '額我略十一世',       'Pope Gregory XI',        1370, 1378, '逝世', '末位法籍教宗、回歸羅馬'],
  [200, '烏爾班六世',         'Pope Urban VI',          1378, 1389, '逝世', '西方大分裂開始'],
];

const valuesParts = popes.map(p => {
  const [n, zh, en, st, ed, reason, notes] = p;
  const safeNotes = notes ? notes.replace(/'/g, "''") : null;
  return `(${n}, '${zh}', '${en}', '羅馬', '天主教', ${st}, ${ed}, ${reason ? `'${reason}'` : 'NULL'}, '正統', 'Liber Pontificalis; Annuario Pontificio', ${safeNotes ? `'${safeNotes}'` : 'NULL'})`;
}).join(',\n  ');

const sql = `INSERT INTO episcopal_succession (succession_number, name_zh, name_en, see, church, start_year, end_year, end_reason, status, sources, notes) VALUES ${valuesParts} ON CONFLICT DO NOTHING RETURNING succession_number;`;
console.log(`Inserting ${popes.length} popes (batch 4)...`);
const res = await q(sql);
console.log(`Inserted ${res.length} new records.`);
