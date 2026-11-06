# Orodha ya maandalizi ya muunganisho (kwa timu ya utekelezaji)

Hati hii inaeleza kazi zinazobaki nje ya prototype. Hakuna muunganisho ulioorodheshwa hapa ambao tayari umetekelezwa.

## USSD
- [ ] Chagua aggregator/MNO na uthibitishe upatikanaji wa short code.
- [ ] Pata API specification, session lifecycle, timeout, callback na retry rules.
- [ ] Tengeneza adapter tofauti na core; usiweke logic ya kodi ndani ya gateway.
- [ ] Jaribu session expiry, kuendelea/kurudi nyuma, network timeout na double-submit.

## IVR / 0800
- [ ] Pata namba ya bure na SIP/voice gateway.
- [ ] Chagua IVR platform na speech-to-text inayotathminiwa kwa Kiswahili cha Tanzania.
- [ ] Weka keypad fallback, replay, human handoff na confirmation kabla ya kutuma taarifa.
- [ ] Pima lafudhi, kelele za sokoni, majina ya maeneo na matamshi ya fedha.

## SMS
- [ ] Pata SMS gateway na sender ID/short code iliyoidhinishwa.
- [ ] Tekeleza delivery receipts, retries, message segmentation na opt-out.
- [ ] Zuia SMS spoofing na usiweke TIN kamili kwenye SMS ya kawaida.

## Lipa Namba za biashara / data za fedha
- [ ] Tumia business Till/Paybill identifier, si namba binafsi ya simu.
- [ ] Pata ruhusa na API docs kutoka kwa watoa huduma husika.
- [ ] Thibitisha ownership ya namba ya biashara na uhusiano wake na TIN.
- [ ] Tofautisha mauzo, refund, reversal, mkopo, uhamisho na commission.
- [ ] Hakikisha miamala inayojirudia, settlement na partial refund vinashughulikiwa.
- [ ] Tumia data minimization, retention rules na access logging.

## TRA / kodi / malipo
- [ ] Thibitisha sheria na viwango na wataalamu wa kodi.
- [ ] Pata sandbox na API contracts rasmi kutoka TRA.
- [ ] Tumia tax rules versioning na tarehe ya kuanza kutumika kwa kila kanuni.
- [ ] Control Number itolewe na mfumo rasmi pekee; prototype reference si Control Number.
- [ ] Thibitisha malipo kupitia callback/verification ya mfumo rasmi kabla ya kuonyesha paid.
- [ ] Weka njia ya marekebisho, objection na appeal yenye audit trail.

## Usalama na uendeshaji
- [ ] Threat model, DPIA na legal review.
- [ ] Authentication, MFA, RBAC/ABAC na least privilege.
- [ ] TLS, encryption at rest, KMS/HSM na secret rotation.
- [ ] Rate limiting, WAF, input validation, CSRF protection na secure headers.
- [ ] PostgreSQL, backups, disaster recovery na retention policy.
- [ ] Centralized logs, monitoring, alerting na incident response.
- [ ] Penetration test na independent security review kabla ya pilot.
