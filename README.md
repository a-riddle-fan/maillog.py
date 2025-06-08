# Ein einfacher Analysator für Postfix-Mail-Logs.

`maillog.py` ist ein Kommandozeilen-Tool, das `maillog.processed`-Dateien analysiert, um einen schnellen Überblick über den E-Mail-Zustellstatus zu geben. Es aggregiert Statistiken zu gesendeten, zurückgestellten, abgelehnten und fehlgeschlagenen E-Mails und bietet Optionen für eine tiefere Analyse.
Ziel ist die häufigsten Analyse-Aufgaben, um Probleme bei der E-Mail-Zustellung schnell zu diagnostizieren.

## Funktionen

*   **Schnelle Statistik**: Zeigt eine Zusammenfassung der Zustellstati (Sent, Deferred, Rejected, Bounced).
*   **Log-Aggregation**: Verarbeitet automatisch die aktuelle `maillog.processed` sowie komprimierte Archive (`.gz`).
*   **Domain-Filterung**: Isoliert die Analyse auf eine bestimmte Empfängerdomain.
*   **Detaillierte Fehleranalyse**: Listet die genauen Log-Einträge für abgelehnte und fehlgeschlagene E-Mails auf.
*   **Bounce-Analyse**: Zählt die häufigsten Gründe für fehlgeschlagene Zustellungen (Bounces).
*   **Plesk-Integration**: Kann alle konfigurierten Postfächer über das Plesk-CLI auflisten.
*   **DKIM-Fehlererkennung**: Identifiziert spezifische DKIM-Fehler im Zusammenhang mit Gmail-Richtlinien.

## Voraussetzungen

*   Python 3
*   Zugriff auf die Mail-Logs des Servers (typischerweise `/var/log/maillog.processed*`).
*   Für die Funktion `--mlist`: Das Skript muss auf einem Server mit **Plesk** ausgeführt werden, und der ausführende Benutzer benötigt die Berechtigung, `plesk bin mail` auszuführen.

## Installation

Es ist keine komplexe Installation erforderlich. Laden Sie das Skript einfach auf Ihren Server und machen Sie es ausführbar.

```bash
wget https://your-repo-url/maillog.py
chmod +x maillog.py
```

## Verwendung

```
usage: maillog.py [-h] [--verbose] [--all] [--domain DOMAIN] [-b] [--mlist] [--dkim]

Analyze mail logs.

optional arguments:
  -h, --help            show this help message and exit
  --verbose, --log, -v  Show detailed logs for rejected and bounced emails.
  --all, -a             Process all maillog.processed files.
  --domain DOMAIN, -d DOMAIN
                        Filter logs for a specific domain.
  -b, --Bounced         Show statistics of bounced emails.
  --mlist, -m           Display all mailboxes on the server
  --dkim                Show DKIM failures.
```

## Parameter

| Option | Langform | Beschreibung |
|---|---|---|
| `-h` | `--help` | Zeigt die Hilfe-Nachricht an und beendet das Programm. |
| `-v` | `--verbose`, `--log` | Zeigt die detaillierten Log-Einträge für `rejected` und `bounced` E-Mails. Nützlich für eine tiefere Ursachenforschung. |
| `-a` | `--all` | Analysiert alle gefundenen Logdateien (`/var/log/maillog.processed*`), einschließlich der rotierten und komprimierten (`.gz`). Standardmäßig wird nur die aktuelle Datei analysiert. |
| `-d DOMAIN` | `--domain DOMAIN` | Filtert die gesamte Analyse auf E-Mails, die an die angegebene Domain gesendet wurden. Der Vergleich ist nicht case-sensitive. |
| `-b` | `--Bounced` | Zeigt eine detaillierte Statistik der Fehlerursachen für als `bounced` markierte E-Mails an. Hilft, wiederkehrende Probleme wie "User unknown" oder "Mailbox full" zu identifizieren. |
| `-m` | `--mlist` | Führt `plesk bin mail --list` aus, um eine Liste aller auf dem Server konfigurierten E-Mail-Postfächer anzuzeigen. **Plesk erforderlich.** |
| | `--dkim` | Durchsucht die Logs nach spezifischen DKIM-Fehlermeldungen, die von Gmail zurückgewiesen wurden, und zeigt die betroffenen Absender an. |

## Beispiele

**1. Schnelle Statistik der aktuellen Logdatei anzeigen:**
```bash
./maillog.py
```

**2. Statistik über alle verfügbaren Logdateien (inkl. Archive) erstellen:**
```bash
./maillog.py -a
```

**3. Alle E-Mails an `beispiel.com` analysieren und die genauen Log-Einträge für Fehler anzeigen:**
```bash
./maillog.py -d beispiel.com -v
```

**4. Eine detaillierte Aufschlüsselung der Bounce-Gründe für alle Logs erhalten:**
```bash
./maillog.py -ab
```
*(Kombination von `--all` und `--Bounced`)*

**5. Alle auf dem Plesk-Server konfigurierten Mailboxen auflisten:**
```bash
./maillog.py -m
```

**6. Nach DKIM-Problemen im Zusammenhang mit Gmail-Zustellungen suchen:**
```bash
./maillog.py -a --dkim
```

## Beispiel-Ausgabe

Eine typische Ausgabe von `./maillog.py -d beispiel.com` könnte so aussehen:

```
----------------------------------------
maillog.py  (Filtered: beispiel.com)
----------------------------------------
✅ Sent (Erfolgreich zugestellt):                           1402
⏳ Deferred (Vorübergehende Verzögerung der Zustellung):    15
❌ Rejected (Zustellung abgelehnt):                         23
💥 Bounced (Zustellung fehlgeschlagen):                     8


```

Bei Verwendung von `./maillog.py -b`:

```
========================================
BOUNCED ERROR STATISTICS
========================================

550-5.1.1 The email account that you tried to reach does not exist: 5
User unknown in virtual alias table: 2
Mailbox full: 1

```

Bei Verwendung von `./maillog.py -v`:

```
----------------------------------------
❌ REJECTED LOGS
----------------------------------------
postfix/smtpd[12345]: NOQUEUE: reject: RCPT from mail-server.sender.com[1.2.3.4]: 554 5.7.1 <recipient@beispiel.com>: Relay access denied; from=<sender@external.com> to=<recipient@beispiel.com> proto=ESMTP helo=<mail-server.sender.com>
...

----------------------------------------
💥  BOUNCED LOGS
----------------------------------------
postfix/smtp[23456]: 1A2B3C4D: to=<user.does.not.exist@beispiel.com>, relay=mx.beispiel.com[5.6.7.8]:25, delay=0.5, delays=0.1/0/0.2/0.2, dsn=5.1.1, status=bounced (host mx.beispiel.com[5.6.7.8] said: 550 5.1.1 <user.does.not.exist@beispiel.com>... User unknown)
...

```
