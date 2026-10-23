# Samordnet koding av løfter i sju nordområdedokumenter

**Hovedpoeng.** Med én felles regel er andelen konkrete løfter 64–78 % i alle sju dokumentene. De opprinnelige lesernotatene ga 50–81 %, og mesteparten av den forskjellen skyldtes ulik terskel hos leserne, ikke dokumentene. Det som faktisk skiller dokumentene, er nye penger: 2020-meldingen har 15 løfter med nytt beløp, 2006-strategien 5, mens 2009, 2017 og 2025 ikke har noen. 2014-dokumentet er i hovedsak en statusrapport. 25 av 92 registrerte punkter er rapporterte resultater og er tatt ut.

Grunnlag: `notater/{2006,…,2025}.json` (462 registrerte tiltak), kontrollert mot `kilder/*.txt`. Utdata: `notater/lofter-samordnet.json`.

## 1. Regelen

- **Konkret:** tiltaket har (a) et tall (beløp, antall, prosent) *og* en frist eller et tidspunkt, eller (b) en avgrenset leveranse som kan kontrolleres i ettertid. Eksempler er at noe opprettes, vedtas, bygges, legges fram, utredes eller kartlegges.
- **Vagt:** tiltaket bæres i hovedsak av «vurdere», «arbeide for», «legge til rette for», «bidra til», «styrke», «videreutvikle», «følge opp», «stimulere», «prioritere» eller tilsvarende retningsverb, og har ingen avgrenset leveranse. Retningsverb er her «øke», «redusere», «utvide», «ta stilling til», «avklare» og «være pådriver».
- **Verken eller:** videreføring av eksisterende ordninger uten tall og frist. Det samme gjelder utfallsmål med frist, men uten tall.
- **Beløpstype:** «nytt» er en ny bevilgning eller økning som ikke var vedtatt da dokumentet kom. Det omfatter nye poster i et budsjettforslag som lå til behandling på samme tid. «Eksisterende» er NTP, langtidsplan for forsvaret, budsjett vedtatt før dokumentdatoen, tidligere vedtak og nivået i en eksisterende ordning. «Uklart» brukes om blandede beløp og anslag.
- **Rapportert resultat:** handlinger dokumentet omtaler som fullført, og rene beskrivelser av eksisterende ordninger uten noen forpliktelse framover. Slike punkter telles ikke. Det gjør heller ikke dubletter innen samme dokument.

## 2. Resultat per dokument

| Dokument | Registrert | Rapportert | Dubletter | n | Konkret | Andel konkret | Vagt | Nye beløp | Eksisterende beløp | Opprinnelig «målbart» |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2006 Nordområdestrategi | 55 | 1 | 0 | 54 | 38 | 70,4 % | 12 | 5 | 3 | 72,7 % |
| 2009 Nye byggesteiner | 63 | 0 | 0 | 63 | 45 | 71,4 % | 18 | 0 | 8 | 73,0 % |
| 2011 Meld. St. 7 | 60 | 1 | 0 | 59 | 46 | 78,0 % | 10 | 1 | 2 | 50,0 % |
| 2014 Nordkloden | 92 | 25 | 0 | 67 | 43 | 64,2 % | 16 | 1 | 6 | 75,0 % |
| 2017 Nordområdestrategi | 58 | 0 | 1 | 57 | 43 | 75,4 % | 11 | 0 | 7 | 55,2 % |
| 2020 Meld. St. 9 | 76 | 0 | 0 | 76 | 56 | 73,7 % | 13 | 15 | 6 | 77,6 % |
| 2025 Norge i nord | 58 | 4 | 1 | 53 | 38 | 71,7 % | 11 | 0 | 6 | 81,0 % |

Andelene er regnet av n. Uklart beløp: 2014 Arktis 2030, 2020 Beaivváš/samisk videregående og 2025 CAOC (ett hver). «Opprinnelig målbart» er andelen i lesernotatene av alle registrerte punkter. Kolonnen er bare med for sammenligning.

