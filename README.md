# Student Performance Analysis System

A beginner-friendly web prototype built with Python, Streamlit and SQLite.

## Features
- Dashboard with student count and class average
- Add, update and delete student details
- Enter and update subject-wise marks
- Calculate total, percentage and grade
- View performance graphs
- Download analysis and individual marks reports as CSV

## Run on your computer for testing
1. Install Python.
2. Open a terminal in this project folder.
3. Install packages:
   `pip install -r requirements.txt`
4. Start the app:
   `streamlit run app.py`

## Deploy online (no localhost for viewers)
1. Create a GitHub account and a new public repository.
2. Upload `app.py`, `database.py`, and `requirements.txt`.
3. Open Streamlit Community Cloud: https://share.streamlit.io/
4. Sign in with GitHub and choose **Create app**.
5. Select your repository, branch `main`, and main file `app.py`.
6. Click **Deploy**. Streamlit will provide a public `*.streamlit.app` link.
7. Share that link. Viewers open it directly in a browser; they do not need to run localhost.

## Important database note
This starter version uses a local SQLite file (`students.db`). On hosted cloud services, local files may not be permanent across app restarts or redeployments. It is suitable for a classroom demo, but for long-term online data storage, connect a hosted database such as Supabase or another persistent database.

## Grade rule used
- 90–100: A+
- 80–89: A
- 70–79: B
- 60–69: C
- 50–59: D
- Below 50: F

You can change these ranges in `database.py` and `app.py` to match your college rules.
