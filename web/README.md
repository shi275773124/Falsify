# Falsify web

Local public-facing product site plus paste-and-go reviewer.

```bash
python web/serve.py
# open http://127.0.0.1:8000
```

The homepage is static and dependency-free. The reviewer form calls `/review`, which reuses `falsify.py` and your configured provider.

```bash
export DEEPSEEK_API_KEY=sk-...
python web/serve.py
```

Without a provider key or `.falsify` config, the reviewer returns a setup error. It does not pretend to run live analysis.
