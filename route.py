from app import *

@app.route('/', methods = ['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for('panel'))
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    error = None
    msg = None
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        first_name = form.first_name.data
        last_name = form.last_name.data
        index_number = form.index_number.data

        if not index_number.isdigit():
            error = 'Incorrect index format'
        else:
            mysql = db_connection()
            cur = mysql.cursor()
            cur.execute('INSERT INTO users(username, password, first_name, last_name, index_number) VALUES (%s, %s, %s, %s, %s)', [username, password, first_name, last_name, index_number])
            mysql.commit()
            cur.close()
            mysql.close()
            return redirect(url_for('login'))

    return render_template('register.html', form = form, error = error, msg = msg)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    #checks if a user is already logged in
    if 'username' in session:
        return redirect(url_for('panel'))

    error = None
    if request.method == 'POST':
        username = request.form['username']
        pass_input = request.form['password']

        mysql = db_connection()
        cur = mysql.cursor()
        res = cur.execute('SELECT * FROM users WHERE username =%s;', [username])

        if res:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(pass_input, password):
                session['username'] = username
                session['id'] = str(data['id'])

                if username == 'admin':
                    session['admin'] = True
                    return redirect(url_for('adm_panel'))


                return redirect(url_for('panel'))
            else:
                error = 'Credentials incorrect!'

            cur.close()

        else:
            error = 'Credentials incorrect!'
        mysql.close()
    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.clear()
    return redirect(url_for('login'))

@app.route('/panel/leaveGroup/<string:id>', methods = ['POST'])
def leaveGroup(id):
    if 'username' in session:
        if request.method == 'POST':
            mysql = db_connection()
            cur = mysql.cursor()
            cur.execute('DELETE FROM memberships WHERE group_id = %s AND user_id = %s', [id, session['id']])
            mysql.commit()
            mysql.close()
            return redirect(url_for('panel'))


@app.route('/fix', methods = ['GET'])
def fix():
    if 'admin' in session:
        mysql = db_connection()
        cur = mysql.cursor()
        cur.execute('SELECT * FROM memberships')
        res = cur.fetchall()
        dict = {}
        for obj in res:
            if not obj['group_id'] in dict:
                dict[obj['group_id']] = 1
            else:
                dict[obj['group_id']] += 1

        for key, value in dict.iteritems():
            cur = mysql.cursor()
            cur.execute('UPDATE group_list SET currentSize = %s WHERE g_id = %s', (str(value), str(key)))
            mysql.commit()
        mysql.close()
        return '<p>fixed</p>'

@app.route('/panel', methods = ['GET', 'POST'])
def panel():
    if 'username' in session:
        mysql = db_connection()
    #leaving a group form
        if request.method == 'POST' and 'removeButton' in request.form:
            removedId = request.form.get('remove')
            cur = mysql.cursor()
            cur.execute('DELETE FROM memberships WHERE group_id = %s AND user_id = %s', [str(removedId), session['id']])
            mysql.commit()
            cur = mysql.cursor()
            cur.execute('UPDATE group_list SET currentSize = currentSize - 1 WHERE g_id = %s', [request.form.get('remove')])
            mysql.commit()
            cur.close()

            mysql.close()
            return redirect(url_for('panel'))

    #joining a group form
        if request.method == 'POST' and 'joinGroup' in request.form:
            cur = mysql.cursor()
            cur.execute('SELECT currentSize, maxSize, enabled FROM group_list WHERE g_id = %s', [request.form.get('group_id')])
            currentGroup = cur.fetchone()
            if currentGroup['currentSize'] < currentGroup['maxSize'] and currentGroup['enabled']:
                cur.execute('INSERT INTO memberships (user_id, group_id) VALUES (%s, %s)', [session['id'], request.form.get('group_id')])
                mysql.commit()
                cur = mysql.cursor()
                cur.execute('UPDATE group_list SET currentSize = currentSize + 1 WHERE g_id = %s', [request.form.get('group_id')])
                mysql.commit()
                cur.close()
            mysql.close()
            return redirect(url_for('panel'))

        if 'username' in session and request.method == 'GET':
            cur = mysql.cursor()
            cur.execute('SELECT subjects.name, subjects.s_id, group_list.time, group_list.day, group_list.g_id FROM group_list INNER JOIN subjects ON subjects.s_id = group_list.subject_id INNER JOIN memberships ON memberships.group_id = group_list.g_id WHERE memberships.user_id = %s', [session['id']])
            enmemberedSubjects = cur.fetchall()

            subIds = [item['s_id'] for item in enmemberedSubjects]
            allRenderInfo = []
            gotGroup = [] #all subjects the user is a signed up for
            noGroup = [] #the user is not signed up for those subjects
            allSubs = get_subjects()
            for sub in allSubs:
                if sub['s_id'] in subIds:
                    for thisSubject in enmemberedSubjects:
                        if thisSubject['s_id'] == sub['s_id']:
                            gotGroup.append({'name': thisSubject['name'], 'day': thisSubject['day'], 'time': thisSubject['time'], 'group_id': thisSubject['g_id']})
                else:
                    noGroup.append({'name': sub['name'], 'groups': get_groups(id = sub['s_id'])})

            mysql.close()
            return render_template('panel.html', gotGroup = gotGroup, noGroup = noGroup)

        mysql.close()
    return redirect(url_for('login'))

@app.route('/settings', methods = ['GET', 'POST'])
def settings():
    if 'username' in session:
        mysql = db_connection()
        error = None
        msg = None
        if request.method == 'POST':
            newIndex = request.form.get('index_number')
            newFirstName = request.form.get('first_name')
            newLastName = request.form.get('last_name')

            cur = mysql.cursor()
            if not newIndex.isdigit() or len(newIndex) != 6:
                error = 'Incorrect index number format'
            else:
                cur.execute('UPDATE users SET first_name = %s, last_name = %s, index_number = %s WHERE id = %s', [newFirstName, newLastName, newIndex, session['id']])
                mysql.commit()
                msg = 'Changes saved successfully.'
            cur.close()
        cur = mysql.cursor()
        cur.execute('SELECT first_name, last_name, index_number FROM users WHERE id = %s', [session['id']])
        userData = cur.fetchone()

        mysql.close()
        return render_template('settings.html', data = userData, error = error, msg = msg)
    return redirect(url_for('login'))
