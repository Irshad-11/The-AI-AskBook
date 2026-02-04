<p align="center">
  <img src="https://github.com/Irshad-11/Documents/blob/main/AskBook%20SRS.png?raw=true" alt="AI AskBook SRS Banner" style="max-width:800px; width:100%;">
</p>


# Software Requirements Specification (SRS)  
**AI AskBook - Prompt Sharing Platform**  
**Version 1.0**  
**IEEE Std 830-1998 Compliant**  
**Prepared by: Irshad Hossain**  
**Date: February 3, 2026**

## Table of Contents
1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Specific Requirements](#3-specific-requirements)

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) defines the functional and non-functional requirements for **AI AskBook**, a full-stack platform for discovering, sharing, and managing high-quality AI prompts. The system enables users to browse proven prompts, contribute their own, and collaborate through voting and moderation.

### 1.2 Scope
AI AskBook provides:
- Public prompt discovery and browsing
- Member-contributed prompt posting with moderation
- Admin content and user management
- Search, filtering, and social features (like, favorite, featured)

**Out of Scope (MVP):** Data portability automation, monetization, advanced analytics.

### 1.3 Definitions, Acronyms, and Abbreviations
| Term | Definition |
|------|------------|
| **Prompt** | Structured text instruction for AI models (ChatGPT, Claude, etc.) |
| **AI Modes** | Target AI platforms (ChatGPT, Claude, Midjourney, etc.) |
| **Feed** | Homepage displaying prompt cards |
| **MVP** | Minimum Viable Product |

