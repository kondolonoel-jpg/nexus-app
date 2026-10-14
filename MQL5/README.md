# Accurate Trend Indicator — MetaTrader 5

Fichier de l'indicateur : `Indicators/AccurateTrendIndicator.mq5`

## Installation

1. Dans MetaTrader 5, ouvrez **Fichier → Ouvrir le dossier des données**.
2. Copiez `AccurateTrendIndicator.mq5` dans `MQL5/Indicators/`.
3. Ouvrez MetaEditor, compilez le fichier avec **F7**, puis ajoutez **Accurate Trend Indicator** au graphique voulu.

## Signaux et alertes en temps réel

- Les croisements du cours de clôture courant avec la ligne Supertrend calculent les signaux **BUY** et **SELL** sur la bougie en formation.
- Les alertes sont envoyées dès que le croisement est détecté, sans attendre la clôture de la bougie. Pour éviter les répétitions à chaque tick, une transition de signal n'est notifiée qu'une fois ; un nouveau croisement ultérieur sur la même bougie peut déclencher une nouvelle alerte.
- L'indicateur ne rejoue pas les alertes historiques ni un signal déjà actif au moment où il est ajouté au graphique : la surveillance commence à son initialisation.
- Comme le cours et le Supertrend évoluent jusqu'à la clôture, un signal intrabougie peut disparaître si le marché revient de l'autre côté. Les notifications déjà envoyées ne peuvent pas être annulées.
- Les bougies reprennent la couleur du dernier signal : vert après BUY, rouge après SELL. Les étiquettes BUY/SELL sont placées sous/au-dessus de la bougie du signal.

Les canaux sont activés par défaut et peuvent être réglés dans les paramètres de l'indicateur :

- **Texte** : alerte MetaTrader (`Alert`).
- **Son** : fichier `alert.wav` par défaut, à placer dans le dossier `Sounds` du terminal si nécessaire.
- **Push mobile** : dans MetaTrader, ouvrez **Outils → Options → Notifications**, activez les notifications push, renseignez le MetaQuotes ID de l'application mobile puis utilisez **Test**. L'indicateur ne peut pas configurer ce réglage à la place de l'utilisateur.

## Paramètres

| Paramètre | Valeur initiale | Description |
|---|---:|---|
| ATR length | 10 | Période de l'ATR de Wilder |
| Supertrend multiplier | 3.0 | Multiplicateur de l'ATR |
| Mobile push | Activé | Envoi sur l'application MetaTrader mobile |
| Sound | Activé | Lecture du fichier sonore choisi |
| Text alert | Activé | Fenêtre d'alerte textuelle MetaTrader |
| Sound file | `alert.wav` | Nom du son dans le dossier `Sounds` |

Copyright : **KONDOLO NOEL — kondolonoel@gmail.com**.
