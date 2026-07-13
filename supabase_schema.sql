-- Solitario Battle · pegá este archivo completo en Supabase > SQL Editor.
-- La publishable key del cliente puede leer e insertar; no incluyas nunca
-- una secret/service_role key en la aplicación.

create table if not exists public.leaderboard_entries (
    id uuid primary key default gen_random_uuid(),
    device_id uuid not null,
    player_name varchar(24) not null check (char_length(trim(player_name)) between 1 and 24),
    difficulty varchar(10) not null check (difficulty in ('facil', 'dificil')),
    score integer not null check (score >= 0),
    piles_finales smallint not null check (piles_finales between 1 and 48),
    moves smallint not null check (moves >= 0),
    duration_seconds integer not null check (duration_seconds >= 0),
    played_at timestamptz not null default now(),
    created_at timestamptz not null default now()
);

create index if not exists leaderboard_global_order
    on public.leaderboard_entries (score desc, duration_seconds asc, moves asc);
create index if not exists leaderboard_personal_order
    on public.leaderboard_entries (device_id, score desc, duration_seconds asc, moves asc);

alter table public.leaderboard_entries enable row level security;

create policy "El ranking mundial es público"
on public.leaderboard_entries for select to anon, authenticated using (true);

create policy "Los clientes pueden publicar partidas"
on public.leaderboard_entries for insert to anon, authenticated with check (
    score >= 0 and piles_finales between 1 and 48 and duration_seconds >= 0
);

-- No hay políticas de UPDATE o DELETE: una partida publicada no se altera
-- desde el cliente. Para una fase competitiva real, sustituí la política de
-- INSERT por Supabase Auth + una Edge Function que valide la partida.
