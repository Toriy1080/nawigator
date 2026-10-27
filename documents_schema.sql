-- =====================================================================
-- Nawigator po procedurach administracyjnych w Polsce
-- Fragment schematu: kategorie, podkategorie i typy dokumentów
--
--   DocumentCategory 1 ──< DocumentSubcategory 1 ──< DocumentType
--   (np. Dokumenty pobytowe → Karty pobytu → Karta pobytu – pobyt czasowy)
--
-- MySQL 8.0.16+ (od tej wersji ograniczenia CHECK są egzekwowane)
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS nawigator
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE nawigator;

-- ---------------------------------------------------------------------
-- Poziom 1: kategoria dokumentu, np. „Dokumenty tożsamości”
-- ---------------------------------------------------------------------
CREATE TABLE DocumentCategory (
  DocumentCategoryKey      TINYINT UNSIGNED  NOT NULL AUTO_INCREMENT
                           COMMENT 'Klucz sztuczny',
  DocumentCategoryName     VARCHAR(60)       NOT NULL
                           COMMENT 'Nazwa po polsku; tłumaczenia w module tłumaczeń',
  DocumentCategoryCode     VARCHAR(10)       NOT NULL
                           COMMENT 'Stały kod, np. TOZ; nie zmienia się przy zmianie nazwy',
  DocumentCategoryStatus   TINYINT           NOT NULL DEFAULT 1
                           COMMENT '1 – aktywna, 0 – wycofana (zamiast usuwania)',
  PRIMARY KEY (DocumentCategoryKey),
  CONSTRAINT DocumentCategoryName_UN UNIQUE (DocumentCategoryName),
  CONSTRAINT DocumentCategoryCode_UN UNIQUE (DocumentCategoryCode),
  CONSTRAINT DocumentCategoryCode_CK
    CHECK (REGEXP_LIKE(DocumentCategoryCode, '^[A-Z0-9_]+$', 'c')),
  CONSTRAINT DocumentCategoryStatus_CK
    CHECK (DocumentCategoryStatus IN (0, 1))
) ENGINE = InnoDB
  COMMENT = 'Kategorie dokumentów (poziom 1)';

-- ---------------------------------------------------------------------
-- Poziom 2: podkategoria, np. „Paszporty” w kategorii „Dokumenty tożsamości”
-- ---------------------------------------------------------------------
CREATE TABLE DocumentSubcategory (
  DocumentSubcategoryKey    SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT
                            COMMENT 'Klucz sztuczny',
  DocumentSubcategoryName   VARCHAR(80)       NOT NULL
                            COMMENT 'Nazwa po polsku; unikalna w ramach kategorii',
  DocumentSubcategoryCode   VARCHAR(10)       NOT NULL
                            COMMENT 'Stały kod, np. TOZ_PASZ',
  DocumentCategoryKey       TINYINT UNSIGNED  NOT NULL
                            COMMENT 'Kategoria nadrzędna',
  DocumentSubcategoryStatus TINYINT           NOT NULL DEFAULT 1
                            COMMENT '1 – aktywna, 0 – wycofana',
  PRIMARY KEY (DocumentSubcategoryKey),
  -- ta sama nazwa (np. „Inne”) może wystąpić w różnych kategoriach;
  -- indeks zaczyna się od klucza obcego, więc obsługuje też FK
  CONSTRAINT DocumentSubcategoryName_UN
    UNIQUE (DocumentCategoryKey, DocumentSubcategoryName),
  CONSTRAINT DocumentSubcategoryCode_UN UNIQUE (DocumentSubcategoryCode),
  CONSTRAINT DocumentSubcategoryCode_CK
    CHECK (REGEXP_LIKE(DocumentSubcategoryCode, '^[A-Z0-9_]+$', 'c')),
  CONSTRAINT DocumentSubcategoryStatus_CK
    CHECK (DocumentSubcategoryStatus IN (0, 1)),
  CONSTRAINT DocumentSubcategory_DocumentCategory_FK
    FOREIGN KEY (DocumentCategoryKey)
    REFERENCES DocumentCategory (DocumentCategoryKey)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
) ENGINE = InnoDB
  COMMENT = 'Podkategorie dokumentów (poziom 2)';

-- ---------------------------------------------------------------------
-- Poziom 3: konkretny typ dokumentu, np. „Wiza krajowa (typ D)”
-- To ten poziom jest później wiązany z procedurami („do procedury X
-- potrzebny jest dokument typu Y”) i z listą dokumentów klienta.
-- ---------------------------------------------------------------------
CREATE TABLE DocumentType (
  DocumentTypeKey          SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT
                           COMMENT 'Klucz sztuczny',
  DocumentTypeName         VARCHAR(120)      NOT NULL
                           COMMENT 'Oficjalna nazwa po polsku',
  DocumentTypeCode         VARCHAR(10)       NOT NULL
                           COMMENT 'Stały kod, np. WIZA_D',
  DocumentSubcategoryKey   SMALLINT UNSIGNED NOT NULL
                           COMMENT 'Podkategoria nadrzędna',
  DocumentTypeStatus       TINYINT           NOT NULL DEFAULT 1
                           COMMENT '1 – aktywny, 0 – ukryty przez administratora',
  HasExpiryDate            BOOLEAN           NOT NULL DEFAULT FALSE
                           COMMENT '1 – dokument ma termin ważności (paszport, wiza); klient podaje datę, system ostrzega',
  RequiresSwornTranslation BOOLEAN           NOT NULL DEFAULT FALSE
                           COMMENT '1 – wydany w języku obcym wymaga tłumaczenia przysięgłego',
  EffectiveStartDate       DATE              NOT NULL
                           COMMENT 'Od kiedy typ jest używany w planach (np. nowy wzór formularza od dnia zmiany przepisów)',
  EffectiveEndDate         DATE              NULL
                           COMMENT 'Do kiedy jest używany; NULL – bezterminowo',
  PRIMARY KEY (DocumentTypeKey),
  CONSTRAINT DocumentTypeName_UN UNIQUE (DocumentTypeName),
  CONSTRAINT DocumentTypeCode_UN UNIQUE (DocumentTypeCode),
  INDEX DocumentType_DocumentSubcategory_IX (DocumentSubcategoryKey),
  CONSTRAINT DocumentTypeCode_CK
    CHECK (REGEXP_LIKE(DocumentTypeCode, '^[A-Z0-9_]+$', 'c')),
  CONSTRAINT DocumentTypeStatus_CK
    CHECK (DocumentTypeStatus IN (0, 1)),
  CONSTRAINT DocumentTypeHasExpiryDate_CK
    CHECK (HasExpiryDate IN (0, 1)),
  CONSTRAINT DocumentTypeRequiresSwornTranslation_CK
    CHECK (RequiresSwornTranslation IN (0, 1)),
  CONSTRAINT DocumentTypeEffectiveDates_CK
    CHECK (EffectiveEndDate IS NULL OR EffectiveEndDate >= EffectiveStartDate),
  CONSTRAINT DocumentType_DocumentSubcategory_FK
    FOREIGN KEY (DocumentSubcategoryKey)
    REFERENCES DocumentSubcategory (DocumentSubcategoryKey)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
) ENGINE = InnoDB
  COMMENT = 'Typy dokumentów (poziom 3)';
