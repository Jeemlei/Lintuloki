# Tietokantasovellus projektin palautusrepositorio

_Repositorio sisältää [tietokantasovellus](https://hy-tsoha.github.io/materiaali/) harjoitustyön sekä siihen liittyvän dokumentaation_

# Lintubongarin lokisovellus

## Sovelluksen tarkoitus

Sovellus tarjoaa alustan lintuhavaintojen kirjaamiseen sekä aiempien havaintojen tarkasteluun ja kommentointiin.
- [Vaatimusmäärittely](/documentation/requirements.md)

## Demo Herokussa

**Linkki herokuun**: [Lintuloki](https://lintuloki.herokuapp.com/)

### Lopullinen palautus:

- Sovellukseen voi rekisteröidä käyttäjän sekä kirjautua sisään ja ulos
- Havaintoja voi tarkastella kirjautumatta sisään
- Havaintoja voi hakea tietyltä aikaväliltä eri kriteereillä
  - Linnun laji
  - Havaintopaikka (kunta tai maakunta)
  - Linnun renkaan kirjainkoodi ja sarjanumero
  - Havainnon tehnyt bongari (nimi tai käyttäjätunnus)
- Havaintojen tarkempiin tietoihin pääsee painamalla havainnon otsikkona olevaa linnun nimeä.
- Käyttäjä kirjataan ulos 15 minuutin epäakttivisuuden jälkeen

#### Normaali käyttäjä voi

- luoda uusia havaintoja
- muokata omia havaintojaan
- lisätä havainnon yhteyteen kuvan luodessaan tai muokatessaan havaintoa
- poistaa kuvan omasta havainnostaan
- poistaa omia havaintojaan
- kommentoida kaikkia havaintoja
- poistaa omia kommenttejaan sekä muiden kommentteja omista havainnoistaan

#### Ylläpitäjä voi lisäksi

- poistaa kaikkien käyttäjien havaintoja
- muokata kaikkien käyttäjien havaintoja (ei linkkiä käyttöliittymässä -> /edit/[id])
- poistaa kaikkien käyttäjien kommentteja

#### Tietokanta

Käyttöön otettaessa tietokanta on alustettu tiedostolla [init.sql](/documentation/db/init.sql).

![dbdiagram.png](/documentation/db/dbdiagram.png)
