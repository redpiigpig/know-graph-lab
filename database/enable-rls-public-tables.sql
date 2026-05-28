-- Enable RLS on the 17 public tables flagged by Supabase security advisor (2026-05-25)
-- Pattern: anon role can SELECT, authenticated role can do everything.
-- Matches the existing policies on ebooks / books / book_categories etc.

DO $$
DECLARE
  t text;
  public_tables text[] := ARRAY[
    'ai_dialogue_categories',
    'ai_dialogue_entry_categories',
    'ai_dialogues',
    'ai_dialogues_chatgpt',
    'ai_dialogues_gemini',
    'annotations',
    'book_tags',
    'church_teachings',
    'concept_links',
    'concepts',
    'ebook_chunks',
    'excerpt_concepts',
    'excerpt_tags',
    'islamic_people',
    'tags',
    'theologians',
    'theological_terms'
  ];
BEGIN
  FOREACH t IN ARRAY public_tables LOOP
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);

    EXECUTE format($f$
      DROP POLICY IF EXISTS anon_read_%1$s ON public.%1$I;
      CREATE POLICY anon_read_%1$s ON public.%1$I
        FOR SELECT TO anon USING (true);
    $f$, t);

    EXECUTE format($f$
      DROP POLICY IF EXISTS auth_select_%1$s ON public.%1$I;
      CREATE POLICY auth_select_%1$s ON public.%1$I
        FOR SELECT TO authenticated USING (true);
    $f$, t);

    EXECUTE format($f$
      DROP POLICY IF EXISTS auth_insert_%1$s ON public.%1$I;
      CREATE POLICY auth_insert_%1$s ON public.%1$I
        FOR INSERT TO authenticated WITH CHECK (true);
    $f$, t);

    EXECUTE format($f$
      DROP POLICY IF EXISTS auth_update_%1$s ON public.%1$I;
      CREATE POLICY auth_update_%1$s ON public.%1$I
        FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
    $f$, t);

    EXECUTE format($f$
      DROP POLICY IF EXISTS auth_delete_%1$s ON public.%1$I;
      CREATE POLICY auth_delete_%1$s ON public.%1$I
        FOR DELETE TO authenticated USING (true);
    $f$, t);
  END LOOP;
END $$;

-- NOTE: spatial_ref_sys (PostGIS reference CRS table) is owned by the PostGIS
-- extension, not the project. Supabase still flags it in the advisor but it
-- cannot be altered via Management API / service role. Safe to ignore — it is
-- a read-only standards table (EPSG codes) and contains no user data.
