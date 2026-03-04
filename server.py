from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
VECTOR_DB_FOLDER = os.path.join(BASE_DIR, 'vector_db')
for d in (UPLOAD_FOLDER, VECTOR_DB_FOLDER):
    if not os.path.exists(d):
        os.makedirs(d)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# models
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    notes_path = db.Column(db.String(500))
    question_path = db.Column(db.String(500))  # store uploaded question paper
    vector_db_path = db.Column(db.String(500))
    evaluations = db.relationship('Evaluation', backref='subject', lazy=True)

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    student_name = db.Column(db.String(120))
    # score may contain non-integer text such as "4.5/52"; store as string
    score = db.Column(db.String(100))
    answer_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    result_text = db.Column(db.Text)

# create DB if not exists
# ensure tables are created when the app starts
with app.app_context():
    db.create_all()
    # the Subject model gained a question_path column; add it if absent
    try:
        # use sqlite3 directly to avoid any SQLAlchemy peculiarity
        import sqlite3
        dbfile = os.path.join(BASE_DIR, 'data.db')
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(subject)")
        cols = [row[1] for row in cur.fetchall()]
        if 'question_path' not in cols:
            print('adding question_path column to subject table')
            cur.execute('ALTER TABLE subject ADD COLUMN question_path VARCHAR(500)')
            conn.commit()
        # ensure evaluation.score column uses text affinity so that non-numeric
        # values can be stored.  SQLite requires table rebuild to change column
        # definition.
        cur.execute("PRAGMA table_info(evaluation)")
        ev_cols = cur.fetchall()
        score_info = [row for row in ev_cols if row[1] == 'score']
        if score_info:
            col_type = score_info[0][2].upper()
            if col_type not in ('TEXT', 'VARCHAR', 'CHAR'):
                print('migrating evaluation.score column to TEXT affinity')
                # create a temporary copy of the table with the new type
                cur.execute('ALTER TABLE evaluation RENAME TO evaluation_old')
                cur.execute('''
CREATE TABLE evaluation (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL,
    student_name VARCHAR(120),
    score TEXT,
    answer_path VARCHAR(500),
    created_at DATETIME,
    result_text TEXT,
    FOREIGN KEY(subject_id) REFERENCES subject(id)
)
''')
                cur.execute('''
INSERT INTO evaluation (id, subject_id, student_name, score, answer_path, created_at, result_text)
SELECT id, subject_id, student_name, score, answer_path, created_at, result_text
FROM evaluation_old
''')
                cur.execute('DROP TABLE evaluation_old')
                conn.commit()
        conn.close()
    except Exception as e:
        # report migration failure for debugging
        print('migration error', e)

# utility functions
def now():
    return datetime.now(timezone.utc)

@app.context_processor
def inject_now():
    # make now() available in templates
    return {'now': now}

# routes
@app.route('/')
def dashboard():
    subjects = Subject.query.all()
    return render_template('dashboard.html', subjects=subjects)

@app.route('/create_subject', methods=['GET', 'POST'])
def create_subject():
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        notes = request.files.get('notes')
        question = request.files.get('question')
        # vectordb name provided by user, must be unique and non-empty
        vect_name = request.form.get('vectordb_name', '').strip()

        # validate inputs
        if not name:
            error = 'Subject name is required.'
        elif not vect_name:
            error = 'Vector DB name is required.'
        else:
            # sanitize vector db name and enforce .pkl extension
            vect_name = os.path.basename(vect_name)
            if not vect_name.lower().endswith('.pkl'):
                vect_name += '.pkl'

            # check for existing subject or vector db with same identifiers
            exists = Subject.query.filter(
                (Subject.name == name) | (Subject.vector_db_path == vect_name)
            ).first()
            if exists:
                error = 'A subject with that name or vector DB name already exists. Choose unique values.'

        notes_path = ''
        q_path = ''
        if not error:
            if notes:
                fname = f"notes_{name}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
                # avoid collisions just in case
                if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], fname)):
                    error = 'Generated notes filename already exists; try again.'
                else:
                    notes.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                    notes_path = fname
            if question:
                fname = f"question_{name}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
                question.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                q_path = fname
            else:
                error = 'Question paper is required for evaluation.'

        if not error:
            # vector db file will live under vector_db folder; don't create it now
            vect_path = vect_name
            subj = Subject(name=name, notes_path=notes_path, question_path=q_path, vector_db_path=vect_path)
            db.session.add(subj)
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('create_subject.html', error=error)

