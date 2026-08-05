create extension if not exists "pgcrypto";

create table if not exists profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    email text unique not null,
    name text not null,
    created_at timestamptz not null default now()
);

create table if not exists tasks (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    scope text not null check (scope in ('personal', 'family')),
    owner_id uuid not null references auth.users (id),
    assignee_id uuid references auth.users (id),
    priority integer not null default 0 check (priority between 0 and 2),
    due_date date,
    completed boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists idx_tasks_owner on tasks (owner_id);
create index if not exists idx_tasks_scope on tasks (scope);

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
    insert into public.profiles (id, email, name)
    values (new.id, new.email, split_part(new.email, '@', 1));
    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user();

alter table profiles enable row level security;
alter table tasks enable row level security;

create policy "profiles_select_any_auth"
    on profiles for select
    to authenticated
    using (true);

create policy "profiles_update_own"
    on profiles for update
    to authenticated
    using (id = auth.uid())
    with check (id = auth.uid());

create policy "tasks_select_visible"
    on tasks for select
    to authenticated
    using (
        scope = 'family'
        or owner_id = auth.uid()
        or assignee_id = auth.uid()
    );

create policy "tasks_insert_own"
    on tasks for insert
    to authenticated
    with check (owner_id = auth.uid());

create policy "tasks_update_visible"
    on tasks for update
    to authenticated
    using (
        owner_id = auth.uid()
        or assignee_id = auth.uid()
        or scope = 'family'
    )
    with check (
        owner_id = auth.uid()
        or assignee_id = auth.uid()
        or scope = 'family'
    );

create policy "tasks_delete_own"
    on tasks for delete
    to authenticated
    using (owner_id = auth.uid());