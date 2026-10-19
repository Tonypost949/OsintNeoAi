import subprocess
import time
import os
import psutil

def set_python_priority(priority_level="Normal"):
    print(f"[PROCESS MANAGER] Setting all Python processes to: {priority_level}")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'python' in proc.info['name'].lower():
                p = psutil.Process(proc.info['pid'])
                if priority_level == "Normal":
                    p.nice(psutil.NORMAL_PRIORITY_CLASS)
                elif priority_level == "BelowNormal":
                    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                elif priority_level == "Idle":
                    p.nice(psutil.IDLE_PRIORITY_CLASS)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def manage_overnight_intake():
    print("==================================================")
    print("OVERNIGHT OCR & MEDIA INTAKE AUTOMATION MANAGER")
    print("==================================================")
    
    # Phase 1: Keep at Normal priority for the next 55 minutes to finish her data fast
    set_python_priority("Normal")
    print("[PHASE 1] Running at full NORMAL priority for 55 minutes to finish her dataset...")
    
    # Sleep for 55 minutes (3300 seconds)
    time.sleep(3300)
    
    # Phase 2: Drop priority to BelowNormal for the rest of the night
    print("\n[PHASE 2] Her dataset processing window completed. Dropping to LOW (BelowNormal) for overnight intake...")
    set_python_priority("BelowNormal")
    
    print("[✓] System configured for silent, low-resource overnight background media intake.")

if __name__ == "__main__":
    manage_overnight_intake()
