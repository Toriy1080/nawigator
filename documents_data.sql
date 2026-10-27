-- =====================================================================
-- Przykładowe dane: kategorie, podkategorie i typy dokumentów
-- Uruchamiać po documents_schema.sql
-- =====================================================================

USE nawigator;

INSERT INTO DocumentCategory
  (DocumentCategoryKey, DocumentCategoryName, DocumentCategoryCode)
VALUES
  (1, 'Dokumenty tożsamości',                  'TOZ'),
  (2, 'Dokumenty pobytowe',                    'POB'),
  (3, 'Dokumenty dotyczące pracy',             'PRA'),
  (4, 'Dokumenty edukacyjne',                  'EDU'),
  (5, 'Akty stanu cywilnego',                  'USC'),
  (6, 'Zaświadczenia urzędowe',                'ZAS'),
  (7, 'Wnioski i formularze',                  'WNI'),
  (8, 'Dokumenty finansowe i ubezpieczeniowe', 'FIN'),
  (9, 'Dokumenty dotyczące mieszkania',        'MIE');

INSERT INTO DocumentSubcategory
  (DocumentSubcategoryKey, DocumentSubcategoryName, DocumentSubcategoryCode, DocumentCategoryKey)
VALUES
  ( 1, 'Paszporty',                           'TOZ_PASZ', 1),
  ( 2, 'Dowody osobiste',                     'TOZ_DOW',  1),
  ( 3, 'Wizy',                                'POB_WIZA', 2),
  ( 4, 'Karty pobytu',                        'POB_KART', 2),
  ( 5, 'Dokumenty pobytowe obywateli UE',     'POB_UE',   2),
  ( 6, 'Umowy',                               'PRA_UMOW', 3),
  ( 7, 'Zezwolenia i powiadomienia o pracy',  'PRA_ZEZW', 3),
  ( 8, 'Dyplomy i świadectwa',                'EDU_DYPL', 4),
  ( 9, 'Dokumenty z uczelni',                 'EDU_UCZL', 4),
  (10, 'Odpisy aktów stanu cywilnego',        'USC_ODP',  5),
  (11, 'Zaświadczenia ewidencyjne',           'ZAS_EWID', 6),
  (12, 'Informacje o niekaralności',          'ZAS_KARN', 6),
  (13, 'Formularze ZUS',                      'WNI_ZUS',  7),
  (14, 'Wnioski CEIDG',                       'WNI_CEID', 7),
  (15, 'Wnioski do urzędów',                  'WNI_URZ',  7),
  (16, 'Dokumenty bankowe',                   'FIN_BANK', 8),
  (17, 'Ubezpieczenie zdrowotne',             'FIN_UBEZ', 8),
  (18, 'Tytuł prawny do lokalu',              'MIE_LOKL', 9);

-- Kolumny flag: HasExpiryDate (termin ważności), RequiresSwornTranslation
-- (tłumaczenie przysięgłe, gdy dokument wydano w języku obcym).
-- EffectiveStartDate = dzień uruchomienia katalogu.
INSERT INTO DocumentType
  (DocumentTypeKey, DocumentTypeName, DocumentTypeCode, DocumentSubcategoryKey,
   HasExpiryDate, RequiresSwornTranslation, EffectiveStartDate)
