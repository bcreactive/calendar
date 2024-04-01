Dies ist ein einfacher Kalender, den ich mit Python und Kivy erstellt habe.
Benutzer können an beliebigem Datum einen Eintrag erstellen, speichern, ändern und löschen.
Der heutige Tag, sowie Tage mit abgespeicherten Notizen werden farblich hervorgehoben.
Wischen nach links oder rechts blättert die Monate vor-/rückwärts.
Mit dem Set-Button (oder mittels Wischen nach oben) öffnet sich ein Auswahlfenster: 
Hier kann ein beliebiger Tag gewählt werden und die jeweilige Tagesansicht öffnet sich.
Wird nicht der aktuelle Monat angezeigt, ändert sich der Set-Button zu einem Home-Button.
Damit kann direkt auf den aktuellen Monat gewechselt werden.

builds: Benutzung auf eigenes Risiko!/Use at your own risk!)
-----------------------------------------------------------

Windows: exe mit Pyinstaller erstellt. Wichtig ist, dass
die Datei save_file.json im gleichen Verzeichnis liegt wie die calendar.exe.

Android: apk mit buildozer erstellt. 
