// Add the approved registration form URL here when recruitment opens.
// Leave empty to keep the visible registration placeholder.
const SIGNUP_URL = '';

if (SIGNUP_URL) {
  document.querySelectorAll('[data-signup]').forEach((link) => {
    link.href = SIGNUP_URL;
    link.replaceChildren(document.createTextNode('Zur Anmeldung '));
    const arrow = document.createElement('span');
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '↗';
    link.append(arrow);
  });
  const note = document.getElementById('anmeldung-info');
  if (note) note.textContent = 'Informationen zur Teilnahme und zum Datenschutz findest du im Anmeldeformular.';
}
