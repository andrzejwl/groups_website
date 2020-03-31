from app import *
from xlsxdump import xlsx_dump

#contains name, id and all groups related to the given subject in a database result format
class Subject():
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.groups = get_groups(self.id)

def missing(db_groups, form_groups):
    ids = []
    for g in db_groups:
        ids.append(g['g_id'])

    for g in form_groups:
        if g['group_id'] in ids and g['group_id'] != 'new' and g['group_id']:
            ids.remove(g['group_id'])

    return ids

@app.route('/adm_panel', methods = ['GET', 'POST'])
def adm_panel():
    if 'admin' in session:
        mysql = db_connection()
        #disabling signing up for a group
        if request.method == 'POST' and 'disId' in request.form:

            cur = mysql.cursor()
            cur.execute('UPDATE group_list SET enabled = false WHERE g_id = %s', [request.form.get('disId')])
            mysql.commit()
            cur.close()
            mysql.close()
            return redirect(url_for('adm_panel'))

        #enabling signing up for a group
        if request.method == 'POST' and 'enId' in request.form:
            cur = mysql.cursor()
            cur.execute('UPDATE group_list SET enabled = true WHERE g_id = %s', [request.form.get('enId')])
            mysql.commit()
            cur.close()
            mysql.close()
            return redirect(url_for('adm_panel'))

        if request.method == 'POST' and 'disAll' in request.form:
            cur = mysql.cursor()
            cur.execute('UPDATE group_list SET enabled = false WHERE subject_id = %s', [request.form.get('disAll')])
            mysql.commit()
            cur.close()
            mysql.close()
            return redirect(url_for('adm_panel'))

        if request.method == 'POST' and 'enAll' in request.form:
            cur = mysql.cursor()
            cur.execute('UPDATE group_list SET enabled = true WHERE subject_id = %s', [request.form.get('enAll')])
            mysql.commit()
            cur.close()
            mysql.close()
            return redirect(url_for('adm_panel'))

        if request.method == 'GET':
            #listing all existing subjects
            sl = []
            for item in get_subjects():
                sl.append(Subject(item['name'], item['s_id']))

            mysql.close()
            return render_template('adm_panel.html', subj_list = sl)
        mysql.close()

    return redirect(url_for('login'))

@app.route('/adm_panel/xlsxdump/<string:id>', methods = ['GET'])
def get_xlsx(id):
    if 'admin' in session:
        mysql = db_connection()
        cur = mysql.cursor()
        groups = []
        cur.execute('SELECT g_id, day, time FROM group_list WHERE subject_id = %s;', [id])
        res = cur.fetchall()
        for g in res:
            cur.execute('SELECT users.first_name, users.last_name, users.index_number FROM users INNER JOIN memberships ON users.id = memberships.user_id WHERE memberships.group_id = %s', [g['g_id']])
            membsTmp = cur.fetchall()
            groups.append({'day': g['day'], 'time': g['time'], 'members': membsTmp})

        cur.execute('SELECT name FROM subjects WHERE s_id = %s', [id])
        subjectName = cur.fetchone()['name']
        cur.close()
        xlsx_dump(subjectName, groups)
        mysql.close()
        return send_file(os.getcwd()+'/excel/'+subjectName+'.xlsx', as_attachment = True)
    return redirect(url_for('login'))


@app.route('/adm_panel/all_users', methods = ['GET'])
def all_users():
    if 'admin' in session:
            mysql = db_connection()
            cur = mysql.cursor()
            cur.execute('SELECT first_name, last_name, index_number FROM users')
            res = cur.fetchall()
            mysql.close()
            return render_template('all_users.html', users = res)
    return redirect(url_for('login'))

@app.route('/adm_panel/members/<string:id>', methods = ['GET', 'POST'])
def members(id):
    if 'admin' in session:
        mysql = db_connection()
        if request.method == 'POST':
            userId = request.form.get('userId')
            cur = mysql.cursor()
            cur.execute('DELETE FROM memberships WHERE group_id = %s AND user_id = %s', [id, userId])
            mysql.commit()
            cur.execute('UPDATE group_list SET currentSize = currentSize - 1 WHERE g_id = %s', [id])
            mysql.commit()

        cur = mysql.cursor()
        cur.execute('SELECT memberships.user_id, users.first_name, users.last_name FROM memberships INNER JOIN users ON memberships.user_id = users.id WHERE memberships.group_id = %s;', [id])
        res = cur.fetchall()

        membersInfo = []
        for item in res:
            membersInfo.append({'name': item['first_name']+ ' ' +item['last_name'], 'id': item['user_id']})

        mysql.close()
        return render_template('members.html', membersInfo = membersInfo)

    return redirect(url_for('login'))

