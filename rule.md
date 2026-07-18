# Nanco Paints Platform Architecture & Security Standards
Version: 1.0
Purpose: Mandatory architecture, security, and development rules for all future development.

---

# Project Overview

This platform consists of:

1. Public Website
2. ERP System
3. Dynamic Poster System
4. Product Management
5. Dealer Management
6. Inventory Management
7. Marketing Content Management
8. Media Storage System

The ERP is the source of truth.

The public website consumes only approved/public data.

---

# Core Principles

## Principle 1

Never trust the frontend.

Frontend is considered compromised by default.

All permissions must be enforced at backend/database level.

---

## Principle 2

Never expose secrets.

The following must NEVER appear in:

- HTML
- JavaScript
- GitHub
- Browser Storage
- Mobile Apps

Forbidden:

- Service Role Keys
- Database Passwords
- SMTP Credentials
- API Secrets
- Stripe Secret Keys
- JWT Signing Secrets

---

## Principle 3

Enable Zero Trust Security.

Every request must be validated.

Never assume a user is authenticated.

Never assume a user has permission.

---

# Architecture

## Public Website

Technology:
- HTML
- CSS
- JavaScript

Allowed Access:
- Published Products
- Published Posters
- Published Banners
- Published Offers

Forbidden:
- Inventory
- ERP Data
- Financial Data
- Employee Data
- User Management

Connection:

Public Website
↓
Supabase (Anon Key Only)
↓
Public Tables Only

---

## ERP System

Technology:
- Next.js
- TypeScript
- Tailwind
- Shadcn UI

Connection:

ERP Frontend
↓
Backend API
↓
Supabase Service Role
↓
Database

ERP must NEVER connect directly using Service Role credentials.

---

# Database Design

Database: PostgreSQL (Supabase)

Schemas:

public
erp
audit

---

## Public Schema

Contains:

products
categories
posters
banners
offers

Website may read these tables.

---

## ERP Schema

Contains:

inventory
sales
purchases
dealers
employees
suppliers
settings
reports

Website must never access these tables.

---

## Audit Schema

Contains:

login_logs
activity_logs
security_logs
api_logs

Append-only.

No deletes allowed.

---

# Row Level Security (RLS)

Mandatory.

Every table must have:

ALTER TABLE ENABLE ROW LEVEL SECURITY;

No exceptions.

---

## Public Policies

Example:

Products:

Allow:
SELECT

Condition:

is_published = true

---

Posters:

Allow:
SELECT

Condition:

status = 'published'

---

## ERP Policies

Authenticated users only.

Admin role required for:

INSERT
UPDATE
DELETE

---

# Authentication

Provider:
Supabase Auth

Roles:

super_admin
admin
manager
employee
viewer

Never use boolean flags like:

is_admin

Use proper role systems.

---

# Authorization

All backend endpoints must verify:

1. Authentication
2. User Status
3. Role
4. Resource Permission

Example:

User
↓
JWT Verification
↓
Role Check
↓
Permission Check
↓
Action

---

# API Security

Every endpoint must:

Validate Input
Sanitize Input
Rate Limit Requests
Log Activity

Use:

Zod

for validation.

---

Example:

POST /api/products

Validate:

name
price
description
category

before database access.

---

# File Storage

Provider:
Supabase Storage

---

## Public Buckets

product-images

posters

banners

marketing-videos

---

## Private Buckets

invoices

erp-documents

employee-files

exports

backups

---

# Signed URLs

Private files must use:

Signed URLs

Expiration:

5–30 minutes

Never expose direct private URLs.

---

# Media Rules

Do not store:

Images
Videos
PDFs

inside PostgreSQL.

Store only:

id
title
storage_path
metadata

Actual files go to Storage.

---

# Backup Strategy

Daily Database Backup

Retention:
30 days

Weekly Backup:
12 weeks

Monthly Backup:
12 months

Test restoration monthly.

---

# Logging

Log:

Login
Logout
Product Changes
Inventory Changes
Permission Changes
Failed Logins
API Errors

Store in audit schema.

---

# Monitoring

Monitor:

Database CPU
Database Storage
Bandwidth
Failed Requests
Failed Logins
Suspicious Activities

Alerts required.

---

# Frontend Security

Use:

Content Security Policy (CSP)

Security Headers:

X-Frame-Options

X-Content-Type-Options

Referrer-Policy

Permissions-Policy

Strict-Transport-Security

---

# Password Rules

Minimum:

12 Characters

Require:

Uppercase
Lowercase
Number
Special Character

Enable MFA for:

super_admin
admin

Mandatory.

---

# Environment Variables

Store only on server:

SUPABASE_SERVICE_ROLE_KEY

JWT_SECRET

SMTP_PASSWORD

API_KEYS

Never expose to frontend.

---

# Development Rules

No direct SQL in frontend.

No Service Role in frontend.

No hardcoded credentials.

No bypassing RLS.

No disabling security policies.

No storing secrets in source code.

---

# Deployment Architecture

Public Website
↓
Cloudflare CDN
↓
Static Hosting

ERP Frontend
↓
Vercel / VPS

Backend API
↓
Vercel Functions / VPS

Supabase
↓
PostgreSQL
↓
Storage
↓
Auth

---

# Future Scalability

Prepare for:

10,000+ Products
100,000+ Media Files
500+ Dealers
50+ ERP Users
1M+ Website Visits

Use:

Pagination
Caching
CDN
Image Optimization
Lazy Loading

---

# AI Agent Development Rules

When generating code:

1. Follow this document strictly.
2. Security overrides convenience.
3. Never expose secrets.
4. Respect schema separation.
5. Use RLS everywhere.
6. Use role-based access control.
7. Validate every input.
8. Log all critical actions.
9. Use least-privilege access.
10. Refuse architectures that violate this document.

END OF DOCUMENT