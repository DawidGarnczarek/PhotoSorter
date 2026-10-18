# Specyfikacja aplikacji do sortowania zdjęć

**Nazwa robocza:** Photo Sorter
**Platforma:** macOS
**Język programowania:** Python 3.12+
**Framework GUI:** PySide6 (Qt for Python)
**Wersja dokumentu:** 1.0
**Status:** Specyfikacja do implementacji

---

## 1. Cel projektu

Celem jest stworzenie prostej, szybkiej i wygodnej aplikacji desktopowej do ręcznej selekcji zdjęć.

Aplikacja ma umożliwiać przeglądanie zdjęć znajdujących się w wybranym folderze, kopiowanie wybranych zdjęć do folderu docelowego za pomocą klawiatury oraz przenoszenie niepożądanych zdjęć do systemowego kosza.

Interfejs ma być maksymalnie prosty. Użytkownik powinien móc wykonać większość operacji bez używania myszy.

Program musi działać lokalnie na komputerze użytkownika. Nie może przesyłać zdjęć do internetu ani korzystać z usług chmurowych.

### Główne założenia

1. Użytkownik wybiera folder źródłowy.
2. Użytkownik wybiera folder docelowy.
3. Aplikacja skanuje folder źródłowy oraz wszystkie jego podfoldery.
4. Zdjęcia są wyświetlane pojedynczo w dużym obszarze podglądu.
5. Spacja kopiuje aktualne zdjęcie do folderu docelowego i przechodzi do następnego.
6. Backspace przenosi aktualne zdjęcie do systemowego kosza i wyświetla następne.
7. Strzałki lewo/prawo pozwalają przeglądać zdjęcia bez wykonywania operacji na plikach.
8. Podgląd zawiera nazwę aktualnego pliku i licznik zdjęć w formacie `12 / 248`.
9. Zdjęcia muszą być wyświetlane z zachowaniem proporcji.
10. Aplikacja umożliwia powiększanie zdjęć kółkiem myszy.
11. Aplikacja obsługuje tryb pełnoekranowy.
12. Program nie wymaga cofania operacji.

---

## 2. Zakres funkcjonalny

### 2.1. Wybór folderu źródłowego

Użytkownik wybiera folder zawierający zdjęcia do przeglądania.

Wymagania:

- Wybór folderu za pomocą systemowego okna dialogowego macOS.
- Możliwość zmiany folderu w dowolnym momencie.
- Rekurencyjne przeszukiwanie wszystkich podfolderów.
- Wczytywanie wyłącznie obsługiwanych formatów.
- Ignorowanie plików ukrytych oraz typowych plików systemowych macOS.
- Sortowanie listy zdjęć według ścieżki względnej w kolejności alfabetycznej, bez rozróżniania wielkości liter.
- Obsługa dużej liczby zdjęć bez konieczności jednoczesnego dekodowania wszystkich plików.

Obsługiwane rozszerzenia:

- `.jpg`
- `.jpeg`
- `.png`
- `.heic`
- `.tif`
- `.tiff`

Rozszerzenia należy rozpoznawać bez rozróżniania wielkości liter.

Program powinien dodatkowo sprawdzać, czy plik można faktycznie odczytać jako obraz. Samo rozszerzenie nie gwarantuje prawidłowego formatu.

### 2.2. Wybór folderu docelowego

Użytkownik wybiera folder, do którego będą kopiowane zaakceptowane zdjęcia.

Wymagania:

- Wybór folderu przez systemowy dialog macOS.
- Wyświetlanie pełnej ścieżki folderu docelowego.
- Możliwość zmiany folderu podczas działania programu.
- Sprawdzenie, czy folder istnieje i jest zapisywalny.
- Folder docelowy nie może znajdować się wewnątrz folderu źródłowego ani być równy folderowi źródłowemu.

Jeżeli użytkownik wybierze nieprawidłową lokalizację, aplikacja ma wyświetlić czytelny komunikat i nie wykonywać operacji na plikach.

**Ważne:** zmiana folderu źródłowego lub docelowego nie może po cichu powodować kopiowania zdjęć do innego miejsca niż wybrane przez użytkownika.

### 2.3. Kopiowanie zdjęcia

Po naciśnięciu spacji aplikacja wykonuje następujące czynności:

1. Sprawdza, czy wybrane jest aktualne zdjęcie.
2. Sprawdza, czy folder docelowy jest dostępny i zapisywalny.
3. Wyznacza nazwę pliku docelowego.
4. Sprawdza, czy plik o takiej nazwie już istnieje.
5. Jeżeli plik nie istnieje, kopiuje zdjęcie do folderu docelowego.
6. Po pomyślnym zakończeniu kopiowania przechodzi do następnego zdjęcia.
7. Aktualizuje licznik oraz nazwę pliku w interfejsie.

Kopiowanie ma zachowywać oryginalny plik w folderze źródłowym.

Nie należy zmieniać zawartości zdjęcia, kompresować go ponownie ani konwertować do innego formatu. Kopiowany ma być oryginalny plik bajt po bajcie.

#### Zachowanie struktury folderów

