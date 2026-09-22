# -*- coding: utf-8 -*-
"""
Transferencia de Fotos — Día 12
Pasa fotos y videos del teléfono al PC por Wi-Fi, sin cables ni apps ni nube.

Mejora del script `pro.py` (que era de consola): ahora es una app de escritorio con
panel de control y, sobre todo, un **código QR** — lo escaneas con el teléfono y se
abre la página de subida al instante (no hace falta escribir la IP ni el token).

Lo robusto se mantiene: token de seguridad, subida por lotes con reintentos, y
ver / descargar / borrar los archivos recibidos.

Autor: KALEVI LATVA AIJO ALEGRIA
"""
import os
import sys
import io
import re
import socket
import secrets
import threading
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify, render_template_string, abort, send_from_directory
from werkzeug.serving import make_server

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFrame,
    QListWidget, QFileDialog, QMessageBox,
)

PUERTO = 5000


def _guard_pythonw():
    if sys.stdout is None or sys.stderr is None:
        d = open(os.devnull, "w")
        sys.stdout = sys.stdout or d
        sys.stderr = sys.stderr or d


# ------------------------------------------------------------ estado + utilidades
class Estado:
    def __init__(self):
        self.folder = Path(os.path.expanduser("~")) / "Fotos_Recibidas_PC"
        self.folder.mkdir(parents=True, exist_ok=True)
        self.token = secrets.token_urlsafe(16)

ESTADO = Estado()


def ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def human_size(n):
    f = float(n)
    for u in ("B", "KB", "MB", "GB", "TB"):
        if f < 1024 or u == "TB":
            return f"{int(f)} {u}" if u == "B" else f"{f:.1f} {u}"
        f /= 1024


def sanitize(name):
    name = os.path.basename(name)
    name = re.sub(r"[^\w\-.() ]+", "_", name).strip().strip(".")
    return name[:200]


def unique_path(dest: Path) -> Path:
    if not dest.exists():
        return dest
    i = 2
    while True:
        cand = dest.with_name(f"{dest.stem} ({i}){dest.suffix}")
        if not cand.exists():
            return cand
        i += 1


# ------------------------------------------------------------ Flask
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = None   # sin límite (videos grandes)


def _check_token():
    if request.args.get("t", "") != ESTADO.token:
        abort(403)


@app.route("/")
def index():
    return render_template_string(PAGINA_TELEFONO, token=ESTADO.token,
                                  folder=str(ESTADO.folder))


@app.route("/upload", methods=["POST"])
def upload():
    _check_token()
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"error": "No file"}), 400
    dest = unique_path(ESTADO.folder / sanitize(f.filename))
    f.save(dest)
    return jsonify({"ok": True, "saved_as": dest.name}), 200


@app.route("/files")
def files():
    _check_token()
    items = []
    for p in sorted(ESTADO.folder.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.is_file():
            st = p.stat()
            items.append({"name": p.name, "size_h": human_size(st.st_size),
                          "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%H:%M:%S")})
    return jsonify({"items": items})


@app.route("/download/<path:filename>")
def download(filename):
    _check_token()
    return send_from_directory(ESTADO.folder, os.path.basename(filename), as_attachment=True)


@app.route("/delete", methods=["POST"])
def delete():
    _check_token()
    name = os.path.basename((request.get_json(silent=True) or {}).get("name", ""))
    target = ESTADO.folder / name
    if name and target.exists() and target.is_file():
        target.unlink(); return jsonify({"ok": True})
    return jsonify({"error": "Not found"}), 404


@app.route("/delete_all", methods=["POST"])
def delete_all():
    _check_token()
    for p in ESTADO.folder.iterdir():
        if p.is_file():
            p.unlink()
    return jsonify({"ok": True})


# ------------------------------------------------------------ servidor en hilo
class Servidor(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True)
        self.srv = make_server(host, port, app, threaded=True)

    def run(self):
        self.srv.serve_forever()

    def detener(self):
        try:
            self.srv.shutdown()
        except Exception:
            pass


