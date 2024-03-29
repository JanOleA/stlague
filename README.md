# Valgresultater med variasjoner på valgsystemet i Norge, samt helt andre valgsystem.
Valgresultatene for Stortingsvalget i Norge, 2021. Resultatene er eksportert fra valgresultat.no den 17. september (kan bli små endringer i ettertid).

Scroll ned for å se de faktiske resultatene + en kort intro til hvordan programmet brukes.

## Forskjellige metoder:
- **Sperregrense 4%**
    - [Modifisert Sainte-Laguë (metoden i bruk)](figs/sperregrense4/modf/README.md)
    - [Umodifisert Sainte-Laguë](figs/sperregrense4/unmodf/README.md)
    - [D'Hondts metode](figs/sperregrense4/dhondt/README.md)
- **Ny fylkesinndeling**
    - [Modifisert Sainte-Laguë](figs/nyefylker/modf/README.md)
    - [Umodifisert Sainte-Laguë](figs/nyefylker/unmodf/README.md)
    - [D'Hondts metode](figs/nyefylker/dhondt/README.md)
- **Sperregrense 3%**
    - [Modifisert Sainte-Laguë](figs/sperregrense3/modf/README.md)
    - [Umodifisert Sainte-Laguë](figs/sperregrense3/unmodf/README.md)
    - [D'Hondts metode](figs/sperregrense3/dhondt/README.md)
- **Sperregrense 5%**
    - [Modifisert Sainte-Laguë](figs/sperregrense5/modf/README.md)
    - [Umodifisert Sainte-Laguë](figs/sperregrense5/unmodf/README.md)
    - [D'Hondts metode](figs/sperregrense5/dhondt/README.md)
- **Ingen sperregrense**
    - [Modifisert Sainte-Laguë](figs/sperregrense0/modf/README.md)
    - [Umodifisert Sainte-Laguë](figs/sperregrense0/unmodf/README.md)
    - [D'Hondts metode](figs/sperregrense0/dhondt/README.md)
- **Ingen utjevningsmandater**
    - [Modifisert Sainte-Laguë](figs/ingenutjvn/modf/README.md)
    - [Umodifisert Sainte-Laguë](figs/ingenutjvn/unmodf/README.md)
    - [D'Hondts metode](figs/ingenutjvn/dhondt/README.md)
- **Absolutt grense på 4%**
    - [Modifisert Sainte-Laguë](figs/abs4/modf/README.md)
    - [Umodifisert Sainte-Laguë](figs/abs4/unmodf/README.md)
    - [D'Hondts metode](figs/abs4/dhondt/README.md)
- **Endring i arealfaktoren for mandatfordeling på fylkene**
    - [Ingen arealfaktor](figs/areal/faktor0/README.md)
    - [Arealfaktor på 1](figs/areal/faktor1/README.md)
    - [Arealfaktor på 3](figs/areal/faktor3/README.md)
- **Hele landet som ett valgdistrikt**
    - [Ett valgdistrikt, 169 mandater](figs/ett_distrikt/README.md)
- **Hjemmesitterne**
    - [Hjemmesitterne har et eget parti](figs/hjemmesitterne/hjem/README.md)
    - [Hjemmesitterne har et eget parti med D'Hondts metode](figs/hjemmesitterne/dhondt/README.md)
    - [Hjemmesitterne har et eget parti og sperregrensen er 3%](figs/hjemmesitterne/hjemsg3/README.md)
    - [Hjemmesitterne + blanke stemmer har et parti sammen](figs/hjemmesitterne/hjemblank/README.md)
- **Amerikanske metoder (First Past The Post)**
    - [Fylkesfordelingen som normalt](figs/usaway/stdmandater/README.md)
    - [Mandatene utdelt til fylker som i USA (først én, deretter resten fordelt etter populasjon (Huntington-Hills metode), og deretter to ekstra til hvert fylke)](figs/usaway/usamandater/README.md)

## Kjøre programmet selv
Om du vil kjøre programmet selv, skriv `python election.py -h` i et terminalvindu i samme mappe du laster ned programmet til for en rask guide til hvordan programmet kan brukes (se evt. på eksemplene i `generate_scenarios.sh`).  
Du trenger en relativt ny versjon av Python installert, og Python-pakkene: numpy, matplotlib, pandas og odfpy.

Du kan også endre antallet stemmer hvert parti fikk ved å fylle ut `justeringer.ods`. Regnearket leses av programmet og stemmene legges til for partiene i de valgkretsene du velger. Dette fungerer bare om du bruker de gamle valgkretsene, ikke hvis du bruker de nye fylkene.

## De faktiske valgresultatene (endringene til høyre viser forskjell fra faktisk resultat, altså null i dette tilfellet):  
![Faktiske resultater](figs/sperregrense4/modf/seter.png)
### Stortinget med disse resultatene:  
![Faktiske resultater, tinget](figs/sperregrense4/modf/tinget.png)
### Kart som viser fordelingen av mandatene på valgdistriktene (gamle fylker):  
![Faktiske resultater, kart](figs/sperregrense4/modf/kart.png)