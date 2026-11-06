# External integration adapters

Core ya KODI MAHIRI haitategemea vendor mmoja. `contracts.py` ina interfaces tu; hakuna API call inayotekelezwa wala credentials zilizowekwa.

## Mlolongo wa kuunganisha
1. Pata idhini, mkataba, API specification na sandbox ya kila taasisi.
2. Tengeneza adapter ya vendor inayotekeleza interface husika; weka secrets kwenye environment/secret manager, si Git.
3. Thibitisha signature, TLS, OAuth/mTLS, idempotency, retries, rate limits na audit logs.
4. Fanya sandbox/UAT na reconciliation; kisha pilot ndogo yenye ruhusa.
5. Washa feature flag husika baada ya security, privacy na legal approval.

| Mfumo | Interface | Inahitajika kabla ya live |
|---|---|---|
| USSD/MNO/aggregator | `USSDGateway` | short code, session callbacks, API docs |
| SMS gateway | `SMSGateway` | sender ID, consent, delivery receipts |
| IVR/0800/SIP | `IVRGateway` | toll-free number, SIP/IVR, Kiswahili ASR/TTS |
| Till/Paybill/financial data | `BusinessTransactionProvider` | biashara ownership proof, consent/legal basis, API access |
| TRA/TIN/EFDMS | `TaxAuthorityProvider` | TRA approval, sandbox, official API contract |
| Official payment | `PaymentProvider` | authorized payment provider and signed callbacks |

Demo mode remains the default. Synthetic records must never be sent to external systems or described as verified evidence. TIN purchase records are corroborative only; they are not automatically turnover. No tax adjustment, penalty, control number, or paid status may be issued by this prototype.
