import os
import re
import datetime
import hashlib
import atexit
from dateutil import parser as date_parser
from dateutil import tz
import ollama

# Global Configuration
# Set this to a standard timezone name (e.g., "America/New_York", "UTC")
# or "local" to dynamically use the local system's timezone.
CALENDAR_TIMEZONE = "local"

# Regex pattern to capture dates in various formats:
# 1. YYYY-MM-DD or YYYY/MM/DD
# 2. MM/DD/YYYY or DD-MM-YYYY
# 3. Month DD, YYYY
# 4. DD Month YYYY
# Includes optional time component (e.g., 14:30:00 or 08:00 AM/PM)
DATE_PATTERN = re.compile(
    r'\b(?P<date>'
    r'\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+(?:at\s+|@\s+)?\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)?'
    r'|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}(?:\s+(?:at\s+|@\s+)?\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)?'
    r'|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}(?:\s+(?:at\s+|@\s+)?\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)?'
    r'|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}(?:\s+(?:at\s+|@\s+)?\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)?'
    r')\b',
    re.IGNORECASE
)

# Regex pattern to capture time ranges like "14:30 - 15:45" or "14:30 to 15:45"
TIME_RANGE_PATTERN = re.compile(
    r'\b(?P<start_time>\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*(?:-|to|until)\s*(?P<end_time>\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\b',
    re.IGNORECASE
)

def escape_ics_text(text):
    """Escapes special characters in text fields according to RFC 5545."""
    if not text:
        return ""
    # Escape backslashes, commas, and semicolons first
    text = text.replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;')
    # Then replace newlines with literal '\n'
    text = text.replace('\r\n', '\\n').replace('\n', '\\n').replace('\r', '\\n')
    return text.strip()

def fold_line(line):
    """Folds a line to comply with the 75-character limit in RFC 5545, encoding-safe."""
    encoded = line.encode('utf-8')
    if len(encoded) <= 75:
        return line
    
    parts = []
    parts.append(encoded[:75].decode('utf-8', errors='ignore'))
    remainder = encoded[75:]
    while remainder:
        # Each folded line begins with a space (1 byte)
        chunk = remainder[:74].decode('utf-8', errors='ignore')
        parts.append(" " + chunk)
        remainder = remainder[len(chunk.encode('utf-8')):]
    return "\r\n".join(parts)

def get_calendar_tz():
    """Resolves the configured timezone name to a dateutil tzinfo object."""
    if CALENDAR_TIMEZONE.lower() == "local":
        return tz.tzlocal()
    target_tz = tz.gettz(CALENDAR_TIMEZONE)
    return target_tz if target_tz is not None else tz.tzutc()

def format_datetime_for_ics(dt):
    """Normalizes and formats a datetime object to standard ICS format, returning (iso_str, tzid)."""
    target_tz = get_calendar_tz()
    
    # Localize naive datetime, or convert aware datetime
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=target_tz)
    else:
        dt = dt.astimezone(target_tz)
        
    # Check if timezone is UTC
    is_utc = False
    if isinstance(dt.tzinfo, tz.tzutc):
        is_utc = True
    else:
        offset = dt.utcoffset()
        if offset is not None and offset.total_seconds() == 0:
            is_utc = True
            
    if is_utc:
        return dt.strftime("%Y%m%dT%H%M%SZ"), None
    
    # Extract TZID
    tzid = None
    if CALENDAR_TIMEZONE.lower() != "local":
        tzid = CALENDAR_TIMEZONE
    elif hasattr(dt.tzinfo, 'tzname'):
        tzid = dt.tzinfo.tzname(dt)
    
    if not tzid:
        tzid = "local"
        
    return dt.strftime("%Y%m%dT%H%M%S"), tzid

def sanitize_datetime_str(dt_str):
    """Cleans up datetime strings to ensure they are parseable by date_parser."""
    if not dt_str:
        return dt_str
    # Replace " at " or " @ " with space
    dt_str = re.sub(r'\s+at\s+|\s+@\s+', ' ', dt_str, flags=re.IGNORECASE)
    # Strip any other common symbols
    dt_str = dt_str.replace('@', '').strip()
    return dt_str