Jeżeli zdjęcia znajdują się w podfolderach, program powinien zachowywać ich strukturę względną w folderze docelowym.

Przykład:

Źródło:

`/Users/user/Photos/Wakacje/2025/gory.jpg`

Folder źródłowy:

`/Users/user/Photos`

Folder docelowy:

`/Users/user/Selected`

Wynik:

`/Users/user/Selected/Wakacje/2025/gory.jpg`

Pozwala to uniknąć konfliktów nazw i zachować informację o pochodzeniu zdjęcia.

Foldery docelowe tworzone automatycznie muszą odpowiadać wyłącznie bezpiecznym ścieżkom względnym wyliczonym względem folderu źródłowego. Nie wolno pozwolić, aby ścieżka docelowa wychodziła poza wybrany folder docelowy.

#### Konflikt nazw

Jeżeli plik docelowy już istnieje:

- Nie nadpisuj go.
- Nie usuwaj istniejącego pliku.
- Nie dopisuj automatycznie numeru do nazwy.
- Nie zmieniaj nazwy pliku źródłowego.
- Wyświetl komunikat informujący o konflikcie.
- Pozostań na aktualnym zdjęciu, aby użytkownik mógł zdecydować, co zrobić.
- Nie zwiększaj licznika wykonanych kopii.

Program nie powinien zakładać, że dwa pliki o tej samej nazwie są identyczne.

#### Bezpieczne kopiowanie

Kopiowanie powinno odbywać się atomowo z perspektywy widoczności pliku docelowego:

1. Zapisz dane do tymczasowego pliku w tym samym folderze docelowym.
2. Zweryfikuj, czy kopiowanie zakończyło się prawidłowo.
3. Opublikuj plik pod nazwą docelową bez nadpisywania istniejącego pliku.
4. Usuń plik tymczasowy po błędzie.

Jeżeli operacja się nie powiedzie, nie przechodź do następnego zdjęcia.

Operacje na dużych plikach nie mogą blokować interfejsu. Należy wykonywać je w zadaniu roboczym lub wątku roboczym.

### 2.4. Usuwanie zdjęcia

Po naciśnięciu Backspace aplikacja przenosi aktualne zdjęcie do systemowego kosza macOS.

Nie wolno zastępować tej operacji trwałym usunięciem przez `os.remove()` lub `Path.unlink()`.

Wymagania:

- Korzystanie z mechanizmu kosza systemowego, np. przez bibliotekę `send2trash`.
- Sprawdzenie, czy plik nadal istnieje.
- Obsługa błędów uprawnień, blokad pliku i niedostępności lokalizacji.
- Po sukcesie przejście do następnego zdjęcia.
- Po błędzie pozostanie na aktualnym zdjęciu i wyświetlenie komunikatu.
- Usunięcie pliku z bieżącej listy po pomyślnym przeniesieniu go do kosza.
- Aktualizacja licznika zdjęć.

Przeniesienie do kosza ma dotyczyć wyłącznie aktualnego pliku, a nie całego folderu ani wszystkich jego kopii.

Jeżeli aplikacja nie może przenieść pliku do kosza, nie powinna automatycznie próbować usuwać go trwale.

### 2.5. Nawigacja pomiędzy zdjęciami

Obsługa klawiatury:

| Klawisz     | Działanie                                               |
| ----------- | ------------------------------------------------------- |
| `←`         | Poprzednie zdjęcie                                      |
| `→`         | Następne zdjęcie                                        |
| `Spacja`    | Kopiuj aktualne zdjęcie i przejdź dalej                 |
| `Backspace` | Przenieś aktualne zdjęcie do kosza i przejdź dalej      |
| `F`         | Włącz/wyłącz pełny ekran                                |
| `Esc`       | Wyjdź z pełnego ekranu lub zamknij aktywne powiększenie |

Jeżeli system macOS lub układ klawiatury mapuje klawisz usuwania w inny sposób, należy zapewnić prawidłową obsługę klawisza Backspace, zwykle reprezentowanego w Qt jako `Qt.Key_Backspace`.

W razie potrzeby można dodać opcjonalny skrót `Fn + Delete` lub `Delete`, ale nie powinien on powodować podwójnego wykonania operacji.

#### Zasady przechodzenia pomiędzy zdjęciami

- Strzałka w lewo na pierwszym zdjęciu nie zmienia aktualnego zdjęcia.
- Strzałka w prawo na ostatnim zdjęciu nie zmienia aktualnego zdjęcia.
- Program nie zapętla listy.
- Spacja i Backspace przechodzą do następnego zdjęcia po udanej operacji.
- Nieudana operacja nie powoduje przejścia do kolejnego zdjęcia.
- Jeśli usunięto ostatnie zdjęcie na liście, wyświetl poprzednie zdjęcie.
- Jeśli lista jest pusta, wyświetl ekran informujący o braku zdjęć.

### 2.6. Licznik zdjęć

W obszarze podglądu musi znajdować się licznik w formacie:

`12 / 248`

Pierwsza liczba oznacza pozycję aktualnego zdjęcia na liście, a druga liczbę zdjęć dostępnych w bieżącej sesji.

Numeracja rozpoczyna się od 1.

