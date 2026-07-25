Title: Live Content

Description: Fetched live

Source: https://task-automation-demo-1.preview.emergentagent.com/static/js/bundle.js

---

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            height: 100vh;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <iframe id="contentFrame" src="https://app.emergent.sh/loading-preview?host=task-automation-demo-1.preview.emergentagent.com" allowfullscreen></iframe>
    <script>
        // Listen for messages from the iframe
        window.addEventListener('message', function(event) {

        	console.log(event.origin);
            // Optional: Add origin check for security
            // if (!['https://dev.emergentagent.com', 'https://app.emergent.sh'].includes(event.origin)) return;

            if (event.data && event.data.type === 'reload') {
                const iframe = document.getElementById('contentFrame');
                window.location.reload();
            }

            if (event.data && event.data.type === 'url') {
                const iframe = document.getElementById('contentFrame');
                window.open(event.data.url, '_blank');
            }
        });
    </script>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v4513226cdae34746b4dedf0b4dfa099e1781791509496" integrity="sha512-ZE9pZaUXND66v380QUtch/5sE9tPFh2zg45pR2PB0CVkCtOREv2AJKkSidISWkysEuQ0EH8faUU5du78bx87UQ==" data-cf-beacon='{"version":"2024.11.0","token":"7f7b0fd8732c4326aae4b9d58d5c514a","server_timing":{"name":{"cfCacheStatus":true,"cfEdge":true,"cfExtPri":true,"cfL4":true,"cfOrigin":true,"cfSpeedBrain":true},"location_startswith":null}}' crossorigin="anonymous"></script>
</body>
</html>

