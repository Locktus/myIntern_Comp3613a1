# MyIntern API collection

Prerequisites: run `python manage.py init`, then `python manage.py run`.

Import `MyIntern_API.postman_collection.json` and `MyIntern_Local.postman_environment.json` into Postman. Set the Runner working directory to this `postman/` folder so the resume fixtures resolve.

Run with Newman from the repository root:

```bash
npx --yes newman run postman/MyIntern_API.postman_collection.json -e postman/MyIntern_Local.postman_environment.json --working-dir postman
```

In the Postman Runner, select the entire collection and confirm that PM-15
through PM-28 are checked. PM-15 must run before the dependent requests because
its response creates the `applicationId` collection variable. If file requests
are shown as unavailable, set the Runner working directory to this `postman/`
folder and confirm that `sample_resume.pdf` and `not_a_resume.txt` are present.

Import the JSON collection and environment files directly. Do not run the
Postman workspace folder `MyIntern API/`; its alphabetic folder ordering can run
Admin before Applications, causing PM-15 to be skipped before `applicationId` is
created. The canonical JSON collection is ordered Setup, Auth, Companies,
Applications, Admin, Users.
