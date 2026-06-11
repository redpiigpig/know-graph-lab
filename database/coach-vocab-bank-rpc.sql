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

grant execute on function public.pick_vocab_bank(text, text, uuid, int) to authenticated, service_role, anon;
grant execute on function public.vocab_bank_categories(text) to authenticated, service_role, anon;