### 1.4 References
- Project README: [GitHub Repository](https://github.com/Irshad-11/The-AI-AskBook)
- Database Design: [Technical Documentation](https://github.com/Irshad-11/The-AI-AskBook/docs/)

### 1.5 Overview
Section 2 provides system perspective and constraints. Section 3 details functional and non-functional requirements using "The system shall..." format.

## 2. Overall Description

### 2.1 Product Perspective
AI AskBook solves the AI prompt engineering bottleneck by creating a community-driven library of battle-tested prompts, eliminating trial-and-error.

### 2.2 Product Functions
- **Public Access:** Browse feed, view prompts, profiles
- **Member Features:** Post prompts, manage profile/posts, like/favorite
- **Admin Controls:** User verification, content moderation, featured selection
- **Discovery:** Search, filter by difficulty/tags, sort by popularity

### 2.3 User Classes and Characteristics
| User Class | Description | Privileges |
|------------|-------------|------------|
| **Public User** | Unauthenticated visitor | View feed, prompts, profiles |
| **Unverified Member** | Registered, pending verification | Post (pending), manage own content |
| **Verified Member** | Approved contributor | Direct posting, full member features |
| **Admin** | Platform moderator | Full system management |

### 2.4 Operating Environment
- **Backend:** Django, PostgreSQL
- **Frontend:** Jinja2, Tailwind CSS
- **Hosting:** Render
- **Browser:** Modern browsers (Chrome 90+, Firefox 88+, Safari 14+)

### 2.5 Design and Implementation Constraints
- Follow existing tech stack (Django, PostgreSQL, Tailwind)
- Responsive design for desktop/mobile
- Manual admin verification (MVP)

### 2.6 Assumptions and Dependencies
- Stable Render hosting
- Manual data migration capability
- PostgreSQL database access

## 3. Specific Requirements

### 3.1 External Interfaces

#### 3.1.1 User Interfaces
**The system shall provide:**
- Responsive feed with prompt cards (title, summary, author, stats)
- Detailed prompt view with full content, tags, difficulty, AI modes
- User profile pages showing posts, likes, favorites
- Search bar with autocomplete
- Filter panels (difficulty, tags, sort options)

#### 3.1.2 Hardware Interfaces
None.

#### 3.1.3 Software Interfaces
- RESTful APIs for frontend-backend communication
- PostgreSQL 13+ database

#### 3.1.4 Communications Interfaces
- HTTPS for all communications
- Render hosting environment

### 3.2 Functional Requirements

#### 3.2.1 Public User Functions (FR-001 to FR-005)
**The system shall allow:**

**FR-001:** Public users to view the homepage feed without authentication.  
**FR-002:** Public users to view any prompt details (title, summary, full prompt, description, tags, difficulty, AI modes).  
**FR-003:** Public users to view any member profile and their public posts.  
**FR-004:** Public users to use keyword search across all public prompts.  
**FR-005:** Public users to filter prompts by difficulty (Beginner, Intermediate, Advanced).

#### 3.2.2 Member Functions (FR-006 to FR-015)
**The system shall allow:**

**FR-006:** Registered members to create accounts via email/password.  
**FR-007:** Unverified members to submit prompts for admin review (pending status).  
**FR-008:** Verified members to post prompts directly (auto-approved).  
**FR-009:** Members to edit/delete their own prompts.  
**FR-010:** Members to like/dislike prompts (toggle functionality).  
**FR-011:** Members to favorite/unfavorite prompts.  
**FR-012:** Members to manage their profile (edit details, delete account).  
**FR-013:** Members to view their posting stats (likes, favorites received).

#### 3.2.3 Admin Functions (FR-016 to FR-022)
**The system shall allow:**

**FR-016:** Admins to view all member accounts and their verification status.  
**FR-017:** Admins to verify/unverify members manually.  
**FR-018:** Admins to approve/reject pending prompts.  
**FR-019:** Admins to mark any prompt as "Featured".  
**FR-020:** Admins to delete any content (prompts, accounts).  
**FR-021:** Admins to view platform analytics (total prompts, users, etc.).  
**FR-022:** Admins to manage system settings (featured prompts rotation).

#### 3.2.4 Search & Discovery (FR-023 to FR-027)
**The system shall allow:**

**FR-023:** Keyword search across prompt titles, summaries, and content.  
**FR-024:** Filtering by difficulty level (Beginner/Intermediate/Advanced).  
**FR-025:** Quick filters: Most Liked, Most Favorited, Featured.  
**FR-026:** Tag-based filtering and search.  
**FR-027:** Sorting by relevance, date, popularity (likes+favorites).

#### 3.2.5 Prompt Structure (FR-028)
**The system shall support prompts containing:**
- Title (max 100 chars)
- Summary (max 200 chars)
- Full Prompt text
- Markdown Description
- Tags (comma-separated)
- Difficulty (Beginner/Intermediate/Advanced)
- AI Modes (multi-select: ChatGPT, Claude, Midjourney, etc.)
- Public/Private toggle

### 3.3 Non-Functional Requirements (NFR)

#### 3.3.1 Performance (NFR-001 to NFR-004)
**The system shall:**
- **NFR-001:** Load feed with 50 prompts in under 3 seconds (Render Free plan cold starts).
- **NFR-002:** Support 100 concurrent users (Render Free plan limits).
- **NFR-003:** Search return results in under 1 second.
- **NFR-004:** Handle 5,000 prompts with acceptable degradation on free tier.


#### 3.3.2 Reliability (NFR-005 to NFR-006)
**The system shall:**
- **NFR-005:** Achieve 99.5% uptime.
- **NFR-006:** Maintain data integrity during admin operations.

#### 3.3.3 Usability (NFR-007 to NFR-009)
**The system shall:**
- **NFR-007:** Be fully responsive on mobile/desktop.
- **NFR-008:** Provide intuitive search/filter UI.
- **NFR-009:** Display loading states and error messages clearly.

#### 3.3.4 Security (NFR-010 to NFR-013)
**The system shall:**
- **NFR-010:** Use HTTPS for all communications.
- **NFR-011:** Implement rate limiting (10 req/min per IP).
- **NFR-012:** Hash passwords with bcrypt.
- **NFR-013:** Prevent CSRF/XSS attacks.

#### 3.3.5 Maintainability (NFR-014 to NFR-015)
**The system shall:**
- **NFR-014:** Follow Django best practices for easy extension.
- **NFR-015:** Support manual database migration.

### 3.4 Other Requirements

#### 3.4.1 Database
Reference: [Database Design Documentation](https://github.com/Irshad-11/The-AI-AskBook/docs/)

#### 3.4.2 Installation
- Deployable on Render with PostgreSQL
- Environment variables for secrets


### 3.5 Use Case — Prompt Submission & Moderation Flow

#### 3.5.1 Use Case Description
This use case describes how a prompt (post) is submitted, reviewed, and published within the AI AskBook platform.  
The workflow varies based on the verification status of the submitting user and ensures content quality through admin moderation.

**Primary Actor:** Registered Member  
**Secondary Actor:** Admin  
**Precondition:** User is authenticated  
**Postcondition:** Prompt is either published to the public feed or returned to the user for revision


#### 3.5.2 Use Case Flow (Post Lifecycle)

```mermaid
flowchart TD
    A[User Submits Prompt] --> B{Is User Verified?}

    B -- Yes --> C[Prompt Auto-Approved]
    C --> D[Published to Live Feed]

    B -- No --> E[Prompt Set to Pending State]
    E --> F[Admin Reviews Prompt]

    F --> G{Admin Decision}

    G -- Approve --> H[Prompt Approved]
    H --> D

    G -- Reject --> I[Admin Adds Rejection Reason]
    I --> J[Prompt Marked as Rejected]
    J --> K[User Edits Prompt]
    K --> A
````


#### 3.5.3 Notes

* Verified users bypass manual moderation to reduce friction and encourage contribution.
* Unverified users follow a controlled review loop to ensure platform quality.
* Rejected prompts are not deleted; they remain editable, enabling iterative improvement.
* The cycle continues until the prompt meets approval criteria and is published.


