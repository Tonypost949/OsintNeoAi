import azure.functions as func
import json
import logging
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

BACKEND_API = "https://osintneoai-app-949.azurewebsites.net"

@app.route(route="serverless_search")
def serverless_search(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Executing serverless OSINT search trigger.')
    query = req.params.get('q')
    if not query:
        try:
            req_body = req.get_json()
            query = req_body.get('q')
        except ValueError:
            query = None

    if query:
        try:
            r = requests.get(f"{BACKEND_API}/api/search?q={query}", timeout=10)
            return func.HttpResponse(r.text, status_code=200, mimetype="application/json")
        except Exception as e:
            return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")
    else:
        return func.HttpResponse(
            json.dumps({"status": "error", "message": "Pass a ?q= parameter in the query string"}),
            status_code=400,
            mimetype="application/json"
        )

@app.route(route="serverless_correlate")
def serverless_correlate(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Executing serverless correlation trigger.')
    try:
        r = requests.get(f"{BACKEND_API}/api/correlate", timeout=10)
        return func.HttpResponse(r.text, status_code=200, mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500, mimetype="application/json")

@app.timer_trigger(schedule="0 0 6 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False)
def daily_osint_cron(myTimer: func.TimerRequest) -> None:
    logging.info('Executing Daily 6:00 AM UTC OSINT Background Ingestion Cron.')
    try:
        r = requests.get(f"{BACKEND_API}/api/correlate", timeout=15)
        logging.info(f"Daily Correlation Sync Complete: Status {r.status_code}")
    except Exception as e:
        logging.error(f"Daily Cron Ingestion failed: {e}")