VALUES
  -- Dokumenty tożsamości
  ( 1, 'Paszport',                                                   'PASZ',       1, 1, 0, '2026-01-01'),
  ( 2, 'Dowód osobisty (polski)',                                    'DOW_PL',     2, 1, 0, '2026-01-01'),
  ( 3, 'Dowód osobisty obywatela UE/EOG',                            'DOW_UE',     2, 1, 0, '2026-01-01'),
  -- Dokumenty pobytowe
  ( 4, 'Wiza krajowa (typ D)',                                       'WIZA_D',     3, 1, 0, '2026-01-01'),
  ( 5, 'Wiza Schengen (typ C)',                                      'WIZA_C',     3, 1, 0, '2026-01-01'),
  ( 6, 'Karta pobytu – zezwolenie na pobyt czasowy',                 'KP_CZAS',    4, 1, 0, '2026-01-01'),
  ( 7, 'Karta pobytu – zezwolenie na pobyt stały',                   'KP_STALY',   4, 1, 0, '2026-01-01'),
  ( 8, 'Zaświadczenie o zarejestrowaniu pobytu obywatela UE',        'UE_REJ',     5, 0, 0, '2026-01-01'),
  -- Praca
  ( 9, 'Umowa o pracę',                                              'UM_PRACA',   6, 0, 0, '2026-01-01'),
  (10, 'Umowa zlecenia',                                             'UM_ZLEC',    6, 0, 0, '2026-01-01'),
  (11, 'Umowa o dzieło',                                             'UM_DZIELO',  6, 0, 0, '2026-01-01'),
  (12, 'Zezwolenie na pracę typu A',                                 'ZEZW_A',     7, 1, 0, '2026-01-01'),
  (13, 'Oświadczenie o powierzeniu wykonywania pracy cudzoziemcowi', 'OSW_PRACA',  7, 1, 0, '2026-01-01'),
  (14, 'Powiadomienie o powierzeniu pracy obywatelowi Ukrainy',      'POW_UKR',    7, 0, 0, '2026-01-01'),
  -- Edukacja
  (15, 'Dyplom ukończenia studiów',                                  'DYPLOM',     8, 0, 1, '2026-01-01'),
  (16, 'Świadectwo ukończenia szkoły średniej',                      'SW_SREDN',   8, 0, 1, '2026-01-01'),
  (17, 'Legitymacja studencka',                                      'LEG_STUD',   9, 1, 0, '2026-01-01'),
  (18, 'Zaświadczenie o statusie studenta',                          'ZAS_STUD',   9, 0, 0, '2026-01-01'),
  (19, 'Decyzja o przyjęciu na studia',                              'DEC_PRZYJ',  9, 0, 0, '2026-01-01'),
  -- Akty stanu cywilnego
  (20, 'Odpis aktu urodzenia',                                       'AKT_UR',    10, 0, 1, '2026-01-01'),
  (21, 'Odpis aktu małżeństwa',                                      'AKT_MALZ',  10, 0, 1, '2026-01-01'),
  -- Zaświadczenia
  (22, 'Zaświadczenie o nadaniu numeru PESEL',                       'ZAS_PESEL', 11, 0, 0, '2026-01-01'),
  (23, 'Zaświadczenie o zameldowaniu na pobyt czasowy',              'ZAS_MELD',  11, 1, 0, '2026-01-01'),
  (24, 'Informacja z Krajowego Rejestru Karnego',                    'KRK',       12, 0, 0, '2026-01-01'),
  (25, 'Zaświadczenie o niekaralności z kraju pochodzenia',          'KARN_ZAGR', 12, 0, 1, '2026-01-01'),
  -- Wnioski i formularze
  (26, 'Formularz ZUS ZUA – zgłoszenie do ubezpieczeń',              'ZUS_ZUA',   13, 0, 0, '2026-01-01'),
  (27, 'Formularz ZUS ZZA – zgłoszenie do ubezpieczenia zdrowotnego','ZUS_ZZA',   13, 0, 0, '2026-01-01'),
  (28, 'Wniosek CEIDG-1 o wpis do CEIDG',                            'CEIDG_1',   14, 0, 0, '2026-01-01'),
  (29, 'Wniosek o nadanie numeru PESEL',                             'WN_PESEL',  15, 0, 0, '2026-01-01'),
  (30, 'Wniosek o udzielenie zezwolenia na pobyt czasowy',           'WN_POBYT',  15, 0, 0, '2026-01-01'),
  -- Finanse i ubezpieczenia
  (31, 'Wyciąg z rachunku bankowego',                                'WYCIAG_BNK',16, 0, 1, '2026-01-01'),
  (32, 'Polisa prywatnego ubezpieczenia zdrowotnego',                'POLISA_ZDR',17, 1, 1, '2026-01-01'),
  (33, 'Europejska Karta Ubezpieczenia Zdrowotnego (EKUZ)',          'EKUZ',      17, 1, 0, '2026-01-01'),
  (34, 'Umowa o dobrowolne ubezpieczenie zdrowotne w NFZ',           'NFZ_DOBR',  17, 0, 0, '2026-01-01'),
  -- Mieszkanie
  (35, 'Umowa najmu lokalu',                                         'UM_NAJMU',  18, 0, 0, '2026-01-01'),
  (36, 'Akt notarialny nabycia lokalu',                              'AKT_NOTAR', 18, 0, 0, '2026-01-01');

-- Gdy zmienia się wzór dokumentu, starego wiersza się nie usuwa (mogą
-- się do niego odwoływać postępy klientów): stary typ dostaje
-- EffectiveEndDate, a nowy wzór jest dodawany z EffectiveStartDate
-- od następnego dnia.

-- ---------------------------------------------------------------------
-- Zapytanie kontrolne: typy dokumentów dostępne dziś, z pełną ścieżką
-- ---------------------------------------------------------------------
SELECT c.DocumentCategoryName    AS Kategoria,
       s.DocumentSubcategoryName AS Podkategoria,
       t.DocumentTypeName        AS TypDokumentu,
       t.DocumentTypeCode        AS Kod
FROM DocumentType t
JOIN DocumentSubcategory s ON s.DocumentSubcategoryKey = t.DocumentSubcategoryKey
JOIN DocumentCategory    c ON c.DocumentCategoryKey    = s.DocumentCategoryKey
WHERE c.DocumentCategoryStatus = 1
  AND s.DocumentSubcategoryStatus = 1
  AND t.DocumentTypeStatus = 1
  AND CURRENT_DATE >= t.EffectiveStartDate
  AND (t.EffectiveEndDate IS NULL OR CURRENT_DATE <= t.EffectiveEndDate)
ORDER BY c.DocumentCategoryKey, s.DocumentSubcategoryKey, t.DocumentTypeName;
