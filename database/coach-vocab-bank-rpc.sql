-- 從共用字庫抽「使用者尚未擁有」的字（隨機）；缺題時 vocab.generate 先呼叫這個，AI 只當最後手段。
create or replace function public.pick_vocab_bank(
  p_language text, p_category text, p_user uuid, p_limit int
) returns setof public.lang_vocab_bank
language sql stable as $$
  select b.* from public.lang_vocab_bank b
  where b.language = p_language
    and b.glossed = true
    and (p_category is null or b.category = p_category)
    and not exists (
      select 1 from public.lang_vocab v
      where v.user_id = p_user and v.language = p_language and v.word = b.word
    )
  order by random()
  limit greatest(1, p_limit);
$$;

-- 該語言字庫的分類標籤 + 數量（前端複習頁推薦 chip / 每日輪替用）。
create or replace function public.vocab_bank_categories(p_language text)
returns table(category text, n bigint)
language sql stable as $$
  select category, count(*)::bigint as n
  from public.lang_vocab_bank
  where language = p_language and glossed = true
  group by category
  order by min(freq_rank) nulls last, category;
$$;

-- 該語言字庫的分級標籤 + 數量（字典瀏覽頁「分級」分頁用）。
create or replace function public.vocab_bank_levels(p_language text)
returns table(level text, n bigint)
language sql stable as $$
  select coalesce(level, '—') as level, count(*)::bigint as n
  from public.lang_vocab_bank
  where language = p_language and glossed = true
  group by coalesce(level, '—')
  order by min(freq_rank) nulls last, level;
$$;

-- 批次寫入語意主題：一次更新整批 [{word, theme}]（theme 分類腳本用）。
create or replace function public.set_vocab_themes(p_language text, p_pairs jsonb)
returns void language sql as $$
  update public.lang_vocab_bank b
  set theme = x.theme, updated_at = now()
  from jsonb_to_recordset(p_pairs) as x(word text, theme text)
  where b.language = p_language and b.word = x.word;
$$;

-- 該語言字庫的語意主題標籤 + 數量（字典「主題」分頁用），依數量排序。
create or replace function public.vocab_bank_themes(p_language text)
returns table(theme text, n bigint)
language sql stable as $$
  select theme, count(*)::bigint as n
  from public.lang_vocab_bank
  where language = p_language and glossed = true and theme is not null
  group by theme
  order by count(*) desc, theme;
$$;

grant execute on function public.pick_vocab_bank(text, text, uuid, int) to authenticated, service_role, anon;
grant execute on function public.vocab_bank_categories(text) to authenticated, service_role, anon;
grant execute on function public.vocab_bank_levels(text) to authenticated, service_role, anon;
grant execute on function public.set_vocab_themes(text, jsonb) to authenticated, service_role, anon;
grant execute on function public.vocab_bank_themes(text) to authenticated, service_role, anon;
