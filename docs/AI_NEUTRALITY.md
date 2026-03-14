# Viten API: KI Neutralität & Prompting Regeln

Da die Viten API im hochsensiblen politischen Raum operiert, sind die System-Prompts für die interne LLM-Verarbeitung (Claim Extraction & Verification) strengstens zu regulieren.

## 1. Die goldene Regel der Neutralität
Das System bewertet **Aussagen**, niemals **Personen, Parteien oder Ideologien**. 
- FALSCH: "Prüfe, ob der AfD-Politiker hier lügt."
- RICHTIG: "Extrahiere überprüfbare Fakten aus folgendem Text und gleiche sie mit Datenbank Y ab."

## 2. Definition der "Verdicts" (Urteile)
Wenn die RAG-Pipeline eine Behauptung bewertet, müssen diese strikten Definitionen angewandt werden:
- **SUPPORTED:** Die offizielle Datenlage (z.B. Destatis) oder der breite wissenschaftliche Konsens stützt die Behauptung eindeutig.
- **REFUTED:** Die Behauptung widerspricht eindeutig den offiziellen Zahlen oder dem wissenschaftlichen Konsens.
- **MIXED:** Die Behauptung ist teilweise wahr, lässt wichtigen Kontext weg (Cherry-Picking) oder die Datenlage ist ambivalent.
- **INCONCLUSIVE:** Es gibt nicht genug verlässliche Daten, um die Behauptung objektiv zu prüfen (z.B. bei reinen Prognosen oder ethischen Werturteilen).

## 3. Claim Extraction (Behauptungen filtern)
Nicht jeder Satz ist eine Behauptung. Das LLM muss trainiert/gepromptet werden, um Meinungen von überprüfbaren Fakten zu trennen.
- Meinung (Ignorieren): "Die Steuern in Deutschland sind viel zu hoch und ungerecht."
- Überprüfbarer Fakt (Extrahieren): "Deutschland hat die höchste Steuerlast aller OECD-Staaten."

## 4. Quellen-Priorisierung im RAG-Prozess
Bei der Suche nach Belegen gilt folgende Hierarchie:
1. Amtliche Statistiken (Destatis, Bundesbank, Eurostat).
2. Wissenschaftliche Dienste des Bundestages & Ministerien (BAMF, UBA).
3. Peer-Reviewte Studien & renommierte Wirtschaftsinstitute (ifo, DIW).
4. Medienberichte dürfen NUR herangezogen werden, wenn sie direkt auf primäre, öffentliche Dokumente verlinken.