import argparse
import gzip
import glob
import re
from collections import Counter
import subprocess

# Funktion zum Lesen der Bounce-Meldungen aus den Protokolldateien
def read_maillog_processed(file_paths, domain_filter=None):
    bounce_reasons = []
    rejected_logs = []
    bounced_logs = []
    for file_path in file_paths:
        with gzip.open(file_path, 'rt') if file_path.endswith('.gz') else open(file_path, 'r') as file:
            for line in file:
                # Regex-Muster zum Extrahieren der E-Mail-Adresse
                match = re.search(r"to=<([^@]+@[^>]+)>", line)
                if match:
                    email = match.group(1)
                    if domain_filter and domain_filter.lower() not in email.lower():
                        continue
                    # Regex-Muster zum Extrahieren des Bounce-Grundes
                    match = re.search(r"status=(\w+)", line)
                    if match:
                        bounce_reason = match.group(1)
                        bounce_reasons.append(bounce_reason)
                        if bounce_reason == "rejected":
                            rejected_logs.append(line.strip())
                        elif bounce_reason == "bounced":
                            bounced_logs.append(line.strip())
    return bounce_reasons, rejected_logs, bounced_logs

# Funktion zur Anzeige der abgelehnten Protokolleinträge
def display_rejected_logs(rejected_logs):
    if rejected_logs:
        print("----------------------------------------")
        print("❌ REJECTED LOGS")
        print("----------------------------------------")
        for log in rejected_logs:
            print(log)
        print("\n\n")

# Funktion zur Anzeige der zurückgeworfenen Protokolleinträge
def display_bounced_logs(bounced_logs):
    if bounced_logs:
        print("----------------------------------------")
        print("💥  BOUNCED LOGS")
        print("----------------------------------------")
        for log in bounced_logs:
            print(log)
        print("\n\n")

# Funktion zur Anzeige der Statistik der Bounce-Gründe
def display_bounce_reason_statistics(bounce_reasons, domain_filter=None):
    bounce_reason_counts = Counter(bounce_reasons)
    print("----------------------------------------")
    print("mlog.py", f" (Filtered: {domain_filter})" if domain_filter else "")
    print("----------------------------------------")
    print(f"✅ Sent (Erfolgreich zugestellt):                           {bounce_reason_counts.get('sent', 0)}")
    print(f"⏳ Deferred (Vorübergehende Verzögerung der Zustellung):    {bounce_reason_counts.get('deferred', 0)}")
    print(f"❌ Rejected (Zustellung abgelehnt):                         {bounce_reason_counts.get('rejected', 0)}")
    print(f"💥 Bounced (Zustellung fehlgeschlagen):                     {bounce_reason_counts.get('bounced', 0)}")
    print("\n\n")

# Funktion zur Anzeige der Statistik der 550-Fehlercodes für die bounced_logs
def display_bounced_error_statistics(bounced_logs):
    error_messages = {
        "550-5.1.1 The email account that you tried to reach does not exist",
        "550-Unrouteable address 550 Sender verify failed",
        "550-5.7.26  DKIM = did not pass",
        "Access denied"
        "Address rejected",
        "Domain has exceeded the max emails per hour (250)",
        "Host not found",
        "Mail quota exceeded",
        "Mailbox full",
        "No such recipient",
        "No such user",
        "No such user",
        "Recipient address rejected:",
        "Refused by local policy. No SPAM please!",
        "Relay access denied",
        "This mail has been blocked because the sender is unauthenticated",
        "Unable to deliver message to the following address(es)",
        "User mailbox exceeds allowed size",
        "User unknown in virtual alias table",
        "domain not found",
        "mailbox unavailable",
        "This address no longer accepts mail."
    }
    error_counts = Counter()
    for log in bounced_logs:
        for error_message in error_messages:
            if error_message in log:
                error_counts[error_message] += 1
    print("========================================")
    print("BOUNCED ERROR STATISTICS")
    print("========================================\n")
    for error_message, count in error_counts.items():
        print(f"{error_message}: {count}")
    print("\n")


def display_mailboxes():
    command = "plesk bin mail --list | awk '{print $2}' | sort | uniq | grep -v name"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_str = result.stdout.decode('utf-8') if result.stdout else ''
    stderr_str = result.stderr.decode('utf-8') if result.stderr else ''

    if result.returncode == 0:
        print("----------------------------------------")
        print("Alle Postfächer\n")
        print("----------------------------------------")
        print(stdout_str)
        print("\n")
        print("\n")
    else:
        print("Fehler beim Abrufen der Mailboxen:", stderr_str)

# Funktion zum Anzeigen von DKIM-Fehlern
def display_dkim_failures(file_paths):
    dkim_failures = {}
    for file_path in file_paths:
        with gzip.open(file_path, 'rt') if file_path.endswith('.gz') else open(file_path, 'r') as file:
            for line in file:
                if "Gmail requires all senders to authenticate with either SPF or DKIM" in line:
                    match = re.search(r"from=<([^@]+@[^>]+)>,.*to=<([^@]+@gmail.com)>", line)
                    if match:
                        sender_email = match.group(1)
                        recipient_email = match.group(2)
                        dkim_failures[sender_email] = recipient_email

    if dkim_failures:
        print("E-Mails mit DKIM-Fehlern, die nicht an Gmail gesendet werden konnten:")
        for sender_email, recipient_email in dkim_failures.items():
            print(f"Sender: {sender_email}, Empfänger: {recipient_email}")
    else:
        print("Keine E-Mails mit DKIM-Fehlern gefunden, die nicht an Gmail gesendet werden konnten.")




# Hauptprogramm
def main():
    # Konfigurieren des Argumentparsers
    parser = argparse.ArgumentParser(description='Analyze mail logs.')
    parser.add_argument('--verbose', '--log','-v', action='store_true', help='Show detailed logs for rejected and bounced emails.')
    parser.add_argument('--all','-a', action='store_true', help='Process all maillog.processed files.')
    parser.add_argument('--domain','-d', help='Filter logs for a specific domain.')
    parser.add_argument('-b', '--Bounced', action='store_true', help='Show statistics of bounced emails.')

    parser.add_argument("--mlist", "-m", action="store_true", help="Display all mailboxes on the server")

    parser.add_argument('--dkim', action='store_true', help='Show DKIM failures.')

    # Parse-Befehlszeilenargumente
    args = parser.parse_args()

    # Definieren Sie den Dateipfad zur maillog.processed Datei
    if args.all:
        maillog_processed_files = glob.glob("/var/log/maillog.processed*")
    else:
        maillog_processed_files = ["/var/log/maillog.processed"]

    # Lesen Sie die Bounce-Gründe und die Protokolleinträge aus den Protokolldateien
    bounce_reasons, rejected_logs, bounced_logs = read_maillog_processed(maillog_processed_files, args.domain)

    # Wenn --verbose angegeben ist, zeigen Sie die abgelehnten und zurückgeworfenen Protokolleinträge an
    if args.verbose:
        display_rejected_logs(rejected_logs)
        display_bounced_logs(bounced_logs)

    # Wenn -b oder --Bounced angegeben ist, zeigen Sie die Statistik der 550-Fehlercodes für die bounced_logs an
    if args.Bounced:
        display_bounced_error_statistics(bounced_logs)

    if args.mlist:
            display_mailboxes()

    if args.dkim:
        display_dkim_failures(maillog_processed_files)

    # Anzeigen der Statistik der Bounce-Gründe
    display_bounce_reason_statistics(bounce_reasons, args.domain)



if __name__ == "__main__":
    main()
