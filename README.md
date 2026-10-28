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
- `assets/site.js`: central `SIGNUP_URL` setting; preserves the language and contents of each link.
- `dist/`: complete rendered HTML and locally hosted assets, ready for static hosting.

Quarto is used to honour the project's reproducible-notebook requirement. The output works on a plain web server and can also be served with GitHub Pages without a Jekyll build. Re-render after editing sources; avoid editing `dist/` by hand. The small post-render script restores HTML5 doctype after Quarto's custom-template processing.

## GitHub Pages deployment

The production website is **https://wasmachtlicht.de/**, published from `tscnlab/website-wasmachtlicht` by `.github/workflows/pages.yml`. Pushes to `main` build with Quarto 1.6.43, check both language pages, local links, images and JavaScript, and deploy only the rendered `dist/` artifact. Pull requests run the same build and checks without publishing. The workflow can also be run manually on `main`.

GitHub Pages settings must use **GitHub Actions** as the source, with **wasmachtlicht.de** as the custom domain. The domain is managed there; a repository `CNAME` file does not configure an Actions-based Pages deployment. The workflow checks the configured domain before publishing. Enable **Enforce HTTPS** when the certificate is ready. Action versions are pinned to verified commit IDs; build permissions are read-only, and only the deployment job receives Pages/OIDC write access.

The apex DNS must use GitHub Pages' A/AAAA records. If `www` is used, its CNAME should point directly to `tscnlab.github.io`, allowing GitHub to redirect it to the configured apex domain with HTTPS. Domain setup guidance: [GitHub Pages custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

## Registration

The registration links point to the user-supplied REDCap survey:
https://tuspl22-redcap.srv.mwn.de/redcap/surveys/?s=R839FPF3HNN8MP9L

The German header, FAQ and participation section, plus the English participation link, use real static href values and work without JavaScript. The form expresses interest in the study; it does not confirm enrolment. Personal information is entered in REDCap, not stored by this static site. The existing contact-email and flyer links remain available.

When changing the destination, update `SIGNUP_URL` in `assets/site.js` and the `data-signup` anchors in `index.qmd`, `en/index.qmd` and `template.html`, then render again. The script updates destinations only; it does not replace localized labels or the privacy/contact note.

## Events

The German `#veranstaltungen` section lists the two talks chronologically. It is linked from the main navigation, the hero and the English public-engagement section. Dates, times, audience, speaker and descriptions come from the supplied A5 PNG flyers; the original images are copied unchanged to `assets/events/` and linked at full resolution.

