-- BigQuery DDL (run in BigQuery console or via bq)
-- Dataset
CREATE SCHEMA IF NOT EXISTS `commerce-data-platform-484619.raw`;

-- USERS
CREATE TABLE IF NOT EXISTS `commerce-data-platform-484619.raw.users` (
  user_id       INT64 NOT NULL,
  batch_date    DATE NOT NULL,
  source        STRING NOT NULL,
  extracted_at  TIMESTAMP NOT NULL,
  loaded_at     TIMESTAMP NOT NULL,
  payload_hash  STRING NOT NULL,
  payload       JSON NOT NULL
)
PARTITION BY batch_date
CLUSTER by user_id;

-- PRODUCTS
CREATE TABLE IF NOT EXISTS `commerce-data-platform-484619.raw.products` (
  product_id    INT64 NOT NULL,
  batch_date    DATE NOT NULL,
  source        STRING NOT NULL,
  extracted_at  TIMESTAMP NOT NULL,
  loaded_at     TIMESTAMP NOT NULL,
  payload_hash  STRING NOT NULL,
  payload       JSON NOT NULL
)
PARTITION BY batch_date
CLUSTER by product_id;

-- CARTS
CREATE TABLE IF NOT EXISTS `commerce-data-platform-484619.raw.carts` (
  cart_id       INT64 NOT NULL,
  batch_date    DATE NOT NULL,
  source        STRING NOT NULL,
  extracted_at  TIMESTAMP NOT NULL,
  loaded_at     TIMESTAMP NOT NULL,
  payload_hash  STRING NOT NULL,
  payload       JSON NOT NULL
)
PARTITION BY batch_date
CLUSTER by cart_id;