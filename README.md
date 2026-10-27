# Nawigator procedur administracyjnych

## 1. Cel i kontekst
**Problem. Informacje są rozproszone po wielu serwisach, często dostępne tylko po polsku,**
a użytkownik nie wie, w jakiej kolejności załatwiać sprawy. Pomyłki kosztują: odrzucony wniosek, utracony termin, zaległe składki.
**Cel. Użytkownik opisuje swoją sytuację życiową, a system w jego języku generuje plan**
kroków, listę dokumentów i odnośniki do oficjalnych źródeł.
**Pozycjonowanie. System działa obok mObywatela, a nie zamiast niego. Odpowiada na**
pytanie „co i w jakiej kolejności”, a mObywatel i urzędy na pytanie „jak to złożyć”.
**Miary sukcesu.**
- odsetek użytkowników, którzy kończą plan,
- krok, na którym użytkownicy najczęściej przerywają,
- odsetek procedur o statusie „aktualne”.
## 2. Dla kogo
System jest uniwersalny i nie dzieli ludzi według kraju pochodzenia. Reguły opierają się na trzech osiach: narodowość (obywatelstwo), podstawa pobytu i cel pobytu.
**Grupy docelowe:**
- obywatele krajów spoza UE (pracownicy, studenci, członkowie rodzin, przedsiębiorcy),
- obywatele Ukrainy (odrębne przepisy specjalne),
- obywatele UE/EOG,
- osoby z polskimi korzeniami,
- Polacy wracający z zagranicy oraz młodzi ludzie przy pierwszej pracy,
- pośrednicy: pracodawcy, biura karier uczelni, organizacje pomocowe.
**Przykładowe persony:**
- Student z Nepalu – potrzebuje zezwolenia na pobyt, ubezpieczenia i informacji o pracy
w trakcie studiów.
- Pracownik z Indii – potrzebuje kolejności: wiza, karta pobytu, PESEL, ZUS, NFZ.
- Ukrainka z dzieckiem – potrzebuje PESEL, świadczeń i zapisu do szkoły.
- Niemiec zakładający JDG – potrzebuje rejestracji pobytu, CEIDG i ZUS dla
przedsiębiorców.
- Polak wracający z Irlandii – potrzebuje zameldowania, NFZ i rozliczenia podatkowego.
## 3. Zakres
**W zakresie:**
konta użytkowników i profil z obowiązkową narodowością,
- generowanie planu działania z grafu zależności między procedurami,
- listy dokumentów i śledzenie postępu,
- wielojęzyczność (PL, EN, RU),
- wyszukiwarka i słownik terminów urzędowych,
- panel administratora z dziennikiem zmian,
- mechanizm aktualności danych (źródło, data weryfikacji, status).
**Poza zakresem:**
- składanie wniosków w imieniu użytkownika,
- przechowywanie skanów i numerów dokumentów (PESEL, paszport, numer karty
pobytu),
- integracja z mObywatelem i systemami państwowymi (system tylko linkuje),
- porady prawne. System ma charakter informacyjny.
## 4. Role użytkowników
Role zapisane są w tabeli ról, a uprawnienia sprawdzane po stronie serwera przy każdym żądaniu. Ukrycie przycisku w interfejsie nie jest zabezpieczeniem.
## 4.1. Gość (użytkownik niezarejestrowany)
Aktor bez konta, więc nie jest rolą w bazie.
- Może: przeglądać procedury i opisy, sprawdzać wymagane dokumenty, korzystać z
wyszukiwarki i słownika, zmieniać język, rejestrować się i logować, wypełnić ankietę i zobaczyć przykładowy plan.
- Nie może: zapisywać postępu ani profilu.
- Cel: obniżyć próg wejścia. Osoba, która dopiero przyjechała, nie musi od razu zakładać
konta.
## 4.2. Klient (użytkownik zarejestrowany)
- Może: uzupełniać i zmieniać profil (narodowość, podstawa pobytu, cel pobytu, forma
zatrudnienia, język), wybierać sytuację życiową, generować plan, oznaczać posiadane dokumenty i wykonane kroki, zapisywać postęp, zapraszać pomocnika i cofać jego dostęp, usunąć konto wraz z danymi.
- Nie może: edytować treści systemu ani widzieć danych innych użytkowników.
- Wymaganie: narodowość jest polem obowiązkowym. Na jej podstawie system
wyznacza grupę obywatelstwa i dobiera dostępne procedury.
## 4.3. Pomocnik (rola opcjonalna)
Osoba lub organizacja wspierająca klientów: wolontariusz, doradca biura karier, asystent organizacji pomocowej.
- Może: widzieć plan i postęp wyłącznie tych klientów, którzy go zaprosili i
zaakceptowali dostęp, dodawać notatki do kroków, oznaczać krok jako wykonany wspólnie z klientem.
- Nie może: widzieć e-maila i hasła klienta, edytować treści systemu, widzieć klientów
bez ich zgody.
- Zasada: klient może cofnąć dostęp w każdej chwili. Każde działanie pomocnika jest
oznaczone w dzienniku.
## 4.4. Redaktor treści (rola opcjonalna)
- Może: edytować procedury, dokumenty, tłumaczenia i źródła, oznaczać procedury jako
zweryfikowane.
- Nie może: zarządzać kontami i rolami ani zmieniać konfiguracji systemu.
- Cel: odciążyć administratora i oddzielić pracę nad treścią od administrowania.
## 4.5. Administrator
- Może: wszystko to, co redaktor, oraz zarządzać kontami (blokowanie, nadawanie i
odbieranie ról), przeglądać dziennik zmian, konfigurować słowniki (kraje, języki, podstawy i cele pobytu), zarządzać zależnościami i regułami dostępności.
- Nie może: odczytywać haseł (przechowywane są wyłącznie w postaci skrótu).
## 5. Funkcjonalności
### A. Konta i profil
- **F-01** Rejestracja i logowanie. E-mail i hasło, hasło zapisane jako skrót, zgoda na
przetwarzanie danych. Kryterium: nie da się założyć dwóch kont na ten sam e-mail.
- **F-02** Profil. Narodowość (obowiązkowa), podstawa pobytu, cel pobytu, forma
zatrudnienia, język. Kryterium: rejestracja nie kończy się bez narodowości.
- **F-03** Zmiana profilu. Po zmianie plan przelicza się z zachowaniem wykonanych kroków.
- **F-04** Usunięcie konta wraz z danymi osobowymi.
### B. Plan i procedury
- **F-05** Wybór sytuacji życiowej (np. „zaczynam pracę”, „studiuję”, „zakładam
działalność”).
- **F-06** Generowanie planu. System wybiera procedury dla sytuacji, filtruje je regułami
dopasowanymi do narodowości, podstawy i celu pobytu, a następnie porządkuje według zależności.
- **F-07** Blokowanie kroków. Krok jest niedostępny, dopóki nie wykonano wymaganych
wcześniej.
- **F-08** Kroki równoległe. Niezależne kroki pokazane są jako możliwe w dowolnej
kolejności.
- **F-09** Karta procedury. Opis, termin, koszt, instytucja, sposób złożenia, link do źródła,
data ostatniej weryfikacji.
### C. Dokumenty i postęp
- **F-10** Lista dokumentów dla każdego kroku: co potrzebne, gdzie uzyskać, czy wymaga
tłumaczenia przysięgłego, czy ma datę ważności.
- **F-11** Oznaczanie posiadanych dokumentów. Plan pomija kroki, których użytkownik nie
musi już wykonywać.
- **F-12** Śledzenie postępu. Odznaczanie kroków i procent ukończenia.
### D. Wyszukiwanie i język
- **F-13** Wyszukiwarka procedur, dokumentów i terminów.
- **F-14** Słownik terminów urzędowych (polski termin, tłumaczenie, wyjaśnienie).
- **F-15** Zmiana języka w dowolnym momencie, z zastępczym językiem (PL lub EN), gdy
brakuje tłumaczenia.
### E. Pomocnik
- **F-16** Zaproszenie pomocnika kodem lub e-mailem, akceptacja i cofnięcie dostępu.
- **F-17** Lista podopiecznych z postępem i miejscami, w których utknęli.
- **F-18** Notatki do kroków, widoczne dla klienta.
### F. Administracja
- **F-19** Zarządzanie danymi: instytucje, procedury, dokumenty, scenariusze.
- **F-20** Edycja zależności i reguł dostępności.
- **F-21** Zarządzanie tłumaczeniami.
- **F-22** Zarządzanie kontami i rolami.
- **F-23** Dziennik zmian: co, kto, kiedy, jaka była stara i nowa wartość.
### G. Aktualność danych
- **F-24** Metadane rekordu: źródło, data weryfikacji, osoba weryfikująca, interwał
przeglądu, status (aktualne, do sprawdzenia, przestarzałe).
- **F-25** Lista „do sprawdzenia” w panelu administratora oraz przycisk „zweryfikowano”.
- **F-26** Baner ostrzegawczy przy procedurze ze statusem „do sprawdzenia”.
## 6. Cechy wyróżniające
1. Graf zależności między procedurami. Rdzeń techniczny: zapytanie rekurencyjne
buduje kolejność kroków.
2. Reguły według narodowości, podstawy i celu pobytu. Nowa grupa użytkowników to
nowy wiersz w danych, a nie zmiana kodu.
3. Warunki AND i OR. Dokument A lub B może wystarczyć do spełnienia kroku.
4. Przeliczanie planu po zmianie statusu. Student, który zaczyna pracę, nie zaczyna od
zera.
5. Wykrywanie cykli w zależnościach przy zapisie przez administratora.
6. Przejrzysta aktualność danych. Każdy rekord ma źródło i datę weryfikacji.
7. Wielojęzyczność z mechanizmem zastępczym.
8. Pomocnik wyłącznie za zgodą klienta.
9. Minimalizacja danych. System nie zbiera numerów dokumentów ani skanów.
## 7. Scenariusze życiowe
Poniższe ścieżki pokazują kształt danych. Szczegóły przepisów (terminy, opłaty, nazwy formularzy) należy zweryfikować w oficjalnych źródłach przed wpisaniem do bazy.
**Scenariusze MVP (pięć):**
1. Student spoza UE: przyjęcie na uczelnię, zezwolenie na pobyt w celu nauki,
ubezpieczenie, PESEL, praca w trakcie studiów.
2. Pracownik spoza UE: umowa lub oświadczenie pracodawcy, wiza, przyjazd, karta
pobytu, PESEL, ZUS i NFZ.
3. Obywatel Ukrainy: PESEL, świadczenia, szkoła dla dziecka, ubezpieczenie.
4. Obywatel UE zakładający JDG: rejestracja pobytu, CEIDG, ZUS dla przedsiębiorców,
urząd skarbowy.
5. Polak wracający z zagranicy: zameldowanie, NFZ, rozliczenie podatkowe, ZUS.
**Scenariusze rozwojowe: utrata pracy, narodziny dziecka, małżonek obywatela Polski,**
wygasająca karta pobytu.
**Przypadki brzegowe, które system musi obsłużyć:**
zmiana statusu w trakcie (student zaczyna pracę), alternatywy w wymaganiach (A lub B), krok wykonany przed użyciem systemu, procedura niedostępna dla danej grupy, błędna zależność cykliczna wprowadzona przez administratora, kroki równoległe, terminy liczone od daty zdarzenia (np. od dnia przyjazdu), brak tłumaczenia na wybrany język.
## 8. Model danych
Podstawa to 20 tabel w pięciu blokach. Narodowość klienta wiąże profil ze słownikiem krajów, a każdy kraj ma przypisaną grupę obywatelstwa. Procedury (6): instytucje, oddziały instytucji, procedury, kroki procedur, zależności między procedurami, reguły dostępności. Dokumenty (3): dokumenty (z flagami: ma datę ważności, wymaga tłumaczenia przysięgłego), powiązanie procedura–dokument, miejsce uzyskania dokumentu. Scenariusze (2): sytuacje życiowe, procedury w sytuacji z kolejnością. Wielojęzyczność i słowniki (3): języki, tłumaczenia, słownik terminów. Aktualność (2): źródła oficjalne, dziennik zmian. Użytkownicy (4): użytkownicy, profile, postęp i dokumenty użytkownika, role. Rozszerzenia (opcjonalnie): uprawnienia i powiązanie ról z uprawnieniami, przypisania pomocników i ich notatki, przypomnienia o terminach, osobna tabela grup warunków AND/OR. Po dodaniu uprawnień baza ma 22 tabele, ze wszystkimi rozszerzeniami do 25. Każda tabela ma uzasadnienie funkcjonalne. Nie dodajemy tabel wyłącznie po to, aby osiągnąć liczbę.
## 9. Wymagania niefunkcjonalne
- Bezpieczeństwo: hasła jako skróty (Argon2id lub bcrypt), sesje w ciasteczkach
HttpOnly i Secure, zapytania z parametrami (ochrona przed SQL injection), ograniczenie prób logowania, komunikat logowania nieujawniający, czy błędny jest e- mail czy hasło.
- RODO: zgoda przy rejestracji, minimalizacja danych, prawo do usunięcia konta, brak
numerów dokumentów i skanów w bazie.
- Dostępność i użyteczność: prosty język, duży kontrast, działanie na telefonie (część
użytkowników ma tylko telefon).
- Wydajność: wygenerowanie planu w czasie poniżej kilku sekund dla scenariuszy MVP.
- Utrzymanie: nowe procedury, grupy i języki dodawane przez dane, bez zmian w kodzie.
- Komunikat prawny: stała informacja, że system jest informacyjny i nie zastępuje
oficjalnych źródeł ani porady prawnej.
## 10. Dane i źródła
- Słowniki: kraje z grupą obywatelstwa, języki, podstawy i cele pobytu, formy
zatrudnienia, role.
- Instytucje: około 15-25, adresy i godziny dla jednego-dwóch miast.
- Procedury: około 25-40 dla pięciu scenariuszy.
- Zależności i reguły: około 40-80 wierszy.
- Dokumenty: około 30-50.
- Treści wielojęzyczne: minimum dwa języki, słownik około 50-100 terminów.
- Źródła publiczne: gov.pl, biznes.gov.pl, strony Urzędu do Spraw Cudzoziemców, ZUS i
NFZ, zbiory dane.gov.pl, strony urzędów. Przepisów nie kopiujemy, wystarczy własne streszczenie i link.
## 11. Etapy realizacji
Założenie: jedna osoba, około 10-12 godzin tygodniowo, razem około 120-150 godzin (10-12 tygodni).
1. Analiza i projekt (15 h): wymagania, scenariusze, diagram ERD, makiety.
2. Baza danych (12 h): schemat, klucze, indeksy, zapytanie rekurencyjne po grafie.
3. Zbieranie danych (25 h): pięć scenariuszy, procedury, dokumenty, źródła.
4. Backend (30 h): logowanie, profil, generowanie planu, lista kontrolna, API.
5. Frontend (25 h): ekrany użytkownika, wielojęzyczność, wyszukiwarka.
6. Panel administratora (15 h): zarządzanie danymi, tłumaczenia, dziennik zmian.
7. Testy (10 h): logika grafu i scenariusze.
8. Dokumentacja i prezentacja (10 h).
**Kamienie milowe:**
- tygodnie 1-2: zatwierdzone wymagania i ERD,
- tygodnie 3-6: pionowy plasterek, czyli jeden scenariusz od bazy po ekran użytkownika,
- tygodnie 7-9: pozostałe cztery scenariusze i panel administratora,
- tygodnie 10-12: testy, dokumentacja, prezentacja.
- Jeśli zabraknie czasu, ograniczamy w tej kolejności: słownik terminów, wyszukiwarka,
role dodatkowe, trzeci język, liczba scenariuszy z pięciu do trzech. Nie ograniczamy: generowania planu z grafu, listy kontrolnej i panelu administratora.
## 12. Ryzyka
- Nieaktualne dane. Źródło i data przy każdym rekordzie, lista „do sprawdzenia”,
interwały przeglądu.
- Zbyt szeroki zakres. Pionowy plasterek najpierw, pięć scenariuszy w MVP.
- Praca nad danymi jest dłuższa niż kodowanie. Zbieranie danych zaczynamy od
pierwszego tygodnia.
- Błąd w procedurze szkodzi użytkownikowi. Dane wpisywane ręcznie i sprawdzane,
komunikat o charakterze informacyjnym.
- Dane wrażliwe (narodowość). Zgoda, minimalizacja, możliwość usunięcia konta.
- Cykle w zależnościach. Walidacja przy zapisie.
## 13. Kryteria odbioru
Klient rejestruje się, podaje narodowość i otrzymuje poprawny plan dla każdego z pięciu scenariuszy. Zmiana profilu przelicza plan bez utraty wykonanych kroków. Kroki wymagające poprzednich są zablokowane. Interfejs działa w co najmniej dwóch językach. Administrator dodaje procedurę, zależność i tłumaczenie bez zmiany kodu, a zmiana trafia do dziennika. Rekord ze starą datą weryfikacji pojawia się na liście „do sprawdzenia”. Próba zapisu cyklu w zależnościach jest zablokowana. Użytkownik bez uprawnień nie ma dostępu do funkcji administracyjnych (sprawdzane na serwerze). Baza liczy co najmniej 20 tabel z udokumentowanymi relacjami (diagram ERD).
## 14. Rozwój po MVP
- przypomnienia o terminach (np. wygasająca karta pobytu),
- mapa urzędów z godzinami i rezerwacją online,
- automatyczne wykrywanie zmian na stronach źródłowych (porównanie skrótów
treści),
- generator wzorów wniosków z opisem pól,
- konta organizacji partnerskich ze statystykami zbiorczymi,
- kolejne języki i scenariusze.
