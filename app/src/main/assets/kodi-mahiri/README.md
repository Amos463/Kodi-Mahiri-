# KODI MAHIRI 2.1 — Prototype ya majaribio

**Kauli kuu:** Huduma za kodi kwa kila mtu, kila mahali — hata bila intaneti.

KODI MAHIRI ni prototype ya kuonyesha namna mlipakodi anavyoweza kuanzisha mazungumzo ya huduma za kodi kwa njia tatu ndani ya tovuti moja: **USSD (*150#), IVR/Sauti (mfano 0800), na SMS**. Pia ina dashboard ya majaribio ya uchambuzi na audit trail.

> **TAHADHARI:** Hii si bidhaa rasmi ya TRA na haijaunganishwa na TRA, TCRA, kampuni za simu, benki, EFDMS, mifumo ya malipo au vyanzo vya data vya serikali. Hakuna Big Data halisi inayotumika. Miamala yote ya Lipa Namba ya biashara, manunuzi, wasambazaji na alama za uchambuzi zinazotolewa kwenye onyesho ni **DATA ZA MFANO (SIMULATED DEMO DATA)**. Rejea `KM-DEMO-...` si Control Number ya TRA. Viwango vya kodi ni mfano wa programu na lazima vikaguliwe dhidi ya sheria na wataalamu wa kodi kabla ya matumizi yoyote.

## 1. Kuendesha kwenye kompyuta au Termux

Inahitaji Python 3.9+; hakuna maktaba za ziada zinazohitajika.

```bash
cd kodi-mahiri
python3 server.py
```

Fungua kwenye browser:

```text
http://127.0.0.1:8000
```

Majaribio:

```bash
python3 tests.py
```

Seva inasikiliza `127.0.0.1` kwa usalama wa demo. Usibadilishe kuwa `0.0.0.0` wala kuiweka moja kwa moja kwenye public hosting bila authentication, TLS, rate limiting, ulinzi wa siri, database salama na security review.

## 2. Njia tatu ndani ya web prototype

### A. USSD — mfano wa *150#
- Bonyeza vitufe vya simu ya mfano.
- Chagua mkoa, wilaya, aina ya biashara, mauzo ya siku na TIN au chagua kutokuwa na TIN.
- Hakiki taarifa kabla ya kuendelea.
- Chagua kama uonyeshe ulinganisho wa data za mfano.

### B. IVR/Sauti — mfano wa 0800
- Andika `0800` kwenye keypad ya simu ya mfano, kisha bonyeza kitufe kijani.
- Jibu kwa kuandika au kwa sauti ikiwa browser inaunga mkono Web Speech API ya Kiswahili.
- Bila API ya AI ya nje, mfumo hutumia kanuni za Kiswahili zilizopo ndani ya `nlu.py`.
- Sauti ya browser si muunganisho wa simu halisi wala IVR ya telecom.

### C. SMS — mfano wa ujumbe mfupi
- Tumia kisanduku cha SMS kwenye ukurasa.
- Tuma taarifa kama eneo, biashara na mauzo; mfumo hujibu hatua inayofuata.
- Hii ni simulation ya SMS ndani ya web app. Uzalishaji utahitaji SMS Gateway, sender ID/short code na makubaliano ya mtoa huduma.

## 3. Lipa Namba: maana na mipaka ya demo

Katika mradi huu, **Lipa Namba inamaanisha namba ya biashara ya kupokea malipo**, kama Till au Paybill — si namba binafsi ya simu ya mfanyabiashara.

Kwa sasa prototype hutengeneza kitambulisho cha kubuni kama `LIPA-DEMO-123456` na miamala ya mfano inayohusishwa na kitambulisho hicho. Hakuna Till/Paybill halisi inayoulizwa, kuthibitishwa au kuunganishwa.

Moduli ya `transaction_intelligence.py` inaonyesha uainishaji wa majaribio kama:
- Malipo ya biashara kupitia Till/Paybill.
- Rejesho (refund).
- Muamala uliobatilishwa (reversal).
- Mkopo uliopokelewa.
- Uhamisho wa mmiliki.
- Kamisheni ya huduma ya uwakala.

Hizi ni rekodi za kubuni na kanuni za kuelezeka, si AI iliyofunzwa kwa Big Data. Katika mfumo halisi, kila aina ya muamala itahitaji uthibitisho wa chanzo, metadata na msingi wa kisheria. Fedha zilizoingia si sawa moja kwa moja na mauzo yanayotozwa kodi.

## 4. Tax engine na ulinzi dhidi ya makosa

- `engine.py` ina mfano wa hesabu za presumptive tax na assumptions za sekta/msimu.
- Miamala ya demo inaweza kuonyesha tahadhari ya tofauti, lakini **haiwezi kubadilisha mauzo yaliyotajwa wala kuongeza kodi**.
- Kodi ya mfano inakokotolewa kutokana na mauzo yaliyotajwa pekee.
- AI/NLU ni msaidizi wa kukusanya na kuelewa taarifa; haipaswi kuwa mamlaka ya mwisho ya kodi.
- Hakuna Control Number halisi inayotolewa. `KM-DEMO-...` ni rejea ya majaribio tu.
- Jedwali la viwango, misamaha ya biashara mpya, sekta za usafirishaji, masharti ya kumbukumbu na hali maalumu za kodi vinahitaji mapitio ya kitaalamu na utekelezaji wa sheria husika kabla ya pilot.

## 5. Muundo wa mradi

| Faili | Kazi |
|---|---|
| `server.py` | Web server ya ndani, API, mazungumzo, USSD na SMS demo |
| `engine.py` | Mfano wa tax calculation na data bandia za uchambuzi |
| `nlu.py` | Kuelewa Kiswahili kwa kanuni; AI ya nje ni hiari |
| `transaction_intelligence.py` | Kutengeneza na kuainisha miamala ya mfano |
| `ledger.py` | Hash-chain audit trail ya majaribio |
| `geo.py` | Orodha ya mikoa/wilaya ya demo |
| `static/index.html` | Interface ya USSD, IVR, SMS na dashboard |
| `tests.py` | Majaribio ya kiotomatiki |
| `data/` | Faili za ledger huundwa wakati wa kuendesha |

## 6. AI ya nje (hiari kabisa)

Prototype inaweza kutumia mtoa huduma wa AI wa nje ikiwa developer ataweka API key kwenye mazingira ya seva. Bila API key, kanuni za ndani zinaendelea kufanya kazi. Usihifadhi API key ndani ya HTML, GitHub au ZIP ya umma.

Mfano wa kuendesha kwa hiari (weka key yako mwenyewe kwenye mazingira ya seva, usiiweke kwenye faili la project):

```bash
export ANTHROPIC_API_KEY='WEKA_KEY_YAKO_KWA_MAZINGIRA_SALAMA'
python3 server.py
```

Namba za TIN zinachakatwa na kanuni za ndani na zimefichwa kabla ya maandishi kupelekwa kwa mtoa huduma wa AI wa nje. Hata hivyo, kabla ya matumizi halisi, fanya tathmini ya faragha na usalama, na usitume taarifa binafsi bila idhini na msingi wa kisheria unaofaa.

## 7. Vitu vinavyohitaji chanzo/muunganisho wa nje

| Kipengele | Kinachohitajika kabla ya uzalishaji |
|---|---|
| USSD | Mkataba na telecom aggregator/MNO, short code, session API na TCRA/utaratibu husika |
| IVR 0800 | Namba ya bure, SIP/voice gateway, IVR platform na speech-to-text ya Kiswahili |
| SMS | SMS gateway, sender ID/short code, delivery receipts na opt-out policy |
| TIN/TRA | API rasmi, ruhusa na uthibitishaji wa utambulisho |
| Lipa Namba za biashara | APIs/miunganisho iliyoidhinishwa kwa Till/Paybill na taarifa za miamala |
| Benki/mobile money | Makubaliano, API security, data minimization na msingi wa kisheria |
| EFDMS/ mifumo ya TRA | API rasmi, sandbox, uthibitishaji na makubaliano ya TRA |
| Malipo/Control Number | Muunganisho rasmi wa mfumo wa malipo na uthibitisho wa malipo |
| AI ya uzalishaji | Model/API, hosting, privacy review, evaluation ya Kiswahili na ulinzi dhidi ya prompt injection |
| Uzalishaji wa server | Cloud/TRA infrastructure, TLS, IAM, secrets manager, backups, monitoring, incident response |

## 8. Architecture inayolengwa

```text
USSD Gateway ─┐
IVR Gateway ───┼── API Gateway + Identity/Consent
SMS Gateway ──┤                 │
Web/App ──────┘                 ▼
                       Kodi Mahiri Core
              ┌──────────┬───────────┬───────────┐
              │ Swahili  │ Tax Rules│ Transaction│
              │ NLU      │ Engine   │ Intelligence│
              └──────────┴───────────┴───────────┘
                          │
               Audit / Privacy / Security
                          │
             TRA-authorized integrations
```

USSD, IVR, SMS na Web ni njia tofauti za kuingia kwenye core moja. Hivyo demo inaonyesha njia zote tatu kwenye browser; baada ya kupata integrations, kila channel inaweza kuunganishwa kivyake kulingana na eneo, gharama na upatikanaji wa huduma.

## 9. Usalama na mipaka

Hii ni prototype ya kuonyesha mtiririko tu. Haijajengwa kwa matumizi ya umma/uzalishaji: haina login ya maafisa, RBAC kamili, CSRF protection, rate limiting, database ya uzalishaji, KMS/HSM, monitoring ya production wala external audit. Hash-chain ya `ledger.py` ni mfano wa kugundua mabadiliko, si dhamana ya kutobadilishika kabisa. Endpoints za majaribio za kubadilisha/kufuta ledger zipo kwa ajili ya kuonyesha audit test na hazipaswi kuwekwa kwenye uzalishaji.

## 10. Mpango wa hatua zinazofuata

1. Kuthibitisha tax rules na wataalamu wa kodi/TRA.
2. Kuweka database, authentication, roles na audit iliyolindwa.
3. Kutengeneza API contracts na sandbox adapters kwa USSD, IVR na SMS.
4. Kutengeneza test data inayotambulika wazi na scenario za refund, reversal, mkopo, uhamisho na commission.
5. Kufanya privacy impact assessment, threat modelling na penetration testing.
6. Kuomba pilot yenye data na idhini rasmi kutoka kwa taasisi husika.

---

**Kumbuka kwa majaji:** prototype inaonyesha user journey na architecture ya channel tatu; data za miamala ni bandia na zimewekewa alama. Muunganisho wa telecom, benki, TRA, EFDMS na mifumo ya malipo ni kazi ya awamu inayohitaji ushirikiano rasmi.

## Toleo 2.1 — reconciliation + officer workflow
- Transaction evidence is reconciled separately from declared turnover. Lipa Namba demo estimate can trigger a review recommendation when the ratio is above 1.3x.
- The initial tax remains based on the taxpayer's declaration. The proposed post-review amount is explicitly separate and cannot change tax automatically.
- TIN purchase records are corroborative only; they are not added to sales.
- Officer dashboard separates payment verification from tax risk. No payment is shown as paid without an authorized provider callback.
- Objections and officer actions are stored as simulated demo records.
- `integrations/contracts.py` defines adapter interfaces for USSD, SMS, IVR, transaction providers, TRA and payment providers. No external service is connected in this ZIP.
- Destructive ledger test endpoints are disabled unless `KODI_MAHIRI_DEMO_ADMIN=1` is set for local testing only.

Run tests: `python3 tests.py`
Run local demo: `python3 server.py` then open `http://127.0.0.1:8000`.
