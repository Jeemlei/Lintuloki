# Tietokantasovellus projektin palautusrepositorio

_Repositorio sisältää [tietokantasovellus](https://hy-tsoha.github.io/materiaali/) harjoitustyön sekä siihen liittyvän dokumentaation_

# Lintubongarin lokisovellus

## Sovelluksen tarkoitus

Sovellus tarjoaa alustan lintuhavaintojen kirjaamiseen sekä aiempien havaintojen tarkasteluun ja kommentointiin.

## Käyttäjät

Sovelluksella on kaksi käyttäjäroolia, jotka ovat ns. _normaali käyttäjä_ ja _ylläpitäjä_.

## Keskeiset toiminnot

- Sovellukseen voi rekisteröidä käyttäjän sekä kirjautua sisään.
- Havaintoja voi hakea ja tarkastella kirjautumatta sisään.
  - Hakutoiminnossa voi rajata havainnot lajin, sijainnin ja/tai ajan mukaan

### Normaali käyttäjä

- Uusien havaintojen luominen
- Omien havaintojen muokkaaminen ja poistaminen
- Kuvan lisääminen oman havainnon yhteyteen
- Minkä tahansa havainnon kommentointi

### Ylläpitäjä

- Pystyy poistamaan kommentteja, havaintoja sekä käyttäjättunnuksia.

## Alustava tietokantakaavio

![banded_enum.png](https://github.com/Jeemlei/tsoha-projekti/blob/main/banded_enum.png)
![observationdb.png](https://github.com/Jeemlei/tsoha-projekti/blob/main/observationdb.png)
