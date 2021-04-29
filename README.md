# Tietokantasovellus projektin palautusrepositorio

_Repositorio sisältää [tietokantasovellus](https://hy-tsoha.github.io/materiaali/) harjoitustyön sekä siihen liittyvän dokumentaation_

# Lintubongarin lokisovellus

## Sovelluksen tarkoitus

Sovellus tarjoaa alustan lintuhavaintojen kirjaamiseen sekä aiempien havaintojen tarkasteluun ja kommentointiin.
- [Vaatimusmäärittely](/documentation/requirements.md)

## Demo Herokussa

**Linkki herokuun**: [Lintuloki](https://lintuloki.herokuapp.com/)

Sovelluksen tämän hetkinen versio on herokussa ja siihen on toteutettu seuraavat [vaatimusmäärittelyssä](/documentation/requirements.md) kirjatut ominaisuudet:

#### Välipalautus 2:

- Uuden käyttäjän rekisteröiminen
- Sisään kirjautuminen
- Ulos kirjautuminen
- Uusien havaintojen luominen
- Kuvan lisääminen havainnon yhteyteen
- Havaintojen tarkastelu
- Havaintojen hakeminen tietyltä aikaväliltä eri kriteereillä
  - Linnun laji
  - Havintopaikka (kunta tai maakunta)
  - Linnun renkaan kirjainkoodi ja sarjanumero
  - Havainnon tehnyt bongari (nimi tai käyttäjätunnus)

#### Välipalautus 3:

- Omien havaintojen muokkaaminen
- Kuvan poistaminen
- Kuvan lisääminen jälkikäteen havainnon yhteyteen
- Havaintojen kommentointi

#### Lopullinen palautus:

- Käyttäjä voi poistaa omia kommenttejaan
- Käyttäjä voi poistaa kenen tahansa kommentteja omista havainnoistaan

Havaintojen tarkempiin tietoihin pääsee painamalla havainnon otsikkona olevaa linnun nimeä.
