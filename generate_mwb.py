#!/usr/bin/env python3
"""
MySQL Workbench (.mwb) Project Generator
for administrative procedures navigation system in Poland.
All entity, attribute, index, and relationship names in ENGLISH.
"""

import os
import uuid
import zipfile
import sqlite3
import xml.etree.ElementTree as ET
from xml.dom import minidom

SCHEMA_NAME = "nawigator"

TYPE_MAP = {
    "TINYINT": "com.mysql.rdbms.mysql.datatype.tinyint",
    "SMALLINT": "com.mysql.rdbms.mysql.datatype.smallint",
    "INT": "com.mysql.rdbms.mysql.datatype.int",
    "BIGINT": "com.mysql.rdbms.mysql.datatype.bigint",
    "VARCHAR": "com.mysql.rdbms.mysql.datatype.varchar",
    "CHAR": "com.mysql.rdbms.mysql.datatype.char",
    "TEXT": "com.mysql.rdbms.mysql.datatype.text",
    "DECIMAL": "com.mysql.rdbms.mysql.datatype.decimal",
    "BOOLEAN": "com.mysql.rdbms.mysql.datatype.boolean",
    "DATE": "com.mysql.rdbms.mysql.datatype.date",
    "DATETIME": "com.mysql.rdbms.mysql.datatype.datetime",
}

BLOCK_COLORS = {
    "lookup": "#D4E6F1",       # Soft Blue
    "procedures": "#D5F5E3",   # Soft Mint Green
    "documents": "#FCF3CF",    # Soft Yellow
    "scenarios": "#E8DAEF",    # Soft Purple
    "i18n": "#FADBD8",         # Soft Pink
    "audit": "#EDBB99",        # Soft Peach / Orange
    "users": "#AED6F1",        # Sky Blue
    "extensions": "#D2B4DE",   # Lavender
}

def gen_id():
    return str(uuid.uuid4())