# ------------------------------------------------------------ ventana
class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transferencia de Fotos")
        self.resize(880, 620)
        self.setStyleSheet(QSS)
        self.servidor = None
        self._ui()
        self._timer = QTimer(self); self._timer.timeout.connect(self._refrescar_recibidos)

    def _ui(self):
        root = QHBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # ---- panel izquierdo: conexión / QR
        izq = QFrame(); izq.setObjectName("izq"); izq.setFixedWidth(400)
        L = QVBoxLayout(izq); L.setContentsMargins(26, 24, 26, 24); L.setSpacing(14)
        t = QLabel("📲 Transferencia de Fotos"); t.setObjectName("h1"); t.setWordWrap(True)
        L.addWidget(t)
        sub = QLabel("Pasa fotos y videos del teléfono al PC por Wi-Fi. Sin cables, sin nube.")
        sub.setObjectName("sub"); sub.setWordWrap(True); L.addWidget(sub)

        self.btn_toggle = QPushButton("▶  Iniciar servidor"); self.btn_toggle.setObjectName("accent")
        self.btn_toggle.clicked.connect(self._toggle); L.addWidget(self.btn_toggle)

        self.estado_lbl = QLabel("● Detenido"); self.estado_lbl.setObjectName("stopped")
        self.estado_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); L.addWidget(self.estado_lbl)

        self.qr = QLabel(); self.qr.setObjectName("qr"); self.qr.setFixedHeight(240)
        self.qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr.setText("Inicia el servidor para\nmostrar el código QR")
        L.addWidget(self.qr)

        self.url_lbl = QLabel(""); self.url_lbl.setObjectName("url"); self.url_lbl.setWordWrap(True)
        self.url_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.url_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        L.addWidget(self.url_lbl)

        self.ayuda = QLabel("1. Inicia el servidor.\n2. Escanea el QR con la cámara del teléfono.\n"
                            "3. Elige fotos y súbelas. (Teléfono y PC en el mismo Wi-Fi.)")
        self.ayuda.setObjectName("sub"); self.ayuda.setWordWrap(True); L.addWidget(self.ayuda)
        L.addStretch()
        root.addWidget(izq)

        # ---- panel derecho: carpeta + recibidos
        der = QVBoxLayout(); der.setContentsMargins(22, 22, 22, 22); der.setSpacing(12)
        fila = QHBoxLayout(); fila.setSpacing(8)
        self.folder_lbl = QLabel(str(ESTADO.folder)); self.folder_lbl.setObjectName("folder")
        self.folder_lbl.setWordWrap(True)
        b_cambiar = QPushButton("Cambiar"); b_cambiar.setObjectName("ghost"); b_cambiar.clicked.connect(self._cambiar_carpeta)
        b_abrir = QPushButton("📂 Abrir"); b_abrir.setObjectName("ghost"); b_abrir.clicked.connect(self._abrir_carpeta)
        fila.addWidget(QLabel("Guardando en:")); fila.addWidget(self.folder_lbl, 1)
        fila.addWidget(b_cambiar); fila.addWidget(b_abrir)
        der.addLayout(fila)

        cab = QHBoxLayout()
        cab.addWidget(QLabel("Archivos recibidos"))
        self.contador = QLabel(""); self.contador.setObjectName("sub"); cab.addStretch(); cab.addWidget(self.contador)
        der.addLayout(cab)

        self.lista = QListWidget(); self.lista.setObjectName("lista")
        self.lista.itemDoubleClicked.connect(lambda _it: self._abrir_carpeta())
        der.addWidget(self.lista, 1)

        acc = QHBoxLayout()
        self.b_refrescar = QPushButton("🔄 Actualizar"); self.b_refrescar.setObjectName("ghost")
        self.b_refrescar.clicked.connect(self._refrescar_recibidos)
        self.b_borrar = QPushButton("🗑 Borrar todo"); self.b_borrar.setObjectName("danger")
        self.b_borrar.clicked.connect(self._borrar_todo)
        acc.addWidget(self.b_refrescar); acc.addStretch(); acc.addWidget(self.b_borrar)
        der.addLayout(acc)
        root.addLayout(der, 1)

        self._refrescar_recibidos()

    # ---------- servidor
    def _toggle(self):
        if self.servidor is None:
            self._iniciar()
        else:
            self._detener()

    def _iniciar(self):
        ESTADO.token = secrets.token_urlsafe(16)   # token nuevo cada arranque
        try:
            self.servidor = Servidor("0.0.0.0", PUERTO)
            self.servidor.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No pude iniciar el servidor:\n{e}")
            self.servidor = None
            return
        url = f"http://{ip_local()}:{PUERTO}/?t={ESTADO.token}"
        self._mostrar_qr(url)
        self.url_lbl.setText(url)
        self.estado_lbl.setText("● Activo — listo para recibir"); self.estado_lbl.setObjectName("running")
        self.estado_lbl.setStyleSheet(""); self.estado_lbl.style().unpolish(self.estado_lbl); self.estado_lbl.style().polish(self.estado_lbl)
        self.btn_toggle.setText("⏹  Detener servidor")
        self._timer.start(2000)

    def _detener(self):
        if self.servidor:
            self.servidor.detener(); self.servidor = None
        self._timer.stop()
        self.qr.setPixmap(QPixmap()); self.qr.setText("Servidor detenido")
        self.url_lbl.setText("")
        self.estado_lbl.setText("● Detenido"); self.estado_lbl.setObjectName("stopped")
        self.estado_lbl.setStyleSheet(""); self.estado_lbl.style().unpolish(self.estado_lbl); self.estado_lbl.style().polish(self.estado_lbl)
        self.btn_toggle.setText("▶  Iniciar servidor")

    def _mostrar_qr(self, url):
        import qrcode
        img = qrcode.make(url)
        buf = io.BytesIO(); img.save(buf, "PNG")
        pm = QPixmap(); pm.loadFromData(buf.getvalue())
        self.qr.setPixmap(pm.scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation))

    # ---------- carpeta / recibidos
    def _cambiar_carpeta(self):
        d = QFileDialog.getExistingDirectory(self, "Carpeta donde guardar las fotos", str(ESTADO.folder))
        if d:
            ESTADO.folder = Path(d); ESTADO.folder.mkdir(parents=True, exist_ok=True)
            self.folder_lbl.setText(d); self._refrescar_recibidos()

    def _abrir_carpeta(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(ESTADO.folder)))

    def _refrescar_recibidos(self):
        self.lista.clear()
        archivos = [p for p in ESTADO.folder.iterdir() if p.is_file()] if ESTADO.folder.exists() else []
        archivos.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        total = 0
        for p in archivos:
            st = p.stat(); total += st.st_size
            hora = datetime.fromtimestamp(st.st_mtime).strftime("%H:%M:%S")
            self.lista.addItem(f"{p.name}    ·    {human_size(st.st_size)}    ·    {hora}")
        self.contador.setText(f"{len(archivos)} archivo(s) · {human_size(total)}")

    def _borrar_todo(self):
        archivos = [p for p in ESTADO.folder.iterdir() if p.is_file()] if ESTADO.folder.exists() else []
        if not archivos:
            return
        r = QMessageBox.question(self, "Borrar todo",
                                 f"¿Borrar los {len(archivos)} archivos recibidos de esta carpeta?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            for p in archivos:
                try: p.unlink()
                except Exception: pass
            self._refrescar_recibidos()

    def closeEvent(self, e):
        if self.servidor:
            self.servidor.detener()
        e.accept()


# la página que ve el teléfono (servida por Flask). Reutiliza el motor robusto del "pro":
# subida por lotes, concurrencia, reintentos, y ver/descargar/borrar.
PAGINA_TELEFONO = r"""
<!doctype html><html lang="es"><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Transferencia a PC</title>
<style>
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
    padding:18px;text-align:center;background:#f2f2f7;color:#1c1c1e;margin:0}
  .c{background:#fff;padding:22px;border-radius:20px;box-shadow:0 6px 20px rgba(0,0,0,.08);max-width:560px;margin:0 auto}
  h1{margin:0 0 6px;font-size:22px}
  .muted{color:#8e8e93;font-size:13px;margin:6px 0 12px}
  .btn{background:#007aff;color:#fff;padding:16px;border-radius:14px;font-size:17px;border:none;font-weight:700;
    cursor:pointer;width:100%;margin:8px 0}
  .btn.sec{background:#34c759} .btn.danger{background:#ff3b30} .btn:disabled{background:#c7c7cc}
  #file{display:none}
  .wrap{width:100%;background:#e5e5ea;border-radius:12px;height:16px;overflow:hidden;margin-top:10px}
  .bar{width:0%;height:100%;background:#34c759;transition:width .15s}
  .log{text-align:left;font-size:12px;color:#555;margin-top:12px;max-height:200px;overflow:auto;
    background:#fafafa;padding:10px;border-radius:10px;border:1px solid #eee}
  .ok{color:#1a7f37}.bad{color:#b42318}
  .rowf{display:flex;gap:8px;align-items:center;margin:6px 0;text-align:left}
  .grow{flex:1;font-size:13px;word-break:break-all}
  a{color:#007aff;text-decoration:none}
</style></head><body>
<div class="c">
  <h1>📲 Enviar al PC</h1>
  <div class="muted">Se guardan en: <b>{{ folder }}</b></div>
  <button class="btn" id="pick" onclick="document.getElementById('file').click()">Seleccionar fotos / videos</button>
  <input type="file" id="file" multiple accept="image/*,video/*">
  <div id="status" class="muted">Esperando selección…</div>
  <div class="wrap"><div class="bar" id="bar"></div></div>
  <div class="log" id="log"></div>
  <div style="display:flex;gap:8px;margin-top:12px">
    <button class="btn sec" style="margin:0" onclick="verRecibidos()">Ver recibidos</button>
    <button class="btn danger" style="margin:0" onclick="borrarTodo()">Borrar todo</button>
  </div>
  <div class="log" id="recibidos" style="margin-top:10px">—</div>
</div>
<script>
const T="{{ token }}", CONC=3, RET=2;
const $=id=>document.getElementById(id);
$('file').addEventListener('change',()=>{const f=[...$('file').files];if(f.length)subir(f);});
function esc(s){return (s||"").replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#039;"}[m]));}
function log(h){$('log').innerHTML+=h+"<br>";$('log').scrollTop=$('log').scrollHeight;}
function prog(d,t){$('bar').style.width=(t?Math.round(d/t*100):0)+"%";}
function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
async function subir(files){
  $('pick').disabled=true;$('log').innerHTML="";prog(0,files.length);
  let done=0,ok=0,fail=0;const q=files.slice(),workers=[];
  $('status').textContent=`Subiendo ${files.length}…`;
  for(let w=0;w<CONC;w++){workers.push((async()=>{while(q.length){const f=q.shift();
    const r=await unoConReintento(f,RET);done++;r?ok++:fail++;prog(done,files.length);}})());}
  await Promise.all(workers);
  $('status').textContent=`¡Listo! OK: ${ok} — Fallos: ${fail}`;
  $('pick').disabled=false;$('pick').textContent="Subir más";$('file').value="";verRecibidos();
}
async function unoConReintento(f,ret){
  for(let a=0;a<=ret;a++){try{await uno(f);log(`<span class="ok">✔</span> ${esc(f.name)}`);return true;}
    catch(e){const last=a===ret;log(`<span class="${last?'bad':'muted'}">${last?'✘':'↻'}</span> ${esc(f.name)}`);
      if(last)return false;await sleep(300+a*400);}}
  return false;
}
function uno(f){return new Promise((res,rej)=>{const fd=new FormData();fd.append("file",f,f.name);
  const x=new XMLHttpRequest();x.open("POST",`/upload?t=${encodeURIComponent(T)}`,true);x.timeout=180000;
  x.onload=()=>x.status===200?res():rej();x.onerror=()=>rej();x.ontimeout=()=>rej();x.send(fd);});}
async function verRecibidos(){try{const r=await fetch(`/files?t=${encodeURIComponent(T)}`);const d=await r.json();
  if(!d.items||!d.items.length){$('recibidos').innerHTML="<span class='muted'>Aún no hay archivos.</span>";return;}
  $('recibidos').innerHTML=d.items.map(it=>`<div class="rowf"><div class="grow">${esc(it.name)}<br>
    <span class="muted">${esc(it.size_h)} · ${esc(it.mtime)}</span></div>
    <a href="/download/${encodeURIComponent(it.name)}?t=${encodeURIComponent(T)}">⬇︎</a></div>`).join("");
  }catch(e){$('recibidos').innerHTML="<span class='bad'>No se pudo cargar.</span>";}}
async function borrarTodo(){if(!confirm("¿Borrar TODOS los archivos recibidos?"))return;
  await fetch(`/delete_all?t=${encodeURIComponent(T)}`,{method:"POST"});verRecibidos();}
verRecibidos();
</script></body></html>
"""

QSS = """
* { font-family: 'Segoe UI'; font-size: 13px; }
QWidget { background: #0f1420; color: #ffffff; }
QLabel { background: transparent; color: #ffffff; }
QFrame#izq { background: #141b2b; border-right: 1px solid #232f47; }
QLabel#h1 { font-size: 20px; font-weight: 800; }
QLabel#sub { color: #aeb7d1; font-size: 12px; }
QLabel#qr { background: #ffffff; border-radius: 14px; color: #8a95b3; }
QLabel#url { color: #7db1ff; font-size: 12px; }
QLabel#folder { color: #cbd3e6; }
QLabel#stopped { color: #f0a0a6; font-weight: 700; }
QLabel#running { color: #6ee7a0; font-weight: 700; }
QPushButton { background: #263149; color: #ffffff; border: none; border-radius: 10px; padding: 11px 14px; font-weight: 700; }
QPushButton:hover { background: #30405f; }
QPushButton#accent { background: #3b82f6; }
QPushButton#accent:hover { background: #2f6fe0; }
QPushButton#ghost { background: #1a2233; border: 1px solid #2c3852; font-weight: 600; }
QPushButton#ghost:hover { background: #263149; }
QPushButton#danger { background: #e0424d; }
QPushButton#danger:hover { background: #c8303b; }
QListWidget#lista { background: #141b2b; border: 1px solid #232f47; border-radius: 12px; padding: 6px; }
QListWidget#lista::item { padding: 8px; border-bottom: 1px solid #1c2740; }
"""


def main():
    _guard_pythonw()
    app_qt = QApplication(sys.argv)
    app_qt.setStyleSheet(QSS)
    v = Ventana(); v.show()
    sys.exit(app_qt.exec())


if __name__ == "__main__":
    main()
