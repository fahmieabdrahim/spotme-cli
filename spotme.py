#!/usr/bin/env python3
"""SPOT-Me CLI: local settings, schedule alerts, portal opening and GPS preview.
This helper does not submit official attendance or movement records.
"""
from __future__ import annotations
import getpass, json, shutil, subprocess, threading, webbrowser
from datetime import datetime
from pathlib import Path

PORTAL="https://spotme.jdn.gov.my"
ROOT=Path.home()/".config"/"spotme-cli"
CONFIG,STATE=ROOT/"config.json",ROOT/"state.json"
DAY_NAMES=["Isnin","Selasa","Rabu","Khamis","Jumaat","Sabtu","Ahad"]
FIELDS={
"1":("Pengguna / ID log masuk","pengguna",""),
"2":("Kata laluan (tidak disimpan)","password",""),
"3":("Lokasi","lokasi",""),
"4":("Ulasan","ulasan","HBH"),
"5":("Sebab bekerja dari rumah","sebab_wfh","Hari Bekerja Hibrid (HBH)"),
"6":("Sebab lewat","sebab_lewat","Tiada"),
"7":("Sebab tidak cukup jam","sebab_jam","Tiada"),
"8":("Catatan tugasan","catatan_tugasan","Menyediakan reka bentuk grafik mengikut arahan dan tempoh pelaksanaan yang ditetapkan"),
"9":("Masa masuk (HH:MM)","masa_masuk","07:25"),
"10":("Masa keluar (HH:MM)","masa_keluar","16:35"),
"11":("Auto pergerakan setiap 1 jam (ya/tidak)","auto_pergerakan",True)}
DEFAULTS={"pengguna":"","lokasi":"","ulasan":"HBH","sebab_wfh":"Hari Bekerja Hibrid (HBH)","sebab_lewat":"Tiada","sebab_jam":"Tiada","catatan_tugasan":"Menyediakan reka bentuk grafik mengikut arahan dan tempoh pelaksanaan yang ditetapkan","masa_masuk":"07:25","masa_keluar":"16:35","auto_pergerakan":True,"hari_bekerja":[0,1,2,3,4]}
def ensure_dirs():
 ROOT.mkdir(parents=True,exist_ok=True)
 try: ROOT.chmod(0o700)
 except OSError: pass
def save_json(path,data):
 ensure_dirs(); tmp=path.with_suffix(".tmp")
 tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 try: tmp.chmod(0o600)
 except OSError: pass
 tmp.replace(path)
 try: path.chmod(0o600)
 except OSError: pass
def load_json(path,default):
 try: return json.loads(path.read_text(encoding="utf-8"))
 except (OSError,json.JSONDecodeError): return default
def load_config():
 cfg=DEFAULTS.copy(); saved=load_json(CONFIG,{})
 if isinstance(saved,dict): cfg.update(saved)
 return cfg
def valid_time(value):
 try: datetime.strptime(value,"%H:%M"); return True
 except (TypeError,ValueError): return False
def first_setup():
 cfg=load_config()
 print("\nTetapan awal SPOT-Me CLI")
 print("Hari bekerja: 0 Isnin, 1 Selasa, 2 Rabu, 3 Khamis, 4 Jumaat, 5 Sabtu, 6 Ahad")
 raw=input("Pilih hari bekerja [0,1,2,3,4]: ").strip() or "0,1,2,3,4"
 try:
  days=sorted({int(x.strip()) for x in raw.split(",") if x.strip()})
  if not days or any(x<0 or x>6 for x in days): raise ValueError
  cfg["hari_bekerja"]=days
 except ValueError:
  print("Pilihan tidak sah; guna Isnin hingga Jumaat."); cfg["hari_bekerja"]=[0,1,2,3,4]
 save_json(CONFIG,cfg); print("Tetapan disimpan.")
def edit_field(choice,cfg):
 label,key,default=FIELDS[choice]
 if key=="password":
  secret=getpass.getpass("Kata laluan (tidak akan disimpan): ")
  del secret
  print("Kata laluan tidak disimpan; tiada login automatik dibuat."); return
 current=cfg.get(key,default)
 if isinstance(default,bool):
  raw=input(f"{label} [{'ya' if current else 'tidak'}]: ").strip().lower()
  if raw in ("ya","y","yes","1"): cfg[key]=True
  elif raw in ("tidak","t","no","n","0"): cfg[key]=False
  elif raw: print("Masukkan ya atau tidak."); return
 else:
  raw=input(f"{label} [{current}]: ").strip()
  if raw:
   if key in ("masa_masuk","masa_keluar") and not valid_time(raw):
    print("Format masa mesti HH:MM, contoh 07:25."); return
   cfg[key]=raw
 save_json(CONFIG,cfg); print("Tetapan disimpan.")
