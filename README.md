# Nawigator po procedurach administracyjnych w Polsce

Projekt bazy danych: system informacyjny, który prowadzi użytkownika przez polskie procedury urzędowe.

## 1. Cel systemu

Informacje o ZUS, NFZ, urzędach miasta czy urzędzie wojewódzkim są rozproszone po wielu stronach, często dostępne tylko po polsku, a przede wszystkim nie wiadomo, w jakiej kolejności załatwiać sprawy.

System zbiera te informacje w jednym miejscu. Użytkownik opisuje swoją sytuację, a system buduje dla niego plan krok po kroku: co zrobić, w jakiej kolejności, jakie dokumenty przygotować i gdzie je uzyskać.

System nie składa wniosków i nie przechowuje dokumentów. W odpowiednim momencie odsyła do oficjalnych serwisów (mObywatel, ZUS, gov.pl).

## 2. Rodzaje użytkowników

| Użytkownik | Kim jest | Co może |
|---|---|---|
| **Gość** | osoba bez konta | przegląda procedury, korzysta z wyszukiwarki i słownika terminów, może się zarejestrować |
| **Klient** | zarejestrowany użytkownik, główny odbiorca systemu | dostaje własny plan działania i zapisuje postęp |
| **Pomocnik** | np. pracownik biura karier uczelni, wolontariusz organizacji pomocowej | prowadzi klientów, którzy sami dali mu dostęp |
| **Administrator** | osoba odpowiedzialna za dane | zarządza procedurami, dokumentami, tłumaczeniami i kontami |

Klientem może być każdy, kto załatwia sprawy w Polsce: obywatel UE, obywatel Ukrainy, osoba spoza Europy (np. student z Nepalu, pracownik z Indii), a także Polak wracający z zagranicy.

## 3. Narodowość użytkownika

Każdy klient podaje w profilu narodowość, czyli wybiera z listy kraj obywatelstwa. W bazie każdy kraj jest przypisany do grupy: **Polska**, **UE/EOG**, **Ukraina** albo **pozostałe kraje**. Reguły systemu opierają się na tych grupach, więc dodanie nowego kraju to jeden nowy wiersz w tabeli, a nie zmiana kodu.

Sama narodowość nie wystarcza, dlatego profil zawiera jeszcze:

- **podstawę pobytu**: brak wymogu, wiza, zezwolenie na pobyt czasowy, status specjalny;
- **cel pobytu**: praca, nauka, rodzina, działalność gospodarcza.

Dopiero te trzy dane razem decydują, które procedury dotyczą danej osoby. Na przykład obywatel Niemiec i obywatel Indii, którzy zaczynają pracę, dostaną różne plany.

## 4. Czynności klienta (od ogólnych do szczegółowych)

**Ogólnie:** klient chce się dowiedzieć, co musi załatwić w urzędach, i przejść przez to krok po kroku.

1. **Opisuje swoją sytuację**
   - zakłada konto (e-mail, hasło, język),
   - uzupełnia profil: narodowość, podstawa i cel pobytu, forma zatrudnienia,
   - wybiera sytuację życiową, np. „zaczynam pracę”, „studiuję”, „zakładam JDG”.
2. **Otrzymuje plan działania**
   - widzi kroki w odpowiedniej kolejności, np. PESEL → rachunek bankowy → ZUS → NFZ,
   - kroki, które wymagają wcześniejszych etapów, są zablokowane do czasu ich wykonania,
   - przy każdym kroku otwiera kartę procedury: opis, termin, koszt, urząd, link do źródła.
3. **Realizuje plan**
   - sprawdza listę wymaganych dokumentów i zaznacza te, które już ma,
   - oznacza wykonane kroki, a system zapisuje postęp,
   - gdy jego sytuacja się zmieni (np. student zaczyna pracę), plan jest przeliczany, a wykonane kroki zostają.
4. **Zarządza kontem**
   - zmienia język interfejsu (PL / EN / RU / UA),
   - zaprasza pomocnika i w każdej chwili może cofnąć mu dostęp,
   - edytuje profil albo usuwa konto razem z danymi (RODO).

## 5. Funkcjonalności systemu

- **Dostępne dla wszystkich:** przeglądanie procedur, wyszukiwarka, słownik terminów urzędowych z tłumaczeniem, wybór języka.
- **Dla klienta:** profil, generowanie planu na podstawie zależności między procedurami, dopasowanie kroków do profilu, lista dokumentów, śledzenie postępu.
- **Dla pomocnika:** lista podopiecznych z ich postępem, notatki do kroków.
- **Dla administratora:** zarządzanie instytucjami, procedurami, dokumentami, zależnościami i tłumaczeniami; aktualizacja źródeł i dat weryfikacji; dziennik zmian; zarządzanie kontami i rolami.
- **Systemowe:** blokada cykli w zależnościach (A wymaga B, B wymaga A), oznaczanie procedur „do sprawdzenia” po upływie terminu weryfikacji, haszowanie haseł, kontrola uprawnień po stronie serwera.

## 6. Zbiory danych

| Zbiór danych | Co zawiera |
|---|---|
| **Słowniki** | kraje z przypisaną grupą obywatelstwa, podstawy pobytu, cele pobytu, formy zatrudnienia, języki |
| **Instytucje** | ZUS, NFZ, urzędy miasta, skarbowe i wojewódzkie, CEIDG, uczelnie; adresy i godziny pracy |
| **Procedury** | opis, termin, opłata, instytucja, sposób załatwienia (online / osobiście) |
| **Zależności i reguły** | „przed X trzeba wykonać Y” oraz dla jakiej kombinacji narodowości, podstawy i celu pobytu procedura jest wymagana; **to serce systemu** |
| **Dokumenty** | paszport, karta pobytu, umowa, zaświadczenia; który dokument jest potrzebny do której procedury i gdzie go uzyskać |
| **Sytuacje życiowe** | uporządkowane zestawy procedur, np. „student spoza UE” |
| **Tłumaczenia** | nazwy i opisy w kilku językach, słownik terminów urzędowych |
| **Źródła i aktualność** | link do oficjalnej strony, data ostatniej weryfikacji, dziennik zmian |
| **Dane użytkowników** | konta, role, profile, postęp, przypisania pomocników |

Dane pochodzą z oficjalnych, publicznych źródeł: gov.pl, biznes.gov.pl, zus.pl, nfz.gov.pl, migracje.gov.pl. Przy każdej procedurze zapisujemy źródło i datę weryfikacji, bo przepisy często się zmieniają. Całość to około 20 tabel.

**Zakres MVP:** 5 sytuacji życiowych (student spoza UE, pracownik spoza UE, obywatel Ukrainy, obywatel UE zakładający JDG, Polak wracający z zagranicy), 2 języki i panel administratora.
