# Pipeline Kit documentation

Local Docusaurus site for the kit. It is **not** copied into customer `.pipeline/` packs.

The landing page (`/`) is the product overview: two kits, model choice, and
install. Markdown under `docs/` is the handbook — leave that layout as-is.
The customer adaptation guide in the repo is still
[`CUSTOMER-GUIDE.md`](../CUSTOMER-GUIDE.md) (copied to `.pipeline/docs/` on
`init`).

```bash
cd website
npm install
npm start
```

Open `http://127.0.0.1:3000`. Production preview:

```bash
npm run build
npm run serve
```
