import sys
from api.main import app

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from cli.cli import run_cli
        run_cli()
    elif len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        import streamlit.web.bootstrap
        streamlit.web.bootstrap.run("dashboard/app.py", "", [], [])
    elif len(sys.argv) > 1 and sys.argv[1] == "agent":
        from agent.agent import main
        main()
    else:
        import os
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=False)
