## What does this PR do?

<!-- Brief description -->

## Type

- [ ] New plugin data
- [ ] Data correction
- [ ] Code change
- [ ] Documentation

## Checklist

- [ ] `python -m plugindb.seed --validate` passes
- [ ] `python -m pytest tests/ -v` passes
- [ ] New plugins have all required fields (slug, name, manufacturer_slug, category, aliases)
- [ ] Aliases include the official plugin name
- [ ] Tags are lowercase and hyphenated
- [ ] No duplicate slugs or aliases