@app.route('/subject/<int:subj_id>')
def view_subject(subj_id):
    subj = Subject.query.get_or_404(subj_id)
    # if question_path missing but a file exists in uploads, auto-associate it
    if not subj.question_path:
        for fname in os.listdir(app.config['UPLOAD_FOLDER']):
            if fname.startswith(f"question_{subj.name}_"):
                subj.question_path = fname
                db.session.commit()
                print(f"[AUTO LINK] associated question file {fname} with subject {subj.id}")
                break
    evaluations = Evaluation.query.filter_by(subject_id=subj_id).all()
    return render_template('subject.html', subject=subj, evaluations=evaluations)

@app.route('/subject/<int:subj_id>/upload', methods=['POST'])
def upload_script(subj_id):
    subj = Subject.query.get_or_404(subj_id)
    student = request.form.get('student_name')
    file = request.files.get('answer_pdf')
    fname = ''
    if file:
        fname = f"answer_{subj.name}_{student}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
    # create evaluation record with placeholder score
    eval = Evaluation(subject_id=subj.id, student_name=student, answer_path=fname)
    db.session.add(eval)
    db.session.commit()
    # if question paper is missing for this subject, do not start evaluation
    if not subj.question_path:
        eval.result_text = 'Question paper missing for subject. Upload question before evaluating.'
        eval.score = None
        db.session.commit()
        return redirect(url_for('view_subject', subj_id=subj.id))

    # perform evaluation synchronously
    try:
        print(f'[SYNC EVAL] Starting evaluation for id={eval.id}')
        evaluate(eval.id)
        print(f'[SYNC EVAL] Finished evaluation for id={eval.id}')
    except Exception as e:
        print(f'[SYNC EVAL] Exception during evaluation id={eval.id}: {e}')
    return redirect(url_for('view_subject', subj_id=subj.id))


@app.route('/subject/<int:subj_id>/upload_notes', methods=['POST'])
def upload_notes(subj_id):
    subj = Subject.query.get_or_404(subj_id)
    notes_file = request.files.get('notes_file')
    if not notes_file:
        return redirect(url_for('view_subject', subj_id=subj.id))
    # delete old notes file if exists
    if subj.notes_path:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], subj.notes_path)
        if os.path.exists(old_path):
            os.remove(old_path)
    fname = f"notes_{subj.name}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    notes_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
    subj.notes_path = fname
    
    # delete vector DB so it gets rebuilt on next evaluation (since notes changed)
    if subj.vector_db_path:
        vdb_path = os.path.join(VECTOR_DB_FOLDER, subj.vector_db_path)
        if os.path.exists(vdb_path):
            os.remove(vdb_path)
            print(f'[UPLOAD_NOTES] Deleted vector DB {subj.vector_db_path} to force rebuild with new notes')
    
    db.session.commit()
    return redirect(url_for('view_subject', subj_id=subj.id))


@app.route('/subject/<int:subj_id>/upload_question', methods=['POST'])
def upload_question(subj_id):
    subj = Subject.query.get_or_404(subj_id)
    qfile = request.files.get('question_file')
    if not qfile:
        return redirect(url_for('view_subject', subj_id=subj.id))
    fname = f"question_{subj.name}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    qfile.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
    subj.question_path = fname
    db.session.commit()
    # after uploading question, automatically re-run any pending evaluations for this subject
    pending = Evaluation.query.filter_by(subject_id=subj.id, score=None).all()
    if pending:
        print(f'[AUTO RE-EVAL] Found {len(pending)} pending evaluations for subject={subj.id}, running sequentially')
        for ev in pending:
            try:
                print(f'[AUTO RE-EVAL] Starting eval for id={ev.id}')
                evaluate(ev.id)
                print(f'[AUTO RE-EVAL] Finished eval for id={ev.id}')
            except Exception as ex:
                print(f'[AUTO RE-EVAL] Exception for id={ev.id}: {ex}')

    return redirect(url_for('view_subject', subj_id=subj.id))


