# Collabstr Full‑Stack AI Developer Project

> Build and demo a tiny but real AI feature with a simple front end. This should take you less than 1 hour.
> 

## 1. Goal

Create a minimal, production‑minded AI feature that showcases:

- Practical LLM orchestration in Python/Django
- Sensible prompt design and guardrails
- Basic telemetry, like latency and token cost
- A lightweight, clean front end using HTML/CSS/JavaScript and jQuery

## 2. What to Build

An “AI Brief Generator” that produces a short campaign brief or creator outreach message for a brand given a few inputs. Keep scope tight so it fits in 1 hour.

### Inputs (front-end form)

- Brand name
- Target platform: Instagram, TikTok, or UGC (select)
- Goal: Awareness, Conversions, or Content Assets (select)
- Tone: Professional, Friendly, or Playful (select)

### Output

- A 4–6 sentence brief tailored to the selections
- 3 suggested content angles
- 3 creator selection criteria bullets

## 3. Requirements

### Back end (Django, Python)

- Repo may be bare‑bones Django (SQLite is fine; no migrations needed beyond defaults)
- One endpoint that:
    - Validates inputs server‑side
    - Calls an LLM (OpenAI or similar) with a concise, deterministic system prompt
        - Use a short system prompt describing style and constraints. Provide a compact user prompt from the inputs.
    - Uses JSON schema or function‑call style output to reliably return fields: `brief`, `angles[]`, `criteria[]`
    - Includes basic safeguards: max tokens, temperature <= 0.5, basic rate-limiting, and a profanity filter or allowlist validation on inputs
    - Returns timing and token usage metrics in the JSON response
- Organize code for clarity: [`views.py`](http://views.py), `services/[llm.py](http://llm.py)` for the model call

### Front end (HTML/CSS/JS/jQuery)

- Single page with a clean, modern look that feels Collabstr‑adjacent
    - You are free to re-use design and styling elements from our live site: https://collabstr.com
- Form with 4 inputs and a Submit button
- On submit: disable button, show a loading state, send AJAX to endpoint
- Render the result neatly: brief paragraph, numbered angles, bulleted criteria

## 4. Deliverables (within 1 hour)

<aside>
💡

Please email the URL for both of these items to clayton@collabstr.com once the project is complete

</aside>

1. Public GitHub repo link
    - Brief notes in README on:
        1. Prompt design choices
        2. Guardrails implemented
        3. How you measured tokens and latency
        4. Short Loom demoing the feature (under 1 minute)
2. Host the live implementation on a publicly available webpage for us to review 

## 5. Evaluation Criteria

### Front end

- Clean, unobtrusive UI with clear loading and error states
- Demonstrated understanding of good design, that looks and feels like a Collabstr product.
- Simple jQuery AJAX that’s easy to follow

### Back end

- Clear code organization and small, readable functions
- Deterministic output via JSON schema or function calls
- Basic safety and cost/latency visibility

If anything is unclear, make a reasonable assumption and proceed. Timebox tightly—shipping a working vertical slice is the goal. You can also email me at clayton@collabstr.com, and I will respond promptly.