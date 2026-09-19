import azure.functions as func
import logging
import sys
import os

# Add repo to path
sys.path.insert(0, os.path.dirname(__file__))

from auto_correlation_enrichment_engine import AutomationOrchestrator

log = logging.getLogger(__name__)

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */5 * * * *")  # Every 5 minutes
def AutoCorrelationEnrichmentTimer(myTimer: func.TimerRequest) -> None:
    """
    Timer-triggered Azure Function for continuous data correlation.
    Runs every 5 minutes automatically.
    """
    if myTimer.past_due:
        log.info('The timer is past due!')
    
    log.info('AUTO-CORRELATION & ENRICHMENT cycle triggered')
    
    try:
        orchestrator = AutomationOrchestrator()
        orchestrator.run_cycle()
        log.info('ACE cycle completed successfully')
    except Exception as e:
        log.error(f'ACE cycle failed: {e}', exc_info=True)
        raise func.HttpResponseError(f'Correlation engine failed: {e}')


@app.route(route='correlation/status', auth_level=func.AuthLevel.ANONYMOUS)
def CorrelationStatus(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP endpoint to check correlation engine status and get latest results.
    """
    import json
    
    try:
        results_file = 'data/correlation_results.json'
        
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            return func.HttpResponse(
                json.dumps(results),
                status_code=200,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({'status': 'pending', 'message': 'No results yet'}),
                status_code=202,
                mimetype="application/json"
            )
    
    except Exception as e:
        log.error(f'Status check failed: {e}')
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route='correlation/trigger', auth_level=func.AuthLevel.FUNCTION)
def CorrelationTrigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP endpoint to manually trigger a correlation cycle.
    Requires function-level auth.
    """
    log.info('Manual ACE cycle triggered via HTTP')
    
    try:
        orchestrator = AutomationOrchestrator()
        orchestrator.run_cycle()
        
        return func.HttpResponse(
            'Correlation cycle started',
            status_code=202
        )
    
    except Exception as e:
        log.error(f'Trigger failed: {e}')
        return func.HttpResponse(
            f'Error: {str(e)}',
            status_code=500
        )