@app.route('/subject/<int:subj_id>/update_question', methods=['POST'])
def update_question(subj_id):
    subj = Subject.query.get_or_404(subj_id)
    qfile = request.files.get('question_file')
    if not qfile:
        return redirect(url_for('view_subject', subj_id=subj.id))
    # delete old question file if exists
    if subj.question_path:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], subj.question_path)
        if os.path.exists(old_path):
            os.remove(old_path)
    fname = f"question_{subj.name}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    qfile.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
    subj.question_path = fname
    db.session.commit()
    return redirect(url_for('view_subject', subj_id=subj.id))


@app.route('/re_eval/<int:eval_id>', methods=['POST', 'GET'])
def re_eval(eval_id):
    ev = Evaluation.query.get_or_404(eval_id)
    subj = ev.subject
    # only run if question exists
    if not subj.question_path:
        ev.result_text = 'Cannot reevaluate: question paper missing for subject.'
        ev.score = None
        db.session.commit()
        return redirect(url_for('view_subject', subj_id=subj.id))
    try:
        print(f'[RE EVAL] Starting re-evaluation for id={eval_id}')
        evaluate(eval_id)
        print(f'[RE EVAL] Finished re-evaluation for id={eval_id}')
    except Exception as e:
        print(f'[RE EVAL] Exception during re-eval {eval_id}: {e}')
    return redirect(url_for('view_subject', subj_id=ev.subject_id))

@app.route('/evaluate/<int:eval_id>')
def evaluate(eval_id):
    evaluation = Evaluation.query.get_or_404(eval_id)
    subj = evaluation.subject

    # validate required files exist
    if not subj.question_path:
        evaluation.result_text = 'Error: Question paper not uploaded for this subject.'
        evaluation.score = None
        db.session.commit()
        return jsonify({'score': "-1"})
    if not evaluation.answer_path:
        evaluation.result_text = 'Error: Answer sheet path missing.'
        evaluation.score = None
        db.session.commit()
        return jsonify({'score': "-2"})

    # build absolute paths
    notes_file = os.path.join(app.config['UPLOAD_FOLDER'], subj.notes_path) if subj.notes_path else ''
    ans_file = os.path.join(app.config['UPLOAD_FOLDER'], evaluation.answer_path)
    qp_file = os.path.join(app.config['UPLOAD_FOLDER'], subj.question_path)
    db_file = os.path.join(VECTOR_DB_FOLDER, subj.vector_db_path)

    # verify files exist
    if not os.path.exists(ans_file):
        evaluation.result_text = f'Error: Answer file not found: {ans_file}'
        evaluation.score = None
        db.session.commit()
        return jsonify({'score': None})
    if not os.path.exists(qp_file):
        evaluation.result_text = f'Error: Question file not found: {qp_file}'
        evaluation.score = None
        db.session.commit()
        return jsonify({'score': None})

    print(1010)

    flag = '0' if os.path.exists(db_file) else '1'

    cmd = [sys.executable, 'app.py', flag, notes_file, db_file, ans_file, qp_file]
    print(f'[EVAL {eval_id}] Running: {" ".join(cmd)}')
    print(f'[EVAL {eval_id}] Working dir: {BASE_DIR}')
    print(f'[EVAL {eval_id}] Files: notes={os.path.exists(notes_file) if notes_file else "(optional)"}, answer={os.path.exists(ans_file)}, qp={os.path.exists(qp_file)}, db={os.path.exists(db_file)}')

    try:
        # use subprocess.run with explicit pipes instead of capture_output (unsupported
        # on older Python versions).  run blocks until completion and returns a
        # CompletedProcess object.
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=BASE_DIR,
            timeout=300,
        )
        out = result.stdout or ''
        err = result.stderr or ''

        # do not dump full model loading logs into server logs; keep only lengths
        # and short preview to avoid corrupting logs
        out_preview = (out[:400] + '...') if len(out) > 400 else out
        err_preview = (err[:400] + '...') if len(err) > 400 else err
        print(f'[EVAL {eval_id}] Return code: {result.returncode} | STDOUT len={len(out)} | STDERR len={len(err)}')
        print(f'[EVAL {eval_id}] STDOUT preview: {repr(out_preview)}')
        if err:
            print(f'[EVAL {eval_id}] STDERR preview: {repr(err_preview)}')

        # Filter out stray lines such as 'None' and empty lines, keep meaningful lines
        lines = [ln.strip() for ln in out.splitlines() if ln.strip() and ln.strip() != 'None']
        score_str = lines[-1] if lines else ''

        if result.returncode != 0:
            print(f'[EVAL {eval_id}] Process failed with return code {result.returncode}')
            # store concise error info; full logs remain visible in server console if needed
            evaluation.result_text = f'Process failed. STDOUT preview: {out_preview}\nSTDERR preview: {err_preview}'
            evaluation.score = None
        else:
            if score_str:
                print(f'[EVAL {eval_id}] Parsed score string: {repr(score_str)}')
                evaluation.score = score_str
                evaluation.result_text = f'Score: {score_str}'
            else:
                print(f'[EVAL {eval_id}] No score line found in stdout')
                # on success but no score found, save a short preview for debugging
                evaluation.score = None
                evaluation.result_text = f'No score found. STDOUT preview: {out_preview}\nSTDERR preview: {err_preview}'
    except subprocess.TimeoutExpired:
        print(f'[EVAL {eval_id}] Subprocess timed out (>300s)')
        evaluation.result_text = 'Evaluation timed out (took more than 5 minutes)'
        evaluation.score = None
    except Exception as ex:
        print(f'[EVAL {eval_id}] Exception: {type(ex).__name__}: {ex}')
        evaluation.result_text = f'Error: {type(ex).__name__}: {ex}'
        evaluation.score = None

    db.session.commit()
    # send back whatever was stored (may be None or text)
    return jsonify({'score': evaluation.score})

