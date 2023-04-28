create schema raw;

create table raw.city (
    id varchar,
    name varchar,
    population integer
);

create table raw.user (
    id varchar,
    name varchar,
    height_cm integer,
    date_of_birth date,
    city_id varchar
);
