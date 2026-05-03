import pg from 'pg'
import dotenv from 'dotenv'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))
dotenv.config({ path: join(__dirname, '../.env') })

const { Pool } = pg

const pool = new Pool({
  host: process.env.SUPABASE_DB_HOST,
  user: process.env.SUPABASE_DB_USER,
  password: process.env.SUPABASE_DB_PASSWORD,
  database: process.env.SUPABASE_DB_NAME,
  port: 5432,
  ssl: { rejectUnauthorized: false },
})

async function run() {
  const client = await pool.connect()
  try {
    await client.query(`
      CREATE TABLE IF NOT EXISTS pong_editors (
        id           BIGSERIAL PRIMARY KEY,
        name         TEXT NOT NULL,
        gender       TEXT,
        age_group    TEXT,
        email        TEXT NOT NULL UNIQUE,
        church       TEXT,
        how_knew     TEXT,
        how_to_help  TEXT,
        role         TEXT NOT NULL DEFAULT 'editor',
        status       TEXT NOT NULL DEFAULT 'pending',
        applied_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
        approved_at  TIMESTAMPTZ,
        approved_by  TEXT,
        last_login   TIMESTAMPTZ,
        notes        TEXT,
        created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
      );
    `)
    console.log('✅ pong_editors table created (or already exists)')

    await client.query(`
      ALTER TABLE pong_media
        ADD COLUMN IF NOT EXISTS proofread_by   TEXT,
        ADD COLUMN IF NOT EXISTS proofread_date DATE,
        ADD COLUMN IF NOT EXISTS proofread_note TEXT;
    `)
    console.log('✅ pong_media proofread columns added')

    await client.query(`ALTER TABLE pong_editors ENABLE ROW LEVEL SECURITY;`)
    console.log('✅ RLS enabled on pong_editors')

  } catch (err) {
    console.error('❌ Error:', err.message)
    process.exit(1)
  } finally {
    client.release()
    await pool.end()
  }
}

run()