Licznik należy aktualizować po:

- zmianie zdjęcia;
- skopiowaniu zdjęcia;
- przeniesieniu zdjęcia do kosza;
- zmianie folderu źródłowego;
- ponownym przeskanowaniu folderu.

Po usunięciu zdjęcia z listy liczba wszystkich zdjęć musi zostać zmniejszona.

Jeśli nie wybrano zdjęcia, licznik może wyświetlać `0 / 0`.

### 2.7. Nazwa pliku

Nazwa aktualnie wyświetlanego pliku powinna być widoczna bezpośrednio pod zdjęciem lub nad nim.

Wymagania:

- Wyświetlanie pełnej nazwy wraz z rozszerzeniem.
- Długie nazwy nie mogą rozpychać interfejsu.
- Nazwa może zostać skrócona wizualnie, ale po najechaniu myszą powinna być dostępna pełna nazwa.
- Nie należy mylić nazwy pliku z jego pełną ścieżką.
- W razie potrzeby pełną ścieżkę można pokazać w podpowiedzi.

### 2.8. Podgląd zdjęć

Podgląd powinien zajmować największą część okna.

Wymagania:

- Dopasowanie obrazu do dostępnej przestrzeni.
- Zachowanie oryginalnych proporcji.
- Brak rozciągania i deformacji.
- Brak obcinania obrazu w domyślnym trybie dopasowania.
- Właściwa obsługa zdjęć pionowych i poziomych.
- Wyświetlanie dużych zdjęć bez konieczności zmiany rozmiaru oryginalnego pliku.
- Obsługa orientacji EXIF.
- Obsługa profili kolorów w zakresie możliwości użytej biblioteki.
- Wyświetlanie komunikatu, gdy plik nie może zostać odczytany jako obraz.

Program nie powinien wczytywać wszystkich pełnowymiarowych obrazów jednocześnie do pamięci.

Należy ładować i dekodować obraz dopiero wtedy, gdy jest potrzebny, z możliwością buforowania miniatur sąsiednich zdjęć.

### 2.9. Powiększanie zdjęć

Użytkownik może powiększać i pomniejszać zdjęcie za pomocą kółka myszy.

Wymagania:

- Kółko w górę powiększa obraz.
- Kółko w dół pomniejsza obraz.
- Powiększanie nie może modyfikować oryginalnego pliku.
- Powiększenie nie może powodować zmiany rozmiaru okna.
- Należy ustalić minimalny i maksymalny poziom powiększenia.
- Zalecany minimalny poziom: dopasowanie do okna.
- Zalecany maksymalny poziom: 8× względem rozmiaru obrazu dopasowanego do okna.
- Przy powiększeniu większym niż obszar widoku należy umożliwić przesuwanie obrazu.
- Po przejściu do następnego zdjęcia należy wrócić do domyślnego dopasowania.

Przy poziomie dopasowania do okna zdjęcie musi być widoczne w całości. Po powiększeniu użytkownik może oglądać szczegóły obrazu.

### 2.10. Tryb pełnoekranowy

Aplikacja powinna umożliwiać pracę w trybie pełnoekranowym.

Wymagania:

- Skrót `F` włącza lub wyłącza pełny ekran.
- `Esc` wychodzi z pełnego ekranu.
- Podgląd zdjęcia nadal zajmuje większość dostępnego miejsca.
- Nazwa pliku i licznik pozostają widoczne.
- Wszystkie skróty klawiaturowe działają również w pełnym ekranie.
- Po wyjściu z pełnego ekranu aplikacja wraca do poprzedniego rozmiaru okna.

---

## 3. Projekt interfejsu

### 3.1. Układ głównego okna

Interfejs powinien być prosty, minimalistyczny i dostosowany do macOS.

Proponowany układ:

```text
┌─────────────────────────────────────────────────────────────┐
│ Photo Sorter                                                 │
├─────────────────────────────────────────────────────────────┤
│ Źródło:  [Wybierz folder...]  /Users/.../Photos              │
│ Cel:     [Wybierz folder...]  /Users/.../Selected             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                                                             │
│                     PODGLĄD ZDJĘCIA                         │
│                                                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    IMG_1234.JPG                              │
│                       12 / 248                               │
├─────────────────────────────────────────────────────────────┤
│ ← Poprzednie   → Następne   Spacja: Kopiuj   ⌫: Kosz        │
└─────────────────────────────────────────────────────────────┘
```

Schemat ma charakter poglądowy. Ostateczny wygląd może wykorzystywać natywne elementy Qt.

### 3.2. Elementy interfejsu

1. Pole wyboru folderu źródłowego.
2. Przycisk wyboru folderu źródłowego.
3. Pole wyświetlające ścieżkę folderu źródłowego.
4. Pole wyboru folderu docelowego.
5. Przycisk wyboru folderu docelowego.
6. Pole wyświetlające ścieżkę folderu docelowego.
7. Centralny obszar podglądu zdjęcia.
8. Etykieta nazwy pliku.
9. Etykieta licznika zdjęć.
10. Pasek skrótów klawiaturowych.
11. Obszar komunikatów i błędów.
12. Opcjonalny wskaźnik operacji w toku.

