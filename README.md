# Commerce Data Platform

## Overview

The **Commerce Data Platform** is an end-to-end analytics pipeline that ingests raw e-commerce data from external APIs, transforms it using modern data modeling practices, and delivers analytics-ready marts in BigQuery. The platform is fully orchestrated with Airflow and follows analytics engineering best practices using dbt.

This project is designed as a **portfolio-grade data platform** demonstrating ingestion, transformation, orchestration, and modeling at production-level quality.

## High-Level Architecture

**Source → Ingestion → Raw → Staging → Marts → Analytics**

1. External APIs (Users, Products, Carts)
2. Python ingestion layer
3. BigQuery raw datasets
4. dbt staging models
5. dbt marts (facts & dimensions)
6. Airflow orchestration (daily schedule)

## Core Components

### 1. Ingestion Layer (Python)

- Modular Python ingestion framework
- Entity-based ingestion (`users`, `products`, `carts`)
- Parameterized by `batch_date`
- Writes raw data directly to BigQuery
- Supports retries and idempotent loads

**Key Features:**

- CLI-driven ingestion (`python -m src.ingestion.run_ingest`)
- Centralized loaders
- Raw table naming conventions

---

### 2. Data Warehouse (BigQuery)

- SIngle project with layered datasets
- Raw ingestion tables
- Analytics dataset for staging and marts
- Optimized for analytical workloads

---

### 3. dbt Transformations

- dbt Core + BigQuery adapter
- Staging mdoels normalize raw API data
- Marts follow Kimball-style dimensional modeling

**Model Layers:**

- `staging`: cleaned, typed, lightly transformed source data
- `marts`: business-ready fact and dimension tables

**dbt Capabilities Used**:

- `ref()`-based dependencies
- Source freshness assumptions
- Tests for data quality

---

### 4. Airflow Orchestration

- Single daily DAG: `commerce_data_platform_daily`
- Fully automated pipeline execution

**DAG Flow**:

1. Ingest users
2. Ingest products
3. Ingest carts
4. Run dbt staging models
5. Run dbt marts
6. Execute dbt tests

**Key Characteristics**:

- BashOperator-based execution
- Environment-driven configuration
- Supports scheduled and manual backfills

## Execution

### Local Development

- Dockerized Airflow environment
- BigQuery service account authentication
- dbt executed inside Airflow container

### Running the Pipeline

- Automatic daily schedule via Airflow
- Manual triggers supported through UI
- Parameterized batch dates for reprocessing

## Design Principles

- **Separation of concerns** (ingestion vs transformation)
- **Analytics engineering best practices**
- **Reproducible, determinstic pipelines**
- **Production-oriented structure**
- **Portfolio-grade documentation and clarity**

## Author

Built as part of a long-term data engineering and analytics portfolio
