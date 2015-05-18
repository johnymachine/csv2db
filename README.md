# csv2db
RDB - Školni projekt

## Školní databáze
```
	psql -h 147.230.21.34 -U student -d postgres
	# jmeno databaze RDB2015_DanielMadera
	# heslo stejné jako na cvičení
```

## Zadání
	- sada souborů CSV
### Struktura
	datum-cas(timestamp), 
	jednotka-veliciny(nvarchar), 
	merici-bod(int), 
	souradnice-x(float), 
	souradnice-y(float), 
	popis-mericiho-bodu(nvarchar), 
	hodnota1(flaot), 
	hodnota2(float), 
	odchylka-veliciny(float), 
	seriove-cislo-pristroje(char, unikatni), 
	odchylka-pristroje(float), 
	popis-pristroje(nvarchar), 
	mereni-id(int, seskupeni mereni do bloku), 
	mereni-popis(nvarchar)

### Funkcionalita
	- databázové schéma
	- import vstupních souboru CSV (i GB soubory)
	- slučování bloků měření
	- vyhledávání, filter: - logický součin hodnot vyhledávání (AND)
		dle datumu - od do
		dle místa - souřadnice
		dle hodnoty mimo odchylku (hodnota1 - hodnota2 > odchylka veličiny)
		dle veličiny
		dle přístroje 
		dle měření
	- optimalizace dotazů
	- export dat do CSV souboru vstupní struktury s možností filtrování dat (i velká data - GB)
	- mazání z databáze (např. všechny záznamy o jednom typu měření)
		- možnost mazání přístroje, smažou se všechny záznamy tohoto přístroje
		- možnost mazání měření
	- loggování událostí (hlavně co se dělo, nemusí být kdo) - vyhledávání, přidávání, mazání, úpravy
	- Windows Server (8GB RAM) - Oracle 12c, PostgresSQL 9.4, MS SQL 5.5, MySQL 5.7
	- vyhazování nekonzistence (přeskočit) - loggovat
	- zobrazení například pouze hlaviček (rozkliknutí)
	- zobrazovat:
		datum-cas, hodnota1, hodnota2, abs(hodnota1-hodnota2), popis-pristroje, odchylka-pristroje
	- náhled do loggování
	- windows prostředí (možnost vlastního notesu)
	- prezentace, poslat email kdo je ve skupině