### 3.3. Zachowanie okna

- Domyślny rozmiar powinien wynosić około 1200 × 800 pikseli.
- Minimalny rozmiar powinien wynosić około 800 × 600 pikseli.
- Interfejs musi prawidłowo skalować się przy zmianie rozmiaru okna.
- Podgląd zdjęcia powinien dostosowywać się do dostępnego miejsca.
- W miarę możliwości należy respektować ustawienia jasnego i ciemnego wyglądu macOS.
- Aplikacja powinna poprawnie działać na ekranach Retina.

---

## 4. Architektura techniczna

### 4.1. Zalecane technologie

| Komponent           | Technologia     | Zastosowanie                             |
| ------------------- | --------------- | ---------------------------------------- |
| Język               | Python 3.12+    | Logika aplikacji                         |
| Interfejs           | PySide6         | Okno, widżety, obsługa klawiatury        |
| Obsługa obrazów     | Pillow          | Dekodowanie, orientacja EXIF, skalowanie |
| HEIC                | pillow-heif     | Obsługa obrazów HEIC/HEIF                |
| Operacje na plikach | pathlib, shutil | Ścieżki i kopiowanie                     |
| Kosz macOS          | send2trash      | Przenoszenie plików do kosza             |
| Testy               | pytest          | Testy automatyczne                       |
| Analiza jakości     | Ruff            | Lintowanie i formatowanie                |
| Typowanie           | typing          | Czytelność i kontrola typów              |

Wersje zależności powinny zostać ustalone i przypięte w pliku zależności projektu.

Biblioteki do obsługi HEIC należy skonfigurować i przetestować na docelowej wersji macOS. Jeśli HEIC nie jest obsługiwany z powodu braku dekodera, aplikacja musi wyświetlić czytelny komunikat, zamiast kończyć działanie.

### 4.2. Podział odpowiedzialności

Aplikację należy podzielić na moduły:

- Interfejs graficzny.
- Skanowanie folderów.
- Ładowanie i skalowanie zdjęć.
- Nawigacja po liście zdjęć.
- Kopiowanie plików.
- Przenoszenie plików do kosza.
- Obsługa błędów.
- Testy.

Operacje na plikach nie powinny być bezpośrednio implementowane w obsłudze widżetów. Interfejs powinien wywoływać osobne klasy lub funkcje odpowiedzialne za operacje.

### 4.3. Proponowana struktura projektu

```text
photo-sorter/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── src/
│   └── photo_sorter/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── main_window.py
│       ├── image_view.py
│       ├── folder_scanner.py
│       ├── image_loader.py
│       ├── file_operations.py
│       ├── navigation.py
│       ├── settings.py
│       └── errors.py
└── tests/
    ├── test_folder_scanner.py
    ├── test_navigation.py
    ├── test_file_operations.py
    ├── test_image_loader.py
    └── test_edge_cases.py
```

### 4.4. Opis modułów

**`app.py`**

- Inicjalizacja aplikacji Qt.
- Konfiguracja aplikacji.
- Utworzenie głównego okna.

**`main_window.py`**

- Główny interfejs.
- Wybór folderów.
- Obsługa skrótów klawiaturowych.
- Wyświetlanie licznika, nazwy pliku i komunikatów.
- Koordynacja pozostałych modułów.

**`image_view.py`**

- Wyświetlanie obrazu.
- Dopasowanie do okna.
- Powiększanie i pomniejszanie.
- Przesuwanie powiększonego obrazu.

**`folder_scanner.py`**

- Rekurencyjne skanowanie folderów.
- Filtrowanie rozszerzeń.
- Sortowanie listy.
- Pomijanie plików ukrytych i systemowych.
- Zwracanie listy ścieżek do plików.

**`image_loader.py`**

- Odczytywanie obrazów.
- Obsługa EXIF.
- Skalowanie obrazu do rozmiaru podglądu.
- Obsługa HEIC.
- Obsługa błędów dekodowania.
- Ograniczone buforowanie.

**`file_operations.py`**

- Bezpieczne kopiowanie.
- Sprawdzanie konfliktów.
- Tworzenie podfolderów.
- Przenoszenie do kosza.
- Obsługa błędów systemowych.

**`navigation.py`**

- Aktualna pozycja na liście.
- Przechodzenie do poprzedniego i następnego zdjęcia.
- Aktualizacja listy po usunięciu pliku.
- Obsługa pustej listy.

**`settings.py`**

- Zapamiętywanie ostatnio wybranych folderów.
- Odczyt i zapis ustawień.
- Walidacja zapisanych ścieżek.

**`errors.py`**

- Wspólne typy błędów aplikacji.
- Ujednolicona obsługa wyjątków i komunikatów.

**`__main__.py`**

- Punkt wejścia pozwalający uruchamiać program jako moduł.

---

## 5. Obsługa klawiatury

### 5.1. Wymagane skróty

