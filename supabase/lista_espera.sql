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

create policy "site pode inscrever"
  on public.lista_espera
  for insert
  to anon
  with check (consentimento = true);

-- Sem políticas de SELECT, UPDATE ou DELETE: com RLS ativo, essas operações ficam bloqueadas
-- para a chave pública. Só o dono do projeto vê os registos (Table Editor / service role).

-- língua do email de confirmação (pt, en, es, fr, ru, ar, vi, zh…), enviada pelo site
alter table public.lista_espera add column if not exists idioma text check (idioma ~ '^[a-z]{2,3}(-[a-z0-9]{2,8})?$');

-- email sem espaços nem "mailto:", "<>", aspas, etc. (o site já limpa; isto é a segunda barreira)
-- "not valid": só se aplica a inscrições novas, não mexe nas que já existem
alter table public.lista_espera add constraint lista_espera_email_limpo check (email !~ '[[:space:]:;,<>()"]') not valid;
