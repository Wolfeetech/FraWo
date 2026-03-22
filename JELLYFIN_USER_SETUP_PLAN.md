# Jellyfin User Management & Profile Plan

## Goal
Establish a secure, fast-switching user architecture for Jellyfin *before* connecting the first TV client. This ensures personalized tracking, parental controls if needed, and avoids mixing watch histories.

## Required Users
1. **Wolf** (Admin / Main User)
   - Full access to all libraries.
   - Admin rights.
2. **Franz** (Main User)
   - Full access to all libraries.
   - Separate watch history.
3. **Gerätespezifische Profile (z.B. "TV Wohnzimmer")**
   - Shared profile for the living room.
   - Restricted or no admin rights.
   - Quick PIN setup for fast switching.

## Quick User Switching Strategy
Jellyfin supports quick user switching via the "Quick Connect" and PIN features.
- **PIN Login**: Enable PIN login for Wolf and Franz. This allows switching between profiles on the same device without typing out complex passwords.
- **Hidden Users**: Hide administrative or background users from the login screen to keep it clean.
- **Auto-Login**: For the "TV Wohnzimmer" profile, configure auto-login in the TV client. When Wolf or Franz want to watch their own content, they select "Switch User" and enter their 4-digit PIN.

## Action Plan (Operator Execution)
Da die Ersteinrichtung der Benutzer in der Jellyfin Web-UI stattfindet und aktuell keine API-Tokens für eine volle Automatisierung hinterlegt sind, führe bitte folgende Schritte aus:

1. Gehe zu `http://192.168.2.20:8096`.
2. Gehe ins **Dashboard** -> **Benutzer**.
3. Lege die Profile `Wolf`, `Franz` und `TV Wohnzimmer` an.
4. Setze für `Wolf` und `Franz` jeweils eine einfache **PIN** (z.B. 4-stellig) in den Profil-Einstellungen und aktiviere "Login per PIN erlauben".
5. Deaktiviere für das `TV Wohnzimmer`-Profil sämtliche Administrationsrechte.
