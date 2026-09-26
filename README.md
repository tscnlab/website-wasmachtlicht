# Was macht Licht? – Das Lichtcafé

A responsive German project landing page and English scientific-interest page, authored as reproducible Quarto documents and rendered to static HTML. The visual design follows the supplied Max Planck corporate design manual. No framework runtime, npm dependencies, remote fonts, tracking, or registration backend.

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

## Corporate design and supplied logos

The supplied `InnereUhr_CorporateStyleGuide.pdf` is the Max Planck Society print manual, version 1.2 (19 July 2022). Following the user’s preference for a selective interpretation, the web layout borrows the house greens (`#006c66`, `#005555`), generous clear space and locally hosted Roboto. White surfaces, sunlit yellow (`#ffda62`) and warm background gradients evoke morning light and brightness; green provides contrast in typography, buttons and institutional branding. Both language pages use this treatment. Sentence-case headings, lighter weights, softer corners and comfortable screen typography make the public-facing project feel more approachable. Print-only page dimensions and print-specific logo positions are not transferred literally to the responsive website.

The MPI logo is placed in the header. MPF, MPS/MPG and MPI logos are also presented together on white, with clear space, preserved proportions and links to the organisations. German and English MPF/MPI artwork is selected by page language. The supplied MPS/MPG artwork has German lettering on both pages; no translated logo was invented. The institutional row does not add an unconfirmed funding-award claim.

- `assets/logos/mpi-de.png`, `mpi-en.png`: rasterised from the supplied wide green MPI EPS files at 288 dpi, with transparency and Ghostscript's print-to-screen colour conversion.
- `assets/logos/mpf-de.png`, `mpf-en.png`: rasterised from the corresponding supplied MPF EPS originals using the same process.
- `assets/logos/mps.png`: the supplied `MPG_Logo_RGB_mpg-green.png`, copied unchanged.
- `assets/fonts/Roboto-Variable.ttf`: locally hosted Roboto; its SIL Open Font License is included in `assets/fonts/OFL-Roboto.txt`.

The logos have not been redrawn, rearranged or modified with image generation. The supplied print artwork is retained rather than inventing a mirrored web variant.

## Photograph

`assets/roadshow-verena-mueller.webp` is a real photograph of the existing mobile research trailer, credited to **Verena Müller**. Original: `32 Fotos Verena/Fuer Nextcloud/Nachtmensch_oder_Frühaufsteher_40.jpg` in the user's roadshow project. The source set also contains the folders `verenamuellerfotografie_Max_Planck_TUE` and `20250426 Verena Müller Roadshow Photos`, which support the attribution. The original is 7087 × 4727 pixels; the website copy is resized to 2400 × 1601 and encoded as WebP. No generated elements, retouching or synthetic alterations have been applied. The responsive layout may crop the display on larger screens.

The caption identifies it as the existing roadshow trailer before the planned Lichtcafé conversion. The previously generated café image has been removed from the current sources and exported website.

`scripts/prepare-brand-assets.py` records the reproducible conversion process. It requires the original roadshow project, Ghostscript and Pillow. Normal `quarto render` builds use the checked-in assets and require none of those external originals.

## Accessibility and maintenance

Semantic headings and landmarks, keyboard-operable native FAQ disclosures, visible focus indicators, a skip link, explicit page languages, descriptive link labels, responsive layouts, image alternative text and reduced-motion support are included. The page remains readable and navigable without JavaScript. `scripts/check-site.py` verifies local routes, assets and fragment targets after rendering.
