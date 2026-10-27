# Nawigator Procedur Administracyjnych — Kompletny Projekt Diagramowy

Niniejszy katalog zawiera pełną dokumentację architektoniczną, bazodanową, procesową i analityczną projektu **Nawigator procedur administracyjnych w Polsce**, opracowaną na podstawie specyfikacji `README.md` z gałęzi `origin/main`.

Wszystkie diagramy zostały wykonane w standardzie **Mermaid** i zapisane w dedykowanych plikach `.mmd`.

---

## 📑 Spis zawartości i mapa diagramów (27 plików)

| Kategoria | Nazwa pliku | Typ diagramu | Opis |
| :--- | :--- | :--- | :--- |
| **Baza danych** | [`erd.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/erd.mmd) | ERD (`erDiagram`) | Kompletny model bazy: 32 tabele w 8 blokach, typy kolumn, klucze PK/FK, ograniczenia i relacje. |
| **Aktorzy i przypadki użycia** | [`use_case.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/use_case.mmd) | Use Case (`flowchart`) | 5 aktorów (Gość, Klient, Pomocnik, Redaktor, Administrator), dziedziczenie ról i 27 przypadków użycia. |
| **Architektura systemu** | [`architecture.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/architecture.mmd) | Architektura (`flowchart TD`) | Warstwy systemu: Frontend (RWD/Mobile), Backend, Bezpieczeństwo, Baza PostgreSQL, Źródła gov. |
| **Komponenty** | [`component.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/component.mmd) | Komponenty (`flowchart LR`) | 8 modułów i serwisów: Auth, Profil, Silnik Grafu, Tłumaczenia, Wyszukiwarka, Panel Admina. |
| **Wdrożenie i infrastruktura** | [`deployment.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/deployment.mmd) | Wdrożenie (`flowchart LR`) | Topologia: Klient (Mobile/Desktop) ➔ Nginx (Reverse Proxy) ➔ Backend Node/Python ➔ PostgreSQL. |
| **Model klas generatora** | [`class_plan_generator.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/class_plan_generator.mmd) | Klasy (`classDiagram`) | Kluczowe klasy silnika grafu (`PlanGenerator`, `DependencyGraph`, `RuleEngine`, `Plan`, `PlanStep`). |
| **Przepływy sekwencji** | [`seq_rejestracja.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/seq_rejestracja.mmd) | Sekwencja (`sequenceDiagram`) | F-01/F-02: Rejestracja, haszowanie Argon2id, obowiązkowa narodowość, sesja HttpOnly, RODO. |
| | [`seq_generowanie_planu.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/seq_generowanie_planu.mmd) | Sekwencja (`sequenceDiagram`) | F-06: Kluczowy algorytm wyliczania kolejności kroków z grafu zależności (CTE, sortowanie topologiczne). |
| | [`seq_zmiana_profilu.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/seq_zmiana_profilu.mmd) | Sekwencja (`sequenceDiagram`) | F-03: Przeliczenie planu po zmianie statusu życiowego bez utraty wykonanych dotychczas kroków. |
| | [`seq_pomocnik.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/seq_pomocnik.mmd) | Sekwencja (`sequenceDiagram`) | F-16..F-18: Zaproszenie asystenta/pomocnika, akceptacja, notatki, wspólne kroki i cofnięcie dostępu. |
| | [`seq_admin_procedury.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/seq_admin_procedury.mmd) | Sekwencja (`sequenceDiagram`) | F-19..F-25: Zarządzanie procedurami przez admina, wykrywanie cykli, weryfikacja aktualności danych. |
| | [`seq_wielojezycznosc.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/seq_wielojezycznosc.mmd) | Sekwencja (`sequenceDiagram`) | F-15: Ładowanie tłumaczeń z tabeli `tlumaczenia` z mechanizmem zastępczym (Fallback: PL ➔ EN). |
| **Maszyny stanów** | [`state_procedura.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/state_procedura.mmd) | Stan (`stateDiagram-v2`) | F-24..F-26: Cykl życia procedury: `aktualne` ➔ `do_sprawdzenia` ➔ `przestarzale`. |
| | [`state_krok_uzytkownika.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/state_krok_uzytkownika.mmd) | Stan (`stateDiagram-v2`) | F-07/F-12: Statusy kroku klienta: `zablokowany` ➔ `dostępny` ➔ `w_trakcie` ➔ `wykonany`. |
| | [`state_pomocnik.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/state_pomocnik.mmd) | Stan (`stateDiagram-v2`) | F-16: Cykl relacji pomocnika: `zaproszony` ➔ `aktywny` ➔ `cofnięty`. |
| | [`state_konto.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/state_konto.mmd) | Stan (`stateDiagram-v2`) | F-01/F-04: Cykl życia konta: `rejestracja` ➔ `aktywne` ➔ `zablokowane` ➔ `usunięte` (RODO). |
| **Algorytmy i logika** | [`flow_generowanie_planu.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_generowanie_planu.mmd) | Aktywność (`flowchart TD`) | Blokowy algorytm silnika grafu od ankiety po plan z blokadami i krokami równoległymi. |
| | [`flow_graf_zaleznosci.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_graf_zaleznosci.mmd) | Graf skierowany DAG | Konkretny przykład grafu procedur z kolorystyką stanów (wykonany, dostępny, zablokowany). |
| | [`flow_przypadki_brzegowe.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_przypadki_brzegowe.mmd) | Przepływ (`flowchart TD`) | Obsługa 6 przypadków brzegowych (cykle, brak języka, warunki OR, kroki historyczne itp.). |
| | [`flow_user_journey.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_user_journey.mmd) | Ścieżka (`flowchart TD`) | Kompletna ścieżka użytkownika (User Journey) od pierwszego wejścia na stronę po sukces. |
| **5 Scenariuszy MVP** | [`flow_scenariusz_student.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_scenariusz_student.mmd) | Scenariusz 1 (`flowchart TD`) | Student spoza UE: przyjęcie, wiza, meldunek, PESEL, ubezpieczenie, oświadczenie o pracy. |
| | [`flow_scenariusz_pracownik.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_scenariusz_pracownik.mmd) | Scenariusz 2 (`flowchart TD`) | Pracownik spoza UE: zezwolenie, wiza, przyjazd, meldunek, PESEL, karta pobytu, ZUS, NFZ. |
| | [`flow_scenariusz_ukraina.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_scenariusz_ukraina.mmd) | Scenariusz 3 (`flowchart TD`) | Obywatel Ukrainy: ochrona czasowa, PESEL UKR, powiadomienie PUP, 800+, szkoła dziecka. |
| | [`flow_scenariusz_ue_jdg.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_scenariusz_ue_jdg.mmd) | Scenariusz 4 (`flowchart TD`) | Obywatel UE: rejestracja pobytu UE, PESEL, CEIDG-1, zgłoszenie ZUS, US/VAT, konto firmowe. |
| | [`flow_scenariusz_polak.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_scenariusz_polak.mmd) | Scenariusz 5 (`flowchart TD`) | Powrót z zagranicy: dowód/paszport, meldunek, rezydencja podatkowa, ulga na powrót, NFZ, ZUS. |
| **Bezpieczeństwo i RODO** | [`flow_bezpieczenstwo.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/flow_bezpieczenstwo.mmd) | Bezpieczeństwo (`flowchart TD`) | 6 warstw ochrony: sanityzacja, Argon2id, HttpOnly/Secure, RBAC serwera, RODO, brak skanów. |
| **Harmonogram projektu** | [`gantt_etapy.mmd`](file:///home/toriy/in/ii/sql/dataplan/diagrams/gantt_etapy.mmd) | Harmonogram (`flowchart LR`) | 12-tygodniowy plan realizacji (120-150h) podzielony na 8 faz z kamieniami milowymi. |

---

## 🏛️ Główne filary projektu

### 1. Model Bazy Danych (`erd.mmd`)
Baza składa się z **32 tabel** zorganizowanych w 8 logicznych bloków:
- **Procedury (6):** `instytucje`, `oddzialy_instytucji`, `procedury`, `kroki_procedur`, `zaleznosci_procedur`, `reguly_dostepnosci`.
- **Dokumenty (3):** `dokumenty`, `procedura_dokument`, `miejsce_uzyskania`.
- **Scenariusze (2):** `sytuacje_zyciowe`, `procedury_w_sytuacji`.
- **Wielojęzyczność (3):** `jezyki`, `tlumaczenia`, `slownik_terminow`.
- **Aktualność i audyt (2):** `zrodla_oficjalne`, `dziennik_zmian`.
- **Użytkownicy i profil (4):** `uzytkownicy`, `profile`, `postep_uzytkownika`, `role`.
- **Słowniki (5):** `kraje`, `grupy_obywatelstwa`, `podstawy_pobytu`, `cele_pobytu`, `formy_zatrudnienia`.
- **Rozszerzenia (7):** `uprawnienia`, `role_uprawnienia`, `uzytkownik_role`, `pomocnicy`, `notatki_pomocnika`, `przypomnienia`, `dokumenty_uzytkownika`.

### 2. Silnik Grafu Zależności (`flow_generowanie_planu.mmd`, `class_plan_generator.mmd`)
- Baza przechowuje zależności w postaci grafu skierowanego DAG (`zaleznosci_procedur`).
- Silnik rekurencyjny CTE buduje kolejność procedur, weryfikując brak cykli (algorytm Tarjana / DFS).
- Warunki **AND / OR**: Procedura może wymagać spełnienia wszystkich poprzedników (AND) lub jednego z alternatywnych (OR).
- Statusy kroków: Krok otrzymuje status `zablokowany`, dopóki jego poprzedniki nie zostaną oznaczone jako `wykonany`.

### 3. Zapewnienie Jakości i Aktualności Danych (`state_procedura.mmd`, `seq_admin_procedury.mmd`)
- Każdy rekord posiada pola: `data_weryfikacji`, `osoba_weryfikujaca`, `interwal_przegladu_dni`, `link_zrodlo`.
- Po przekroczeniu interwału status procedury automatycznie przechodzi w `do_sprawdzenia`, a w interfejsie użytkownika pojawia się żółty baner ostrzegawczy.
- Każda zmiana w konfiguracji systemu jest zapisywana w tabeli `dziennik_zmian` (wartość przed i po).

---

## 🛠️ Jak przeglądać diagramy
Pliki `.mmd` można otworzyć:
1. W dowolnym edytorze z wtyczką Mermaid (np. VS Code, JetBrains).
2. Wklejając treść bezpośrednio do edytora online: [mermaid.live](https://mermaid.live).
3. Bezpośrednio w podglądzie Markdown wspieranym przez GitHub / GitLab / IDE.
