<div align="center">
  <h1>🚀 ProjectMatch</h1>
  <p><strong>A collaborative team-formation web application driven by Machine Learning.</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge"/>
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django Badge"/>
    <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-learn Badge"/>
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS Badge"/>
    <img src="https://img.shields.io/badge/Alpine.js-8BC0D0?style=for-the-badge&logo=alpine.js&logoColor=white" alt="Alpine Badge"/>
  </p>
</div>

<br>

ProjectMatch is a collaborative web platform built in Django. It intelligently matches user profiles based on skills, interests, and project descriptions using **TF-IDF feature extraction** and **cosine similarity**, helping users build high-synergy, cross-functional product teams.

## ✨ Key Features

### 🏷️ Dynamic Alpine.js Profile Inputs
In the user profile edit page, standard flat text inputs for **Skills** and **Interests** are upgraded to dynamic, interactive tag-style inputs.
- Type a skill/interest and press **Enter** (or click **Add**) to create a badge pill.
- Click the **×** on any badge to easily remove it.
- Automatically serializes into a clean, comma-separated format on form submission.

### 🧠 Gap-Aware ML Re-ranking
On the matches page, users can filter candidates to intelligently fill missing roles in their team:
- **Roles Available:** Designer, Developer, Domain Expert, Data/Research, Marketing/Ops.
- **ML Logic:** Re-ranks candidates by boosting match scores (+0.25 for skill keyword match, +0.15 for looking-for text match) if they align with the chosen role.
- **Explainability:** Displays a special gap-fit card highlight and custom explanation prefix (e.g., *"Fills your Designer gap — strong UI/UX background."*).

### 💎 Premium Responsive UI
- Unified, modern typography using the **Outfit** Google Font.
- Sleek glassmorphic navigation bar with an Alpine.js-powered mobile menu toggler.
- Modern loading skeleton overlay that activates when computing matches to prevent page lock-up and enhance UX.

---

## 💻 Local Setup & Run

Follow these steps to get the project running locally:

**1. Activate Virtual Environment**
```bash
source .venv/bin/activate
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Database Setup & Demo Data**
Apply migrations and seed the database with demo profiles:
```bash
python manage.py migrate
python manage.py seed_data
```

**4. Start Development Server**
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your browser.

---

## ☁️ Deployment Configuration

This repository is optimized for modern PaaS deployment environments like **Render**, **Heroku**, or **Railway**.

- ⚙️ **Procfile:** Declares the web server entrypoint `web: gunicorn projectmatch.wsgi`.
- 📦 **WhiteNoise:** Integrated to safely compile and serve production static files (e.g., admin assets) even with `DEBUG=False`.
- 🔒 **Environment Variables:**
  - `DEBUG`: Set to `True` for development, `False` for production.
  - `ALLOWED_HOSTS`: Set to a comma-separated list of allowed domains (e.g., `your-app.render.com`).
  - `SECRET_KEY`: Set to a secure, private key.
