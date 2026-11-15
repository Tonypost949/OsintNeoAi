Toxic Trace Atlas
Created by Perplexity for OsintNeoAi
Revision r3 — orbit fix
Changed: separated schematic site coordinates; real yaw/pitch rotation with variable depth and perspective; collision-aware labels; responsive layout and reliable individual site buttons.

RUN OFFLINE
Extract the folder and open index.html in a modern browser. No build, internet, accounts, API keys, external libraries or fonts are required.

CONTROLS
Drag the stage horizontally for yaw and vertically for pitch. Scroll to zoom.
Zoom + / Zoom - adjust the view; Rotate left and Tilt up provide button alternatives.
Reset view restores the separated default layout. Click or keyboard-activate any site to update its evidence panel.

DATA AND PROVENANCE
All four sites and their risk indices, contaminants and event timelines are fictional demonstration data. The constellation is schematic, not geographic. Risk scores are illustrative, not a validated scientific or legal assessment.
The original analyst note is preserved verbatim:
This prototype uses illustrative records only. Replace the embedded dataset with authorized, source-linked public records before investigative use.
This is a standalone replacement built from the reported defects and the live page's visible content; it is not a byte-preserving patch of an available r2 source archive.

IMPLEMENTATION
World coordinates rotate around Y (yaw), then X (pitch). Rotated Z feeds 5/(5-Z) perspective. Node size varies with that perspective; labels are placed against node and prior-label bounding boxes. Rendering runs on input and resize. No network requests are made.
An arbitrary edge-on 3D view can align nodes. Reset view restores the tested separated layout. No claim of overlap-free geometry at every possible orbit angle is made.

VERIFIED TESTS
Headless Chromium 134, desktop 1440 x 1000 and phone-sized 390 x 844 viewport; local file URL.
At each size clicked all four nodes and checked the selected name and three timeline events. Repeated node clicks after two-axis dragging.
Clicked Zoom +, Zoom -, Rotate left, Tilt up, Reset view; confirmed camera text changed for every control.
Dragged 30 pixels horizontally and 25 vertically; confirmed yaw and pitch changed and projected coordinates changed. Checked wheel zoom.
Checked default and dragged rendered element bounds for node-node, label-label and node-label overlaps; none found. No horizontal page overflow or JavaScript errors detected.
Full-page screenshots captured at both widths with Harbor Fuel Terminal selected.
Tests are automated Chromium mouse-input tests, not physical-device touch tests or exhaustive orbit-angle testing.