def parse_end_time(end_time_str, start_dt):
    """Parses the end time, optionally using the date component of start_dt if missing."""
    if not end_time_str or end_time_str.strip().lower() == "none" or end_time_str.strip() == "":
        return start_dt + datetime.timedelta(hours=1)
    
    try:
        dt_end = date_parser.parse(sanitize_datetime_str(end_time_str))
        # If the end date defaults to today but start_dt has a different date,
        # we align the end date with the start date if no explicit date was in end_time_str.
        now = datetime.datetime.now()
        if dt_end.year == now.year and dt_end.month == now.month and dt_end.day == now.day:
            # Check if date separators are absent, indicating time-only
            if not any(char in end_time_str for char in ['-', '/']) and not any(m in end_time_str.lower() for m in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                dt_end = dt_end.replace(year=start_dt.year, month=start_dt.month, day=start_dt.day)
        return dt_end
    except Exception:
        return start_dt + datetime.timedelta(hours=1)

def append_to_ics_file(filename, summary, start_time_str, description="", end_time_str=None, source_url=None):
    """
    Directly appends an event block to a standard universal calendar file.
    Uses timezone-aware formatting, stable hashlib UIDs, and source references.
    """
    try:
        dt = date_parser.parse(sanitize_datetime_str(start_time_str))
        # Handle cases where explicit hours aren't provided by default to 8 AM
        if dt.hour == 0 and dt.minute == 0:
            dt = dt.replace(hour=8)
            
        start_iso, tzid = format_datetime_for_ics(dt)
        
        # Resolve the end time
        end_dt = parse_end_time(end_time_str, dt)
        end_iso, _ = format_datetime_for_ics(end_dt)
        
        # Event timestamp in UTC
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        
        # Generate a stable UID using hashlib
        unique_str = f"{start_iso}-{summary}"
        event_hash = hashlib.md5(unique_str.encode('utf-8')).hexdigest()
        uid = f"{event_hash}@local.matrix"
        
        # Build strict compliance iCalendar blocks
        lines = [
            "BEGIN:VEVENT",
            fold_line(f"UID:{uid}"),
            fold_line(f"DTSTAMP:{timestamp}"),
            fold_line(f"DTSTART;TZID={tzid}:{start_iso}" if tzid else f"DTSTART:{start_iso}"),
            fold_line(f"DTEND;TZID={tzid}:{end_iso}" if tzid else f"DTEND:{end_iso}"),
            fold_line(f"SUMMARY:{escape_ics_text(summary)}"),
        ]
        
        if source_url and source_url.strip().lower() != "none" and source_url.strip() != "":
            lines.append(fold_line(f"URL:{escape_ics_text(source_url)}"))
            ref_desc = f"{description}\n\nSource Reference: {source_url}" if description else f"Source Reference: {source_url}"
            lines.append(fold_line(f"DESCRIPTION:{escape_ics_text(ref_desc)}"))
        else:
            lines.append(fold_line(f"DESCRIPTION:{escape_ics_text(description)}"))
            
        lines.append("END:VEVENT")
        
        with open(filename, "a", encoding="utf-8", newline="") as f:
            for line in lines:
                f.write(line + "\r\n")
        return True
    except Exception as e:
        print(f"Skipping entry due to parsing error: {e}")
        return False

def prepare_ics_file(filename):
    """Initializes the calendar file or removes the sealing line if it exists."""
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8", newline="") as f:
            f.write("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Local//Timeline Agent//EN\r\n")
    else:
        # Read the file and strip the END:VCALENDAR if present
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        pattern = r"END:VCALENDAR\s*$"
        if re.search(pattern, content):
            clean_content = re.sub(pattern, "", content)
            clean_lines = [line.strip() for line in clean_content.splitlines() if line.strip()]
            with open(filename, "w", encoding="utf-8", newline="") as f:
                for line in clean_lines:
                    f.write(line + "\r\n")

def seal_calendar_file(filename):
    """Ensures the .ics file is sealed correctly on exit."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        if not re.search(r"END:VCALENDAR\s*$", content):
            with open(filename, "a", encoding="utf-8", newline="") as f:
                if content and not content.endswith("\n") and not content.endswith("\r"):
                    f.write("\r\n")
                f.write("END:VCALENDAR\r\n")
            print(f"\n[Auto-Seal] Calendar file sealed successfully at: {os.path.abspath(filename)}")

def fallback_parse_text(text):
    """
    Deterministic fallback parser when the LLM is unavailable or fails.
    Attempts to parse:
    - Start and end datetimes (from multiple dates or time ranges)
    - Summary and details
    - Source references (URLs or file names)
    """
    # 1. Search for source reference (URLs or standard document references)
    url_match = re.search(r'https?://[^\s,;]+', text)
    source = url_match.group(0) if url_match else None
    
    if not source:
        doc_match = re.search(r'\b(?:source|doc|ref|file):\s*(?P<ref>[^\s,;]+)', text, re.IGNORECASE)
        if doc_match:
            source = doc_match.group('ref')
            
    # Clean source from text to avoid summary pollution
    text_clean = text
    if source:
        text_clean = text_clean.replace(source, '')
        text_clean = re.sub(r'\b(?:source|doc|ref|file):\s*$', '', text_clean, flags=re.IGNORECASE)
        
    # 2. Extract dates and times
    matches = list(DATE_PATTERN.finditer(text_clean))
    
    start_time = None
    end_time = None
    
    if len(matches) >= 2:
        start_time = matches[0].group('date')
        end_time = matches[1].group('date')
        for m in matches[:2]:
            text_clean = text_clean.replace(m.group('date'), '')
    elif len(matches) == 1:
        start_time = matches[0].group('date')
        text_clean = text_clean.replace(start_time, '')
        
        # Look for a time range (e.g., 14:30 to 15:45) in the text
        time_range = TIME_RANGE_PATTERN.search(text)
        if time_range:
            t_start = time_range.group('start_time')
            t_end = time_range.group('end_time')
            
            try:
                dt_parsed = date_parser.parse(sanitize_datetime_str(start_time))
                date_only = dt_parsed.strftime("%Y-%m-%d")
                start_time = f"{date_only} {t_start}"
                end_time = f"{date_only} {t_end}"
            except Exception:
                pass
            text_clean = text_clean.replace(time_range.group(0), '')
            
    if not start_time:
        return None
        
    # Clean up description text
    text_clean = re.sub(r'^[-\s,;:.]+', '', text_clean)
    text_clean = re.sub(r'[-\s,;:.]+$', '', text_clean).strip()
    
    if text_clean:
        summary = text_clean.split('.')[0]
        if len(summary) > 60:
            summary = summary[:57] + "..."
        detail = text_clean
    else:
        summary = "Log Event"
        detail = text
        
    return sanitize_datetime_str(start_time), sanitize_datetime_str(end_time), summary, detail, source

def run_matrix_processor():
    output_file = "master_incident_timeline.ics"
    
    # Prepare the calendar file (remove existing seal if appending)
    prepare_ics_file(output_file)
    
    # Register automatic sealing of the file on script exit or crash
    atexit.register(seal_calendar_file, output_file)

    print("=== ABSOLUTE LOCAL TIMELINE PARSER ACTIVATED ===")
    print(f"Timezone: {CALENDAR_TIMEZONE} (detected name will be injected)")
    print(f"All events will write sequentially to: {os.path.abspath(output_file)}")
    print("Drop a data chunk or log file input below. Type 'FINISH' to seal the file.\n")
    
    system_instruction = (
        "You are an offline structural parser. Identify start datetimes, end datetimes, "
        "event descriptions, and source documents/references from the provided incident texts. "
        "You must respond ONLY in a raw comma-separated values (CSV) format with 5 columns: "
        "START_TIME, END_TIME, SUMMARY, DETAIL, SOURCE. "
        "If end time or source is not mentioned, use 'None'. "
        "Do not include markdown formatting, backticks, or intro talk."
    )

    while True:
        try:
            user_input = input("Feed Log Text: ")
        except KeyboardInterrupt:
            print("\nExiting timeline parser.")
            break
            
        if user_input.strip().upper() == "FINISH":
            break
            
        if not user_input.strip():
            continue

        parsed_any = False
        
        try:
            # Query the 1.6GB local model via Ollama
            response = ollama.chat(
                model='gemma2:2b',
                messages=[
                    {'role': 'system', 'content': system_instruction},
                    {'role': 'user', 'content': user_input}
                ]
            )
            
            raw_output = response['message']['content']
            
            # Parse the structured local output lines
            for line in raw_output.split('\n'):
                if ',' in line:
                    parts = line.split(',', 4)
                    if len(parts) >= 3:
                        extracted_start = parts[0].strip()
                        extracted_end = parts[1].strip()
                        extracted_summary = parts[2].strip()
                        extracted_detail = parts[3].strip() if len(parts) > 3 else ""
                        extracted_source = parts[4].strip() if len(parts) > 4 else ""
                        
                        if extracted_end.lower() == "none" or not extracted_end:
                            extracted_end = None
                        if extracted_source.lower() == "none" or not extracted_source:
                            extracted_source = None
                        
                        # Verify start date parsing is valid before locking in
                        try:
                            date_parser.parse(extracted_start)
                            success = append_to_ics_file(
                                output_file, 
                                extracted_summary, 
                                extracted_start, 
                                extracted_detail,
                                end_time_str=extracted_end,
                                source_url=extracted_source
                            )
                            if success:
                                print(f" -> Locked (LLM): [{extracted_start}] {extracted_summary}")
                                parsed_any = True
                        except Exception:
                            pass

        except Exception as e:
            print(f"Local LLM processing interruption: {e}")
            
        # Fallback to regex if LLM was bypassed, failed, or returned unparseable text
        if not parsed_any:
            print("Attempting deterministic regex fallback extraction...")
            fallback_result = fallback_parse_text(user_input)
            if fallback_result:
                extracted_start, extracted_end, extracted_summary, extracted_detail, extracted_source = fallback_result
                success = append_to_ics_file(
                    output_file, 
                    extracted_summary, 
                    extracted_start, 
                    extracted_detail,
                    end_time_str=extracted_end,
                    source_url=extracted_source
                )
                if success:
                    print(f" -> Locked (Fallback Regex): [{extracted_start}] {extracted_summary}")
            else:
                print(" -> Skipped: No dates or parseable data found in input.")

    print("\n[Process Finalized].")
    print("To sync with Google Calendar: Settings -> Import & Export -> Import -> Upload this file.")

if __name__ == "__main__":
    run_matrix_processor()
