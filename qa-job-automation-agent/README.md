# qa-job-automation-agent

AI-powered QA job search and application automation agent with a Flask web dashboard.

## What it does

- **Job matching** — scores job postings against your resume (`agent/job_matcher.py`)
- **Resume parsing** — extracts structured data from resumes (`agent/resume_parser.py`)
- **Application tracking** — tracks applications through the pipeline (`agent/application_tracker.py`)
- **Web dashboard** — monitor jobs, applications, and analytics from the browser (`web_dashboard/app.py`)

## Project structure

```
qa-job-automation-agent/
├── web_dashboard/
│   ├── app.py                # Flask application entry point
│   ├── agent/                # resume_parser, job_matcher, application_tracker
│   ├── templates/            # dashboard, applications, analytics, settings, login
│   ├── static/               # CSS assets
│   ├── scripts/              # init_db.py, create_test_resume.py
│   ├── data/                 # resume JSON, reports, logs (created at runtime)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── render.yaml               # Render.com deploy config
```

## Run locally

```bash
cd web_dashboard
pip install -r requirements.txt
python scripts/init_db.py
python app.py
```

Then open http://localhost:5000 (or the port in `$PORT`).

## Deploy

Push to Render using `render.yaml` (`gunicorn web_dashboard.app:app`), or build the Docker image:

```bash
cd web_dashboard
docker compose up --build
```

## License

MIT
