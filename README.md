# python_images

## Aplikacja internetowa, do komunikacji z CouchDB.

### Funkcjonalności
1. (1 zakładka) Wgrywanie zdjęć, które bedą nam służyć jako pojedyncze kafelki. Podczas zapisu do CouchDB jest obliczane średnie rgb dla każdego z nich 
2. (2 zakładka) Wgrywanie jednego zdjęcia , które będzie nam służyło do zrobienia naszej mozaiki.
3. (3 zakładka) Generowanie mozaiki ze zdjęcia z punktu 2.
    Przebieg metody:
      * Zmieniamy wielkość naszego zdjęcia do rozmiarów `width*image.width,height*image.height`, gdzie width i height to dane wejściowe z formularza. Zapisujemy nasze nowe zdjęcie do CouchDB
      * Obliczamy R-G-B dla naszego przeskalowanego zdjęcia, i zwraca nam macierz rozmiarów starego zdjęcia, która przechowuje **id** zdjęć jakie będą potrzebne do wygenerowania tego zdjęcia.
      * Pobieramy z widoku, stworzonego w CouchDB te zdjęcia, które są przechowywane w tablicy wygenerowanej powyżej.
      * Kopiujemy je do nowego obrazka, o rozmiarach naszego przeskalowanego obrazka
      * Zapisujemy nowy obrazek jako *mosaic* i wyświetlamy na widok.
      
**TODO**
 * Zmienić sposób wyświetlania zdjęcia zamiast z linku to przekonwertowany na base64.
 
 
 
 Widok:
 ```javascript
function (doc) {
  if(doc._id != 'big_image') {
  emit(doc._id, {
    r: doc.red,
    g: doc.green,
    b: doc.blue
  }, doc);
  }
}
```