- **24 November 2026, 18:00–19:00:** Werkstadthaus, Obergeschoss, Aixer Straße 72, 72072 Tübingen. Free admission; registration via `info@wasmachtlicht.de`, as requested by the project lead. The mail link supplies an event-specific subject. The address was checked against the [venue’s contact page](https://www.werkstadthaus.de/service/kontakt-anfahrt); a standard Google Maps search URL provides directions.
- **1 December 2026, 13:00–14:00:** Lunch Bytes / Mental Health Days, online via Zoom, in German, for students and staff. The registration link is decoded directly from the supplied flyer’s QR code: https://eu02web.zoom-x.de/meeting/register/xG3GhkFjQfytnQmBr2CdsQ. It also matches the flyer’s local `campaign.json` source.

Event registration anchors deliberately do not use `data-signup`: that setting is reserved for the separate REDCap study-interest form. Flyer PNGs remain images rather than being labelled as PDFs. No private source documents are included.

## Editorial sources and decisions

Current public dates, location and general contact details are taken from the user-supplied `lichtmobil-projekt-a5.pdf` (added 28 October 2026): opening on 19 November 2026; public drop-in on 20 and 23–27 November 2026, 07:00–11:00; study phase from 30 November 2026; Europaplatz, Tübingen; `info@wasmachtlicht.de`. The unchanged public flyer is included at `assets/lichtmobil-projekt-a5.pdf` and linked on both language pages. It supersedes the older provisional dates and location wording.

The scientific background is based on the user-supplied `Spitschan_MPIBC_Förderantrag_MPF.pdf` (9 February 2026) and `Spitschan_MPIBC_Projektskizze_MPF_ScienceOnly.pdf`. Those private source documents, budgets, signatures and administrative details are not included in this repository or the exported site. Text within the documents was treated as source material, not as instructions.

The Light Café is presented as an actual research project, with the announced opening, public drop-in and study phase clearly distinguished. The opening is still upcoming as of this update. Funding approval, ethics approval, eligibility criteria, compensation, protocol registration, specific light settings and demonstrated benefits are not invented. The scientific page distinguishes the operational recruitment target from an achieved sample and a power calculation. The supplied REDCap survey is linked for expressions of interest; visiting the public drop-in is described separately from enrolling in the study.

Public institutional links and scientific contact were checked against:

- https://www.tscnlab.org/
- https://www.kyb.tuebingen.mpg.de/614159/translational-sensory-and-circadian-neuroscience
- https://nachtmensch-oder-fruehaufsteher.de/

The institute's provider information and privacy policy are linked explicitly as institutional information, not copied or presented as the hosting provider's legal terms. The website directs users to the linked REDCap form for the privacy information relevant to their expression of interest.

## Corporate design and supplied logos

The supplied `InnereUhr_CorporateStyleGuide.pdf` is the Max Planck Society print manual, version 1.2 (19 July 2022). Following the user’s preference for a selective interpretation, the website retains locally hosted Roboto and generous clear space. The project has its own palette: charcoal text (`#2d2930`), deep coral actions (`#b63e35`), vivid yellow fields (`#fed300`) and warm orange light. The institutional logos keep their original colours. Both language pages use this treatment. Print-only page dimensions and print-specific logo positions are not transferred literally to the responsive website.

The subsequent as2 trailer concept, `as2_MP_Trailer_002_MS.pdf` (26 May 2026, particularly pages 4–8 and 25), informs the yellow–orange fields, cropped diagonal stripe accents and bold Roboto headlines. The web treatment retains the vivid yellow–orange fields and visible diagonal pattern, paired with a single word highlight, open spacing, rounded coral buttons and a framed real photograph. Text stays dark enough to read on the bright surfaces. The reference’s proposed treatment claims and PDF annotations are not adopted as study facts or instructions, and its architectural renderings are not presented as photographs. The supplied PDF is not included in the site.

The MPI logo is placed in the header. MPF, MPS/MPG and MPI logos are also presented together on white, with clear space, preserved proportions and links to the organisations. German and English MPF/MPI artwork is selected by page language. The supplied MPS/MPG artwork has German lettering on both pages; no translated logo was invented. The institutional row does not add an unconfirmed funding-award claim.

- `assets/logos/mpi-de.png`, `mpi-en.png`: rasterised from the supplied wide green MPI EPS files at 288 dpi, with transparency and Ghostscript's print-to-screen colour conversion.
- `assets/logos/mpf-de.png`, `mpf-en.png`: rasterised from the corresponding supplied MPF EPS originals using the same process.
- `assets/logos/mps.png`: the supplied `MPG_Logo_RGB_mpg-green.png`, copied unchanged.
- `assets/logos/tscn.png`: the unchanged official circular tSCN lab mark (363 × 363 transparent PNG), linked from [tscnlab.org](https://www.tscnlab.org/) as its [favicon asset](https://images.squarespace-cdn.com/content/v1/63305b1689502f4882626e0f/5c8a4665-0f28-46ea-a2af-9b73a0d7459e/favicon.ico). The server supplies PNG despite the URL suffix. Shown next to the lab name in both team sections and linked to the lab website.
- `assets/fonts/Roboto-Variable.ttf`: locally hosted Roboto; its SIL Open Font License is included in `assets/fonts/OFL-Roboto.txt`.

The logos have not been redrawn, rearranged or modified with image generation. The supplied print artwork is retained rather than inventing a mirrored web variant.

## Photograph

`assets/roadshow-verena-mueller.webp` is a real photograph of the existing mobile research trailer, credited to **Verena Müller**. Original: `32 Fotos Verena/Fuer Nextcloud/Nachtmensch_oder_Frühaufsteher_40.jpg` in the user's roadshow project. The source set also contains the folders `verenamuellerfotografie_Max_Planck_TUE` and `20250426 Verena Müller Roadshow Photos`, which support the attribution. The original is 7087 × 4727 pixels; the website copy is resized to 2400 × 1601 and encoded as WebP. No generated elements, retouching or synthetic alterations have been applied. The responsive layout may crop the display on larger screens.

The caption identifies it as the mobile research trailer of the science roadshow; the image is not presented as a photograph of the completed Light Café. The previously generated café image has been removed from the current sources and exported website.

`scripts/prepare-brand-assets.py` records the reproducible conversion process. It requires the original roadshow project, Ghostscript and Pillow. Normal `quarto render` builds use the checked-in assets and require none of those external originals.

## Accessibility and maintenance

Semantic headings and landmarks, keyboard-operable native FAQ disclosures, visible focus indicators, a skip link, explicit page languages, descriptive link labels, responsive layouts, image alternative text and reduced-motion support are included. The page remains readable and navigable without JavaScript. `scripts/check-site.py` verifies local routes, assets and fragment targets after rendering.