def gps_preview():
 command=shutil.which("termux-location")
 if not command: return "GPS tidak tersedia melalui CLI ini pada peranti tersebut."
 try:
  r=subprocess.run([command,"-p","gps","-r","once"],capture_output=True,text=True,timeout=25)
  if r.returncode==0 and r.stdout.strip():
   try:
    d=json.loads(r.stdout); lat,lon=d.get("latitude"),d.get("longitude")
    if lat is not None and lon is not None: return f"GPS semasa: {lat}, {lon}"
   except json.JSONDecodeError: pass
   return "Data GPS diterima: "+r.stdout.strip()[:250]
  return "GPS gagal dibaca. Semak Termux:API dan kebenaran lokasi."
 except (OSError,subprocess.TimeoutExpired): return "GPS tidak dapat dibaca atau terlalu lama."
def notify(title,detail):
 print(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] {title}\n{detail}\n",flush=True)
 command=shutil.which("termux-notification")
 if command:
  try: subprocess.run([command,"--title",title,"--content",detail[:250]],timeout=5,check=False,capture_output=True)
  except (OSError,subprocess.TimeoutExpired): pass
 try: webbrowser.open(PORTAL,new=2)
 except Exception: pass
def scheduler(cfg,stop_event):
 fired=load_json(STATE,{})
 while not stop_event.is_set():
  now=datetime.now(); today=now.date().isoformat()
  if now.weekday() in cfg.get("hari_bekerja",[]):
   hhmm=now.strftime("%H:%M")
   for key,title in (("masa_masuk","Peringatan daftar masuk"),("masa_keluar","Peringatan daftar keluar")):
    event_id=f"{today}:{key}"
    if valid_time(cfg.get(key,"")) and hhmm==cfg[key] and fired.get(event_id)!="done":
     notify(title,"Portal dibuka. Semak butiran dan sahkan sendiri dalam portal.")
     fired[event_id]="done"; save_json(STATE,fired)
   if cfg.get("auto_pergerakan") and valid_time(cfg.get("masa_masuk","")) and valid_time(cfg.get("masa_keluar","")):
    start=datetime.combine(now.date(),datetime.strptime(cfg["masa_masuk"],"%H:%M").time())
    end=datetime.combine(now.date(),datetime.strptime(cfg["masa_keluar"],"%H:%M").time())
    elapsed=(now-start).total_seconds()
    if start<now<=end and elapsed>=3600 and int(elapsed)%3600<60:
     hour=int(elapsed//3600); event_id=f"{today}:movement:{hour}"
     if fired.get(event_id)!="done":
      notify(f"Peringatan pergerakan #{hour}",gps_preview()+" — semak lokasi dan rekod sebelum pengesahan.")
      fired[event_id]="done"; save_json(STATE,fired)
  stop_event.wait(1)
def show_config(cfg):
 print("\nTetapan semasa")
 for n,(label,key,default) in FIELDS.items():
  value="Tidak disimpan" if key=="password" else cfg.get(key,default)
  if key=="auto_pergerakan": value="Ya" if value else "Tidak"
  print(f"{n}. {label}: {value}")
 print("Hari bekerja: "+", ".join(DAY_NAMES[x] for x in cfg.get("hari_bekerja",[]) if 0<=x<=6))
def main():
 ensure_dirs()
 if not CONFIG.exists(): first_setup()
 cfg=load_config(); stop=threading.Event()
 worker=threading.Thread(target=scheduler,args=(cfg,stop),name="spotme-scheduler")
 worker.start()
 print("\nSPOT-Me CLI — berjalan selagi aplikasi dibuka.")
 print("Peringatan membuka portal; rekod rasmi mesti disemak dan dihantar sendiri.")
 try:
  while True:
   print("\n1-11. Ubah tetapan\nS. Lihat tetapan\nP. Buka portal SPOT-Me\n0. Exit")
   choice=input("\nPilihan: ").strip().lower()
   if choice=="0": break
   elif choice=="s": show_config(cfg)
   elif choice=="p": webbrowser.open(PORTAL,new=2)
   elif choice in FIELDS: edit_field(choice,cfg); cfg.update(load_config())
   else: print("Pilihan tidak sah.")
 except (KeyboardInterrupt,EOFError): print("\nMenutup SPOT-Me CLI...")
 finally:
  stop.set(); worker.join(timeout=3); print("Semua proses SPOT-Me CLI dihentikan.")
if __name__=="__main__": main()
