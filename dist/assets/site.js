// Keep the static data-signup links in the Quarto pages/template in sync.
// Their native href values also work when JavaScript is disabled.
const SIGNUP_URL = 'https://tuspl22-redcap.srv.mwn.de/redcap/surveys/?s=R839FPF3HNN8MP9L';

if (SIGNUP_URL) {
  document.querySelectorAll('[data-signup]').forEach((link) => {
    link.href = SIGNUP_URL;
  });
}