| Klawisz          | Operacja                                  | Przejście do kolejnego zdjęcia |
| ---------------- | ----------------------------------------- | ------------------------------ |
| Strzałka w lewo  | Poprzednie zdjęcie                        | Nie dotyczy                    |
| Strzałka w prawo | Następne zdjęcie                          | Nie dotyczy                    |
| Spacja           | Kopiowanie                                | Tak, tylko po sukcesie         |
| Backspace        | Przeniesienie do kosza                    | Tak, tylko po sukcesie         |
| F                | Pełny ekran                               | Nie                            |
| Esc              | Wyjście z pełnego ekranu lub powiększenia | Nie                            |

### 5.2. Wymagania implementacyjne

- Skróty muszą działać niezależnie od tego, który element interfejsu ma fokus.
- Nie należy dopuścić, aby spacja aktywowała przypadkowo przycisk lub inną kontrolkę zamiast kopiować zdjęcie.
- Skróty nie mogą uruchamiać operacji wielokrotnie z powodu jednego naciśnięcia.
- Podczas kopiowania lub przenoszenia bieżącego pliku należy zablokować kolejną operację na tym samym pliku.
- Nawigacja powinna pozostać responsywna, o ile nie koliduje z trwającą operacją na bieżącym zdjęciu.
- Skróty muszą działać w trybie pełnoekranowym.

---

## 6. Obsługa błędów

Aplikacja ma wyświetlać zrozumiałe komunikaty dla użytkownika, a szczegóły techniczne zapisywać w logu diagnostycznym.

Nie należy pokazywać użytkownikowi surowych tracebacków w standardowym interfejsie.

### 6.1. Błędy folderów

| Sytuacja                                         | Zachowanie                                  |
| ------------------------------------------------ | ------------------------------------------- |
| Folder źródłowy nie istnieje                     | Komunikat i brak skanowania                 |
| Brak uprawnień do źródła                         | Komunikat z informacją o uprawnieniach      |
| Folder docelowy nie istnieje                     | Komunikat i brak kopiowania                 |
| Folder docelowy nie jest zapisywalny             | Komunikat i pozostanie na zdjęciu           |
| Źródło i cel są takie same                       | Odrzucenie wyboru                           |
| Folder docelowy znajduje się w źródle            | Odrzucenie wyboru                           |
| Źródło znajduje się wewnątrz celu                | Odrzucenie wyboru                           |
| Folder został odłączony lub stał się niedostępny | Komunikat i bezpieczne zatrzymanie operacji |

### 6.2. Błędy obrazów

| Sytuacja                         | Zachowanie                                             |
| -------------------------------- | ------------------------------------------------------ |
| Uszkodzony plik                  | Komunikat i możliwość przejścia dalej                  |
| Nieobsługiwany format wewnętrzny | Komunikat o niemożności odczytu                        |
| Brak obsługi HEIC                | Informacja o wymaganym dekoderze                       |
| Brak uprawnień do odczytu        | Komunikat i możliwość dalszej nawigacji                |
| Plik został usunięty zewnętrznie | Odświeżenie listy i wybór kolejnego dostępnego zdjęcia |
| Plik zmienił się podczas odczytu | Ponowna walidacja i komunikat w przypadku błędu        |

### 6.3. Błędy kopiowania

| Sytuacja                           | Zachowanie                                          |
| ---------------------------------- | --------------------------------------------------- |
| Plik docelowy już istnieje         | Brak nadpisania i komunikat                         |
| Brak miejsca na dysku              | Przerwanie kopiowania, usunięcie pliku tymczasowego |
| Błąd odczytu źródła                | Przerwanie kopiowania                               |
| Błąd zapisu celu                   | Usunięcie niekompletnego pliku tymczasowego         |
| Brak uprawnień                     | Komunikat i pozostanie na zdjęciu                   |
| Źródło zniknęło podczas kopiowania | Przerwanie operacji i aktualizacja listy            |
| Podwójne naciśnięcie spacji        | Tylko jedna operacja dla aktualnego zdjęcia         |

### 6.4. Błędy kosza

Jeżeli operacja przeniesienia do kosza nie powiedzie się:

- Nie usuwaj pliku trwale.
- Nie zmieniaj jego lokalizacji.
- Nie przechodź do kolejnego zdjęcia.
- Wyświetl komunikat.
- Pozwól użytkownikowi spróbować ponownie.

---

## 7. Bezpieczeństwo plików

Bezpieczeństwo danych jest jednym z najważniejszych wymagań.

### 7.1. Zakaz trwałego usuwania

Aplikacja nie może trwale usuwać zdjęć w ramach normalnej obsługi.

Backspace musi korzystać z kosza systemowego. Nie wolno implementować awaryjnego przejścia do trwałego usunięcia.

### 7.2. Zakaz nadpisywania

Nigdy nie nadpisuj istniejącego pliku docelowego.

Sprawdzenie konfliktu powinno być odporne na sytuację, w której plik pojawi się w folderze docelowym między sprawdzeniem a zapisaniem wyniku.

Końcowe utworzenie pliku musi odbywać się z gwarancją braku nadpisania. W razie konfliktu aplikacja ma przerwać operację.

### 7.3. Integralność kopiowania

