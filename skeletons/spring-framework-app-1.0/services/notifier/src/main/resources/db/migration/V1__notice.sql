-- The notices of the ${{ values.title }}: one per event that deserves one.
create table notice (
    id          bigserial    primary key,
    event_id    uuid         not null unique,
    type        varchar(80)  not null,
    recipient   varchar(120),
    text        varchar(400) not null,
    created_at  timestamptz  not null default now()
);
