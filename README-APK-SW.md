# KODI MAHIRI 2.1 — Android APK (Hybrid Offline Demo)

## Muundo
- APK ina WebView ya Android.
- Python 3.11 backend inaendeshwa ndani ya app kupitia Chaquopy.
- Backend inasikiliza `127.0.0.1:8765` pekee; haifungui port kwa mtandao.
- HTML, Python modules na data za mfano zimefungwa ndani ya APK.
- Demo ya msingi (USSD, IVR/Sauti, SMS, hesabu, reconciliation, afisa na pingamizi) inaendeshwa ndani ya simu bila internet.
Huduma za TRA, USSD za mtandao wa simu, SMS halisi, IVR/0800, na data za fedha bado ni simulation/adapters za baadaye.
Hii ni offline-first demo yenye backend ya ndani; si mfumo wa offline/online synchronization. Uunganishaji wa seva za nje utaongezwa baada ya kupata API na ruhusa.

## Kujenga APK kupitia GitHub Codespaces
1. Pakia yaliyomo kwenye folda hii kwenye repository (au unzip hapa).
2. Commit na push kwenye `main` au `master`.
3. Fungua GitHub repository > Actions > **Build KODI MAHIRI APK**.
4. Subiri workflow ikamilike.
5. Fungua run iliyofanikiwa > Artifacts > `kodi-mahiri-2.1-debug-apk`.
6. Download ZIP ya artifact, ifungue, kisha sakinisha `app-debug.apk` kwenye Android.

Unaweza pia kuanzisha build kwa mikono kupitia Actions > Build KODI MAHIRI APK > Run workflow.

## Mahitaji
- Android 7.0+ (API 24+).
- Build hutumia Java 17, Gradle 8.11.1, Android SDK 35, Chaquopy 16.1.0.
- APK ya debug ni ya majaribio; kabla ya uzalishaji tengeneza release signing key salama.

## Ruhusa
- INTERNET: WebView hutumia loopback ya kifaa; ruhusa pia inaruhusu integrations za baadaye lakini hakuna provider iliyowashwa.
- RECORD_AUDIO: kwa jaribio la sauti; Web Speech hutegemea uwezo wa Android WebView na huduma za kifaa. Uandishi wa maandishi unabaki kama fallback.

## Data na usalama
- Data ya demo huhifadhiwa kwenye private app storage.
- Kufuta app kunaweza kufuta data ya ndani.
- Hakuna data halisi ya TRA/benki/mobile money iliyounganishwa.
- Usitumie data binafsi au za walipakodi halisi kwenye demo.
- Usisambaze debug APK kama toleo la production.
