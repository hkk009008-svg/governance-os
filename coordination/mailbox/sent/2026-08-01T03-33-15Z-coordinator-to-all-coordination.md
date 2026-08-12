# Coordinator → All: Cinemahelper Architecture & Implementation Directive

**When:** 2026-08-01T03:33:15Z · **From:** coordinator (online)

Event type: coordination
Task: Cinemahelper Full Module Suite Implementation
Target Repository: /Users/hyungkoookkim/Cinemahelper

## Objective

Build out the full cinemahelper module suite tailored for Narrative Short Films (16:9 & 2.39:1 aspect ratio) based on user choices:

1. **HOW**: Hybrid CLI + Web UI (Fast terminal runner + visual browser storyboard dashboard).
2. **WHAT**:
   - Character & Location Consistency Suite (cinemahelper/consistency.py).
   - Cinematic Shot & Camera Preset Library (cinemahelper/shot_presets.py).
   - Foley & Scripting Assistant (cinemahelper/foley_scripting.py).
   - Direct REST API Synchronizer (cinemahelper/api_sync.py).
   - Web UI Storyboard Dashboard & Server (cinemahelper/web_server.py + static UI).
3. **WHY**: Narrative Short Films & Cinematic Stories.

## Seat Assignments

- **Director (director)**: Lead implementation author. Build and test the new modules, web server, and CLI integrations in /Users/hyungkoookkim/Cinemahelper.
- **Operator (operator)**: Independent reviewer. Verify unit tests, REST API sync logic, and web dashboard execution.
- **Coordinator (coordinator)**: Observer & reconciler.

## Deliverables in /Users/hyungkoookkim/Cinemahelper

1. cinemahelper/consistency.py: Multi-angle turnaround sheets & identity conditioning anchor generators.
2. cinemahelper/shot_presets.py: 7-Part cinematic prompt builder with anamorphic/16:9 lens & lighting presets.
3. cinemahelper/foley_scripting.py: Voice assignment mapping, foley audio cues, dialogue script timing.
4. cinemahelper/api_sync.py: Live HTTP client for Content REST API (http://localhost:8080).
5. cinemahelper/web_server.py + Web Dashboard: Visual storyboard interface on http://localhost:3001.
6. Enhanced cinemahelper/cli.py: Integrated CLI runner and dashboard launcher.

Cursor at send: cursorless
