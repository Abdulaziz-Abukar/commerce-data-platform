-- RAW layer schema
create schema if not exists raw;

-- USERS
create table if not exists raw.users (
    user_id          int                not null,
    batch_date       date               not null,
    source           text               not null,
    extracted_at     timestamptz        not null,
    loaded_at        timestamptz        not null,        default,        now(),
    payload_hash     text               not null,
    payload          jsonb              not null,
    primary key (user_id, batch_date)
);

-- PRODUCTS
create table if not exists raw.products (
    product_id       int                 not null,
    batch_date       date               not null,
    source           text               not null,
    extracted_at     timestamptz        not null,
    loaded_at        timestamptz        not null,        default,        now(),
    payload_hash     text               not null,
    payload          jsonb              not null,
    primary key (product_id, batch_date)
);

-- CARTS (orders)
create table if not exists raw.carts (
    cart_id       int                 not null,
    batch_date       date               not null,
    source           text               not null,
    extracted_at     timestamptz        not null,
    loaded_at        timestamptz        not null,        default,        now(),
    payload_hash     text               not null,
    payload          jsonb              not null,
    primary key (cart_id, batch_date)
)