from flask_jwt_extended import decode_token
from jwt.exceptions import InvalidTokenError


access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjE1OTEwNiwianRpIjoiNjY4ZTRlOTItN2RkYS00ODI1LWIzNWYtYmNhOWY2ZTBlMzM3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InN0cmluZyIsIm5iZiI6MTc1MjE1OTEwNiwiY3NyZiI6IjMyYjRhMmM2LWVjMWYtNDM2Ny1hY2M1LWNjOTIyNzM1N2E0YSIsImV4cCI6MTc1MjE2MDAwNn0.A3nBxmBB0HCrxCUDA9L_iV3OCYhiE2w1wYgbI563uSk'

try:
    decoded = decode_token(access_token)  # Tự động xác minh chữ ký và thời gian hết hạn
    username = decoded['sub'] #Lấy identity
    findUserByUsername(username)
except InvalidTokenError as e:
    print("Token không hợp lệ:", str(e))