// Keep the static data-signup links in the Quarto pages/template in sync.
// Their native href values also work when JavaScript is disabled.
const SIGNUP_URL = 'https://tuspl22-redcap.srv.mwn.de/redcap/surveys/?s=R839FPF3HNN8MP9L';

if (SIGNUP_URL) {
  document.querySelectorAll('[data-signup]').forEach((link) => {
    link.href = SIGNUP_URL;
  });
}

// The first photograph remains visible when JavaScript is unavailable.
// Images change only on request, so there is no automatic motion to pause.
document.querySelectorAll('[data-carousel]').forEach((carousel) => {
  const slides = [...carousel.querySelectorAll('[data-slide]')];
  const controls = carousel.querySelector('.carousel-controls');
  const dots = [...carousel.querySelectorAll('[data-slide-to]')];
  const status = carousel.querySelector('[data-carousel-status]');
  const viewport = carousel.querySelector('.carousel-slides');
  if (slides.length < 2 || !controls || !status || !viewport) return;

  let current = 0;
  const show = (index) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    dots.forEach((dot, i) => {
      if (i === current) dot.setAttribute('aria-current', 'true');
      else dot.removeAttribute('aria-current');
    });
    status.textContent = `Bild ${current + 1} von ${slides.length}`;
  };

  carousel.querySelector('[data-previous]').addEventListener('click', () => show(current - 1));
  carousel.querySelector('[data-next]').addEventListener('click', () => show(current + 1));
  dots.forEach((dot) => dot.addEventListener('click', () => show(Number(dot.dataset.slideTo))));
  controls.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const destinations = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: slides.length - 1 };
    if (!(event.key in destinations)) return;
    event.preventDefault();
    show(destinations[event.key]);
  });

  // Horizontal swipes and mouse drags change images; vertical scrolling stays native.
  let gesture = null;
  viewport.addEventListener('pointerdown', (event) => {
    if (!event.isPrimary || event.button !== 0) return;
    gesture = { id: event.pointerId, x: event.clientX, y: event.clientY };
  });
  viewport.addEventListener('pointerup', (event) => {
    if (!gesture || gesture.id !== event.pointerId) return;
    const dx = event.clientX - gesture.x;
    const dy = event.clientY - gesture.y;
    gesture = null;
    if (Math.abs(dx) >= 48 && Math.abs(dx) > Math.abs(dy) * 1.5) {
      show(current + (dx < 0 ? 1 : -1));
    }
  });
  viewport.addEventListener('pointercancel', () => { gesture = null; });
  viewport.addEventListener('pointerleave', () => { gesture = null; });
  controls.hidden = false;
});
