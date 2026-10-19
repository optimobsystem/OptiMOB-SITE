-- OptiMOB · lista de espera do acesso antecipado
-- Correr uma vez no Supabase: Dashboard › SQL Editor › New query › colar › Run.

create table if not exists public.lista_espera (
  id             uuid primary key default gen_random_uuid(),
  criado_em      timestamptz not null default now(),
  email          text not null check (char_length(email) between 5 and 254 and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]{2,}$'),
  perfil         text not null check (perfil in ('Marcenaria', 'Designer de interiores', 'Fábrica de mobiliário', 'Outro')),
  origem         text check (origem in ('topo', 'final')),
  consentimento  boolean not null check (consentimento = true)
);

-- um email só entra uma vez (sem diferenciar maiúsculas)
create unique index if not exists lista_espera_email_unico on public.lista_espera (lower(email));

-- Segurança: o site (chave pública) só pode INSERIR. Ninguém de fora pode ler, alterar ou apagar.
alter table public.lista_espera enable row level security;

drop policy if exists "site pode inscrever" on public.lista_espera;
create policy "site pode inscrever"
  on public.lista_espera
  for insert
  to anon
  with check (consentimento = true);

revoke all on public.lista_espera from anon, authenticated;
grant insert (email, perfil, origem, consentimento) on public.lista_espera to anon;
