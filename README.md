# DocuDoc

> Communication Platform for Medical Treatments

## Running Locally

- First clone the repository: `git clone https://github.com/ayan-b/DocuDoc`
- Install the necessary dependencies: `pip install -r requirements.txt`
- Make the migrations:
  ```shell
  python manage.py makemigrations
  python manage.py migrate
  ```
- Create superuser: `python manage.py createsuperuser`. Provide a username, email and password.
- Now run the server: `python manage.py runserver` and the site should be live at localhost!

> In order to use the log in with drchrono and onpatient functionality, you need to add the following
> environment variables: `SOCIAL_AUTH_DRCHRONO_KEY`, `SOCIAL_AUTH_DRCHORONO_SECRET`, `SOCIAL_AUTH_ONPATIENT_KEY`
> and `SOCIAL_AUTH_ONPATIENT_SECRET`.

Also create the groups `doctor`, `patient`, `pharmacy` and `diagnosis_center` using the admin panel.

Coding Convention: PEP8 with line length 120.


## Troubleshooting

If you are getting `500 Internal Server Error` during adding a case or adding a user, make sure the user (patient or pharmacy or diagnosis center) exists.

## Credits

1. Hand xray: <span>Photo by <a href="https://unsplash.com/@owenbeard?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Owen Beard</a> on <a href="https://unsplash.com/s/photos/medical?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
2. Heart: <span>Photo by <a href="https://unsplash.com/@averey?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Robina Weermeijer</a> on <a href="https://unsplash.com/s/photos/medical?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
3. Chest xray: <span>Photo by <a href="https://unsplash.com/@cdc?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">CDC</a> on <a href="https://unsplash.com/s/photos/x-ray?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
4. Logo and favicon: [icons-for-free](https://icons-for-free.com/doctor+drug+health+healthcare+hospital+icon-1320167777175921163/).

## License

[MIT](./LICENSE)
