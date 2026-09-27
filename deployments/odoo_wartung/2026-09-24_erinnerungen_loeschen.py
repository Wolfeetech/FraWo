# 🤖 [Claude] 24.09.2026 — 30 automatische Erinnerungen (Frist-Kopien, "Blocker prüfen", leere Agent-Vorschlaege) leise loeschen. Freigabe Wolf 24.09.2026
COMMIT = __COMMIT__
ERWARTET = {459:1092, 436:845, 437:845, 438:844, 439:844, 440:846, 441:846, 442:847, 443:847,
            502:1099, 503:377, 526:1045, 527:1051, 528:1199, 529:1200, 530:1201, 531:465, 532:905,
            539:467, 542:1263, 545:1268, 556:1422, 584:1047, 586:1462,
            588:953, 589:1265, 590:1266, 591:1267, 592:1272, 593:1274}
ctx = dict(tracking_disable=True, mail_notrack=True, dont_notify=True, mail_auto_subscribe_no_notify=True)
def notif():
    env.cr.execute("select count(*) from mail_notification where res_partner_id=7")
    return env.cr.fetchone()[0]
vorher = notif()
acts = env['mail.activity'].with_context(ctx).browse(list(ERWARTET)).exists()
for a in acts:
    assert a.res_model == 'project.task' and a.res_id == ERWARTET[a.id], "Abweichung bei %s" % a.id
    assert a.summary and (a.summary.startswith('⏰ Frist:') or a.summary.startswith('Blocker prüfen') or a.summary.startswith('Agent-Vorschlag')), "Unerwarteter Text bei %s: %s" % (a.id, a.summary)
print("gefunden:", len(acts), "von", len(ERWARTET))
acts.unlink()
env.cr.execute("select count(*) from mail_activity where user_id=6 and date_deadline < current_date")
print("Ueberfaellige Erinnerungen Wolf danach:", env.cr.fetchone()[0], "| neue Meldungen:", notif() - vorher)
if COMMIT:
    env.cr.commit(); print("COMMIT")
else:
    env.cr.rollback(); print("ROLLBACK (Probelauf)")
