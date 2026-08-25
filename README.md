# ProjectMatch 🚀

ProjectMatch is a collaborative team-formation web application built in Django. It matches user profiles based on skills, interests, and project descriptions using TF-IDF feature extraction and cosine similarity, helping build high-synergy cross-functional product teams.

## Tech Stack
* **Backend**: Django 6.1, SQLite, Gunicorn
* **Logic**: Scikit-learn (TF-IDF Vectorization, Cosine Similarity)
* **Styling**: Tailwind CSS (via CDN)
* **Interactivity**: Alpine.js (via CDN)
* **Production Static Management**: WhiteNoise

---

## Key Features

### 1. Tag-Style Alpine.js Profile Inputs
In the user profile edit page, standard flat text inputs for **Skills** and **Interests** are upgraded to dynamic tag-style inputs.
* Type a skill/interest and press **Enter** (or click **Add**) to create a badge pill.
* Click the **×** on any badge to remove it.
* Automatically serializes into a comma-separated format on form submission.

### 2. Gap-Aware Re-ranking
On the matches page, users can filter candidates to fill missing roles:
* **Roles**: Designer, Developer, Domain Expert, Data/Research, Marketing/Ops.
* **Logic**: Re-ranks candidates by boosting match scores (+0.25 for skill keyword match, +0.15 for looking-for text match) if they align with the chosen role.
* **Explainability**: Displays a special gap-fit card highlight and custom explanation prefix (e.g. *"Fills your Designer gap — strong UI/UX background."*).

### 3. Responsive Premium UI
* Unified typography using the **Outfit** Google Font.
* Sleek glassmorphic navigation bar with an Alpine.js mobile menu toggler.
* Modern loading skeleton overlay that activates when computing matches to prevent page lock-up and enhance UX.

---

## Local Setup & Run

1. **Activate Virtual Environment**:
   ```bash
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup & Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the app at `http://127.0.0.1:8000/`.

---

## Deployment Configuration

This repository is optimized for deployment to cloud platforms like Render or Railway.

* **Procfile**: Declares the web server entrypoint `web: gunicorn projectmatch.wsgi`.
* **WhiteNoise**: Integrated to safely compile and serve production static files (e.g., admin assets) even with `DEBUG=False`.
* **Environment Variables**:
  * `DEBUG`: Set to `True` for development, `False` for production.
  * `ALLOWED_HOSTS`: Set to a comma-separated list of allowed domains (e.g. `your-app.render.com`).
  * `SECRET_KEY`: Set to a secure, private key.
