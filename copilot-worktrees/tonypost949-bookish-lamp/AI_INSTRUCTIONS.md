# Master AI Alignment & Path Instructions

**To the Other Agent / Code:**
We are coordinating on local storage boundaries to protect C: drive limits. Adhere to these parameters:

1. **Junction Link Requirement**:
   * The project files reside on the external G: drive at `G:\OsintNeoAi\repo` to keep the 1.5 GB footprint off the C: drive.
   * `C:\OsintNeoAi` is now successfully established as a Directory Junction pointing to `G:\OsintNeoAi\repo`.

2. **C: Drive Space Protected**:
   * Reclaimed C: space is currently at **8.09 GB** free.
   * Do not run any commands downloading Takeout zips to C:. Keep all downloads targeted to `G:\OsintNeoAi\`.

3. **Venv Execution**:
   * Create the virtual environment and run the collection suite using G: drive's physical storage via the link:
   ```powershell
   cd C:\OsintNeoAi
   python -m venv venv
   venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python main.py --mode collect
   ```

4. **Confirm Status**:
   * Write your completion status and updates back to:
     `C:\OsintNeoAi\AI_RESPONSE.md`
