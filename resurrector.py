import subprocess
import time
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Resurrector] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def resurrect(command, restart_delay=5):
    """
    Runs a command and continuously restarts it if it stops or crashes.
    """
    logging.info(f"Watching command: {' '.join(command)}")
    
    while True:
        logging.info("Starting process...")
        try:
            # Start the target process
            process = subprocess.Popen(command)
            
            # Wait for the process to terminate
            process.wait()
            
            # If we get here, the process has died or exited
            if process.returncode != 0:
                logging.warning(f"Process crashed/exited with error code {process.returncode}.")
            else:
                logging.info(f"Process exited normally with code {process.returncode}.")
                
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt caught. Shutting down resurrector...")
            # Ensure the child process is also terminated
            if 'process' in locals() and process.poll() is None:
                logging.info("Terminating child process...")
                process.terminate()
                process.wait()
            break
        except Exception as e:
            logging.error(f"Failed to start or monitor process: {e}")
            
        logging.info(f"Resurrecting in {restart_delay} seconds...\n" + "="*50)
        time.sleep(restart_delay)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python resurrector.py <command_to_run> [args...]")
        print("Example: python resurrector.py python aegis_correlation_engine.py --daemon")
        sys.exit(1)
        
    cmd_to_run = sys.argv[1:]
    resurrect(cmd_to_run)