@app.route('/result/<int:eval_id>')
def show_result(eval_id):
    evaluation = Evaluation.query.get_or_404(eval_id)
    return render_template('evaluation_result.html', evaluation=evaluation)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/vector_db/<path:filename>')
def serve_vector_db(filename):
    return send_from_directory(VECTOR_DB_FOLDER, filename)


# deletion endpoints
@app.route('/delete_subject/<int:subj_id>', methods=['POST'])
def delete_subject(subj_id):
    subj = Subject.query.get_or_404(subj_id)
    # remove associated files and evaluations
    for ev in list(subj.evaluations):
        if ev.answer_path:
            path = os.path.join(app.config['UPLOAD_FOLDER'], ev.answer_path)
            if os.path.exists(path):
                os.remove(path)
        db.session.delete(ev)
    if subj.notes_path:
        path = os.path.join(app.config['UPLOAD_FOLDER'], subj.notes_path)
        if os.path.exists(path):
            os.remove(path)
    if subj.question_path:
        path = os.path.join(app.config['UPLOAD_FOLDER'], subj.question_path)
        if os.path.exists(path):
            os.remove(path)
    if subj.vector_db_path:
        path = os.path.join(VECTOR_DB_FOLDER, subj.vector_db_path)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(subj)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/delete_evaluation/<int:eval_id>', methods=['POST'])
def delete_evaluation(eval_id):
    ev = Evaluation.query.get_or_404(eval_id)
    subj_id = ev.subject_id
    if ev.answer_path:
        path = os.path.join(app.config['UPLOAD_FOLDER'], ev.answer_path)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(ev)
    db.session.commit()
    return redirect(url_for('view_subject', subj_id=subj_id))


@app.route('/rename_evaluation/<int:eval_id>', methods=['POST'])
def rename_evaluation(eval_id):
    ev = Evaluation.query.get_or_404(eval_id)
    subj_id = ev.subject_id
    new_name = request.form.get('student_name', '').strip()
    if new_name:
        ev.student_name = new_name
        db.session.commit()
    return redirect(url_for('view_subject', subj_id=subj_id))

if __name__ == '__main__':
    app.run(debug=True)
