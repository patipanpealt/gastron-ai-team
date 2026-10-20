# Login, secrets, deploy

## Login
- `AUTH_USERS` = JSON `[{"email","role":"admin"|"member","hash":"scrypt:<salt-hex>:<hash-hex>"}]`, `AUTH_SECRET` = random hex (signs the cookie; change = log everyone out). Empty `AUTH_USERS` = open app (local dev).
- Use `:` in the hash format, **not `$`** — `.env` loaders expand `$words` and silently corrupt the hash (login always fails).
- Make hashes with node `crypto.scrypt` (16-byte salt, 32-byte key). Plain passwords are never stored. Warn about weak passwords (6-digit dates).
- `proxy.ts` (Next 16 middleware) lets `/login`, `/api/login`, `/brand/*` through; other API calls get 401, pages redirect to `/login`.
- To check the logged-in UI without typing real passwords: mint a short-lived cookie locally with `AUTH_SECRET`, then delete it.

## Secrets
- `.env.local` (chmod 600, gitignored) holds keys + `AUTH_*`. `.env.vercel` (gitignored) is a paste-ready copy for Vercel's env page.
- Before every commit: `git grep` staged files for key prefixes (`AIza`, `AQ.`, `sk-ant-`), `scrypt:`, and the passwords.
- The agent must not type keys/passwords into web forms; the user pastes them into Vercel.

## GitHub + Vercel
- `.gitignore`: `.env*`, `.next`, `node_modules`, `._*`, `.claude/`, third-party reference images (`Ref/`), old experiments, `**/preview/`, `skill-pack/*.zip`.
- Vercel: import the GitHub repo (Next.js preset) → auto-deploy on every push to `main`. The Vercel MCP connector may 403 on the team scope; the dashboard import works when the user is logged in.
- After adding env vars on Vercel: Redeploy. Check `/api/status` (`demo:false`, provider) and that `/` redirects to `/login`.
- Deployment URLs other than the production alias are behind Vercel auth (302): share only the production URL.

## Ops gotchas
- External drive: AppleDouble `._*` files after every write; turbopack cache corruption → `rm -rf .next`.
- HMR does not patch a live engine instance: reload the page after engine edits.
- Browser automation: background tabs give a 300 px canvas; 127.0.0.1 doesn't hydrate; use `?slot=qa`.
