# Generated contract type checkpoint

The five established Zod wire schemas remain authoritative. Python TypedDicts are
now generated from their exported JSON Schema with pinned datamodel-code-generator
0.83.0, including nested/discriminated models, optional keys and recursive JSON.
Identification validation continues to use the same complete JSON Schema rules.
The one cast following successful validation is an audited narrowing, not a
replacement for validation; generated TypedDicts do not validate at runtime.

Run from this repository:

```sh
python3 -m venv /tmp/chirp-quality
/tmp/chirp-quality/bin/pip install -r backend-inference/requirements-quality.lock
/tmp/chirp-quality/bin/python scripts/generate_python_contracts.py --check
cd backend-inference
/tmp/chirp-quality/bin/mypy --config-file pyproject.toml
/tmp/chirp-quality/bin/ruff check app/models/identification.py app/models/generated
/tmp/chirp-quality/bin/ruff format --check app/models/identification.py app/models/generated
/tmp/chirp-quality/bin/python -m unittest discover -s tests -p 'test_*contract.py'
```

This checkpoint passes 34 contract tests and strict mypy on seven contract modules.
It does not claim the legacy prototype inference service is production-typed;
the new modular audio service is a separate workstream. Generated camelCase keys
have a narrow naming-lint exception to preserve published wire names. Generators
reject non-local references before compilation; no provider or network schema
resolution is authorized.

Sources consulted: [generator documentation](https://datamodel-code-generator.koxudaxi.dev/),
[mypy strict configuration](https://mypy.readthedocs.io/en/stable/config_file.html),
[Pydantic schema modes](https://docs.pydantic.dev/latest/concepts/json_schema/).
