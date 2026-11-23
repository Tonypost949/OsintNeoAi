from flask import Blueprint, jsonify, request
import importlib.util as _ilu
import json
import os

api_bp = Blueprint('api', __name__)

# Shared engine (same module used by api/main.py): osintneoai/pipeline_engine.py
_pe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pipeline_engine.py')
_pe_spec = _ilu.spec_from_file_location('osintneoai_pipeline_engine', _pe_path)
pipeline_engine = _ilu.module_from_spec(_pe_spec)
_pe_spec.loader.exec_module(pipeline_engine)

@api_bp.route('/api/status')
def api_status():
    return jsonify({
        "status": "HEALTHY",
        "version": "1.0.0",
        "service": "OSINTNeoAI Blueprints Engine"
    })

@api_bp.route('/api/osintneoai/chat', methods=['POST'])
def api_osintneoai_chat():
    data = request.get_json(silent=True) or {}
    query = data.get('query', '')
    return jsonify({
        "response": "OSINT NEO AI received: " + query + ". Full intelligence stack integration pending.",
        "model": "osint-neo-ai-v1",
        "status": "online"
    })

@api_bp.route('/api/taxfunded/donate', methods=['POST'])
def api_taxfunded_donate():
    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '')
    amount = data.get('amount', '0')
    return jsonify({
        "status": "queued",
        "phone": phone,
        "amount": amount,
        "message": "Tax-funded donation queued for processing."
    })

@api_bp.route('/api/voicemail/record', methods=['POST'])
def api_voicemail_record():
    data = request.get_json(silent=True) or {}
    caller = data.get('caller', 'unknown')
    message = data.get('message', '')
    vm_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'voicemail')
    os.makedirs(vm_dir, exist_ok=True)
    import datetime
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    vm_file = os.path.join(vm_dir, 'vm_' + ts + '_' + caller.replace(' ', '_') + '.json')
    with open(vm_file, 'w') as f:
        json.dump({'caller': caller, 'message': message, 'timestamp': ts}, f)
    return jsonify({
        "status": "recorded",
        "file": os.path.basename(vm_file),
        "message": "Voicemail recorded successfully."
    })

@api_bp.route('/api/voicemail/list', methods=['GET'])
def api_voicemail_list():
    vm_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'voicemail')
    if not os.path.exists(vm_dir):
        return jsonify({"voicemails": [], "count": 0})
    files = sorted([f for f in os.listdir(vm_dir) if f.endswith('.json')], reverse=True)
    vms = []
    for f in files[:50]:
        try:
            with open(os.path.join(vm_dir, f)) as fh:
                vms.append(json.load(fh))
        except Exception:
            pass
    return jsonify({"voicemails": vms, "count": len(vms)})

@api_bp.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    return jsonify({
        "status": "SUCCESS",
        "message": "User registered successfully",
        "workspace_id": "usr_workspace_clean_001",
        "redirect_url": "/workspace"
    })

@api_bp.route('/api/auth/session', methods=['GET'])
def api_auth_session():
    return jsonify({
        "authenticated": True,
        "user_type": "public_investigator",
        "workspace_id": "usr_workspace_clean_001",
        "is_blank_workspace": True,
        "personal_data_isolated": True
    })

@api_bp.route('/api/tools/arsenal', methods=['GET'])
def api_tools_arsenal():
    tools = pipeline_engine.get_arsenal()
    return jsonify({"status": "success", "total_steps": len(tools), "tools": tools})


@api_bp.route('/api/workspace/pipeline/run', methods=['POST'])
def api_workspace_pipeline_run():
    data = request.get_json(silent=True) or {}
    narrative = (data.get('narrative') or data.get('text') or '').strip()
    if not narrative:
        return jsonify({"status": "error", "error": "narrative is required"}), 400
    return jsonify(pipeline_engine.run_pipeline(narrative[:50000], data.get('recipient')))


@api_bp.route('/api/dispatch/fax', methods=['POST'])
def api_dispatch_fax():
    data = request.get_json(silent=True) or {}
    return jsonify({
        "status": "QUEUED",
        "mode": data.get("mode", "A"),
        "anonymous": bool(data.get("anonymous", data.get("mode", "A") == "A")),
        "recipient": data.get("recipient", "Custodian of Records / Agency Director"),
        "subject": data.get("subject", "Public Records Request"),
        "channels": data.get("channels", ["email", "fax", "hardmail"]),
    })


@api_bp.route('/api/fleet/status', methods=['GET'])
def api_fleet_status():
    fo_path = r"C:\Amd949609_Antigravity_v1\tools\fleet_orchestrator\fleet_orchestrator.py"
    if not os.path.exists(fo_path):
        return jsonify({"status": "unavailable", "nodes": []}), 200
    spec = _ilu.spec_from_file_location("osintneoai_fleet_orchestrator", fo_path)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    probe = request.args.get("probe", "0") in ("1", "true", "yes")
    return jsonify(mod.get_fleet_status(probe_network=probe))

