# 📲 Transferencia de Fotos

Autor / Author / Tekijä: **KALEVI LATVA AIJO ALEGRIA** · Windows · 100 % local

> 🇪🇸 Español · 🇬🇧 English · 🇫🇮 Suomi — el mismo documento en tres idiomas más abajo.

---

## 🇪🇸 Español

Pasa **fotos y videos del teléfono al PC por Wi-Fi**, escaneando un **código QR**. Sin cables,
sin apps en el teléfono, sin nube: las imágenes viajan directo del teléfono a tu computadora
por tu propia red.

### ✨ Qué hace
- **Código QR**: lo escaneas con la cámara del teléfono y se abre la página de subida (no hay que
  escribir la IP ni contraseñas).
- **Con clave**: cada sesión usa un **token** único → nadie más en la red puede entrar.
- **A prueba de fallos**: sube muchas fotos a la vez (por lotes, en paralelo, con **reintentos**).
- **Fotos y videos** en calidad original.
- **Panel de escritorio**: inicia/detén el servidor, ve los archivos recibidos, cambia la carpeta
  destino y ábrela con un clic.

### ▶️ Cómo usarlo
1. Ejecuta **`instalar.bat`** una vez.
2. Abre la app con **`Abrir-transferencia.bat`**.
3. Pulsa **▶ Iniciar servidor** → aparece un **QR**.
4. **Escanea el QR** con la cámara del teléfono (teléfono y PC en el **mismo Wi-Fi**).
5. En el teléfono elige fotos/videos → llegan a tu carpeta del PC.

### 🔒 Privacidad
La transferencia ocurre **solo en tu red local**; nada se sube a internet. Las fotos recibidas se
guardan en tu carpeta (por defecto `Fotos_Recibidas_PC/` en tu carpeta de usuario) y están
**excluidas de Git**.

### 🔨 Generar el .exe
`crear_exe.bat` crea **dos** versiones: **carpeta** (`dist\Transferencia\`) y **empaquetada** en un
solo archivo (`dist\Transferencia.exe`).

---

## 🇬🇧 English

Send **photos and videos from your phone to your PC over Wi-Fi** by scanning a **QR code**. No
cables, no phone app, no cloud: images travel straight from the phone to your computer over your
own network.

### ✨ What it does
- **QR code**: scan it with the phone camera and the upload page opens (no typing IP or passwords).
- **Keyed**: each session uses a unique **token** → nobody else on the network can get in.
- **Fault-tolerant**: uploads many photos at once (batched, in parallel, with **retries**).
- **Photos and videos** in original quality.
- **Desktop panel**: start/stop the server, see received files, change the destination folder and
  open it with one click.

### ▶️ How to use
1. Run **`instalar.bat`** once.
2. Open the app with **`Abrir-transferencia.bat`**.
3. Press **▶ Start server** → a **QR** appears.
4. **Scan the QR** with the phone camera (phone and PC on the **same Wi-Fi**).
5. On the phone pick photos/videos → they arrive in your PC folder.

### 🔒 Privacy
The transfer happens **only on your local network**; nothing is uploaded to the internet. Received
photos are saved in your folder (default `Fotos_Recibidas_PC/`) and are **excluded from Git**.

### 🔨 Build the .exe
`crear_exe.bat` builds **two** versions: **folder** (`dist\Transferencia\`) and **single-file**
(`dist\Transferencia.exe`).

---

## 🇫🇮 Suomi

Siirrä **valokuvat ja videot puhelimesta tietokoneelle Wi-Fin kautta** skannaamalla **QR-koodi**.
Ei johtoja, ei puhelinsovellusta, ei pilveä: kuvat siirtyvät suoraan puhelimesta tietokoneelle
omassa verkossasi.

### ✨ Mitä se tekee
- **QR-koodi**: skannaa se puhelimen kameralla ja lähetyssivu aukeaa (ei IP-osoitteita eikä salasanoja).
- **Avaimella**: jokainen istunto käyttää yksilöllistä **tunnusta** → kukaan muu verkossa ei pääse sisään.
- **Vikasietoinen**: lähettää monta kuvaa kerralla (erissä, rinnakkain, **uudelleenyrityksin**).
- **Kuvat ja videot** alkuperäislaadulla.
- **Työpöytäpaneeli**: käynnistä/pysäytä palvelin, katso vastaanotetut tiedostot, vaihda
  kohdekansio ja avaa se yhdellä klikkauksella.

### ▶️ Käyttö
1. Aja **`instalar.bat`** kerran.
2. Avaa sovellus **`Abrir-transferencia.bat`**-tiedostolla.
3. Paina **▶ Käynnistä palvelin** → näkyviin tulee **QR**.
4. **Skannaa QR** puhelimen kameralla (puhelin ja PC samassa **Wi-Fi**-verkossa).
5. Valitse puhelimessa kuvat/videot → ne saapuvat tietokoneesi kansioon.

### 🔒 Yksityisyys
Siirto tapahtuu **vain paikallisverkossasi**; mitään ei ladata internetiin. Vastaanotetut kuvat
tallentuvat kansioosi (oletus `Fotos_Recibidas_PC/`) ja on **jätetty pois Gitistä**.

### 🔨 Luo .exe
`crear_exe.bat` luo **kaksi** versiota: **kansio** (`dist\Transferencia\`) ja **yhden tiedoston**
(`dist\Transferencia.exe`).

---

## 🧩 Tecnología / Technology / Teknologia

**Python** · **PySide6** (Qt 6, panel) · **Flask** + **Werkzeug** (servidor local) · **qrcode**
(código QR) · **Pillow**.

## 🌐 Web / Pages

La carpeta `web/` muestra la interfaz que ve el teléfono (para funcionar necesita el servidor de
la app: se abre escaneando el QR). La página de presentación pública está en `docs/` (GitHub Pages).

---

Hecho con cariño para pasar fotos sin sufrir — **KALEVI LATVA AIJO ALEGRIA**
