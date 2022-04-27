import jwt
from random import randrange
from passlib.context import CryptContext
from datetime import datetime, timedelta


class AuthJwt():
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def generate_verify_code(self) -> str:
        return str(randrange(0, 10)) + str(randrange(10**4, 10**5))

    def generate_hashed_pw(self, password):
        return self.pwd_ctx.hash(password)

    def verify_pw(self, plane_pw, hashed_pw):
        return self.pwd_ctx.verify(plane_pw, hashed_pw)

    def encode_jwt(self, username, code, exp, iat):
        payload = {
            'exp': exp,
            'iat': iat,
            'sub': username
        }

        return jwt.encode(payload, code, algorithm='HS256')

    def decode_jwt(self, token, code):
        try:
            payload = jwt.decode(token, code, algorithms=['HS256'])
            return True

        except jwt.ExpiredSignatureError as e:
            print(e)
            return False

    def verify_jwt(self, db_jwt_token, jwt_token, code) -> dict:
        if not self.decode_jwt(jwt_token, code):  # codeの有効期限が切れていないかどうか。
            # 切れていた場合の処理
            return {'status': False, 'error_id': 'expired'}

        if db_jwt_token == jwt_token:  # データベースのtokenと入力された値から作られたtokenが合うか
            return {'status': True, 'error_id': None}
        else:
            return {'status': False, 'error_id': 'wrong_input'}


if __name__ == '__main__':
    print('hi')
