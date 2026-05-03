#!/usr/bin/env node
/**
 * db_write_from_transcripts.cjs
 * 讀取 stores/transcripts/<youtube_id>.txt，寫入或更新 pong_media
 * 用法：node scripts/db_write_from_transcripts.cjs
 */
const fs = require('fs');
const path = require('path');
const https = require('https');

require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

const BASE_URL = process.env.VITE_SUPABASE_URL.replace(/\/$/, '');
const KEY = process.env.SUPABASE_SERVICE_KEY;
const TRANSCRIPT_DIR = path.join(__dirname, '..', 'stores', 'transcripts');

const TALKS = [
  {
    youtube_id: '9aWpePHshxE',
    youtube_start: 28,
    media_type: 'talk',
    title: '負責的恩典：當代門徒與受苦的世界',
    broadcast_date: '2018-11-22',
    source: '2018苦難神學研討會',
    source_en: '2018 Theology of Suffering Symposium',
    program_name: '身心障礙者與福音的對遇',
    location: '天主教大坪林聖三堂',
    interviewer: '董倫賢牧師（引言）',
    description: '2018年苦難神學研討會主題演講。龐君華牧師探討當代門徒如何在受苦的世界中活出「負責的恩典」，並正視身心障礙者與福音相遇的神學課題。',
    tags: ['苦難神學', '門徒訓練', '身心障礙', '恩典'],
    lang: 'zh',
  },
  {
    youtube_id: 'Px2I24CRPxo',
    youtube_start: 23,
    media_type: 'talk',
    title: '門徒：有別於世界的信仰群體',
    broadcast_date: '2019-10-01',
    source: '聖光神學院',
    source_en: 'Taiwan Theological Seminary and College',
    program_name: '',
    location: '聖光神學院',
    interviewer: '',
    description: '龐君華牧師於聖光神學院演講，探討門徒身分的核心意義——信仰群體如何成為「有別於世界」的見證。',
    tags: ['門徒訓練', '信仰群體', '教會'],
    lang: 'zh',
  },
  {
    youtube_id: 'YrtfxTB6_i4',
    youtube_start: 0,
    media_type: 'talk',
    title: '主共同體的成聖：約翰衛斯理小組和教會更新運動',
    broadcast_date: '2015-03-24',
    source: '衛斯理學術研討會',
    source_en: 'Wesleyan Academic Symposium',
    program_name: '',
    location: '聖光神學院',
    interviewer: '',
    description: '龐君華牧師於衛斯理學術研討會發表，探討約翰衛斯理的小組傳統與教會更新運動，如何透過主共同體的實踐走向成聖。',
    tags: ['成聖', '衛斯理神學', '信仰群體', '學術'],
    lang: 'zh',
  },
];

function sbRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const bodyStr = body ? JSON.stringify(body) : '';
    const url = new URL(BASE_URL + path);
    const opts = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: {
        'apikey': KEY,
        'Authorization': `Bearer ${KEY}`,
        'Content-Type': 'application/json',
        'Prefer': method === 'GET' ? 'return=representation' : 'return=minimal',
        'Content-Length': Buffer.byteLength(bodyStr),
      },
    };
    const req = https.request(opts, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: data ? JSON.parse(data) : null }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

async function checkExisting(youtube_id) {
  const r = await sbRequest('GET', `/rest/v1/pong_media?youtube_id=eq.${youtube_id}&select=id,title,transcript`);
  return r.body && r.body[0] ? r.body[0] : null;
}

async function patchTranscript(id, transcript) {
  const r = await sbRequest('PATCH', `/rest/v1/pong_media?id=eq.${id}`, { transcript });
  if (r.status === 200 || r.status === 204) {
    console.log(`  ✅ PATCH 成功 id=${id}`);
  } else {
    console.log(`  ❌ PATCH 失敗 ${r.status}: ${JSON.stringify(r.body).slice(0, 200)}`);
  }
}

async function insertMedia(talk, transcript) {
  const url = `https://www.youtube.com/watch?v=${talk.youtube_id}`;
  const payload = {
    title: talk.title,
    source: talk.source || '',
    source_en: talk.source_en || null,
    program_name: talk.program_name || null,
    interviewer: talk.interviewer || null,
    media_type: talk.media_type,
    platform: 'youtube',
    youtube_id: talk.youtube_id,
    youtube_start: talk.youtube_start || null,
    url,
    broadcast_date: talk.broadcast_date,
    transcript,
    description: talk.description || '',
    tags: talk.tags || [],
    is_published: true,
  };
  const r = await sbRequest('POST', '/rest/v1/pong_media', payload);
  if (r.status === 200 || r.status === 201) {
    console.log(`  ✅ INSERT 成功`);
  } else {
    console.log(`  ❌ INSERT 失敗 ${r.status}: ${JSON.stringify(r.body).slice(0, 300)}`);
  }
}

async function main() {
  if (!fs.existsSync(TRANSCRIPT_DIR)) {
    console.log('stores/transcripts/ 資料夾不存在，請先跑 Whisper 轉錄。');
    return;
  }

  for (const talk of TALKS) {
    const txtPath = path.join(TRANSCRIPT_DIR, `${talk.youtube_id}.txt`);
    if (!fs.existsSync(txtPath)) {
      console.log(`\n[SKIP] ${talk.title} — 找不到 ${talk.youtube_id}.txt，請先轉錄`);
      continue;
    }
    const transcript = fs.readFileSync(txtPath, 'utf-8').trim();
    console.log(`\n═══ ${talk.title} (${talk.youtube_id}) ═══`);
    console.log(`  逐字稿：${transcript.length} 字元`);

    const existing = await checkExisting(talk.youtube_id);
    if (existing) {
      if (existing.transcript) {
        console.log(`  已存在且有逐字稿（id=${existing.id}），跳過`);
      } else {
        console.log(`  已存在但無逐字稿（id=${existing.id}），補跑 PATCH...`);
        await patchTranscript(existing.id, transcript);
      }
    } else {
      console.log(`  不存在，INSERT 中...`);
      await insertMedia(talk, transcript);
    }
  }
  console.log('\n全部完成。');
}

main().catch(e => { console.error(e); process.exit(1); });