**Forbehold.** Hvilke tiltak som står i listene, bestemte de opprinnelige leserne. Ingen tiltak er lagt til. For 2011 er 60 tiltak registrert av over 100 prioriteringer, og komiteen (Innst. 236 S, s. 8) kalte prioriteringene vage. Derfor er andelen konkret i 2011 trolig for høy. Lista for 2009 tok heller ikke med statusvedlegget (s. 90–92), og derfor er ingen 2009-punkter rapporterte. Skal andelene sammenlignes strengt, må tiltakene trekkes ut på nytt med samme terskel.

## 3. Grensetilfeller og avgjørelser

1. **Utrede eller vurdere.** «Utrede», «kartlegge», «gjennomgå» og «evaluere» gir en leveranse og kodes konkret (2006 isgående fartøy, 2011 visumpraksis, 2017 vekstnæringer). «Vurdere», «ta stilling til», «avklare» og «komme tilbake til» kodes vagt, også når de har frist. Eksempler er SIOS og Framsenteret i 2015 (2014) og innsigelsesforsøket (2017). Etter samme regel er 2009-punktet om å vurdere petroleumsrammene på nytt i 2010 kodet vagt.
2. **Videreføring.** Videreføring uten tall og frist er verken konkret eller vagt. Det gjelder Loran-C (2006), NGU-programmet (2011), Polarforskningsprogrammet og telemedisin (2014), tiltakssonen, arbeidsgiveravgiften og Interreg (2020) samt mineralkartlegging (2025). Når tall og tidspunkt står i teksten, er punktet konkret. Et eksempel er Forskningsløft i nord 2014–2016 (2014).
3. **Retningsverb uten tall** kodes vagt. Eksempler er økt øvingsaktivitet (2011), utvidet kapasitet på Nordlands- og Ofotbanen (2009) og redusert nedbygging av natur (2025). Unntaket er en reduksjon i en administrativt fastsatt størrelse, som maksimaltakstene på flyruter i 2006. Den er kodet konkret.
3b. **Mål uten tall** med frist er verken konkret eller vagt. Det gjelder «tapet stanses innen 2010» (2006) og «lavutslippssamfunn innen 2050» (2025). Det samme gjelder tall uten frist, som minst 50 % av Barents 2020-midlene (2011) og halvert planleggingstid (2014, 2017). Faste frekvenser («årlig», «halvårlige møter», «per år») regnes som tidspunkt.
4. **Internasjonale prosesser.** Er Norge bare «pådriver» eller «arbeider for» noe, kodes punktet vagt. Det gjelder polarkoden i 2009, 2011 og 2014, sotkrav i IMO og planene i Arktisk råd (2014). Er Norge med på å forhandle eller utarbeide resultatet, kodes punktet konkret. Det gjelder samekonvensjonen, oljeverninstrumentet (2011), handlingsplanen for isbjørn og avtalen om fiske i Polhavet (2017).
5. **Blandede punkter** kodes etter den avgrensede leveransen når den er regjeringens egen. Eksempler er sekretariatsansvaret til fylkeskommunene (2017) og investeringsbeslutningen om Mo i Rana i revidert budsjett 2021 (2020). Ellers kodes punktet etter hovedverbet. Et eksempel er «videreføre bredbåndstilskudd; vurdere leveringsplikt» (2020), som er kodet vagt.
6. **Beløp og tidspunkt.** Når 2009- og 2017-dokumentene kom, var budsjettet for samme år allerede vedtatt. Derfor er alle beløp i disse to dokumentene eksisterende. Det gjelder også økningene på 25 og 15 millioner kroner til kultursamarbeid i 2009 og ITS på E8 med 30 millioner kroner i 2017. 2006, 2011, 2014 og 2020 kom mens budsjettforslaget for neste år var til behandling, og nye poster der er kodet som nye. 150 millioner kroner fra UD for 2014–2019 (2014) var satt av før dokumentet kom og er kodet eksisterende. Satser per enhet gir beløpstype, men ikke et beløp i millioner. Det gjelder 8 øre/kWh (2006), 25 000 kroner per lærer (2020) og 500 kroner i barnetrygdtillegg (2025). Marbanks «0» er satt til ingen beløp. 4,1 milliarder kroner til tiltakssonen (2020) er lagt inn fordi beløpet står i tiltaksteksten.
7. **Rapportert eller løfte.** Bevilgninger for inneværende år og vedtatte tiltak som ennå ikke er gjennomført, telles som løfter. Eksempler er 130 millioner kroner til Russland-samarbeid i 2009 og 18,8 millioner kroner til MAREANO. Lovforslag som allerede er fremmet, telles som rapportert, fordi regjeringens del er gjort. Det gjelder minerallova i 2025. Beskrivelser av eksisterende ordninger uten forpliktelse framover er også rapportert. Det gjelder tiltakssonen (2014) og tillegget for idrettsanlegg (2025).
8. **Dubletter.** I 2017 er «over 16 mrd. kroner i første del av NTP» en delmengde av «om lag 40 mrd. kroner til investeringer i nord (NTP 2018–2029)» og er tatt ut. I 2025 kommer «over 1 700 nye arbeidsplasser» fra samme setning og samme plan som «over 50 mrd. kroner i forsvarsinvesteringer i nord» og er tatt ut. Forsvarsløftet på 611 milliarder kroner er beholdt for seg, fordi det er en nasjonal ramme og ikke spesifikt for nord.

