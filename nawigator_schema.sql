-- =====================================================================
-- Administrative Procedures Navigator in Poland (Nawigator)
-- Complete Database Schema for MySQL 8.0.16+
-- All entity, attribute, index, and constraint names in ENGLISH.
-- Generated for MySQL Workbench project: nawigator.mwb
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS nawigator
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE nawigator;

SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------
-- BLOCK 1: LOOKUP / DICTIONARIES
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS citizenship_groups;
CREATE TABLE citizenship_groups (
  id INT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(20) NOT NULL,
  name VARCHAR(80) NOT NULL,
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_citizenship_groups_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Citizenship categories: EU/EEA, non-EU, Ukraine, Polish roots';

DROP TABLE IF EXISTS countries;
CREATE TABLE countries (
  id SMALLINT UNSIGNED AUTO_INCREMENT,
  iso_code CHAR(3) NOT NULL,
  name VARCHAR(100) NOT NULL,
  citizenship_group_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_countries_iso_code UNIQUE (iso_code),
  CONSTRAINT uq_countries_name UNIQUE (name),
  CONSTRAINT fk_countries_citizenship_group FOREIGN KEY (citizenship_group_id) REFERENCES citizenship_groups (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Countries dictionary linked to citizenship group';

DROP TABLE IF EXISTS residence_bases;
CREATE TABLE residence_bases (
  id SMALLINT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(30) NOT NULL,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_residence_bases_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Legal basis for stay in Poland (visa, temporary residence permit)';

DROP TABLE IF EXISTS residence_purposes;
CREATE TABLE residence_purposes (
  id SMALLINT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(30) NOT NULL,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_residence_purposes_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Purpose of stay (work, studies, sole trader business, family)';

DROP TABLE IF EXISTS employment_types;
CREATE TABLE employment_types (
  id TINYINT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(30) NOT NULL,
  name VARCHAR(80) NOT NULL,
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_employment_types_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Types of employment contracts (employment, mandate, B2B JDG)';

-- ---------------------------------------------------------------------
-- BLOCK 2: PROCEDURES & INSTITUTIONS
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS institutions;
CREATE TABLE institutions (
  id SMALLINT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(30) NOT NULL,
  name VARCHAR(150) NOT NULL,
  type VARCHAR(50) NOT NULL,
  website_url VARCHAR(255) NULL,
  description TEXT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_institutions_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Public administration institutions (ZUS, NFZ, Voivodeship Office)';

DROP TABLE IF EXISTS institution_branches;
CREATE TABLE institution_branches (
  id INT UNSIGNED AUTO_INCREMENT,
  institution_id SMALLINT UNSIGNED NOT NULL,
  city VARCHAR(80) NOT NULL,
  address VARCHAR(150) NOT NULL,
  postal_code VARCHAR(10) NOT NULL,
  phone VARCHAR(30) NULL,
  email VARCHAR(100) NULL,
  opening_hours VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_institution_branches_institution FOREIGN KEY (institution_id) REFERENCES institutions (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Regional branches with addresses and working hours';

DROP TABLE IF EXISTS procedures;
CREATE TABLE procedures (
  id INT UNSIGNED AUTO_INCREMENT,
  institution_id SMALLINT UNSIGNED NOT NULL,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT NULL,
  processing_days SMALLINT UNSIGNED NULL,
  cost_pln DECIMAL(8,2) NOT NULL DEFAULT 0.00,
  submission_mode VARCHAR(100) NOT NULL,
  source_url VARCHAR(255) NOT NULL,
  verification_date DATE NOT NULL,
  verified_by VARCHAR(100) NOT NULL,
  review_interval_days SMALLINT UNSIGNED NOT NULL DEFAULT 90,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_procedures_code UNIQUE (code),
  CONSTRAINT fk_procedures_institution FOREIGN KEY (institution_id) REFERENCES institutions (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Catalog of administrative procedures in Poland';

DROP TABLE IF EXISTS procedure_steps;
CREATE TABLE procedure_steps (
  id INT UNSIGNED AUTO_INCREMENT,
  procedure_id INT UNSIGNED NOT NULL,
  step_number TINYINT UNSIGNED NOT NULL,
  name VARCHAR(150) NOT NULL,
  description TEXT NULL,
  is_optional BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id),
  CONSTRAINT uq_procedure_steps_order UNIQUE (procedure_id, step_number),
  CONSTRAINT fk_procedure_steps_procedure FOREIGN KEY (procedure_id) REFERENCES procedures (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Granular execution steps for a procedure';

DROP TABLE IF EXISTS procedure_dependencies;
CREATE TABLE procedure_dependencies (
  id INT UNSIGNED AUTO_INCREMENT,
  procedure_id INT UNSIGNED NOT NULL,
  required_procedure_id INT UNSIGNED NOT NULL,
  dependency_type VARCHAR(10) NOT NULL DEFAULT 'AND',
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_procedure_dependencies_pair UNIQUE (procedure_id, required_procedure_id),
  CONSTRAINT fk_procedure_dependencies_procedure FOREIGN KEY (procedure_id) REFERENCES procedures (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_procedure_dependencies_required FOREIGN KEY (required_procedure_id) REFERENCES procedures (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Directed acyclic graph (DAG) edges of procedure prerequisites';

DROP TABLE IF EXISTS availability_rules;
CREATE TABLE availability_rules (
  id INT UNSIGNED AUTO_INCREMENT,
  procedure_id INT UNSIGNED NOT NULL,
  citizenship_group_id INT UNSIGNED NULL,
  residence_basis_id SMALLINT UNSIGNED NULL,
  residence_purpose_id SMALLINT UNSIGNED NULL,
  is_available BOOLEAN NOT NULL DEFAULT TRUE,
  special_condition VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_availability_rules_procedure FOREIGN KEY (procedure_id) REFERENCES procedures (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_availability_rules_citizenship FOREIGN KEY (citizenship_group_id) REFERENCES citizenship_groups (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_availability_rules_residence_basis FOREIGN KEY (residence_basis_id) REFERENCES residence_bases (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_availability_rules_residence_purpose FOREIGN KEY (residence_purpose_id) REFERENCES residence_purposes (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Procedure accessibility matrix by citizenship and residency';

-- ---------------------------------------------------------------------
-- BLOCK 3: DOCUMENTS (HIERARCHY)
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS document_categories;
CREATE TABLE document_categories (
  id TINYINT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(20) NOT NULL,
  name VARCHAR(80) NOT NULL,
  status TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  CONSTRAINT uq_document_categories_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Level 1 hierarchy: broad document categories';

DROP TABLE IF EXISTS document_subcategories;
CREATE TABLE document_subcategories (
  id SMALLINT UNSIGNED AUTO_INCREMENT,
  category_id TINYINT UNSIGNED NOT NULL,
  code VARCHAR(20) NOT NULL,
  name VARCHAR(100) NOT NULL,
  status TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  CONSTRAINT uq_document_subcategories_code UNIQUE (code),
  CONSTRAINT fk_document_subcategories_category FOREIGN KEY (category_id) REFERENCES document_categories (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Level 2 hierarchy: document subcategories';

DROP TABLE IF EXISTS documents;
CREATE TABLE documents (
  id INT UNSIGNED AUTO_INCREMENT,
  subcategory_id SMALLINT UNSIGNED NOT NULL,
  code VARCHAR(30) NOT NULL,
  name VARCHAR(150) NOT NULL,
  has_expiry_date BOOLEAN NOT NULL DEFAULT FALSE,
  requires_sworn_translation BOOLEAN NOT NULL DEFAULT FALSE,
  description TEXT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_documents_code UNIQUE (code),
  CONSTRAINT fk_documents_subcategory FOREIGN KEY (subcategory_id) REFERENCES document_subcategories (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Level 3 hierarchy: specific official document types';

DROP TABLE IF EXISTS procedure_documents;
CREATE TABLE procedure_documents (
  id INT UNSIGNED AUTO_INCREMENT,
  procedure_id INT UNSIGNED NOT NULL,
  document_id INT UNSIGNED NOT NULL,
  is_required BOOLEAN NOT NULL DEFAULT TRUE,
  alternative_group VARCHAR(20) NULL,
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_procedure_documents_pair UNIQUE (procedure_id, document_id),
  CONSTRAINT fk_procedure_documents_procedure FOREIGN KEY (procedure_id) REFERENCES procedures (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_procedure_documents_document FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Prerequisite documents for procedures with AND/OR alternative groupings';

DROP TABLE IF EXISTS document_issuing_places;
CREATE TABLE document_issuing_places (
  id INT UNSIGNED AUTO_INCREMENT,
  document_id INT UNSIGNED NOT NULL,
  institution_id SMALLINT UNSIGNED NOT NULL,
  description VARCHAR(255) NULL,
  portal_url VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_document_issuing_places_document FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_document_issuing_places_institution FOREIGN KEY (institution_id) REFERENCES institutions (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Institutions and online portals where documents can be obtained';

-- ---------------------------------------------------------------------
-- BLOCK 4: LIFE SITUATIONS / SCENARIOS
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS life_situations;
CREATE TABLE life_situations (
  id SMALLINT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(150) NOT NULL,
  description TEXT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_life_situations_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Life situations (Student, Worker, Ukraine Protection, Business, Returning Citizen)';

DROP TABLE IF EXISTS situation_procedures;
CREATE TABLE situation_procedures (
  id INT UNSIGNED AUTO_INCREMENT,
  situation_id SMALLINT UNSIGNED NOT NULL,
  procedure_id INT UNSIGNED NOT NULL,
  default_order SMALLINT UNSIGNED NOT NULL,
  is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (id),
  CONSTRAINT uq_situation_procedures_pair UNIQUE (situation_id, procedure_id),
  CONSTRAINT fk_situation_procedures_situation FOREIGN KEY (situation_id) REFERENCES life_situations (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_situation_procedures_procedure FOREIGN KEY (procedure_id) REFERENCES procedures (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Procedures assigned to a life situation with ordering';

-- ---------------------------------------------------------------------
-- BLOCK 5: MULTILINGUAL CONTENT & GLOSSARY
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS languages;
CREATE TABLE languages (
  id TINYINT UNSIGNED AUTO_INCREMENT,
  code CHAR(2) NOT NULL,
  name VARCHAR(50) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id),
  CONSTRAINT uq_languages_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Supported system languages (en, pl, uk, ru)';

DROP TABLE IF EXISTS translations;
CREATE TABLE translations (
  id INT UNSIGNED AUTO_INCREMENT,
  language_id TINYINT UNSIGNED NOT NULL,
  table_name VARCHAR(50) NOT NULL,
  column_name VARCHAR(50) NOT NULL,
  record_id INT UNSIGNED NOT NULL,
  content TEXT NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_translations_lookup UNIQUE (language_id, table_name, column_name, record_id),
  CONSTRAINT fk_translations_language FOREIGN KEY (language_id) REFERENCES languages (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Polymorphic table storing entity text translations';

DROP TABLE IF EXISTS glossary_terms;
CREATE TABLE glossary_terms (
  id INT UNSIGNED AUTO_INCREMENT,
  term_pl VARCHAR(100) NOT NULL,
  definition_pl TEXT NOT NULL,
  category VARCHAR(50) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_glossary_terms_term UNIQUE (term_pl)
) ENGINE=InnoDB COMMENT='Glossary of official administrative terminology with explanations';

-- ---------------------------------------------------------------------
-- BLOCK 6: DATA FRESHNESS & AUDIT LOG
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS official_sources;
CREATE TABLE official_sources (
  id SMALLINT UNSIGNED AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  url VARCHAR(255) NOT NULL,
  type VARCHAR(50) NOT NULL,
  description VARCHAR(255) NULL,
  last_checked_at DATETIME NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_official_sources_url UNIQUE (url)
) ENGINE=InnoDB COMMENT='Official government portals, legislation registers, and bulletin URLs';

DROP TABLE IF EXISTS change_log;
CREATE TABLE change_log (
  id BIGINT UNSIGNED AUTO_INCREMENT,
  user_id INT UNSIGNED NULL,
  table_name VARCHAR(50) NOT NULL,
  record_id INT UNSIGNED NOT NULL,
  column_name VARCHAR(50) NOT NULL,
  old_value TEXT NULL,
  new_value TEXT NULL,
  changed_at DATETIME NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB COMMENT='Complete audit trail for changes to procedures and system rules';

-- ---------------------------------------------------------------------
-- BLOCK 7: USERS & RBAC
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
  id TINYINT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(30) NOT NULL,
  name VARCHAR(60) NOT NULL,
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_roles_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='System security roles: Guest, Client, Helper, Editor, Admin';

DROP TABLE IF EXISTS permissions;
CREATE TABLE permissions (
  id SMALLINT UNSIGNED AUTO_INCREMENT,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_permissions_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='Fine-grained system permissions for server-side verification';

DROP TABLE IF EXISTS role_permissions;
CREATE TABLE role_permissions (
  role_id TINYINT UNSIGNED NOT NULL,
  permission_id SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  CONSTRAINT fk_role_permissions_role FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_role_permissions_permission FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Mapping of roles to atomic permissions';

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INT UNSIGNED AUTO_INCREMENT,
  email VARCHAR(120) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  language_id TINYINT UNSIGNED NOT NULL DEFAULT 1,
  gdpr_consent BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL,
  last_login_at DATETIME NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_users_email UNIQUE (email),
  CONSTRAINT fk_users_language FOREIGN KEY (language_id) REFERENCES languages (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='User accounts with GDPR compliance';

-- Connect change_log to users
ALTER TABLE change_log
  ADD CONSTRAINT fk_change_log_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL ON UPDATE RESTRICT;

DROP TABLE IF EXISTS user_roles;
CREATE TABLE user_roles (
  user_id INT UNSIGNED NOT NULL,
  role_id TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (user_id, role_id),
  CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Role assignments to user accounts';

DROP TABLE IF EXISTS user_profiles;
CREATE TABLE user_profiles (
  id INT UNSIGNED AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  country_id SMALLINT UNSIGNED NOT NULL,
  residence_basis_id SMALLINT UNSIGNED NULL,
  residence_purpose_id SMALLINT UNSIGNED NULL,
  employment_type_id TINYINT UNSIGNED NULL,
  arrival_date DATE NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_user_profiles_user UNIQUE (user_id),
  CONSTRAINT fk_user_profiles_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_user_profiles_country FOREIGN KEY (country_id) REFERENCES countries (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_user_profiles_residence_basis FOREIGN KEY (residence_basis_id) REFERENCES residence_bases (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_user_profiles_residence_purpose FOREIGN KEY (residence_purpose_id) REFERENCES residence_purposes (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_user_profiles_employment_type FOREIGN KEY (employment_type_id) REFERENCES employment_types (id) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Client profile: citizenship mandatory, stay basis and purpose';

-- ---------------------------------------------------------------------
-- BLOCK 8: PROGRESS, HELPERS & EXTENSIONS
-- ---------------------------------------------------------------------

DROP TABLE IF EXISTS user_progress;
CREATE TABLE user_progress (
  id INT UNSIGNED AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  procedure_id INT UNSIGNED NOT NULL,
  step_id INT UNSIGNED NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'not_started',
  completed_at DATETIME NULL,
  completed_by VARCHAR(20) NOT NULL DEFAULT 'client',
  note TEXT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_user_progress_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_user_progress_procedure FOREIGN KEY (procedure_id) REFERENCES procedures (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_user_progress_step FOREIGN KEY (step_id) REFERENCES procedure_steps (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Progress tracking for client procedures and steps';

DROP TABLE IF EXISTS user_documents;
CREATE TABLE user_documents (
  id INT UNSIGNED AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  document_id INT UNSIGNED NOT NULL,
  is_possessed BOOLEAN NOT NULL DEFAULT TRUE,
  expiry_date DATE NULL,
  added_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_user_documents_pair UNIQUE (user_id, document_id),
  CONSTRAINT fk_user_documents_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_user_documents_document FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Checklist of documents possessed by user';

DROP TABLE IF EXISTS helpers;
CREATE TABLE helpers (
  id INT UNSIGNED AUTO_INCREMENT,
  helper_id INT UNSIGNED NOT NULL,
  client_id INT UNSIGNED NOT NULL,
  invitation_code VARCHAR(36) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'invited',
  invited_at DATETIME NOT NULL,
  accepted_at DATETIME NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_helpers_invitation_code UNIQUE (invitation_code),
  CONSTRAINT fk_helpers_helper FOREIGN KEY (helper_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_helpers_client FOREIGN KEY (client_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Helper assignments granting verified assistants access to ward plans';

DROP TABLE IF EXISTS helper_notes;
CREATE TABLE helper_notes (
  id INT UNSIGNED AUTO_INCREMENT,
  assignment_id INT UNSIGNED NOT NULL,
  step_id INT UNSIGNED NULL,
  content TEXT NOT NULL,
  created_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_helper_notes_assignment FOREIGN KEY (assignment_id) REFERENCES helpers (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_helper_notes_step FOREIGN KEY (step_id) REFERENCES procedure_steps (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Advisory notes and hints added by helpers to ward steps';

DROP TABLE IF EXISTS reminders;
CREATE TABLE reminders (
  id INT UNSIGNED AUTO_INCREMENT,
  user_id INT UNSIGNED NOT NULL,
  procedure_id INT UNSIGNED NULL,
  reminder_date DATE NOT NULL,
  content VARCHAR(255) NOT NULL,
  is_sent BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (id),
  CONSTRAINT fk_reminders_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_reminders_procedure FOREIGN KEY (procedure_id) REFERENCES procedures (id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB COMMENT='Deadline and document expiry reminders for users';

SET FOREIGN_KEY_CHECKS = 1;
