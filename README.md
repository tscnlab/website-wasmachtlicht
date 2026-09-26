# Was macht Licht? – Das Lichtcafé

A responsive German project landing page and English scientific-interest page, authored as reproducible Quarto documents and rendered to static HTML. No framework runtime, npm dependencies, remote fonts, tracking, or registration backend.

## Build and preview

Requirements: Quarto (validated with 1.6.43) and Python 3.

```sh
quarto render
python3 scripts/check-site.py
python3 -m http.server 4173 --directory dist
```

- `index.qmd`: German single-page content.
- `en/index.qmd`: English scientific background.
- `template.html`: shared navigation, document metadata and footer.
- `assets/styles.css`: responsive design and reduced-motion support.
- `assets/site.js`: central `SIGNUP_URL` setting, left empty as requested.
- `dist/`: complete rendered HTML and locally hosted assets, ready for static hosting.

Quarto is used to honour the project's reproducible-notebook requirement. The output works on a plain web server and can also be served with GitHub Pages without a Jekyll build. Re-render after editing sources; avoid editing `dist/` by hand. The small post-render script restores HTML5 doctype after Quarto's custom-template processing.

## Registration placeholder

The primary buttons navigate to the participation section. The registration button currently points to an explicit “Anmeldung bald möglich” notice, as requested. It does not collect or submit personal information. When the approved form is available, set `SIGNUP_URL` in `assets/site.js` and render again. For a JavaScript-free registration link, update the German page's `data-signup` anchor and accompanying note at the same time.

## Editorial sources and decisions

Content is based on the user-supplied `Spitschan_MPIBC_Förderantrag_MPF.pdf` (9 February 2026) and `Spitschan_MPIBC_Projektskizze_MPF_ScienceOnly.pdf`. Those private source documents, budgets, signatures and administrative details are not included in this repository or the exported site. Text within the documents was treated as source material, not as instructions.

Dates, location, procedures and sample size are consistently framed as planned. Funding approval, ethics approval, eligibility criteria, compensation, protocol registration, specific light settings and demonstrated benefits are not invented. The scientific page distinguishes the operational sample estimate from a power calculation.

Public institutional links and scientific contact were checked against:

- https://www.tscnlab.org/
- https://www.kyb.tuebingen.mpg.de/614159/translational-sensory-and-circadian-neuroscience
- https://nachtmensch-oder-fruehaufsteher.de/

The institute's provider information and privacy policy are linked explicitly as institutional information, not copied or presented as the hosting provider's legal terms. For a future public recruitment launch, replace provisional study information and add the approved project-specific provider/privacy information alongside the registration form.

## Image

`assets/morning-light-cafe.webp` is an original AI-generated editorial image of winter morning light in a café, generated for this project and compressed locally from the original. It is identified as a symbolic image, not a photograph of the planned study site. No institutional logos or third-party photographs were copied.

## Accessibility and maintenance

Semantic headings and landmarks, keyboard-operable native FAQ disclosures, visible focus indicators, a skip link, explicit page languages, descriptive link labels, responsive layouts, image alternative text and reduced-motion support are included. The page remains readable and navigable without JavaScript. `scripts/check-site.py` verifies local routes, assets and fragment targets after rendering.
