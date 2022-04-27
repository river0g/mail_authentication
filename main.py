from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime, timedelta
from database import db_get_account, db_get_tmp_account, db_create_account, db_create_tmp_account, db_delete_tmp_account
from auth_utils import AuthJwt
from send_mail import send_mail

app = Flask(__name__)

auth = AuthJwt()


def error_type(error_id):
    error_not_verify_request = '※ 有効なリクエストではありません。※'
    error_wrong_username_password = '※ ユーザー名かパスワードを間違えています。※'
    error_existed_account = '※ そのユーザー名はすでに使われています。※'
    error_wrong_input = '※ 入力したコードが間違っています。※'
    error_token_expired = '※ コードの有効期限が切れています。※'

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
def home():
    return render_template('index.html', username='reiji')


@app.route("/test-child")
def test_child():
    return render_template('test.html')


@app.route("/test", methods=['GET', 'POST'])
async def test():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        print('post method')
        print(username, password, email)
        data = {'username': username,
                'email': email, 'password': password}

        await db_create_tmp_account(data)

        db_data = await db_get_tmp_account(username)
        return render_template('main.html', data=db_data)

    username = 'lisa'
    db_data = await db_get_tmp_account(username)
    username, email = None, None
    if db_data:
        username = db_data.get('username')
        email = db_data.get('email')

    return render_template("main.html", data={'username': username, 'email': email})


@app.route("/signup", methods=['GET'])
def sign_up():
    error_id = request.query_string.decode().split('&')[0]
    error_id = error_id.replace('error_id=', '')

    print(error_id)
    message = error_type(error_id)
    print(message)

    return render_template('signup.html', message=message)


@app.route("/login", methods=['GET'])
def login():
    error_id = request.query_string.decode().split('&')[0]
    error_id = error_id.replace('error_id=', '')

    message = error_type(error_id)

    return render_template('login.html', message=message)


@app.route("/auth", methods=['GET', 'POST'])
async def auth_page():
    req_page = request.form.get('this-page')
    if request.method == 'POST' and req_page:
        username = request.form.get('username')
        password = request.form.get('password')
        print(username, password)

        exp = datetime.utcnow() + timedelta(days=0, minutes=5)  # 間接的にverify_codeの有効時間になる。
        iat = datetime.utcnow()
        code = auth.generate_verify_code()

        if req_page == 'signup':
            print('signup')
            exist_account = await db_get_account(username)
            print(exist_account)
            if exist_account:  # 入力されたusernameがすでに存在する場合
                return redirect(url_for('sign_up', error_id='existed'))

            email = request.form.get('email')
            hashed_password = auth.generate_hashed_pw(password)
            jwt_token = auth.encode_jwt(username, code, exp, iat)
            data = {'email': email, 'username': username,
                    'password': hashed_password, 'jwt': jwt_token, 'exp': exp, 'iat': iat}
            await db_create_tmp_account(data)
            # send_mail(email, code)
            print(email, code)
            return render_template('auth.html', username=username, req_page='signup')

        elif req_page == 'login':
            user_data = await db_get_account(username)
            if not user_data:  # 入力されたユーザーが存在しない場合
                return redirect(url_for('login', error_id='wrong_un_pw'))

            db_password = user_data['password']
            result = auth.verify_pw(password, db_password)

            if not result:  # ユーザーが存在しないか、パスワードが間違っている時
                return redirect(url_for('login', error_id='wrong_un_pw'))

            # ユーザーが存在し、そのユーザーのパスワードが合っている時の処理
            email = user_data['email']
            jwt_token = auth.encode_jwt(username, code, exp, iat)
            # send_mail(email, code)
            print(email, code)
            data = {'email': email, 'username': username,
                    'jwt': jwt_token, 'exp': exp, 'iat': iat}
            await db_create_tmp_account(data)
            return render_template('auth.html', username=username)

    # GET methodかlogin, signup以外のところからのPOST methodでのアクセスのとき
    return redirect(url_for('login', error_id='notverify'))


@app.route('/main', methods=['GET', 'POST'])
async def main():
    req_page = request.form.get('this-page')
    if request.method == 'POST' and req_page:
        req_page = request.form.get('req-page')  # signupかloginの判定に使う。
        code = request.form.get('verify')
        username = request.form.get('username')

        res = await db_get_tmp_account(username)

        # todo: 以下の1文はauth.encode_jwt(res)としてauth_utilsで変数代入の処理をしたほうがいいかも。
        exp, iat, db_jwt_token = res['exp'], res['iat'], res['jwt']
        jwt_token = auth.encode_jwt(username, code, exp, iat)
        is_verify_jwt = auth.verify_jwt(
            db_jwt_token, jwt_token, code)  # 期限が切れていないかつjwtが合致するか

        email = res['email']
        render_user_data = {'username': username, 'email': email}

        if not is_verify_jwt['status']:  # formで送信された確認コードが合わないか期限切れの場合
            error_id = is_verify_jwt['error_id']
            message = error_type(error_id)
            return render_template('auth.html', username=username, message=message)

        if req_page == 'signup':  # signupからのリクエストでデータベースにユーザーを登録する。
            password = res['password']
            user_data = dict(password=password, **render_user_data)
            await db_create_account(user_data)

        await db_delete_tmp_account(username)
        return render_template('main.html', data=render_user_data, req_page=req_page)

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
