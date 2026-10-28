-- The ${{ values.entities }}: the same table as the ${{ values.name }} of the Python Framework. Its name quoted: an application made from this one
-- may name its table as a word of SQL (order, user).
create table "${{ values.entity }}" (
    id          bigserial    primary key,
    name        varchar(80)  not null unique,
    category     varchar(40)  not null,
    status      varchar(16)  not null default 'active',
    start_date  date,
    created_at  timestamptz  not null default now(),
    created_by  varchar(120) not null
);
create index ${{ values.entity }}_category on "${{ values.entity }}" (category);
create index ${{ values.entity }}_status on "${{ values.entity }}" (status);
