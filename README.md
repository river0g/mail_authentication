# メアド認証を行うプログラム

- https://mail-auth-project.herokuapp.com/ (認証の際eriver.bot@gmail.comからメールが来ます。)
- 使い道 \
  メールアドレスを用いたアカウント作成時に、そのメールアドレスが有効かどうかの確認するために使う。\
  ログイン時のなりすまし防止のために使う。

## 実装のために使う技術

- Language -> Python
- Library -> Flask
- DetaBase -> Mongodb (認証番号を保存するコレクションと、ユーザー情報を保存するコレクション)

## ルーティング

- /signup/, methods=['GET']
- /login/, methods=['GET', 'POST']
- /auth/, methods=['GET', 'POST']
- /main/, methods=['GET']

## ファイル構成

- `main.py`
- `send_mail.py`
- `database.py`
- `auth_utils.py`
- `templates/*.html`
- `static/*.css`

## 内容

signup にはメールアドレスとパスワードを入力してもらう。 \
入力してもらったメアドに対して 6 桁の乱数を発行する。それをメールで送る。\
サーバー側では認証番号を保存するコレクションに対してメアド、pwd(hash 化), 6 桁乱数からなる JWTToken を保存。\
フロント側は signup ページから auth ページに遷移 \
認証に成功したら main ページに遷移、ユーザー情報があるコレクションにメアド、pwd(hash 化)を保存 \
\
認証に成功 or 再発行をしたら認証番号を保存するコレクションからユーザー情報を削除する。

## やらないこと

- メアド認証を実装したいだけなので、Flask にある認証系を使ってどうたらこうたらすることはしない。
- パスワードの強化云々。
- クッキーに token を保存して遷移してもログイン状態を保つなど。
- Flask を用いた webapplication, website を作ることもしない。
- Flask には側の役割だけしてもらう。

## ローカルでの使い方。

mongodb の登録と gmail の 2 段階認証をオンにしてアプリパスワードを発行するところまで終わっていると想定

1. clone する
2. `python3 -m venv [環境変数名]`
3. `source [環境変数名]/bin/activate`
4. `pip install -r requirements.txt`
5. `.env`に下の「.env に書いてあること」を参考に mongodb_uri, gmail, その app pass を記入
6. `python3 main.py`
7. http://localhost:5000/signup にアクセス
8. *自分の*メールアドレスとテキトーなユーザーネームとパスワード入れる。メアドに認証番号が届く。
9. それ打っておわり。

### .env に書いてあること

MONGO_DB_URI -> MongoBD に接続するための URI
MAIL_ADDRESS -> 送信元のメールアドレス。
MAIL_PASSWORD -> 送信元のメールアドレスのアプリパスワード(gmail 想定)

## todo

- 値の管理をクッキーでする。
- コードの整理
- ログイン、ログアウトの実装(多分やらない)
- 新規作成時に認証をやらなかった時に tmp_account を消す処理を追加
- ログイン時にパスワードを忘れた時の処理(username に紐づけられているメアドにパスワード送信。)(たぶんやらない)
- 有効期限切れか間違えたのコードが入力された時の振る舞いを柔軟に書く(もう一度送信 というボタンを設置してもう一回コードを発行して入力させるなど。)
- verify ボタンの下にコードを再送ボタンを配置すれば解決しそう。