@app.route('/adm_panel/create_subject', methods = ['GET', 'POST'])
def create_subject():
    if 'admin' in session:
        mysql = db_connection()
        msg = None
        error = None
        if request.method == 'POST':
            desired_name = request.form['desired_name']
            cur = mysql.cursor()
            res = cur.execute('SELECT * FROM subjects WHERE name = %s;', [desired_name])

            if desired_name == '':
                error = 'Incorrect name'
            elif res:
                error = 'Name already in use'
            else:
                cur.execute('INSERT INTO subjects(name) VALUES(%s);', [desired_name])
                mysql.commit()
                msg = 'Subject created successfully'
        mysql.close()
        return render_template('create_subject.html', msg = msg, error = error)
    return redirect(url_for('login'))

@app.route('/adm_panel/edit_subject/<string:id>', methods = ['GET', 'POST'])
def edit_subject(id):
    if 'admin' in session:
        mysql = db_connection()
        cur = mysql.cursor()
        cur.execute('SELECT name FROM subjects WHERE s_id = %s;', [id])
        subject = cur.fetchone()
        days_select = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        groups = get_groups(id)
        cur.close()

        if request.method == 'POST' and 'removeButton' in request.form:
            cur = mysql.cursor()
            cur.execute('DELETE FROM subjects WHERE s_id = %s;', [id])
            mysql.commit()
            cur.execute('SELECT g_id FROM group_list WHERE subject_id = %s;', [id])

            for g in cur.fetchall():
                cur.execute('DELETE FROM memberships WHERE group_id = %s;', [g['g_id']])
                mysql.commit()

            cur.execute('DELETE FROM group_list WHERE subject_id = %s;', [id])
            mysql.commit()
            cur.close()
            mysql.close()
            return redirect(url_for('adm_panel'))

        if request.method == 'POST':
            name = request.form.get('desired_name')

            if name != subject['name']:
                cur = mysql.cursor()
                cur.execute('UPDATE subjects SET name = %s WHERE s_id = %s;', [name, id])
                mysql.commit()

            headers = ('day', 'time', 'group_id', 'max')
            values = (
                request.form.getlist('day[]'),
                request.form.getlist('time[]'),
                request.form.getlist('group_id[]'),
                request.form.getlist('max[]')
                )

            items = [{} for i in range(len(values[0]))]
            for x,i in enumerate(values):
                for _x,_i in enumerate(i):
                    items[_x][headers[x]] = _i
            for i in items:
                if i['group_id'] != 'new':
                    i['group_id'] = int(i['group_id'])

            missing_groups = missing(groups, items)
            #update groups
            cur = mysql.cursor()

            for m_id in missing_groups:
                cur.execute('DELETE FROM group_list WHERE g_id = %s;', [str(m_id)])
                mysql.commit()
                cur.execute('DELETE FROM memberships WHERE group_id = %s;', [str(m_id)])
                mysql.commit()

            for group in items:
                if group['group_id'] == 'new':
                    cur.execute('INSERT INTO group_list(subject_id, day, time, maxSize) VALUES (%s, %s, %s, %s);', [id, group['day'], group['time'], group['max']])
                    mysql.commit()
                else:
                    for gr in groups:
                        if gr['g_id'] == group['group_id']:
                            if not gr['currentSize'] > int(group['max']):
                                cur.execute('UPDATE group_list SET day = %s, time = %s, maxSize = %s WHERE g_id = %s;', [group['day'], group['time'], group['max'], group['group_id']])
                                mysql.commit()
                            else:
                                pass
                            break
            mysql.close()
            return redirect(url_for('adm_panel'))

        cur.close()
        mysql.close()
        return render_template('edit_subject.html', name = subject['name'], subj_id = id, groups = groups, size = len(groups), options = days_select)
    return redirect(url_for('login'))
