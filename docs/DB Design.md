<p align="center">
  <img src="https://github.com/Irshad-11/Documents/blob/main/AskBook%20DBD.png?raw=true" alt="AI AskBook SRS Banner" style="max-width:800px; width:100%;">
</p>


# AI AskBook Database Design Documentation

**Version 1.0**  
**Date: February 3, 2026**  
**Prepared by: Irshad Hossain**

## Table of Contents
- [AI AskBook Database Design Documentation](#ai-askbook-database-design-documentation)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Scope](#12-scope)
  - [2. Database Overview](#2-database-overview)
  - [3. Entity Relationship Diagram (ERD)](#3-entity-relationship-diagram-erd)
  - [4. Detailed Table Specifications](#4-detailed-table-specifications)
    - [4.1 User Table](#41-user-table)
    - [4.2 Post Table](#42-post-table)
    - [4.3 Core Relationships](#43-core-relationships)
  - [5. Database Connections \& Relationships](#5-database-connections--relationships)
    - [5.1 Django → PostgreSQL Connection](#51-django--postgresql-connection)
    - [5.2 Connection Flow Diagram](#52-connection-flow-diagram)
  - [6. Indexes \& Constraints](#6-indexes--constraints)
    - [6.1 Primary Indexes (Auto-created)](#61-primary-indexes-auto-created)
    - [6.2 Foreign Key Constraints](#62-foreign-key-constraints)

## 1. Introduction

### 1.1 Purpose
This document specifies the complete database schema for **AI AskBook**, a PostgreSQL database powering a prompt-sharing platform. It includes entity relationships, constraints, indexes, and deployment details for Render hosting.

### 1.2 Scope
- PostgreSQL 13+ relational schema
- Django ORM mapping
- Render PostgreSQL deployment
- Production-ready indexes and constraints

## 2. Database Overview

**Database Name:** `ai_askbook_production`  
**Engine:** PostgreSQL 15+  
**Hosting:** Render PostgreSQL (Free tier)  
**Character Set:** UTF8MB4  
**Collation:** `en_US.UTF-8`

```
Connection Flow:
Django App (Render Web Service) 
    ↓ (DATABASE_URL env var)
PostgreSQL Instance (Render Database)
```

## 3. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USER ||--o{ POST : "created_by"
    USER ||--o{ FAVOURITE : "favourites"
    USER ||--o{ POST_REACTION : "post_reactions"
    
    POST ||--o{ POST_TAG : "post_tags"
    POST ||--o{ FAVOURITE : "favourited_by"
    POST ||--o{ POST_REACTION : "reactions"
    
    TAG ||--o{ POST_TAG : "tag_posts"
    
    USER {
        int id PK
        varchar username
        varchar email UK
        boolean is_verified
        text bio
        varchar works_at
        varchar institute_at
        varchar location
        varchar avatar
        varchar avatar_url
        varchar profile_slug UK
        varchar github_url
        varchar linkedin_url
        timestamp date_joined
        timestamp last_login
    }
    
    POST {
        int id PK
        varchar title
        varchar slug UK
        text summary
        text prompt_text
        text description_md
        int created_by FK
        varchar status
        boolean is_public
        boolean is_featured
        int views_count
        int likes_count
        int dislikes_count
        text rejection_reason
        varchar ai_model
        varchar difficulty_level
        timestamp created_at
        timestamp updated_at
        timestamp published_at
    }
    
    TAG {
        int id PK
        varchar name
        varchar slug UK
        timestamp created_at
    }
    
    POST_TAG {
        int id PK
        int post FK
        int tag FK
    }
    
    FAVOURITE {
        int id PK
        int user FK
        int post FK
        timestamp created_at
    }
    
    POST_REACTION {
        int id PK
        int user FK
        int post FK
        varchar reaction_type
        timestamp created_at
        timestamp updated_at
    }
```

## 4. Detailed Table Specifications

### 4.1 User Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `SERIAL PK` | PRIMARY KEY | Auto-incrementing user ID |
| `email` | `VARCHAR(254) UNIQUE` | NOT NULL, UNIQUE | User email address |
| `is_verified` | `BOOLEAN` | DEFAULT FALSE | Admin verification status |
| `bio` | `TEXT` | NULLABLE | User biography |
| `profile_slug` | `VARCHAR(160) UNIQUE` | UNIQUE | URL-friendly username slug |

### 4.2 Post Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `SERIAL PK` | PRIMARY KEY | Auto-incrementing post ID |
| `slug` | `VARCHAR(255) UNIQUE` | UNIQUE, NOT NULL | URL-friendly post title |
| `status` | `VARCHAR(10)` | CHECK(STATUS_CHOICES) | PENDING/APPROVED/REJECTED |
| `is_featured` | `BOOLEAN` | DEFAULT FALSE | Admin featured status |

### 4.3 Core Relationships


```mermaid
graph TB
    U[User] -->|1:N<br/>created_by| P[Post]
    P -->|1:N<br/>post_tags| PT[PostTag]
    PT -->|N:1<br/>tag| T[Tag]
    
    U -->|N:M<br/>post_reactions| PR[PostReaction]
    PR -->|N:1<br/>reactions| P
    
    U -->|N:M<br/>favourites| F[Favourite]
    F -->|N:1<br/>favourited_by| P
    
    classDef entity fill:#e1f5fe,stroke:#01579b,stroke-width:3px,color:#000
    class U,P,T,PT,PR,F entity
    
    style U fill:#c8e6c9
    style P fill:#fff3e0
```

## 5. Database Connections & Relationships

### 5.1 Django → PostgreSQL Connection
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ai_askbook_production',
        'USER': os.environ.get('PGUSER'),
        'PASSWORD': os.environ.get('PGPASSWORD'),
        'HOST': os.environ.get('PGHOST'),
        'PORT': os.environ.get('PGPORT'),
    }
}
```

**Render Environment Variables:**
```
DATABASE_URL=postgresql://user:pass@hostname:port/dbname
PGUSER=ai_askbook_user
PGPASSWORD=secure_password
PGHOST=dpg-xxx.render.com
PGPORT=5432
```

### 5.2 Connection Flow Diagram
```mermaid
graph TD
    A[Render Web Service<br/>Django App] -->|DATABASE_URL<br/>SSL Connection| B[Render PostgreSQL<br/>ai_askbook_production]
    A -->|Django ORM Queries| C[(User Table)]
    A -->|Django ORM Queries| D[(Post Table)]
    B --> C
    B --> D
    C --> E[(Tag Table)]
    D --> F[(PostTag Junction)]
    D --> G[(Reaction Table)]
```

## 6. Indexes & Constraints

### 6.1 Primary Indexes (Auto-created)
```
POST: status, created_at (compound index)
POST_REACTION: post, reaction_type
POST_TAG: UNIQUE(post, tag)
FAVOURITE: UNIQUE(user, post)
```

### 6.2 Foreign Key Constraints
```
created_by → auth_user.id (CASCADE)
post → auth_user.id (CASCADE)
tag → tag.id (CASCADE)
user → auth_user.id (CASCADE)
```
