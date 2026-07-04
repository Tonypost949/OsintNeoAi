"""
azure_transcribe_audio.py — Transcribe mp3/m4a evidence files via Azure Speech + pipe to BigQuery.
Requires: azure_config.json or AZURE_SPEECH_KEY / AZURE_SPEECH_REGION env vars.
Run: python azure_transcribe_audio.py
"""
import os, json, sys, glob
from google.cloud import bigquery
import azure.cognitiveservices.speech as speechsdk

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azure_config.json")
alt = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\azure_config.json"

config = {}
for p in [config_path, alt]:
    if os.path.exists(p):
        with open(p) as f: config = json.load(f); break

key = config.get("speech_key") or os.environ.get("AZURE_SPEECH_KEY")
region = config.get("speech_region") or os.environ.get("AZURE_SPEECH_REGION") or "westus2"
PROJECT = "project-743aab84-f9a5-4ec7-954"

if not key:
    print("Azure Speech not configured. Run azure_setup.py --provision first.")
    sys.exit(1)

speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
speech_config.speech_recognition_language = "en-US"

# Find audio evidence files
audio_dirs = [
    r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP",
    r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent",
    r"G:\DL BACKUP",
    r"G:\buckp moto\Download",
]
audio_files = []
for d in audio_dirs:
    if os.path.exists(d):
        audio_files.extend(glob.glob(os.path.join(d, "*.mp3"), recursive=False))
        audio_files.extend(glob.glob(os.path.join(d, "*.m4a"), recursive=False))
        audio_files.extend(glob.glob(os.path.join(d, "*.wav"), recursive=False))

# Build known evidence file names
known_evidence = [
    "California hides toxic waste under homeless shelters",
    "Orange_County_Administrative_Attacks_and_Toxic_Shelters",
]

audio_files = list(set(audio_files))
print(f"=== Azure Speech — Transcribe {len(audio_files)} audio files ===\n")

bq = bigquery.Client(project=PROJECT)

# Ensure BigQuery table
table_id = f"{PROJECT}.ai_sandbox.audio_transcriptions"
try:
    bq.get_table(table_id)
except:
    from google.cloud.bigquery import SchemaField, Table
    schema = [
        SchemaField("file_path", "STRING"),
        SchemaField("filename", "STRING"),
        SchemaField("transcription", "STRING"),
        SchemaField("duration_seconds", "FLOAT64"),
        SchemaField("transcription_timestamp", "TIMESTAMP"),
    ]
    bq.create_table(Table(table_id, schema=schema))
    print(f"Created {table_id}")

count = 0
for fpath in audio_files:
    if count >= 20: break  # limit per run
    fname = os.path.basename(fpath)
    
    try:
        audio_config = speechsdk.audio.AudioConfig(filename=fpath)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        # Continuous recognition
        transcription_parts = []
        done = False
        
        def handle_result(evt):
            transcription_parts.append(evt.result.text)
        def handle_stop(evt):
            nonlocal done; done = True
        
        recognizer.recognized.connect(handle_result)
        recognizer.session_stopped.connect(handle_stop)
        recognizer.canceled.connect(lambda evt: handle_stop(evt))
        
        recognizer.start_continuous_recognition()
        # Wait up to 5 minutes for transcription
        wait_time = 0
        while not done and wait_time < 300:
            import time; time.sleep(0.5); wait_time += 0.5
        recognizer.stop_continuous_recognition()
        
        transcription = " ".join(transcription_parts)[:50000]
        
        if transcription.strip():
            bq.query(f"""
                INSERT INTO `{table_id}` (file_path, filename, transcription, duration_seconds, transcription_timestamp)
                VALUES (@path, @name, @text, @dur, CURRENT_TIMESTAMP())
            """, job_config=bigquery.QueryJobConfig(query_parameters=[
                bigquery.ScalarQueryParameter("path", "STRING", fpath),
                bigquery.ScalarQueryParameter("name", "STRING", fname),
                bigquery.ScalarQueryParameter("text", "STRING", transcription),
                bigquery.ScalarQueryParameter("dur", "FLOAT64", float(wait_time)),
            ])).result()
            
            count += 1
            preview = transcription[:100]
            print(f"  [{count}] {fname[:50]} — {len(transcription)} chars: \"{preview}...\"")
        else:
            print(f"  SKIP: {fname[:50]} — no speech detected")
    except Exception as e:
        print(f"  ERROR: {fname[:50]} — {e}")

print(f"\nDone. Transcribed: {count} files.")
print(f"BigQuery table: {table_id}")

# Copy config + scripts to osint-agent for IDE sync
sync_dir = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
for script in ["azure_setup.py", "azure_search_index.py", "azure_ocr_permits.py", "azure_transcribe_audio.py"]:
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
    dst = os.path.join(sync_dir, script)
    if os.path.exists(src):
        import shutil; shutil.copy2(src, dst)
        print(f"  {script} synced to osint-agent")
