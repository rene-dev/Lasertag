# Lasertag
pew pew!
Ein freies und offenes Lasertag Projekt der warpzone in Münster.

## Aktueller Stand
Hard- und Software haben viele Kinderkrankheiten, spielbar ist es noch nicht. Es existieren 2 Waffel-Prototypen mit tiefgezogenen Gehäusen und ein Paar Hitpoints. Westen wollen noch gebaut werden.
* __Hitpoint__: voll funktionsfähig aber dirty gecoded
* __Lasermodul__: Im groben funktioniert alles. Einige Pins sind falsch beschriftet. IR funktioniert, sendet auch ganz leicht wenn es nicht senden soll. Sound ist viel zu leise.
* __Pi__: Da ist noch einiges zu tun. Grundlegende Kommunikation mit den Modulen ist möglich. Grundlegender Server Client per TCP.

## Grundstruktur
In jeder Waffel steckt ein Raspberry Pi, ein Lasermodul und ein Hitpoint. Das Lasermodul ist ein HAT für den Pi und dient als Schnittstelle zur Waffel-Hardware. Die High-Level Kommunikation (Spielmodus, Powerups, Map, ...) zwischen den Pis läuft per WLAN. Die Low-Level Kommunikation (Player-ID, Schaden) per gebündeltem IR-LED-UART auf TSOP-Empfänger.

### Raspberry Pi
In Python wird Netzwerk gemacht, per I2C die Module angesprochen und das SPI-Touch-Display angesteuert.

### Lasermodul
Kommt in jede Waffel:
* Atmega 328p
* IR-LED zum Daten senden
* roten Laser, damit man auch was sieht (Klasse 1 mit deutschem Zertifikat)
* starke RGBW ansteuern für Lichteffekte
* Trefferzone über einen Front-TSOP
* Taster auslesen
* LiPo auf 5V Step-Up Wandler
* An-Aus Taster
* Akkuüberwachung
* Audioverstärker

### Hitpoint
Kommt in jede Waffel und mehrere an die Weste (Schultern, Bauch, Rücken, ...):
* Attiny 2313A
* 4 10mm RGB-LEDs
* 4 TSOP-IR-Empfänger