## 4. Stikkprøver mot kildeteksten

Sidetall følger konvensjonen for hvert dokument: PDF-side for 2006, 2009, 2014 og 2025, og trykt side for 2011 (lik PDF-side).

| # | Dokument, side | Tiltak | Kildetekst (kort) | Koding |
|---|---|---|---|---|
| 01 | 2006, s. 48 | Døgnvakt ved redningshelikopterbasen i Bodø | 16,5 millioner kroner foreslått i budsjettet for 2007, vakt fra andre halvår 2007 | Konkret, nytt (budsjett 2007 ikke vedtatt 1. desember 2006) |
| 02 | 2006, s. 55 | Såkornfond i Tromsø og Bodø | «Regjeringen har derfor etablert to distriktsrettede såkornfond» | Rapportert, tatt ut |
| 03 | 2009, s. 57 | Økt kultursamarbeid, 40 millioner kroner | Fra 2009 øker innsatsen med 25 millioner kroner fra KUD og 15 millioner kroner fra UD | Konkret, eksisterende (budsjett 2009 vedtatt før 12. mars 2009) |
| 04 | 2009, s. 15 | BarentsWatch | «arbeide videre med utvikling av et mer helhetlig» system | Vagt (var registrert som ikke målbart, nå eksplisitt vagt) |
| 05 | 2011, s. 107 | 5 % vekst i oppdrett i Troms og Finnmark | «Regjeringen har i år åpnet for 5 % vekst» | Rapportert, tatt ut |
| 06 | 2011, s. 71 | Ny grensestasjon på Storskog | Regjeringen går inn for å bygge og kommer tilbake til tidspunktet | Konkret etter (b), uten frist (var ikke målbart) |
| 07 | 2014, s. 22 | Forskningsløft i nord | Forlenget 2014–2016, 100 millioner kroner fordelt i 2014, program siden 2009 | Konkret, eksisterende |
| 08 | 2014, s. 23 | Arktis 2030 | Ny ordning, ramme på 150 millioner kroner for 2015, slår sammen Barents 2020 og Arktisk samarbeid | Konkret, uklart beløp |
| 09 | 2025, s. 27 | Boligtilskudd i finnmarkskommuner med bygdevekstavtale | «Vi har etablert et nytt tilskudd» | Rapportert, tatt ut |
| 10 | 2025, s. 21 | NATO-senter for luftoperasjoner (CAOC) på Reitan | Besluttet å tilby, investeringen «foreløpig anslått» til om lag 4,8 milliarder kroner | Konkret, uklart beløp (anslag, ikke bevilgning) |

Det er også kontrollert enkelte punkter i 2017 og 2020. ITS på E8 (2017, PDF-side 50) har 30 millioner kroner «satt av» i 2017 og er kodet eksisterende. Fiskerikontrollen (2020, trykt s. 92) er «foreslått» styrket med 42 millioner kroner i 2021 og er kodet nytt.

*Kodingen er gjort med `analyse/nordomrade/samordne_lofter.py`, som leser de sju JSON-filene, legger én kode på hvert tiltak og skriver `lofter-samordnet.json`.*
