from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_login import login_required, login_user, logout_user
from datetime import datetime, timedelta
app = Flask(__name__)


def error_type(error_id):
    error_not_verify_request = '有効なリクエストではありません。'
    error_wrong_username_password = 'ユーザー名かパスワードを間違えています。'
    error_existed_accout = 'そのユーザー名はすでに使われています。'
    error_wrong_input = '入力したコードが間違っています'
    error_token_expired = 'コードの有効期限が切れています'

    if error_id == 'wrong_un_pw':
        message = error_wrong_username_password
    elif error_id == 'notverify':
        message = error_not_verify_request
    elif error_id == 'existed':
        message = error_existed_account
    elif error_id == 'wrong_input':
        message = error_wrong_input
    elif error_id == 'expired':
        message = error_token_expired
    else:
        message = None

    return message


@app.route("/")
def hello_world(username='Reiji'):
    req_page = 'asite'
    if request.method == 'GET' and req_page == ('asite' or 'bsite'):
        print('success')
        return redirect(url_for('index', name='lisa'))
    return render_template('index.html', username=username)
    # return redirect(url_for('index', user=username))


@app.route("/index")
# @app.route("/index/<name>")
def index(name='jisoo'):
    url_query = request.query_string.decode().split('&')
    name = url_query[0]  # クエリが何も無い時は空文字を含めたリストが返却される。
    return render_template('index.html', username=name)


@app.route("/signup", methods=['GET'])
def sign_up():
    error_id = request.query_string.decode().split('&')[0]
    message = error_type(error_id)

    return render_template('signup.html', message=message)


@app.route("/login", methods=['GET'])
def login():
    error_id = request.query_string.decode().split('&')[0]
    message = error_type(error_id)

    return render_template('login.html', message=message)


@app.route("/auth", methods=['GET', 'POST'])
def auth():
    req_page = request.form.get('this-page')
    if request.method == 'POST' and req_page:
        username = request.form.get('username')
        password = request.form.get('password')

        exp = datetime.utcnow() + timedelta(days=0, minutes=5)  # 間接的にverify_codeの有効時間になる。
        iat = datetime.utcnow()
        # code = auth.generate_verify_code()

        if req_page == 'signup':
            exist_account = db_get_user(username)
            if not exist_account:  # 入力されたusernameがすでに存在する場合
                return redirect(url_for('signup', error='existed'))

            email = request.form.get('email')
            hashed_password = auth.generate_hashed_pw(password)
            jwt_token = auth.encode_jwt(username, code, exp, iat)
            # db_generate_tmp_account(email, username, hashed_password, jwt, exp, iat)
            # send_mail(email, code)
            return render_template('auth.html', username=username, req_page='signup')

        elif req_page == 'login':
            # user_data = db_get_user(username)
            if not user_data:  # 入力されたユーザーが存在しない場合
                return redirect(url_for('login', error='wrong'))

            # db_password = user_data['password']
            # result = auth.verify_pw(password, db_password)

            if not result:  # ユーザーが存在しないか、パスワードが間違っている時
                return redirect(url_for('login', error='wrong'))

            # ユーザーが存在し、そのユーザーのパスワードが合っている時の処理
            # email = user_data['email']
            # send_mail(email, code)
            # db_generate_tmp_account(email, username, password, code, exp, iat)
            return render_template('auth.html', username=username)

    # GET methodかlogin, signup以外のところからのPOST methodでのアクセスのとき
    return redirect(url_for('login', error='notverify'))


@app.route('/main', methods=['GET', 'POST'])
def main():
    req_page = request.form.get('this-page')
    if request.method == 'POST' and req_page:
        req_page = request.form.get('req-page')  # signupかloginの判定に使う。
        code = request.form.get('verify')
        username = request.form.get('username')
        res = db_get_tmp_user({'username': username})
        # exp, iat, db_jwt_token = res['exp'], res['iat'], res['jwt']
        # jwt_token = auth.encode_jwt(username, code, exp, iat)
        # is_verify_jwt = verify_jwt(db_jwt_token, jwt_token, code) # 期限が切れていないかつjwtが合致するか

        if not is_verify_jwt['status']:  # formで送信された確認コードが合わないか期限切れの場合
            error_id = is_verify_jwt['error_id']
            message = error_type(error_id)
            return render_template('auth.html', username=username, message=message)

        if req_page == 'signup':  # signupからのリクエストでデータベースにユーザーを登録する。
            password = res['password']
            email = res['email']
            user_data = {'username': username,
                         'password': password, 'email': email}
            db_create_user(user_data)

        db_delete_tmp_user(username)
        return render_template('main.html', data=data)

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