- Kopiuj oryginalne bajty pliku.
- Nie modyfikuj pliku źródłowego podczas kopiowania.
- Nie zapisuj pod docelową nazwą pliku częściowo skopiowanego.
- Po błędzie usuwaj wyłącznie pliki tymczasowe utworzone przez aplikację.
- Nie usuwaj innych plików z folderu docelowego.
- Po zakończeniu kopiowania sprawdź, czy rozmiar kopii odpowiada rozmiarowi źródła.

Weryfikacja sumą kontrolną może być opcjonalna ze względu na koszt wydajnościowy, ale należy przewidzieć możliwość jej dodania.

### 7.4. Bezpieczeństwo ścieżek

- Wszystkie ścieżki należy normalizować i walidować.
- Ścieżki docelowe muszą pozostać wewnątrz wybranego folderu docelowego.
- Nie wolno budować ścieżek docelowych na podstawie niezaufanych fragmentów, które mogłyby zawierać `..` lub ścieżki absolutne.
- Nie kopiuj folderu docelowego do samego siebie.
- Nie pozwalaj na skanowanie rekurencyjne folderu docelowego jako części źródła.
- Zwróć szczególną uwagę na dowiązania symboliczne. Domyślnie nie podążaj za dowiązaniami symbolicznymi podczas skanowania.
- Uwzględnij specyfikę systemu plików macOS, w tym wielkość liter oraz nazwy plików różniące się normalizacją Unicode.

### 7.5. Uprawnienia macOS

Aplikacja powinna korzystać ze zwykłych uprawnień użytkownika i nie wymagać uruchamiania z uprawnieniami administratora.

Jeżeli macOS ograniczy dostęp do folderu, aplikacja powinna wyświetlić komunikat o wymaganych uprawnieniach.

Nie należy obchodzić mechanizmów bezpieczeństwa systemu.

---

## 8. Wydajność

Program ma sprawnie działać również przy dużej liczbie zdjęć.

Wymagania:

- Skanowanie folderów nie może blokować głównego wątku GUI.
- Kopiowanie i przenoszenie do kosza powinno odbywać się poza głównym wątkiem interfejsu.
- Obrazy należy dekodować na żądanie.
- Nie należy ładować pełnych wersji wszystkich zdjęć do pamięci.
- Dopuszczalne jest buforowanie aktualnego zdjęcia oraz ograniczonej liczby zdjęć sąsiednich.
- Należy korzystać z sygnałów Qt do informowania interfejsu o zakończeniu zadań.
- Długie operacje powinny sygnalizować stan wykonywania.
- Podczas operacji nie wolno dopuścić do podwójnego kopiowania lub usuwania aktualnego pliku.
- Program nie może utracić responsywności podczas kopiowania dużego zdjęcia.

Docelowe zachowanie: przechodzenie pomiędzy zwykłymi zdjęciami powinno być płynne, a czas oczekiwania na załadowanie obrazu powinien być możliwie krótki.

---

## 9. Ustawienia i ponowne uruchamianie

Aplikacja powinna zapamiętywać:

- ostatni folder źródłowy;
- ostatni folder docelowy;
- opcjonalnie ostatni rozmiar i położenie okna.

Ustawienia należy przechowywać w standardowej lokalizacji ustawień aplikacji w macOS, np. za pomocą `QSettings`.

Przy ponownym uruchomieniu:

1. Wczytaj zapisane ścieżki.
2. Sprawdź, czy foldery nadal istnieją.
3. Nie rozpoczynaj automatycznie kopiowania ani usuwania.
4. Jeśli folder źródłowy jest dostępny, zeskanuj go ponownie.
5. Jeśli folder docelowy jest niedostępny, poproś użytkownika o wybranie nowego.

Nie jest wymagane zapisywanie historii ani cofanie operacji.

Nie należy przechowywać pełnych zdjęć w ustawieniach aplikacji.

---

## 10. Instrukcja uruchomienia

### 10.1. Wymagania wstępne

Na komputerze z macOS powinny być dostępne:

- Python 3.12 lub nowszy, zgodny z używanymi bibliotekami;
- pip;
- terminal;
- uprawnienia do odczytu i zapisu wybranych folderów.

### 10.2. Przygotowanie środowiska

W terminalu przejdź do folderu projektu:

```bash
cd photo-sorter
```

Utwórz środowisko wirtualne:

```bash
python3 -m venv .venv
```

Aktywuj je:

```bash
source .venv/bin/activate
```

Zainstaluj zależności:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 10.3. Uruchomienie aplikacji

Po przygotowaniu projektu uruchom:

```bash
python -m photo_sorter
```

Jeżeli projekt korzysta z układu `src/`, należy zainstalować go w trybie developerskim:

```bash
python -m pip install -e .
```

Następnie można uruchamiać:

```bash
python -m photo_sorter
```

### 10.4. Przykładowe zależności

Plik `requirements.txt` powinien zawierać co najmniej:

```text
PySide6
Pillow
pillow-heif
send2trash
pytest
ruff
```

Implementacja powinna następnie ustalić i przypiąć przetestowane wersje bibliotek.

### 10.5. Uruchamianie testów

```bash
pytest
```

Sprawdzenie jakości kodu:

```bash
ruff check .
```

Formatowanie:

```bash
ruff format .
```