TABLES_DEF = [
    # BLOCK 1: LOOKUP / DICTIONARIES
    {
        "name": "citizenship_groups",
        "block": "lookup",
        "comment": "Citizenship categories: EU/EEA, non-EU, Ukraine (special act), Polish roots, returning citizen",
        "columns": [
            ("id", "INT", True, True, None, "PK of citizenship group", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 20, "Unique code: EU, NON_EU, UKRAINE, POLAND", []),
            ("name", "VARCHAR", False, False, 80, "Display name of citizenship group", []),
            ("description", "VARCHAR", False, False, 255, "Summary of legal rights and group rules", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_citizenship_groups_code", ["code"])],
        "fks": [],
    },
    {
        "name": "countries",
        "block": "lookup",
        "comment": "Countries dictionary linked to citizenship group",
        "columns": [
            ("id", "SMALLINT", True, True, None, "PK of country", ["UNSIGNED"]),
            ("iso_code", "CHAR", False, False, 3, "ISO 3166-1 alpha-3 code (e.g. POL, UKR, IND)", []),
            ("name", "VARCHAR", False, False, 100, "Full country name", []),
            ("citizenship_group_id", "INT", False, False, None, "FK to citizenship group", ["UNSIGNED"]),
        ],
        "pk": ["id"],
        "uniques": [
            ("uq_countries_iso_code", ["iso_code"]),
            ("uq_countries_name", ["name"]),
        ],
        "fks": [
            ("fk_countries_citizenship_group", ["citizenship_group_id"], "citizenship_groups", ["id"])
        ],
    },
    {
        "name": "residence_bases",
        "block": "lookup",
        "comment": "Legal basis for stay in Poland (visa, temporary residence permit, visa-free)",
        "columns": [
            ("id", "SMALLINT", True, True, None, "PK of residence basis", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 30, "Code: VISA_FREE, NATIONAL_VISA_D, TEMP_RESIDENCE", []),
            ("name", "VARCHAR", False, False, 100, "Residence basis name", []),
            ("description", "VARCHAR", False, False, 255, "Legal details and requirements", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_residence_bases_code", ["code"])],
        "fks": [],
    },
    {
        "name": "residence_purposes",
        "block": "lookup",
        "comment": "Purpose of stay (employment, university studies, business activity, family reunification)",
        "columns": [
            ("id", "SMALLINT", True, True, None, "PK of residence purpose", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 30, "Code: WORK, STUDIES, BUSINESS, FAMILY", []),
            ("name", "VARCHAR", False, False, 100, "Purpose name", []),
            ("description", "VARCHAR", False, False, 255, "Brief description", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_residence_purposes_code", ["code"])],
        "fks": [],
    },
    {
        "name": "employment_types",
        "block": "lookup",
        "comment": "Types of employment contracts (employment contract, mandate, B2B sole trader)",
        "columns": [
            ("id", "TINYINT", True, True, None, "PK of employment type", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 30, "Code: EMPLOYMENT_CONTRACT, MANDATE, B2B_JDG", []),
            ("name", "VARCHAR", False, False, 80, "Display name of contract type", []),
            ("description", "VARCHAR", False, False, 255, "Social security and tax implications", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_employment_types_code", ["code"])],
        "fks": [],
    },

    # BLOCK 2: PROCEDURES & INSTITUTIONS
    {
        "name": "institutions",
        "block": "procedures",
        "comment": "Public administration offices and institutions (ZUS, NFZ, Voivodeship Office)",
        "columns": [
            ("id", "SMALLINT", True, True, None, "PK of institution", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 30, "Code: UW, ZUS, NFZ, UDSC, PUP, CEIDG, US, UM", []),
            ("name", "VARCHAR", False, False, 150, "Full name of the institution", []),
            ("type", "VARCHAR", False, False, 50, "Governmental, Regional, Social Insurance, Healthcare", []),
            ("website_url", "VARCHAR", False, False, 255, "Official portal URL", []),
            ("description", "TEXT", False, False, None, "Scope of authority and services", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_institutions_code", ["code"])],
        "fks": [],
    },
    {
        "name": "institution_branches",
        "block": "procedures",
        "comment": "Regional branches of institutions with addresses and working hours",
        "columns": [
            ("id", "INT", True, True, None, "PK of branch", ["UNSIGNED"]),
            ("institution_id", "SMALLINT", False, False, None, "Parent institution", ["UNSIGNED"]),
            ("city", "VARCHAR", False, False, 80, "City location", []),
            ("address", "VARCHAR", False, False, 150, "Street address and unit", []),
            ("postal_code", "VARCHAR", False, False, 10, "Postal code (e.g. 00-001)", []),
            ("phone", "VARCHAR", False, False, 30, "Contact telephone / helpline", []),
            ("email", "VARCHAR", False, False, 100, "Official email address", []),
            ("opening_hours", "VARCHAR", False, False, 255, "Customer service working hours", []),
        ],
        "pk": ["id"],
        "uniques": [],
        "fks": [
            ("fk_institution_branches_institution", ["institution_id"], "institutions", ["id"])
        ],
    },
    {
        "name": "procedures",
        "block": "procedures",
        "comment": "Catalog of administrative procedures in Poland",
        "columns": [
            ("id", "INT", True, True, None, "PK of procedure", ["UNSIGNED"]),
            ("institution_id", "SMALLINT", False, False, None, "Competent institution", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 50, "Unique procedure code", []),
            ("name", "VARCHAR", False, False, 200, "Official name of the procedure", []),
            ("description", "TEXT", False, False, None, "Plain-language summary of the procedure", []),
            ("processing_days", "SMALLINT", False, False, None, "Statutory processing timeframe in days", ["UNSIGNED"]),
            ("cost_pln", "DECIMAL", False, False, None, "Official administrative fee in PLN", []),
            ("submission_mode", "VARCHAR", False, False, 100, "InPerson, Online, Postal, Hybrid", []),
            ("source_url", "VARCHAR", False, False, 255, "Link to official gov.pl source", []),
            ("verification_date", "DATE", False, False, None, "Date of last content verification", []),
            ("verified_by", "VARCHAR", False, False, 100, "Editor who verified the data", []),
            ("review_interval_days", "SMALLINT", False, False, None, "Review interval (default 90 days)", ["UNSIGNED"]),
            ("status", "VARCHAR", False, False, 20, "Status: active, needs_review, obsolete", []),
            ("created_at", "DATETIME", False, False, None, "Creation timestamp", []),
            ("updated_at", "DATETIME", False, False, None, "Last update timestamp", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_procedures_code", ["code"])],
        "fks": [
            ("fk_procedures_institution", ["institution_id"], "institutions", ["id"])
        ],
    },
    {
        "name": "procedure_steps",
        "block": "procedures",
        "comment": "Granular execution steps for a single procedure",
        "columns": [
            ("id", "INT", True, True, None, "PK of procedure step", ["UNSIGNED"]),
            ("procedure_id", "INT", False, False, None, "Parent procedure", ["UNSIGNED"]),
            ("step_number", "TINYINT", False, False, None, "Sequential order within procedure", ["UNSIGNED"]),
            ("name", "VARCHAR", False, False, 150, "Title of the step", []),
            ("description", "TEXT", False, False, None, "Actionable instructions for the step", []),
            ("is_optional", "BOOLEAN", False, False, None, "Whether this step is optional", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_procedure_steps_order", ["procedure_id", "step_number"])],
        "fks": [
            ("fk_procedure_steps_procedure", ["procedure_id"], "procedures", ["id"])
        ],
    },
    {
        "name": "procedure_dependencies",
        "block": "procedures",
        "comment": "Directed acyclic graph (DAG) edges representing procedure prerequisites",
        "columns": [
            ("id", "INT", True, True, None, "PK of dependency edge", ["UNSIGNED"]),
            ("procedure_id", "INT", False, False, None, "Dependent procedure (blocked until fulfilled)", ["UNSIGNED"]),
            ("required_procedure_id", "INT", False, False, None, "Preceding procedure required first", ["UNSIGNED"]),
            ("dependency_type", "VARCHAR", False, False, 10, "Logical operator: AND / OR", []),
            ("description", "VARCHAR", False, False, 255, "Legal reasoning for the prerequisite", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_procedure_dependencies_pair", ["procedure_id", "required_procedure_id"])],
        "fks": [
            ("fk_procedure_dependencies_procedure", ["procedure_id"], "procedures", ["id"]),
            ("fk_procedure_dependencies_required", ["required_procedure_id"], "procedures", ["id"]),
        ],
    },
    {
        "name": "availability_rules",
        "block": "procedures",
        "comment": "Procedure accessibility rules based on citizenship and residence status",
        "columns": [
            ("id", "INT", True, True, None, "PK of availability rule", ["UNSIGNED"]),
            ("procedure_id", "INT", False, False, None, "Target procedure", ["UNSIGNED"]),
            ("citizenship_group_id", "INT", False, False, None, "Target citizenship group (NULL=all)", ["UNSIGNED"]),
            ("residence_basis_id", "SMALLINT", False, False, None, "Target residence basis (NULL=all)", ["UNSIGNED"]),
            ("residence_purpose_id", "SMALLINT", False, False, None, "Target residence purpose (NULL=all)", ["UNSIGNED"]),
            ("is_available", "BOOLEAN", False, False, None, "Whether procedure is applicable for this profile", []),
            ("special_condition", "VARCHAR", False, False, 255, "Special statutory provision notes", []),
        ],
        "pk": ["id"],
        "uniques": [],
        "fks": [
            ("fk_availability_rules_procedure", ["procedure_id"], "procedures", ["id"]),
            ("fk_availability_rules_citizenship", ["citizenship_group_id"], "citizenship_groups", ["id"]),
            ("fk_availability_rules_residence_basis", ["residence_basis_id"], "residence_bases", ["id"]),
            ("fk_availability_rules_residence_purpose", ["residence_purpose_id"], "residence_purposes", ["id"]),
        ],
    },

    # BLOCK 3: DOCUMENTS (HIERARCHY)
    {
        "name": "document_categories",
        "block": "documents",
        "comment": "Level 1 hierarchy: broad document categories (Identity, Civil Status, Financial)",
        "columns": [
            ("id", "TINYINT", True, True, None, "PK of category", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 20, "Category code (e.g. ID, RESIDENCE, TAX)", []),
            ("name", "VARCHAR", False, False, 80, "Category name", []),
            ("status", "TINYINT", False, False, None, "1=active, 0=retired", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_document_categories_code", ["code"])],
        "fks": [],
    },
    {
        "name": "document_subcategories",
        "block": "documents",
        "comment": "Level 2 hierarchy: subcategories (Passports, Visas, Declarations)",
        "columns": [
            ("id", "SMALLINT", True, True, None, "PK of subcategory", ["UNSIGNED"]),
            ("category_id", "TINYINT", False, False, None, "Parent category", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 20, "Subcategory code", []),
            ("name", "VARCHAR", False, False, 100, "Subcategory name", []),
            ("status", "TINYINT", False, False, None, "1=active, 0=retired", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_document_subcategories_code", ["code"])],
        "fks": [
            ("fk_document_subcategories_category", ["category_id"], "document_categories", ["id"])
        ],
    },
    {
        "name": "documents",
        "block": "documents",
        "comment": "Level 3 hierarchy: specific document types (National Visa D, Lease Agreement)",
        "columns": [
            ("id", "INT", True, True, None, "PK of document", ["UNSIGNED"]),
            ("subcategory_id", "SMALLINT", False, False, None, "Parent subcategory", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 30, "Document code", []),
            ("name", "VARCHAR", False, False, 150, "Official document name", []),
            ("has_expiry_date", "BOOLEAN", False, False, None, "Whether document has an expiration date", []),
            ("requires_sworn_translation", "BOOLEAN", False, False, None, "Whether foreign document requires sworn translation", []),
            ("description", "TEXT", False, False, None, "Guidelines on how to obtain or verify", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_documents_code", ["code"])],
        "fks": [
            ("fk_documents_subcategory", ["subcategory_id"], "document_subcategories", ["id"])
        ],
    },
    {
        "name": "procedure_documents",
        "block": "documents",
        "comment": "Prerequisite documents for procedures with AND/OR alternative groupings",
        "columns": [
            ("id", "INT", True, True, None, "PK of requirement", ["UNSIGNED"]),
            ("procedure_id", "INT", False, False, None, "Associated procedure", ["UNSIGNED"]),
            ("document_id", "INT", False, False, None, "Required document", ["UNSIGNED"]),
            ("is_required", "BOOLEAN", False, False, None, "Strictly mandatory", []),
            ("alternative_group", "VARCHAR", False, False, 20, "Group for OR conditions (e.g. OR_GRP_1)", []),
            ("description", "VARCHAR", False, False, 255, "Notes (original vs certified copy)", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_procedure_documents_pair", ["procedure_id", "document_id"])],
        "fks": [
            ("fk_procedure_documents_procedure", ["procedure_id"], "procedures", ["id"]),
            ("fk_procedure_documents_document", ["document_id"], "documents", ["id"]),
        ],
    },
    {
        "name": "document_issuing_places",
        "block": "documents",
        "comment": "Public bodies or portals where each document can be issued or requested",
        "columns": [
            ("id", "INT", True, True, None, "PK of issuing place", ["UNSIGNED"]),
            ("document_id", "INT", False, False, None, "Target document", ["UNSIGNED"]),
            ("institution_id", "SMALLINT", False, False, None, "Issuing institution", ["UNSIGNED"]),
            ("description", "VARCHAR", False, False, 255, "Application method details", []),
            ("portal_url", "VARCHAR", False, False, 255, "Direct portal application link", []),
        ],
        "pk": ["id"],
        "uniques": [],
        "fks": [
            ("fk_document_issuing_places_document", ["document_id"], "documents", ["id"]),
            ("fk_document_issuing_places_institution", ["institution_id"], "institutions", ["id"]),
        ],
    },

    # BLOCK 4: LIFE SITUATIONS / SCENARIOS
    {
        "name": "life_situations",
        "block": "scenarios",
        "comment": "Life situations (Student, Worker, Ukraine Protection, EU Business, Returning Citizen)",
        "columns": [
            ("id", "SMALLINT", True, True, None, "PK of situation", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 50, "Situation code: NON_EU_STUDENT, NON_EU_WORKER, etc.", []),
            ("name", "VARCHAR", False, False, 150, "Title of life situation", []),
            ("description", "TEXT", False, False, None, "Scenario overview and target personas", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_life_situations_code", ["code"])],
        "fks": [],
    },
    {
        "name": "situation_procedures",
        "block": "scenarios",
        "comment": "Procedures assigned to a life situation with default suggested order",
        "columns": [
            ("id", "INT", True, True, None, "PK of mapping", ["UNSIGNED"]),
            ("situation_id", "SMALLINT", False, False, None, "Associated situation", ["UNSIGNED"]),
            ("procedure_id", "INT", False, False, None, "Assigned procedure", ["UNSIGNED"]),
            ("default_order", "SMALLINT", False, False, None, "Default sequential position", ["UNSIGNED"]),
            ("is_mandatory", "BOOLEAN", False, False, None, "Whether mandatory for this situation", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_situation_procedures_pair", ["situation_id", "procedure_id"])],
        "fks": [
            ("fk_situation_procedures_situation", ["situation_id"], "life_situations", ["id"]),
            ("fk_situation_procedures_procedure", ["procedure_id"], "procedures", ["id"]),
        ],
    },

    # BLOCK 5: MULTILINGUAL CONTENT & GLOSSARY
    {
        "name": "languages",
        "block": "i18n",
        "comment": "Supported system languages (en, pl, uk, ru)",
        "columns": [
            ("id", "TINYINT", True, True, None, "PK of language", ["UNSIGNED"]),
            ("code", "CHAR", False, False, 2, "ISO 639-1 code (en, pl, uk, ru)", []),
            ("name", "VARCHAR", False, False, 50, "Native name of the language", []),
            ("is_active", "BOOLEAN", False, False, None, "Whether language is enabled", []),
            ("is_default", "BOOLEAN", False, False, None, "Default / fallback language flag", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_languages_code", ["code"])],
        "fks": [],
    },
    {
        "name": "translations",
        "block": "i18n",
        "comment": "Polymorphic table storing entity text translations",
        "columns": [
            ("id", "INT", True, True, None, "PK of translation", ["UNSIGNED"]),
            ("language_id", "TINYINT", False, False, None, "Target language", ["UNSIGNED"]),
            ("table_name", "VARCHAR", False, False, 50, "Source table name", []),
            ("column_name", "VARCHAR", False, False, 50, "Source column name", []),
            ("record_id", "INT", False, False, None, "ID of the translated record", ["UNSIGNED"]),
            ("content", "TEXT", False, False, None, "Translated localized text", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_translations_lookup", ["language_id", "table_name", "column_name", "record_id"])],
        "fks": [
            ("fk_translations_language", ["language_id"], "languages", ["id"])
        ],
    },
    {
        "name": "glossary_terms",
        "block": "i18n",
        "comment": "Glossary of official administrative terminology with explanations",
        "columns": [
            ("id", "INT", True, True, None, "PK of term", ["UNSIGNED"]),
            ("term_pl", "VARCHAR", False, False, 100, "Official Polish term (e.g. PESEL, Meladunek)", []),
            ("definition_pl", "TEXT", False, False, None, "Clear definition and explanation", []),
            ("category", "VARCHAR", False, False, 50, "Category: Civil, Residency, Taxes, Healthcare", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_glossary_terms_term", ["term_pl"])],
        "fks": [],
    },

    # BLOCK 6: DATA FRESHNESS & AUDIT LOG
    {
        "name": "official_sources",
        "block": "audit",
        "comment": "Official government portals, legislation registers, and bulletin URLs",
        "columns": [
            ("id", "SMALLINT", True, True, None, "PK of source", ["UNSIGNED"]),
            ("name", "VARCHAR", False, False, 120, "Official source title", []),
            ("url", "VARCHAR", False, False, 255, "Canonical source URL", []),
            ("type", "VARCHAR", False, False, 50, "GovernmentPortal, Ministry, LegalAct, CityHall", []),
            ("description", "VARCHAR", False, False, 255, "Monitored topics and regulatory scope", []),
            ("last_checked_at", "DATETIME", False, False, None, "Last automated / manual check timestamp", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_official_sources_url", ["url"])],
        "fks": [],
    },
    {
        "name": "change_log",
        "block": "audit",
        "comment": "Complete audit trail for changes to procedures and system rules",
        "columns": [
            ("id", "BIGINT", True, True, None, "PK of audit entry", ["UNSIGNED"]),
            ("user_id", "INT", False, False, None, "User who performed the change (or NULL for system)", ["UNSIGNED"]),
            ("table_name", "VARCHAR", False, False, 50, "Target table", []),
            ("record_id", "INT", False, False, None, "Target record ID", ["UNSIGNED"]),
            ("column_name", "VARCHAR", False, False, 50, "Modified column name", []),
            ("old_value", "TEXT", False, False, None, "Previous value", []),
            ("new_value", "TEXT", False, False, None, "Updated value", []),
            ("changed_at", "DATETIME", False, False, None, "Timestamp of change", []),
        ],
        "pk": ["id"],
        "uniques": [],
        "fks": [
            ("fk_change_log_user", ["user_id"], "users", ["id"])
        ],
    },

    # BLOCK 7: USERS & RBAC
    {
        "name": "roles",
        "block": "users",
        "comment": "System security roles: Guest, Client, Helper, ContentEditor, Administrator",
        "columns": [
            ("id", "TINYINT", True, True, None, "PK of role", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 30, "Role code: CLIENT, HELPER, EDITOR, ADMIN", []),
            ("name", "VARCHAR", False, False, 60, "Display name", []),
            ("description", "VARCHAR", False, False, 255, "Role permissions overview", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_roles_code", ["code"])],
        "fks": [],
    },
    {
        "name": "permissions",
        "block": "users",
        "comment": "Fine-grained system permissions for server-side verification",
        "columns": [
            ("id", "SMALLINT", True, True, None, "PK of permission", ["UNSIGNED"]),
            ("code", "VARCHAR", False, False, 50, "Permission code (e.g. PROCEDURE_CREATE, AUDIT_VIEW)", []),
            ("name", "VARCHAR", False, False, 100, "Permission title", []),
            ("description", "VARCHAR", False, False, 255, "Authorized operation details", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_permissions_code", ["code"])],
        "fks": [],
    },
    {
        "name": "role_permissions",
        "block": "users",
        "comment": "Mapping of roles to atomic permissions",
        "columns": [
            ("role_id", "TINYINT", False, False, None, "Role", ["UNSIGNED"]),
            ("permission_id", "SMALLINT", False, False, None, "Permission", ["UNSIGNED"]),
        ],
        "pk": ["role_id", "permission_id"],
        "uniques": [],
        "fks": [
            ("fk_role_permissions_role", ["role_id"], "roles", ["id"]),
            ("fk_role_permissions_permission", ["permission_id"], "permissions", ["id"]),
        ],
    },
    {
        "name": "users",
        "block": "users",
        "comment": "User accounts with GDPR compliance (no document scans or sensitive national IDs stored)",
        "columns": [
            ("id", "INT", True, True, None, "PK of user", ["UNSIGNED"]),
            ("email", "VARCHAR", False, False, 120, "User email (login)", []),
            ("password_hash", "VARCHAR", False, False, 255, "Argon2id password hash", []),
            ("language_id", "TINYINT", False, False, None, "Preferred UI language", ["UNSIGNED"]),
            ("gdpr_consent", "BOOLEAN", False, False, None, "Consent for data processing", []),
            ("is_active", "BOOLEAN", False, False, None, "Account active flag", []),
            ("created_at", "DATETIME", False, False, None, "Registration timestamp", []),
            ("last_login_at", "DATETIME", False, False, None, "Last login timestamp", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_users_email", ["email"])],
        "fks": [
            ("fk_users_language", ["language_id"], "languages", ["id"])
        ],
    },
    {
        "name": "user_roles",
        "block": "users",
        "comment": "Role assignments to user accounts",
        "columns": [
            ("user_id", "INT", False, False, None, "User", ["UNSIGNED"]),
            ("role_id", "TINYINT", False, False, None, "Assigned role", ["UNSIGNED"]),
        ],
        "pk": ["user_id", "role_id"],
        "uniques": [],
        "fks": [
            ("fk_user_roles_user", ["user_id"], "users", ["id"]),
            ("fk_user_roles_role", ["role_id"], "roles", ["id"]),
        ],
    },
    {
        "name": "user_profiles",
        "block": "users",
        "comment": "Client profile: citizenship mandatory, stay basis and purpose",
        "columns": [
            ("id", "INT", True, True, None, "PK of profile", ["UNSIGNED"]),
            ("user_id", "INT", False, False, None, "Associated user (1:1 relation)", ["UNSIGNED"]),
            ("country_id", "SMALLINT", False, False, None, "Nationality / citizenship country (MANDATORY)", ["UNSIGNED"]),
            ("residence_basis_id", "SMALLINT", False, False, None, "Current legal stay basis", ["UNSIGNED"]),
            ("residence_purpose_id", "SMALLINT", False, False, None, "Main stay purpose", ["UNSIGNED"]),
            ("employment_type_id", "TINYINT", False, False, None, "Type of employment in Poland", ["UNSIGNED"]),
            ("arrival_date", "DATE", False, False, None, "Date of entry into Poland for calculating deadlines", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_user_profiles_user", ["user_id"])],
        "fks": [
            ("fk_user_profiles_user", ["user_id"], "users", ["id"]),
            ("fk_user_profiles_country", ["country_id"], "countries", ["id"]),
            ("fk_user_profiles_residence_basis", ["residence_basis_id"], "residence_bases", ["id"]),
            ("fk_user_profiles_residence_purpose", ["residence_purpose_id"], "residence_purposes", ["id"]),
            ("fk_user_profiles_employment_type", ["employment_type_id"], "employment_types", ["id"]),
        ],
    },

    # BLOCK 8: PROGRESS, HELPERS & EXTENSIONS
    {
        "name": "user_progress",
        "block": "extensions",
        "comment": "Progress tracking for client procedures and steps",
        "columns": [
            ("id", "INT", True, True, None, "PK of progress item", ["UNSIGNED"]),
            ("user_id", "INT", False, False, None, "Client following the plan", ["UNSIGNED"]),
            ("procedure_id", "INT", False, False, None, "Procedure in the plan", ["UNSIGNED"]),
            ("step_id", "INT", False, False, None, "Specific step (or NULL for procedure-level)", ["UNSIGNED"]),
            ("status", "VARCHAR", False, False, 20, "Status: not_started, in_progress, completed", []),
            ("completed_at", "DATETIME", False, False, None, "Completion timestamp", []),
            ("completed_by", "VARCHAR", False, False, 20, "Who marked completion: client / helper", []),
            ("note", "TEXT", False, False, None, "Client's personal note", []),
        ],
        "pk": ["id"],
        "uniques": [],
        "fks": [
            ("fk_user_progress_user", ["user_id"], "users", ["id"]),
            ("fk_user_progress_procedure", ["procedure_id"], "procedures", ["id"]),
            ("fk_user_progress_step", ["step_id"], "procedure_steps", ["id"]),
        ],
    },
    {
        "name": "user_documents",
        "block": "extensions",
        "comment": "Checklist of documents possessed by user (no scans or numbers stored)",
        "columns": [
            ("id", "INT", True, True, None, "PK of document possession", ["UNSIGNED"]),
            ("user_id", "INT", False, False, None, "Client owner", ["UNSIGNED"]),
            ("document_id", "INT", False, False, None, "Document type", ["UNSIGNED"]),
            ("is_possessed", "BOOLEAN", False, False, None, "Whether client has this document in hand", []),
            ("expiry_date", "DATE", False, False, None, "Expiration date (for warning notifications)", []),
            ("added_at", "DATETIME", False, False, None, "Date marked in profile", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_user_documents_pair", ["user_id", "document_id"])],
        "fks": [
            ("fk_user_documents_user", ["user_id"], "users", ["id"]),
            ("fk_user_documents_document", ["document_id"], "documents", ["id"]),
        ],
    },
    {
        "name": "helpers",
        "block": "extensions",
        "comment": "Helper assignments granting verified assistants access to ward plans",
        "columns": [
            ("id", "INT", True, True, None, "PK of helper relationship", ["UNSIGNED"]),
            ("helper_id", "INT", False, False, None, "Helper user account", ["UNSIGNED"]),
            ("client_id", "INT", False, False, None, "Ward client user account", ["UNSIGNED"]),
            ("invitation_code", "VARCHAR", False, False, 36, "Single-use invitation token", []),
            ("status", "VARCHAR", False, False, 20, "Status: invited, active, revoked", []),
            ("invited_at", "DATETIME", False, False, None, "Invitation timestamp", []),
            ("accepted_at", "DATETIME", False, False, None, "Acceptance timestamp", []),
        ],
        "pk": ["id"],
        "uniques": [("uq_helpers_invitation_code", ["invitation_code"])],
        "fks": [
            ("fk_helpers_helper", ["helper_id"], "users", ["id"]),
            ("fk_helpers_client", ["client_id"], "users", ["id"]),
        ],
    },
    {
        "name": "helper_notes",
        "block": "extensions",
        "comment": "Advisory notes and hints added by helpers to ward steps",
        "columns": [
            ("id", "INT", True, True, None, "PK of helper note", ["UNSIGNED"]),
            ("assignment_id", "INT", False, False, None, "Helper assignment relationship", ["UNSIGNED"]),
            ("step_id", "INT", False, False, None, "Specific procedure step", ["UNSIGNED"]),
            ("content", "TEXT", False, False, None, "Helper guidance note content", []),
            ("created_at", "DATETIME", False, False, None, "Creation timestamp", []),
        ],
        "pk": ["id"],
        "uniques": [],
        "fks": [
            ("fk_helper_notes_assignment", ["assignment_id"], "helpers", ["id"]),
            ("fk_helper_notes_step", ["step_id"], "procedure_steps", ["id"]),
        ],
    },
    {
        "name": "reminders",
        "block": "extensions",
        "comment": "Deadline and document expiry reminders for users",
        "columns": [
            ("id", "INT", True, True, None, "PK of reminder", ["UNSIGNED"]),
            ("user_id", "INT", False, False, None, "Recipient user", ["UNSIGNED"]),
            ("procedure_id", "INT", False, False, None, "Associated procedure (or NULL)", ["UNSIGNED"]),
            ("reminder_date", "DATE", False, False, None, "Target reminder date", []),
            ("content", "VARCHAR", False, False, 255, "Reminder message text", []),
            ("is_sent", "BOOLEAN", False, False, None, "Whether notification has been delivered", []),
        ],
        "pk": ["id"],
        "uniques": [],
        "fks": [
            ("fk_reminders_user", ["user_id"], "users", ["id"]),
            ("fk_reminders_procedure", ["procedure_id"], "procedures", ["id"]),
        ],
    },
]

def build_mwb_xml():
    doc_id = gen_id()
    log_model_id = gen_id()
    phys_model_id = gen_id()
    catalog_id = gen_id()
    schema_id = gen_id()
    diagram_id = gen_id()
    root_layer_id = gen_id()

    table_id_map = {}
    col_id_map = {}
    table_pk_index_map = {}
    table_fig_map = {}
    fk_obj_map = {}

    for tdef in TABLES_DEF:
        tname = tdef["name"]
        t_id = gen_id()
        table_id_map[tname] = t_id
        table_fig_map[tname] = gen_id()
        for col in tdef["columns"]:
            cname = col[0]
            col_id_map[(tname, cname)] = gen_id()

    root = ET.Element("data", {
        "grt_format": "2.0",
        "document_type": "MySQL Workbench Model",
        "version": "1.4.4"
    })

    doc = ET.SubElement(root, "value", {
        "type": "object",
        "struct-name": "workbench.Document",
        "id": doc_id,
        "struct-checksum": "0x7131bf99"
    })

    log_model = ET.SubElement(doc, "value", {
        "type": "object",
        "struct-name": "workbench.logical.Model",
        "id": log_model_id,
        "struct-checksum": "0xf4220370",
        "key": "logicalModel"
    })
    ET.SubElement(log_model, "value", {"_ptr_": "0x1000", "type": "list", "content-type": "object", "content-struct-name": "workbench.logical.Diagram", "key": "diagrams"})
    ET.SubElement(log_model, "value", {"_ptr_": "0x1001", "type": "dict", "key": "customData"})
    ET.SubElement(log_model, "value", {"_ptr_": "0x1002", "type": "list", "content-type": "object", "content-struct-name": "model.Marker", "key": "markers"})
    ET.SubElement(log_model, "value", {"_ptr_": "0x1003", "type": "dict", "key": "options"})
    ET.SubElement(log_model, "value", {"type": "string", "key": "name"})
    owner_log = ET.SubElement(log_model, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"})
    owner_log.text = doc_id

    ET.SubElement(doc, "value", {"_ptr_": "0x1004", "type": "list", "content-type": "object", "content-struct-name": "workbench.OverviewPanel", "key": "overviewPanels"})

    phys_models = ET.SubElement(doc, "value", {
        "_ptr_": "0x1005",
        "type": "list",
        "content-type": "object",
        "content-struct-name": "workbench.physical.Model",
        "key": "physicalModels"
    })

    phys_model = ET.SubElement(phys_models, "value", {
        "type": "object",
        "struct-name": "workbench.physical.Model",
        "id": phys_model_id,
        "struct-checksum": "0x5f896d18"
    })

    catalog = ET.SubElement(phys_model, "value", {
        "type": "object",
        "struct-name": "db.mysql.Catalog",
        "id": catalog_id,
        "struct-checksum": "0x82ad3466",
        "key": "catalog"
    })
    ET.SubElement(catalog, "value", {"_ptr_": "0x1006", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.LogFileGroup", "key": "logFileGroups"})

    schemata = ET.SubElement(catalog, "value", {
        "_ptr_": "0x1007",
        "type": "list",
        "content-type": "object",
        "content-struct-name": "db.mysql.Schema",
        "key": "schemata"
    })

    schema = ET.SubElement(schemata, "value", {
        "type": "object",
        "struct-name": "db.mysql.Schema",
        "id": schema_id,
        "struct-checksum": "0x20b94c22"
    })
    ET.SubElement(schema, "value", {"_ptr_": "0x1008", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.RoutineGroup", "key": "routineGroups"})
    ET.SubElement(schema, "value", {"_ptr_": "0x1009", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.Routine", "key": "routines"})
    ET.SubElement(schema, "value", {"_ptr_": "0x100A", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.Sequence", "key": "sequences"})
    ET.SubElement(schema, "value", {"_ptr_": "0x100B", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.StructuredDatatype", "key": "structuredTypes"})
    ET.SubElement(schema, "value", {"_ptr_": "0x100C", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.Synonym", "key": "synonyms"})

    tables_list = ET.SubElement(schema, "value", {
        "_ptr_": "0x100D",
        "type": "list",
        "content-type": "object",
        "content-struct-name": "db.mysql.Table",
        "key": "tables"
    })

    all_connections = []

    for tdef in TABLES_DEF:
        tname = tdef["name"]
        t_id = table_id_map[tname]
        t_elem = ET.SubElement(tables_list, "value", {
            "type": "object",
            "struct-name": "db.mysql.Table",
            "id": t_id,
            "struct-checksum": "0x4564421a"
        })
        ET.SubElement(t_elem, "value", {"type": "string", "key": "avgRowLength"})
        c_sum = ET.SubElement(t_elem, "value", {"type": "int", "key": "checksum"})
        c_sum.text = "0"

        # Columns
        cols_elem = ET.SubElement(t_elem, "value", {
            "_ptr_": f"0xcols_{t_id[:8]}",
            "type": "list",
            "content-type": "object",
            "content-struct-name": "db.mysql.Column",
            "key": "columns"
        })

        for col_def in tdef["columns"]:
            cname, ctype, is_pk, is_ai, length, comment, flags = col_def
            cid = col_id_map[(tname, cname)]
            c_elem = ET.SubElement(cols_elem, "value", {
                "type": "object",
                "struct-name": "db.mysql.Column",
                "id": cid,
                "struct-checksum": "0xba88e21c"
            })
            ai_el = ET.SubElement(c_elem, "value", {"type": "int", "key": "autoIncrement"})
            ai_el.text = "1" if is_ai else "0"
            ET.SubElement(c_elem, "value", {"type": "string", "key": "expression"})
            gen_el = ET.SubElement(c_elem, "value", {"type": "int", "key": "generated"})
            gen_el.text = "0"
            ET.SubElement(c_elem, "value", {"type": "string", "key": "generatedStorage"})
            ET.SubElement(c_elem, "value", {"type": "string", "key": "characterSetName"})
            ET.SubElement(c_elem, "value", {"_ptr_": f"0xchk_{cid[:8]}", "type": "list", "content-type": "object", "content-struct-name": "db.CheckConstraint", "key": "checks"})
            ET.SubElement(c_elem, "value", {"type": "string", "key": "collationName"})
            ET.SubElement(c_elem, "value", {"type": "string", "key": "datatypeExplicitParams"})
            ET.SubElement(c_elem, "value", {"type": "string", "key": "defaultValue"})
            dnull_el = ET.SubElement(c_elem, "value", {"type": "int", "key": "defaultValueIsNull"})
            dnull_el.text = "0"

            flags_el = ET.SubElement(c_elem, "value", {
                "_ptr_": f"0xflg_{cid[:8]}",
                "type": "list",
                "content-type": "string",
                "key": "flags"
            })
            for fl in flags:
                fel = ET.SubElement(flags_el, "value", {"type": "string"})
                fel.text = fl

            not_null_el = ET.SubElement(c_elem, "value", {"type": "int", "key": "isNotNull"})
            not_null_el.text = "1" if is_pk or cname in ["code", "name", "email", "password_hash", "status", "verification_date", "changed_at", "term_pl", "definition_pl", "url", "table_name", "column_name", "content"] else "0"

            len_el = ET.SubElement(c_elem, "value", {"type": "int", "key": "length"})
            len_el.text = str(length) if length else "-1"

            prec_el = ET.SubElement(c_elem, "value", {"type": "int", "key": "precision"})
            prec_el.text = "8" if ctype == "DECIMAL" else "-1"
            scale_el = ET.SubElement(c_elem, "value", {"type": "int", "key": "scale"})
            scale_el.text = "2" if ctype == "DECIMAL" else "-1"

            st_link = ET.SubElement(c_elem, "link", {"type": "object", "struct-name": "db.SimpleDatatype", "key": "simpleType"})
            st_link.text = TYPE_MAP.get(ctype, "com.mysql.rdbms.mysql.datatype.varchar")

            c_comment = ET.SubElement(c_elem, "value", {"type": "string", "key": "comment"})
            c_comment.text = comment

            c_name = ET.SubElement(c_elem, "value", {"type": "string", "key": "name"})
            c_name.text = cname
            c_oldname = ET.SubElement(c_elem, "value", {"type": "string", "key": "oldName"})
            c_oldname.text = cname

            c_owner = ET.SubElement(c_elem, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"})
            c_owner.text = t_id

        # Indices
        indices_elem = ET.SubElement(t_elem, "value", {
            "_ptr_": f"0xidx_{t_id[:8]}",
            "type": "list",
            "content-type": "object",
            "content-struct-name": "db.mysql.Index",
            "key": "indices"
        })

        pk_id = gen_id()
        table_pk_index_map[tname] = pk_id

        pk_idx = ET.SubElement(indices_elem, "value", {
            "type": "object",
            "struct-name": "db.mysql.Index",
            "id": pk_id,
            "struct-checksum": "0xdb1989cd"
        })
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "algorithm"})
        pk_cols = ET.SubElement(pk_idx, "value", {
            "_ptr_": f"0xpkcol_{pk_id[:8]}",
            "type": "list",
            "content-type": "object",
            "content-struct-name": "db.mysql.IndexColumn",
            "key": "columns"
        })
        for pk_col_name in tdef["pk"]:
            pk_col_idx_id = gen_id()
            pk_col_elem = ET.SubElement(pk_cols, "value", {
                "type": "object",
                "struct-name": "db.mysql.IndexColumn",
                "id": pk_col_idx_id,
                "struct-checksum": "0x62630b3c"
            })
            ET.SubElement(pk_col_elem, "value", {"type": "int", "key": "columnLength"}).text = "0"
            ET.SubElement(pk_col_elem, "value", {"type": "string", "key": "comment"})
            ET.SubElement(pk_col_elem, "value", {"type": "int", "key": "descend"}).text = "0"
            ET.SubElement(pk_col_elem, "value", {"type": "string", "key": "expression"})
            ref_col = ET.SubElement(pk_col_elem, "link", {"type": "object", "struct-name": "db.Column", "key": "referencedColumn"})
            ref_col.text = col_id_map[(tname, pk_col_name)]
            ET.SubElement(pk_col_elem, "value", {"type": "string", "key": "name"})
            pk_col_owner = ET.SubElement(pk_col_elem, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"})
            pk_col_owner.text = pk_id

        ET.SubElement(pk_idx, "value", {"type": "string", "key": "indexKind"})
        ET.SubElement(pk_idx, "value", {"type": "int", "key": "keyBlockSize"}).text = "0"
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "lockOption"})
        ET.SubElement(pk_idx, "value", {"type": "int", "key": "visible"}).text = "1"
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "withParser"})
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "comment"})
        ET.SubElement(pk_idx, "value", {"type": "int", "key": "deferability"}).text = "0"
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "indexType"}).text = "PRIMARY"
        ET.SubElement(pk_idx, "value", {"type": "int", "key": "isPrimary"}).text = "1"
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "name"}).text = "PRIMARY"
        ET.SubElement(pk_idx, "value", {"type": "int", "key": "unique"}).text = "0"
        ET.SubElement(pk_idx, "value", {"type": "int", "key": "commentedOut"}).text = "0"
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "createDate"})
        ET.SubElement(pk_idx, "value", {"_ptr_": f"0xcust_{pk_id[:8]}", "type": "dict", "key": "customData"})
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "lastChangeDate"})
        ET.SubElement(pk_idx, "value", {"type": "int", "key": "modelOnly"}).text = "0"
        pk_owner = ET.SubElement(pk_idx, "link", {"type": "object", "struct-name": "GrtNamedObject", "key": "owner"})
        pk_owner.text = t_id
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "temp_sql"})
        ET.SubElement(pk_idx, "value", {"type": "string", "key": "oldName"}).text = "PRIMARY"

        # Unique Indices
        for u_name, u_cols in tdef.get("uniques", []):
            u_id = gen_id()
            u_idx = ET.SubElement(indices_elem, "value", {
                "type": "object",
                "struct-name": "db.mysql.Index",
                "id": u_id,
                "struct-checksum": "0xdb1989cd"
            })
            ET.SubElement(u_idx, "value", {"type": "string", "key": "algorithm"})
            u_cols_el = ET.SubElement(u_idx, "value", {
                "_ptr_": f"0xucol_{u_id[:8]}",
                "type": "list",
                "content-type": "object",
                "content-struct-name": "db.mysql.IndexColumn",
                "key": "columns"
            })
            for col_n in u_cols:
                u_col_id = gen_id()
                u_col_elem = ET.SubElement(u_cols_el, "value", {
                    "type": "object",
                    "struct-name": "db.mysql.IndexColumn",
                    "id": u_col_id,
                    "struct-checksum": "0x62630b3c"
                })
                ET.SubElement(u_col_elem, "value", {"type": "int", "key": "columnLength"}).text = "0"
                ET.SubElement(u_col_elem, "value", {"type": "string", "key": "comment"})
                ET.SubElement(u_col_elem, "value", {"type": "int", "key": "descend"}).text = "0"
                ET.SubElement(u_col_elem, "value", {"type": "string", "key": "expression"})
                u_ref = ET.SubElement(u_col_elem, "link", {"type": "object", "struct-name": "db.Column", "key": "referencedColumn"})
                u_ref.text = col_id_map[(tname, col_n)]
                ET.SubElement(u_col_elem, "value", {"type": "string", "key": "name"})
                u_owner = ET.SubElement(u_col_elem, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"})
                u_owner.text = u_id

            ET.SubElement(u_idx, "value", {"type": "string", "key": "indexKind"})
            ET.SubElement(u_idx, "value", {"type": "int", "key": "keyBlockSize"}).text = "0"
            ET.SubElement(u_idx, "value", {"type": "string", "key": "lockOption"})
            ET.SubElement(u_idx, "value", {"type": "int", "key": "visible"}).text = "1"
            ET.SubElement(u_idx, "value", {"type": "string", "key": "withParser"})
            ET.SubElement(u_idx, "value", {"type": "string", "key": "comment"})
            ET.SubElement(u_idx, "value", {"type": "int", "key": "deferability"}).text = "0"
            ET.SubElement(u_idx, "value", {"type": "string", "key": "indexType"}).text = "UNIQUE"
            ET.SubElement(u_idx, "value", {"type": "int", "key": "isPrimary"}).text = "0"
            ET.SubElement(u_idx, "value", {"type": "string", "key": "name"}).text = u_name
            ET.SubElement(u_idx, "value", {"type": "int", "key": "unique"}).text = "1"
            ET.SubElement(u_idx, "value", {"type": "int", "key": "commentedOut"}).text = "0"
            ET.SubElement(u_idx, "value", {"type": "string", "key": "createDate"})
            ET.SubElement(u_idx, "value", {"_ptr_": f"0xcust_{u_id[:8]}", "type": "dict", "key": "customData"})
            ET.SubElement(u_idx, "value", {"type": "string", "key": "lastChangeDate"})
            ET.SubElement(u_idx, "value", {"type": "int", "key": "modelOnly"}).text = "0"
            u_idx_owner = ET.SubElement(u_idx, "link", {"type": "object", "struct-name": "GrtNamedObject", "key": "owner"})
            u_idx_owner.text = t_id
            ET.SubElement(u_idx, "value", {"type": "string", "key": "temp_sql"})
            ET.SubElement(u_idx, "value", {"type": "string", "key": "oldName"}).text = u_name

        # Foreign Keys
        fks_elem = ET.SubElement(t_elem, "value", {
            "_ptr_": f"0xfks_{t_id[:8]}",
            "type": "list",
            "content-type": "object",
            "content-struct-name": "db.mysql.ForeignKey",
            "key": "foreignKeys"
        })

        for fk_def in tdef.get("fks", []):
            fk_name, fk_cols, ref_table_name, ref_cols = fk_def
            fk_id = gen_id()
            fk_obj_map[fk_name] = fk_id

            fk_elem = ET.SubElement(fks_elem, "value", {
                "type": "object",
                "struct-name": "db.mysql.ForeignKey",
                "id": fk_id,
                "struct-checksum": "0x51b4657d"
            })
            fk_reftab = ET.SubElement(fk_elem, "link", {"type": "object", "struct-name": "db.mysql.Table", "key": "referencedTable"})
            fk_reftab.text = table_id_map[ref_table_name]

            fk_cols_list = ET.SubElement(fk_elem, "value", {
                "_ptr_": f"0xfkc_{fk_id[:8]}",
                "type": "list",
                "content-type": "object",
                "content-struct-name": "db.Column",
                "key": "columns"
            })
            for c_n in fk_cols:
                fk_c_link = ET.SubElement(fk_cols_list, "link", {"type": "object"})
                fk_c_link.text = col_id_map[(tname, c_n)]

            ET.SubElement(fk_elem, "value", {"_ptr_": f"0xfkcust_{fk_id[:8]}", "type": "dict", "key": "customData"})
            ET.SubElement(fk_elem, "value", {"type": "int", "key": "deferability"}).text = "0"
            ET.SubElement(fk_elem, "value", {"type": "string", "key": "deleteRule"}).text = "RESTRICT"

            fk_idx_link = ET.SubElement(fk_elem, "link", {"type": "object", "struct-name": "db.Index", "key": "index"})
            fk_idx_link.text = pk_id

            ET.SubElement(fk_elem, "value", {"type": "int", "key": "mandatory"}).text = "1"
            ET.SubElement(fk_elem, "value", {"type": "int", "key": "many"}).text = "1"
            ET.SubElement(fk_elem, "value", {"type": "int", "key": "modelOnly"}).text = "0"

            fk_owner = ET.SubElement(fk_elem, "link", {"type": "object", "struct-name": "db.Table", "key": "owner"})
            fk_owner.text = t_id

            ref_cols_list = ET.SubElement(fk_elem, "value", {
                "_ptr_": f"0xfkrefc_{fk_id[:8]}",
                "type": "list",
                "content-type": "object",
                "content-struct-name": "db.Column",
                "key": "referencedColumns"
            })
            for rc_n in ref_cols:
                rc_link = ET.SubElement(ref_cols_list, "link", {"type": "object"})
                rc_link.text = col_id_map[(ref_table_name, rc_n)]

            ET.SubElement(fk_elem, "value", {"type": "int", "key": "referencedMandatory"}).text = "1"
            ET.SubElement(fk_elem, "value", {"type": "string", "key": "updateRule"}).text = "RESTRICT"
            ET.SubElement(fk_elem, "value", {"type": "string", "key": "comment"})
            ET.SubElement(fk_elem, "value", {"type": "string", "key": "name"}).text = fk_name
            ET.SubElement(fk_elem, "value", {"type": "string", "key": "oldName"}).text = fk_name

            all_connections.append({
                "name": fk_name,
                "fk_id": fk_id,
                "start_table": tname,
                "end_table": ref_table_name
            })

        # Table standard attributes
        ET.SubElement(t_elem, "value", {"type": "string", "key": "connectionString"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "defaultCharacterSetName"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "defaultCollationName"})
        ET.SubElement(t_elem, "value", {"type": "int", "key": "delayKeyWrite"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "string", "key": "keyBlockSize"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "maxRows"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "mergeInsert"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "mergeUnion"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "minRows"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "nextAutoInc"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "packKeys"})
        ET.SubElement(t_elem, "value", {"type": "int", "key": "partitionCount"}).text = "0"
        ET.SubElement(t_elem, "value", {"_ptr_": f"0xpdef_{t_id[:8]}", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.PartitionDefinition", "key": "partitionDefinitions"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "partitionExpression"})
        ET.SubElement(t_elem, "value", {"type": "int", "key": "partitionKeyAlgorithm"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "string", "key": "partitionType"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "password"})

        pk_link = ET.SubElement(t_elem, "link", {"type": "object", "struct-name": "db.mysql.Index", "key": "primaryKey"})
        pk_link.text = pk_id

        ET.SubElement(t_elem, "value", {"type": "string", "key": "raidChunkSize"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "raidChunks"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "raidType"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "rowFormat"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "statsAutoRecalc"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "statsPersistent"})
        ET.SubElement(t_elem, "value", {"type": "int", "key": "statsSamplePages"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "int", "key": "subpartitionCount"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "string", "key": "subpartitionExpression"})
        ET.SubElement(t_elem, "value", {"type": "int", "key": "subpartitionKeyAlgorithm"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "string", "key": "subpartitionType"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "tableDataDir"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "tableEngine"}).text = "InnoDB"
        ET.SubElement(t_elem, "value", {"type": "string", "key": "tableIndexDir"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "tableSpace"})
        ET.SubElement(t_elem, "value", {"_ptr_": f"0xtrig_{t_id[:8]}", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.Trigger", "key": "triggers"})
        ET.SubElement(t_elem, "value", {"type": "int", "key": "isStub"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "int", "key": "isSystem"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "int", "key": "isTemporary"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "string", "key": "temporaryScope"})
        ET.SubElement(t_elem, "value", {"type": "int", "key": "commentedOut"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "string", "key": "createDate"}).text = "2026-10-27 15:30"
        ET.SubElement(t_elem, "value", {"_ptr_": f"0xtcust_{t_id[:8]}", "type": "dict", "key": "customData"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "lastChangeDate"}).text = "2026-10-27 15:30"
        ET.SubElement(t_elem, "value", {"type": "int", "key": "modelOnly"}).text = "0"
        ET.SubElement(t_elem, "value", {"type": "string", "key": "name"}).text = tname
        ET.SubElement(t_elem, "link", {"type": "object", "struct-name": "GrtNamedObject", "key": "owner"}).text = schema_id
        ET.SubElement(t_elem, "value", {"type": "string", "key": "temp_sql"})
        ET.SubElement(t_elem, "value", {"type": "string", "key": "comment"}).text = tdef["comment"]
        ET.SubElement(t_elem, "value", {"type": "string", "key": "oldName"}).text = tname

    ET.SubElement(schema, "value", {"_ptr_": "0x100E", "type": "list", "content-type": "object", "content-struct-name": "db.mysql.View", "key": "views"})
    ET.SubElement(schema, "value", {"type": "string", "key": "defaultCharacterSetName"}).text = "utf8mb4"
    ET.SubElement(schema, "value", {"type": "string", "key": "defaultCollationName"}).text = "utf8mb4_0900_ai_ci"
    ET.SubElement(schema, "value", {"type": "int", "key": "commentedOut"}).text = "0"
    ET.SubElement(schema, "value", {"type": "string", "key": "createDate"}).text = "2026-10-27 15:30"
    ET.SubElement(schema, "value", {"_ptr_": "0x100F", "type": "dict", "key": "customData"})
    ET.SubElement(schema, "value", {"type": "string", "key": "lastChangeDate"}).text = "2026-10-27 15:30"
    ET.SubElement(schema, "value", {"type": "int", "key": "modelOnly"}).text = "0"
    ET.SubElement(schema, "value", {"type": "string", "key": "name"}).text = SCHEMA_NAME
    ET.SubElement(schema, "link", {"type": "object", "struct-name": "GrtNamedObject", "key": "owner"}).text = catalog_id
    ET.SubElement(schema, "value", {"type": "string", "key": "temp_sql"})
    ET.SubElement(schema, "value", {"type": "string", "key": "comment"}).text = "Administrative procedures navigator database"
    ET.SubElement(schema, "value", {"type": "string", "key": "oldName"}).text = SCHEMA_NAME

    st_list = ET.SubElement(catalog, "value", {
        "_ptr_": "0x1010",
        "type": "list",
        "content-type": "object",
        "content-struct-name": "db.SimpleDatatype",
        "key": "simpleDatatypes"
    })
    for st_name in [
        "tinyint", "smallint", "mediumint", "int", "bigint", "float", "real", "double", "decimal",
        "char", "nchar", "varchar", "nvarchar", "binary", "varbinary", "tinytext", "text",
        "mediumtext", "longtext", "tinyblob", "blob", "mediumblob", "longblob", "json",
        "datetime", "datetime_f", "date", "time", "time_f", "year", "timestamp", "timestamp_f",
        "geometry", "point", "linestring", "polygon", "geometrycollection", "multipoint",
        "multilinestring", "multipolygon", "bit", "boolean", "enum", "set"
    ]:
        st_link = ET.SubElement(st_list, "link", {"type": "object"})
        st_link.text = f"com.mysql.rdbms.mysql.datatype.{st_name}"

    ET.SubElement(catalog, "value", {"_ptr_": "0x1011", "type": "list", "content-type": "object", "content-struct-name": "db.UserDatatype", "key": "userDatatypes"})
    ET.SubElement(catalog, "value", {"_ptr_": "0x1012", "type": "list", "content-type": "object", "content-struct-name": "db.User", "key": "users"})

    ver_id = gen_id()
    ver_elem = ET.SubElement(catalog, "value", {
        "type": "object",
        "struct-name": "GrtVersion",
        "id": ver_id,
        "struct-checksum": "0x7aaa4ede",
        "key": "version"
    })
    ET.SubElement(ver_elem, "value", {"type": "int", "key": "buildNumber"}).text = "-1"
    ET.SubElement(ver_elem, "value", {"type": "int", "key": "majorNumber"}).text = "8"
    ET.SubElement(ver_elem, "value", {"type": "int", "key": "minorNumber"}).text = "0"
    ET.SubElement(ver_elem, "value", {"type": "int", "key": "releaseNumber"}).text = "47"
    ET.SubElement(ver_elem, "value", {"type": "int", "key": "status"}).text = "0"
    ET.SubElement(ver_elem, "value", {"type": "string", "key": "name"}).text = "Version"
    ET.SubElement(ver_elem, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"}).text = catalog_id

    ET.SubElement(catalog, "value", {"type": "string", "key": "comment"})
    ET.SubElement(catalog, "value", {"type": "string", "key": "name"}).text = "default"
    ET.SubElement(catalog, "value", {"type": "string", "key": "oldName"})
    ET.SubElement(catalog, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"}).text = phys_model_id

    ET.SubElement(phys_model, "value", {"type": "string", "key": "connectionNotation"}).text = "crowsfoot"
    ET.SubElement(phys_model, "value", {"_ptr_": "0x1013", "type": "list", "content-type": "object", "content-struct-name": "db.mgmt.Connection", "key": "connections"})

    # DIAGRAM EER
    diagrams_list = ET.SubElement(phys_model, "value", {
        "_ptr_": "0x1014",
        "type": "list",
        "content-type": "object",
        "content-struct-name": "workbench.physical.Diagram",
        "key": "diagrams"
    })

    diagram = ET.SubElement(diagrams_list, "value", {
        "type": "object",
        "struct-name": "workbench.physical.Diagram",
        "id": diagram_id,
        "struct-checksum": "0x232c2434"
    })
    ET.SubElement(diagram, "value", {"type": "int", "key": "closed"}).text = "0"

    diag_conns = ET.SubElement(diagram, "value", {
        "_ptr_": "0x1015",
        "type": "list",
        "content-type": "object",
        "content-struct-name": "model.Connection",
        "key": "connections"
    })

    for conn_def in all_connections:
        conn_id = gen_id()
        c_elem = ET.SubElement(diag_conns, "value", {
            "type": "object",
            "struct-name": "workbench.physical.Connection",
            "id": conn_id,
            "struct-checksum": "0x9baebc92"
        })
        ET.SubElement(c_elem, "value", {"type": "string", "key": "caption"}).text = conn_def["name"]
        ET.SubElement(c_elem, "value", {"type": "real", "key": "captionXOffs"}).text = "0"
        ET.SubElement(c_elem, "value", {"type": "real", "key": "captionYOffs"}).text = "0"
        ET.SubElement(c_elem, "value", {"type": "string", "key": "comment"})
        ET.SubElement(c_elem, "value", {"type": "real", "key": "endCaptionXOffs"}).text = "0"
        ET.SubElement(c_elem, "value", {"type": "real", "key": "endCaptionYOffs"}).text = "0"
        ET.SubElement(c_elem, "value", {"type": "string", "key": "extraCaption"})
        ET.SubElement(c_elem, "value", {"type": "real", "key": "extraCaptionXOffs"}).text = "0"
        ET.SubElement(c_elem, "value", {"type": "real", "key": "extraCaptionYOffs"}).text = "0"

        ET.SubElement(c_elem, "link", {"type": "object", "struct-name": "db.ForeignKey", "key": "foreignKey"}).text = conn_def["fk_id"]
        ET.SubElement(c_elem, "value", {"type": "real", "key": "middleSegmentOffset"}).text = "0"
        ET.SubElement(c_elem, "value", {"type": "real", "key": "startCaptionXOffs"}).text = "0"
        ET.SubElement(c_elem, "value", {"type": "real", "key": "startCaptionYOffs"}).text = "0"
        ET.SubElement(c_elem, "value", {"type": "int", "key": "drawSplit"}).text = "0"

        ET.SubElement(c_elem, "link", {"type": "object", "struct-name": "model.Figure", "key": "endFigure"}).text = table_fig_map[conn_def["end_table"]]
        ET.SubElement(c_elem, "link", {"type": "object", "struct-name": "model.Figure", "key": "startFigure"}).text = table_fig_map[conn_def["start_table"]]
        ET.SubElement(c_elem, "link", {"type": "object", "struct-name": "model.Diagram", "key": "owner"}).text = diagram_id
        ET.SubElement(c_elem, "value", {"type": "int", "key": "visible"}).text = "1"
        ET.SubElement(c_elem, "value", {"type": "string", "key": "name"})

    ET.SubElement(diagram, "value", {"type": "string", "key": "description"})

    diag_figures = ET.SubElement(diagram, "value", {
        "_ptr_": "0x1016",
        "type": "list",
        "content-type": "object",
        "content-struct-name": "model.Figure",
        "key": "figures"
    })

    COLUMN_MAP = {
        "lookup": 0,
        "procedures": 1,
        "documents": 2,
        "scenarios": 3,
        "i18n": 3,
        "audit": 4,
        "users": 4,
        "extensions": 5,
    }
    col_y_cursors = [40, 40, 40, 40, 40, 40]
    X_OFFSETS = [40, 420, 800, 1180, 1560, 1940]
    FIG_WIDTH = 300

    fig_ids_list = []

    for tdef in TABLES_DEF:
        tname = tdef["name"]
        tid = table_id_map[tname]
        fid = table_fig_map[tname]
        fig_ids_list.append(fid)

        col_idx = COLUMN_MAP[tdef["block"]]
        left_pos = X_OFFSETS[col_idx]
        top_pos = col_y_cursors[col_idx]

        col_count = len(tdef["columns"])
        fig_height = 80 + col_count * 22
        col_y_cursors[col_idx] += fig_height + 40

        tf_elem = ET.SubElement(diag_figures, "value", {
            "type": "object",
            "struct-name": "workbench.physical.TableFigure",
            "id": fid,
            "struct-checksum": "0x3b14eccb"
        })
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "columnsExpanded"}).text = "1"
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "foreignKeysExpanded"}).text = "0"
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "indicesExpanded"}).text = "0"
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "summarizeDisplay"}).text = "-1"
        ET.SubElement(tf_elem, "link", {"type": "object", "struct-name": "db.Table", "key": "table"}).text = tid
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "triggersExpanded"}).text = "0"
        ET.SubElement(tf_elem, "value", {"type": "string", "key": "color"}).text = BLOCK_COLORS[tdef["block"]]
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "expanded"}).text = "1"
        ET.SubElement(tf_elem, "value", {"type": "real", "key": "height"}).text = str(fig_height)
        ET.SubElement(tf_elem, "link", {"type": "object", "struct-name": "model.Layer", "key": "layer"}).text = root_layer_id
        ET.SubElement(tf_elem, "value", {"type": "real", "key": "left"}).text = str(left_pos)
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "locked"}).text = "0"
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "manualSizing"}).text = "0"
        ET.SubElement(tf_elem, "value", {"type": "real", "key": "top"}).text = str(top_pos)
        ET.SubElement(tf_elem, "value", {"type": "real", "key": "width"}).text = str(FIG_WIDTH)
        ET.SubElement(tf_elem, "link", {"type": "object", "struct-name": "model.Diagram", "key": "owner"}).text = diagram_id
        ET.SubElement(tf_elem, "value", {"type": "int", "key": "visible"}).text = "1"
        ET.SubElement(tf_elem, "value", {"type": "string", "key": "name"}).text = tname

    max_canvas_height = max(col_y_cursors) + 200
    canvas_width = 2350.0

    ET.SubElement(diagram, "value", {"type": "real", "key": "height"}).text = str(max_canvas_height)
    ET.SubElement(diagram, "value", {"_ptr_": "0x1017", "type": "list", "content-type": "object", "content-struct-name": "model.Layer", "key": "layers"})
    ET.SubElement(diagram, "value", {"type": "string", "key": "name"}).text = "Nawigator - Complete EER Model"
    ET.SubElement(diagram, "value", {"_ptr_": "0x1018", "type": "dict", "key": "options"})
    ET.SubElement(diagram, "link", {"type": "object", "struct-name": "model.Model", "key": "owner"}).text = phys_model_id

    root_layer = ET.SubElement(diagram, "value", {
        "type": "object",
        "struct-name": "workbench.physical.Layer",
        "id": root_layer_id,
        "struct-checksum": "0x1d14ca4b",
        "key": "rootLayer"
    })
    ET.SubElement(root_layer, "value", {"type": "string", "key": "color"})
    ET.SubElement(root_layer, "value", {"type": "string", "key": "description"})
    rl_figs = ET.SubElement(root_layer, "value", {
        "_ptr_": "0x1019",
        "type": "list",
        "content-type": "object",
        "content-struct-name": "model.Figure",
        "key": "figures"
    })
    for fid in fig_ids_list:
        ET.SubElement(rl_figs, "link", {"type": "object"}).text = fid

    ET.SubElement(root_layer, "value", {"_ptr_": "0x101A", "type": "list", "content-type": "object", "content-struct-name": "model.Group", "key": "groups"})
    ET.SubElement(root_layer, "value", {"type": "real", "key": "height"}).text = str(max_canvas_height)
    ET.SubElement(root_layer, "value", {"type": "real", "key": "left"}).text = "0"
    ET.SubElement(root_layer, "value", {"_ptr_": "0x101B", "type": "list", "content-type": "object", "content-struct-name": "model.Layer", "key": "subLayers"})
    ET.SubElement(root_layer, "value", {"type": "real", "key": "top"}).text = "0"
    ET.SubElement(root_layer, "value", {"type": "real", "key": "width"}).text = str(canvas_width)
    ET.SubElement(root_layer, "link", {"type": "object", "struct-name": "model.Diagram", "key": "owner"}).text = diagram_id
    ET.SubElement(root_layer, "value", {"type": "int", "key": "visible"}).text = "1"
    ET.SubElement(root_layer, "value", {"type": "string", "key": "name"})

    ET.SubElement(diagram, "value", {"_ptr_": "0x101C", "type": "list", "content-type": "object", "content-struct-name": "model.Object", "key": "selection"})
    ET.SubElement(diagram, "value", {"type": "int", "key": "updateBlocked"}).text = "0"
    ET.SubElement(diagram, "value", {"type": "real", "key": "width"}).text = str(canvas_width)
    ET.SubElement(diagram, "value", {"type": "real", "key": "x"}).text = "0"
    ET.SubElement(diagram, "value", {"type": "real", "key": "y"}).text = "0"
    ET.SubElement(diagram, "value", {"type": "real", "key": "zoom"}).text = "0.85"

    ET.SubElement(phys_model, "value", {"type": "string", "key": "figureNotation"}).text = "workbench/default"
    ET.SubElement(phys_model, "value", {"_ptr_": "0x101D", "type": "list", "content-type": "object", "content-struct-name": "GrtStoredNote", "key": "notes"})
    ET.SubElement(phys_model, "link", {"type": "object", "struct-name": "db.mgmt.Rdbms", "key": "rdbms"}).text = "com.mysql.rdbms.mysql"
    ET.SubElement(phys_model, "value", {"_ptr_": "0x101E", "type": "list", "content-type": "object", "content-struct-name": "db.Script", "key": "scripts"})
    ET.SubElement(phys_model, "value", {"_ptr_": "0x101F", "type": "dict", "key": "syncProfiles"})
    ET.SubElement(phys_model, "value", {"_ptr_": "0x1020", "type": "list", "content-type": "object", "content-struct-name": "GrtObject", "key": "tagCategories"})
    ET.SubElement(phys_model, "value", {"_ptr_": "0x1021", "type": "list", "content-type": "object", "content-struct-name": "meta.Tag", "key": "tags"})
    ET.SubElement(phys_model, "link", {"type": "object", "struct-name": "model.Diagram", "key": "currentDiagram"}).text = diagram_id
    ET.SubElement(phys_model, "value", {"_ptr_": "0x1022", "type": "dict", "key": "customData"})
    ET.SubElement(phys_model, "value", {"_ptr_": "0x1023", "type": "list", "content-type": "object", "content-struct-name": "model.Marker", "key": "markers"})
    ET.SubElement(phys_model, "value", {"_ptr_": "0x1024", "type": "dict", "key": "options"})
    ET.SubElement(phys_model, "value", {"type": "string", "key": "name"})
    ET.SubElement(phys_model, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"}).text = doc_id

    info_id = gen_id()
    info_elem = ET.SubElement(doc, "value", {
        "type": "object",
        "struct-name": "app.DocumentInfo",
        "id": info_id,
        "struct-checksum": "0xbba780b8",
        "key": "info"
    })
    ET.SubElement(info_elem, "value", {"type": "string", "key": "author"}).text = "Nawigator Team"
    ET.SubElement(info_elem, "value", {"type": "string", "key": "caption"}).text = "Administrative Procedures Navigator - Complete EER Model"
    ET.SubElement(info_elem, "value", {"type": "string", "key": "dateChanged"}).text = "2026-10-27 15:55"
    ET.SubElement(info_elem, "value", {"type": "string", "key": "dateCreated"}).text = "2026-10-27 15:00"
    ET.SubElement(info_elem, "value", {"type": "string", "key": "description"}).text = "Comprehensive database model with 34 tables in English for the Administrative Procedures Navigator in Poland."
    ET.SubElement(info_elem, "value", {"type": "string", "key": "project"}).text = "Nawigator"
    ET.SubElement(info_elem, "value", {"type": "string", "key": "version"}).text = "1.0.0"
    ET.SubElement(info_elem, "value", {"type": "string", "key": "name"}).text = "Properties"
    ET.SubElement(info_elem, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"}).text = doc_id

    page_id = gen_id()
    page_elem = ET.SubElement(doc, "value", {
        "type": "object",
        "struct-name": "app.PageSettings",
        "id": page_id,
        "struct-checksum": "0x7dc77977",
        "key": "pageSettings"
    })
    ET.SubElement(page_elem, "value", {"type": "real", "key": "marginBottom"}).text = "14.46"
    ET.SubElement(page_elem, "value", {"type": "real", "key": "marginLeft"}).text = "6.35"
    ET.SubElement(page_elem, "value", {"type": "real", "key": "marginRight"}).text = "6.35"
    ET.SubElement(page_elem, "value", {"type": "real", "key": "marginTop"}).text = "6.35"
    ET.SubElement(page_elem, "value", {"type": "string", "key": "orientation"}).text = "landscape"
    ET.SubElement(page_elem, "link", {"type": "object", "struct-name": "app.PaperType", "key": "paperType"}).text = "com.mysql.wb.papertype.a3"
    ET.SubElement(page_elem, "value", {"type": "real", "key": "scale"}).text = "100"
    ET.SubElement(page_elem, "value", {"type": "string", "key": "name"})
    ET.SubElement(page_elem, "link", {"type": "object", "struct-name": "GrtObject", "key": "owner"}).text = doc_id

    ET.SubElement(doc, "value", {"type": "string", "key": "name"})

    return root

def generate_sqlite_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE XP_PROC (
        view_name TEXT,
        param_list TEXT,
        xSQL TEXT,
        def_param TEXT,
        opt_param TEXT,
        comment TEXT,
        PRIMARY KEY (view_name)
    );
    """)
    conn.commit()
    conn.close()

def main():
    target_dir = "/home/toriy/in/ii/sql/dataplan"
    mwb_path = os.path.join(target_dir, "nawigator.mwb")
    xml_out_path = os.path.join("/tmp", "document.mwb.xml")
    sqlite_out_path = os.path.join("/tmp", "@db", "data.db")
    lock_path = os.path.join("/tmp", "lock")

    print("Generating MySQL Workbench Model XML with English names...")
    root_el = build_mwb_xml()
    xml_str = ET.tostring(root_el, encoding="utf-8")
    parsed = minidom.parseString(xml_str)
    pretty_xml = parsed.toprettyxml(indent="  ", encoding="utf-8")

    with open(xml_out_path, "wb") as f:
        f.write(pretty_xml)
    print(f"Saved XML ({len(pretty_xml)} bytes).")

    print("Initializing SQLite data.db...")
    generate_sqlite_db(sqlite_out_path)

    with open(lock_path, "w") as f:
        f.write("manual")

    print(f"Creating ZIP archive: {mwb_path}...")
    with zipfile.ZipFile(mwb_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(lock_path, "lock")
        zf.write(xml_out_path, "document.mwb.xml")
        zf.write(sqlite_out_path, "@db/data.db")

    print(f"Successfully generated MySQL Workbench project: {mwb_path} ({os.path.getsize(mwb_path)} bytes).")

if __name__ == "__main__":
    main()
