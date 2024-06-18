# **PortfoGuard**

### Co je to **PortfoGuard**?
První český open-source portfolio tracker.

### Na co potřebuji potřebuji portfolio tracker?
> Máte investice a mohl bych je vidět?
Mnoho investorů investuje na různých platformách do různých produktů bez možnosti se na své portfolio podívat komplexněji. DObrý portfolio tracker by nám měl umožnit získat odpověďi na palčivé otázky:
- jak se moje investice vyvíjí v čase?
- kolik mám celkem peněz v jednotlivých typech aktiv?
- neudělal bych lépe, kdybych namísto výběru jednotlivých akcií kupoval jenom indexové ETF?

V čem je **PortfoGuard** vyjímečný?
- je open-source = můžete se sami podívat jak přesně jsou která čísla počítána
- je kompletně offline = nemusíte nikomu sdílet informace o Vašich nákupech a prodejích
- je na gitu = chybí vám nějaká funkcionalita? Není nic jednoduššího než ji přidat a udělat merge request
- je v češtině = jazyk ještě stále může být pro část investorů limitující při použití některých aktuálně dostupných řešení

## Vstupní data
**PortfoGuard** pracuje se dvěmi vstupními soubory: 'trades.tsv' a 'watchlist.tsv'. V prvním zmíněném souboru vedeme evidenci našich nákupů do portfolia. Ve druhém souboru pak můžeme uvést akcie, které nás zajímají a cenu, za kterou bychom je rádi do našeho portfolia přidali.
### Nákupy a prodeje (trades.tsv)

Soubor `trades.tsv` tvoří databázi našich nákupů a prodejů. Obsahuje celkem 10 sloupečků:
- name = náš vlastní název akcie
- ticker = ticker symbol aktiva pocházející z finance.yahoo.com
- type = typ aktiva akcie/ETF/krypto
- tradeType = typ zápisu Buy/Sell
- date = datum realizace obchodu
- units = počet zobchodovaných aktiv
- price = cena aktiva
- fees = poplatky spojené s obchodem
- currency = měna obchodu
- note = libovolná poznámka

Ukázka souboru

```
name	ticker	type	tradeType	date	units	price	fees	currency	note
Moneta	MONET.PR	Akcie	Buy	27.4.2022	106	94	0	CZK	Spe
S&P500	VUAA.DE	ETF	Buy	17.1.2024	1.9273	82.1060	0	EUR
Bitcoin	BTC-USD	Krypto	Buy	11.12.2023	0.00052719	948424		CZK
```

### Sledované akcie

## Fungování

## Kontakty
Pokud Vás PortfoGuard zaujal nebo máte nějaké dodatečné informace, máte nápad na vylepšení, nestyďte se napsat na fajtak.l@gmail.com.