### 10.6. Opcjonalne przygotowanie aplikacji do dystrybucji

Po ukończeniu podstawowej wersji można przygotować samodzielną aplikację `.app` dla macOS.

Można rozważyć PyInstaller lub inne narzędzie zgodne z PySide6.

Pakowanie nie jest wymagane w pierwszym etapie implementacji.

---

## 11. Plan testowania

Testy muszą sprawdzać zarówno normalne działanie aplikacji, jak i skrajne przypadki.

### 11.1. Testy skanowania folderów

1. Folder zawierający pliki JPG i PNG.
2. Folder zawierający wszystkie obsługiwane rozszerzenia.
3. Rozszerzenia zapisane wielkimi literami.
4. Zdjęcia w wielu poziomach podfolderów.
5. Puste foldery.
6. Folder bez zdjęć.
7. Folder z uszkodzonym obrazem.
8. Folder zawierający pliki tekstowe i inne nieobsługiwane pliki.
9. Folder z plikami ukrytymi.
10. Folder zawierający dowiązanie symboliczne.
11. Bardzo duża liczba zdjęć.
12. Folder źródłowy, do którego program nie ma dostępu.

### 11.2. Testy nawigacji

1. Przejście do następnego zdjęcia.
2. Przejście do poprzedniego zdjęcia.
3. Próba przejścia w lewo na pierwszym zdjęciu.
4. Próba przejścia w prawo na ostatnim zdjęciu.
5. Nawigacja po liście zawierającej jedno zdjęcie.
6. Nawigacja po pustej liście.
7. Usunięcie ostatniego zdjęcia.
8. Usunięcie jedynego zdjęcia.
9. Aktualizacja licznika po zmianie listy.
10. Próba wykonania kilku operacji szybko jedna po drugiej.

### 11.3. Testy kopiowania

1. Kopiowanie zwykłego pliku JPG.
2. Kopiowanie pliku PNG.
3. Kopiowanie HEIC.
4. Kopiowanie zdjęcia z podfolderu.
5. Zachowanie oryginału źródłowego.
6. Zachowanie bajtowej zawartości oryginału.
7. Brak nadpisania istniejącego pliku.
8. Konflikt nazwy w podfolderze docelowym.
9. Brak miejsca na dysku.
10. Brak uprawnień do zapisu.
11. Utrata dostępu do folderu podczas kopiowania.
12. Podwójne naciśnięcie spacji.
13. Błąd w trakcie kopiowania dużego pliku.
14. Sprawdzenie, czy nie pozostają niekompletne pliki docelowe.
15. Sprawdzenie, czy nie dochodzi do kopiowania folderu docelowego do samego siebie.

### 11.4. Testy kosza

1. Przeniesienie zdjęcia do kosza.
2. Sprawdzenie, czy plik zniknął z folderu źródłowego.
3. Sprawdzenie, czy aplikacja nie użyła trwałego usuwania.
4. Brak uprawnień do przeniesienia do kosza.
5. Próba przeniesienia pliku, który został już usunięty.
6. Błąd systemowego kosza.
7. Przeniesienie ostatniego zdjęcia.
8. Przeniesienie jedynego zdjęcia.

Testy nie mogą usuwać rzeczywistych zdjęć użytkownika. Należy używać tymczasowych katalogów testowych i plików wygenerowanych na potrzeby testów.

### 11.5. Testy interfejsu

1. Wybór folderu źródłowego.
2. Wybór folderu docelowego.
3. Wyświetlenie nazwy pliku.
4. Wyświetlenie licznika.
5. Dopasowanie zdjęcia pionowego.
6. Dopasowanie zdjęcia poziomego.
7. Powiększanie kółkiem myszy.
8. Pomniejszanie kółkiem myszy.
9. Powrót do dopasowania po zmianie zdjęcia.
10. Włączenie i wyłączenie pełnego ekranu.
11. Obsługa `Esc`.
12. Obsługa skrótów bez względu na fokus.
13. Zmiana rozmiaru okna.
14. Działanie na ekranie Retina.
15. Wyświetlanie komunikatów o błędach.

---

## 12. Kryteria akceptacji

Aplikację można uznać za gotową, jeśli wszystkie poniższe warunki są spełnione.

### Funkcjonalność

- [ ] Użytkownik może wybrać folder źródłowy.
- [ ] Użytkownik może wybrać folder docelowy.
- [ ] Program znajduje zdjęcia również w podfolderach.
- [ ] Program rozpoznaje JPG, JPEG, PNG, HEIC, TIF i TIFF.
- [ ] Zdjęcia wyświetlają się z zachowaniem proporcji.
- [ ] Pod zdjęciem wyświetlana jest nazwa pliku.
- [ ] Licznik ma format `aktualny numer / liczba zdjęć`.
- [ ] Strzałki zmieniają zdjęcia.
- [ ] Spacja kopiuje zdjęcie i przechodzi dalej po sukcesie.
- [ ] Backspace przenosi zdjęcie do kosza i przechodzi dalej po sukcesie.
- [ ] Program nie zapętla listy.
- [ ] Po usunięciu zdjęcia licznik jest aktualizowany.
- [ ] Powiększanie kółkiem myszy działa.
- [ ] Pełny ekran działa.

