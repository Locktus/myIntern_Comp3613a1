# MyIntern API collection

Prerequisites: run `python manage.py init`, then `python manage.py run`.

Import `MyIntern_API.postman_collection.json` and `MyIntern_Local.postman_environment.json` into Postman. Set the Runner working directory to this `postman/` folder so the resume fixtures resolve.

Run with Newman from the repository root:

```bash
npx --yes newman run postman/MyIntern_API.postman_collection.json -e postman/MyIntern_Local.postman_environment.json --working-dir postman
```
