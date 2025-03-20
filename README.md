# Markup Language

- The markup language is reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html

# Instructions

## Generate HTML Code

- Activate virtual environment: `. venv/bin/activate`
- Generate HTML code: `make html`
- Run dev server: `python3 -m http.server -b 127.0.0.1 -d build/html`
- Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

- for automatic updates while editing use `make livehtml` instead
  (automatically builds the html on changes and re-loads the browser page when saving the source document
  -- but the browser reloading only works, when opening the page from the sphinx output, i.e., just entering the adress is sometimes not sufficient.)

## Generate Latex PDF

- Activate virtual environment: `. venv/bin/activate`
- Generate Latex PDF: `make latexpdf`

# Initial Setup

- Create virtual environment: `python3 -m venv venv`
- Activate virtual environment: `. venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

# Publish new Version

- Activate virtual environment: `. venv/bin/activate`
- Run: `sphinx-build src/ docs/`
- Run: `make latexpdf`
- Copy `build/latex/securityanalysisofcryptographicprotocolswithdy.pdf` to `docs/`
- Commit and push repository

# Troubleshooting

If no static files are loaded, you have to add an empty file called `.nojekyll` to the `docs/` folder.