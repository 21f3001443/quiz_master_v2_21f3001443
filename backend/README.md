# Quiz Master API
It is an API that acts as an integration point for frontend and backend database.

## 🖥️ How to Run the Application

### Prerequisites
- Python 3.11.11
- Miniconda (Environemnt management)
- VS Code
- Git desktop

### Step 1: Clone the Repository
Using any option
- Using Git desktop
- Using VScode
- Using terminal as below (Use Vscode for editing)
```bash
git clone https://github.com/21f3001443/quiz_master_21f3001443.git
cd quiz_master_21f3001443
```

### Step 2: Create and Activate Environment
```bash
conda create --name qm --file requirements.txt python=3.11.11 -y
conda activate qm
```
or 

```bash
conda create -n qm python=3.11.11 -y
conda activate qm
pip install -r requirements_pip.txt
```

or manually
```bash
pip install flask flask-restful flask_sqlalchemy bcrypt requests
```

### Step 5: Run the App
```bash
python app.py
```

### Step 6: Open in Browser
Visit: `http://127.0.0.1:5000/`

---

# ER DIAGRAM
![here](static/QUIZ_MASTER_ERD.jpg)

# 📄 ER Diagram Summary – Quiz System Schema

## 🔹 User management entities

- **`user`**
  - Stores user profile data including name, qualification, and role.
- **`role`**
  - Defines roles such as user or admin.
- **`login`**
  - Contains login credentials, linked to a specific `user`.

---

## 🧠 Syllabus Structure

- **`subject`**
  - Represents a course or domain (e.g., Math, Physics).
- **`chapter`**
  - Linked to a `subject`, represents a sub-topic or module.
- **`question`**
  - Associated with a `chapter`.
  - Contains a question title(MOCK, QUIZ1, QUIZ2 etc) and question statement.
- **`option`**
  - Belongs to a `question`, stores multiple answer choices.
  - Includes an `option_key` to identify the correct answer.

---

## 📝 Assessment Structure

- **`quiz`**
  - Represents a test under a subject.
  - Includes metadata like `date` and `duration`.
- **`quiz_question_association`**
  - Implements a many-to-many relationship between `quiz` and `question`.
- **`quiz_user_association`**
  - Implements a many-to-many relationship between `quiz` and `user`.

---

## 📥 User Responses

- **`response`**
  - Captures a user's selected `option` for a given `question` in a `quiz`.
  - Links to `user`, `quiz`, `question`, and `option`.
  - Extended to include `score`, `time`, `attempt`, etc.

---

## 🔗 Relationship Highlights

- Many-to-many relationships are normalized using **association tables**:
  - `quiz_user_association` (quiz ⇄ user)
  - `quiz_question_association` (quiz ⇄ question)
- Relationships are strictly defined using **foreign key constraints**.

---

## 🔐 Security

- User credentials are securely stored in the `login` table, separated from user identity.
- Role-based access is managed via a `role` table.

---

## ✅ Design Strengths

- **Well-normalized**: Avoids data duplication and supports clean joins.
- **Extensible**: Can be expanded with scoring, grading, analytics, and feedback modules.
- **Join-friendly**: Logical relationships enable rich querying for reports and dashboards.
- **Modular ownership**: Subjects → Chapters → Questions allow structured content delivery.

---