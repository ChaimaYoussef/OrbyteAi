# Guide de Déploiement Local Multi-Appareils (LAN / WiFi) — Orbyte

Ce guide explique comment déployer et partager **Orbyte** sur un réseau local (WiFi de la faculté, réseau d'entreprise ou domicile) afin que plusieurs utilisateurs puissent se connecter depuis leurs propres appareils (smartphones, tablettes, PC portables) sans rien installer.

---

## ⚡ Résumé Rapide : Accessibilité réseau

> **Accessibilité depuis d'autres appareils : OUI (Conditionnel)**
> 
> **Conditions de succès :**
> 1. Les appareils doivent être connectés au **même réseau WiFi / LAN**.
> 2. Le pare-feu du PC hôte (Windows Firewall) doit autoriser les connexions entrantes sur le port **3000** (ou 80).
> 3. Le point d'accès WiFi ne doit pas activer l'**Isolation AP / Client Isolation** (paramètre réseau interdisant aux appareils WiFi de communiquer entre eux).

---

## 📂 Fichiers de Déploiement Créés / Modifiés

| Fichier | Rôle |
|---|---|
| [`start.bat`](file:///c:/Users/LENOVO/Desktop/orbyte%20ahmed/orbyte-master/orbyte-master/start.bat) | Script automatique Windows (CMD/PowerShell) qui détecte l'IP LAN, injecte les variables `WEB_DOMAIN` et `CORS_ALLOWED_ORIGIN` et lance Docker Compose. |
| [`DEPLOYMENT_LOCAL.md`](file:///c:/Users/LENOVO/Desktop/orbyte%20ahmed/orbyte-master/orbyte-master/DEPLOYMENT_LOCAL.md) | La présente documentation de déploiement multi-utilisateurs. |
| [`deployment/docker_compose/docker-compose.yml`](file:///c:/Users/LENOVO/Desktop/orbyte%20ahmed/orbyte-master/orbyte-master/deployment/docker_compose/docker-compose.yml) | Service Nginx mappé sur `"${HOST_PORT:-3000}:80"` (écoute sur `0.0.0.0` sur l'hôte). |
| [`deployment/docker_compose/.env`](file:///c:/Users/LENOVO/Desktop/orbyte%20ahmed/orbyte-master/orbyte-master/deployment/docker_compose/.env) | Configuration locale sécurisée avec secrets régénérés. |

---

## 🚀 Guide de Démarrage Rapide (Machine Hôte)

### Étape 1 : Prérequis sur le PC hôte
- Windows 10/11 ou Linux/macOS avec **Docker Desktop** ou **Docker Engine + Docker Compose v2+**.
- Le PC hôte doit être connecté au WiFi/LAN de la faculté.

### Étape 2 : Lancement automatique
Sur le PC hôte, exécutez le script à la racine du projet :

- **Sur Windows :** Double-cliquez sur [`start.bat`](file:///c:/Users/LENOVO/Desktop/orbyte%20ahmed/orbyte-master/orbyte-master/start.bat) (ou lancez `cmd.exe /c start.bat` dans un terminal).

Le script effectue automatiquement les opérations suivantes :
1. Détection de l'adresse IP IPv4 locale active sur votre carte WiFi/Ethernet (ex: `192.168.1.42`).
2. Injection dynamique des variables d'environnement :
   - `WEB_DOMAIN=http://192.168.1.42:3000`
   - `CORS_ALLOWED_ORIGIN=http://192.168.1.42:3000,http://localhost:3000`
3. Affichage de l'URL claire à partager à vos utilisateurs.
4. Lancement des conteneurs via `docker compose up -d`.

---

## 📱 Instructions pour les utilisateurs invités

Les utilisateurs qui se connectent n'ont **absolument rien à installer**.

1. Connectez l'appareil (smartphone, PC portable, tablette) au **même réseau WiFi** que le PC hôte.
2. Ouvrez n'importe quel navigateur Web moderne (Chrome, Safari, Firefox, Edge).
3. Saisissez l'URL transmise par le script (ex: `http://192.168.1.42:3000`).
4. Créez un compte ou connectez-vous pour commencer à utiliser Orbyte.

---

## 🛡️ Pare-feu Windows & Droits Administrateur

Docker écoute sur `0.0.0.0:3000`, mais le pare-feu réseau de Windows peut bloquer les connexions entrantes issues du réseau WiFi.

### 1. Vérification des règles existantes (PowerShell sans droits Admin)
Exécutez dans PowerShell :
```powershell
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*Docker*" -or $_.DisplayName -like "*3000*" } | Select-Object DisplayName, Enabled, Direction, Action
```

### 2. Création d'une règle (Optionnel — Si vous avez les droits Admin)
Si vous disposez des droits administrateur sur le PC :
```powershell
New-NetFirewallRule -DisplayName "Orbyte LAN Web (Port 3000)" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

### 3. Alternative Si vous n'avez PAS les droits Admin (Mode Démo Faculté)
Si Windows demande un mot de passe administrateur que vous n'avez pas :
- **Solution A (Partage de connexion Mobile) :** Activez le *Point d'accès sans fil* (Hotspot WiFi) sur votre smartphone et connectez le PC hôte et les appareils de démo sur ce WiFi personnel. Sur un Hotspot mobile, Windows bascule souvent en profil réseau privé avec moins de restrictions.
- **Solution B (Tester un port déjà ouvert) :** Certains ports comme le port `80` ou `8080` possèdent déjà des exceptions autorisées par l'administrateur système pour d'autres applications. Vous pouvez configurer `HOST_PORT=80` dans votre `.env`.

---

## 🧪 Checklist de Test Avant le Jour J (À faire 24h avant)

Effectuez ces vérifications **AVANT** le jour de la présentation :

- [ ] **Test 1 — Validation locale :** Sur le PC hôte, ouvrez `http://localhost:3000` et vérifiez que l'interface Orbyte s'affiche et que la connexion fonctionne.
- [ ] **Test 2 — Récupération de l'IP :** Exécutez `start.bat` et notez l'IP LAN détectée (ex: `192.168.1.42`).
- [ ] **Test 3 — Test Smartphone WiFi :**
  1. Connectez votre smartphone au réseau WiFi.
  2. Désactivez les données mobiles (4G/5G) sur le téléphone pour forcer le passage par le WiFi.
  3. Naviguez vers `http://<IP_DETECTEE>:3000`.
  4. Testez la création d'un compte et l'envoi d'un message de chat.
- [ ] **Test 4 — Reconnexion / Re-fetch :** Vérifiez que les réponses streaming de chat s'affichent correctement sur le téléphone sans erreur CORS ou WebSocket.

---

## 🔍 Guide de Dépannage (Troubleshooting)

### 🔴 Symptôme 1 : "Impossible d'accéder au site" depuis le téléphone
1. **Isolation AP du WiFi :** Certains réseaux WiFi publics/faculté activent l'*Isolation Client / AP Isolation*, empêchant les appareils WiFi de se parler directement.  
   *Solution :* Utilisez le partage de connexion d'un smartphone pour créer un réseau WiFi local d'appoint pour la démo.
2. **Pare-feu Windows :** Le pare-feu bloque le port 3000.  
   *Solution :* Ajoutez la règle de pare-feu ou désactivez temporairement le pare-feu réseau public/privé le temps de la démo.
3. **Changement d'IP LAN :** Si le PC s'est déconnecté/reconnecté au WiFi, son IP a pu changer.  
   *Solution :* Relancez `start.bat` pour redétecter la nouvelle IP.

### 🔴 Symptôme 2 : L'interface s'affiche mais le Login / Chat échoue avec une erreur réseau
1. **Origine CORS non autorisée :**  
   *Cause :* `CORS_ALLOWED_ORIGIN` ou `WEB_DOMAIN` ne contiennent pas l'IP LAN actuelle.  
   *Solution :* Relancez via `start.bat` pour injecter dynamiquement `WEB_DOMAIN=http://<IP_LAN>:3000` et `CORS_ALLOWED_ORIGIN=http://<IP_LAN>:3000,http://localhost:3000`.

---

## 📊 Limites de Capacité Simultanée

Sur une machine hôte portable standard :

| Ressource Hôte | Capacité Estimée | Recommandations |
|---|---|---|
| **PC Portable Standard (16 Go RAM / CPU 4-8 Coeurs)** | **10 à 20 utilisateurs simultanés** | Idéal pour des démos de classe/faculté. |
| **Goulot d'étranglement principal** | CPU pour les modèles d'embedding/reranking local | Si 10 utilisateurs lancent une recherche RAG lourde en même temps, le délai de réponse augmentera légèrement. |
| **Mémoire Vive (RAM)** | ~6 à 8 Go consommés par la stack Docker complète | Conserver au moins 4 Go de RAM libre pour le système d'exploitation hôte. |