### Bezpieczeństwo

- [ ] Program nie usuwa zdjęć trwale.
- [ ] Program nie nadpisuje plików docelowych.
- [ ] Program nie przechodzi dalej po nieudanym kopiowaniu.
- [ ] Program nie przechodzi dalej po nieudanym przenoszeniu do kosza.
- [ ] Program sprząta własne niekompletne pliki tymczasowe.
- [ ] Program nie kopiuje folderu docelowego do samego siebie.
- [ ] Program obsługuje brak uprawnień.
- [ ] Program nie modyfikuje oryginalnych plików podczas podglądu.

### Stabilność

- [ ] Pusta lista nie powoduje błędu.
- [ ] Uszkodzony obraz nie powoduje zamknięcia aplikacji.
- [ ] Niedostępny folder powoduje czytelny komunikat.
- [ ] Duże zdjęcia nie blokują na stałe interfejsu.
- [ ] Szybkie naciskanie klawiszy nie powoduje wielokrotnych operacji na tym samym zdjęciu.
- [ ] Testy automatyczne przechodzą poprawnie.

---

## 13. Jednoznaczne zachowanie w sytuacjach brzegowych

| Sytuacja                                | Oczekiwane działanie                                      |
| --------------------------------------- | --------------------------------------------------------- |
| Nie wybrano źródła                      | Nie wyświetlaj zdjęć; poproś o wybór folderu              |
| Nie wybrano celu                        | Można przeglądać zdjęcia, ale kopiowanie jest zablokowane |
| Lista zdjęć jest pusta                  | Wyświetl `0 / 0` i informację o braku zdjęć               |
| Jedno zdjęcie na liście                 | Nawigacja pozostaje na tym zdjęciu                        |
| Usunięcie ostatniego zdjęcia            | Wyświetl poprzednie zdjęcie                               |
| Usunięcie jedynego zdjęcia              | Wyświetl pusty stan                                       |
| Kopia już istnieje                      | Pokaż komunikat, nie nadpisuj, pozostań na zdjęciu        |
| Kopiowanie nie powiodło się             | Pozostań na zdjęciu                                       |
| Przeniesienie do kosza nie powiodło się | Pozostań na zdjęciu                                       |
| Zdjęcie jest uszkodzone                 | Pokaż informację i umożliwiaj dalszą nawigację            |
| Plik źródłowy zniknął                   | Odśwież odpowiednią pozycję i poinformuj użytkownika      |
| Źródło zmieniono w trakcie pracy        | Zbuduj nową listę i ustaw pierwsze zdjęcie                |
| Cel zmieniono w trakcie pracy           | Kolejne operacje wykorzystują nowy, zweryfikowany cel     |
| Brak miejsca na dysku                   | Przerwij kopiowanie i usuń niekompletny plik tymczasowy   |
| Wciśnięto spację kilka razy             | Nie uruchamiaj równoległych kopii tego samego zdjęcia     |
| Zdjęcie jest powiększone                | Po zmianie zdjęcia wróć do dopasowania                    |
| Okno jest w trybie pełnoekranowym       | Wszystkie podstawowe skróty nadal działają                |

---

## 14. Zasady implementacji dla modelu AI

Podczas generowania kodu należy przestrzegać następujących zasad:

1. Wygeneruj kompletny, uruchamialny projekt, a nie wyłącznie fragmenty kodu.
2. Stosuj podział na moduły zgodny z opisaną architekturą.
3. Nie umieszczaj całej aplikacji w jednym pliku.
4. Nie pomijaj obsługi wyjątków w operacjach na plikach.
5. Nie zastępuj przenoszenia do kosza trwałym usuwaniem.
6. Nie pozwalaj na nadpisywanie istniejących plików.
7. Nie blokuj głównego wątku GUI podczas skanowania i kopiowania.
8. Używaj mechanizmów Qt do komunikacji między wątkiem roboczym a interfejsem.
9. Nie deklaruj obsługi HEIC jako działającej bez sprawdzenia integracji dekodera.
10. Zapewnij czytelne komunikaty dla użytkownika.
11. Dodaj testy automatyczne.
12. Dołącz instrukcję instalacji i uruchomienia.
13. Zadbaj o zgodność z macOS.
14. Nie implementuj cofania operacji.
15. Nie dodawaj niezamówionych funkcji, które komplikują interfejs.
16. W przypadku konfliktu wymagań bezpieczeństwo plików ma pierwszeństwo przed szybkością działania.

### Oczekiwany rezultat

Końcowym rezultatem ma być działająca aplikacja desktopowa na macOS, którą można uruchomić w środowisku Python bez ręcznego poprawiania wygenerowanego kodu.

Projekt powinien zawierać:

- kompletny kod źródłowy;
- plik zależności;
- instrukcję uruchomienia;
- testy;
- obsługę błędów;
- czytelny i prosty interfejs;
- bezpieczne kopiowanie i przenoszenie zdjęć do kosza.

Implementacja powinna zostać uznana za ukończoną dopiero po uruchomieniu aplikacji i sprawdzeniu kryteriów akceptacji.
