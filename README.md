# メアド認証を行うプログラム

- 使い道 \
  メールアドレスを用いたアカウント作成時に、そのメールアドレスが有効かどうかの確認するために使う。\
  ログイン時のなりすまし防止のために使う。

## 実装のために使う技術

- Language -> Python
- Library -> Flask
- DetaBase -> Mongodb (認証番号を保存するコレクションと、ユーザー情報を保存するコレクション)

## ルーティング

- /signup/
- /auth/
- /login/
- /logout/
- /main/

## ファイル構成

- `main.py`
- `send_mail.py`
- `database.py`
- `auth_utils.py`
- `something.html`

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

### .env に書いてあること

MONGO_DB_URI -> MongoBD に接続するための URI