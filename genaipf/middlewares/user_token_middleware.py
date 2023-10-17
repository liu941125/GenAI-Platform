from interfaces.common_response import success, fail
from sanic import Request
from conf.path_without_login import PATH_WITHOUT_LOGIN
from constant.error_code import ERROR_CODE
import services.user_service as user_service
from utils.jwt_utils import JWTManager
from utils.redis_utils import RedisConnectionPool


# 判断用户的登陆态并赋值给request对象
async def check_user(request: Request):
    request_path = request.path
    # 判断当前路由是否在不需要登陆态的路由中
    if request_path in PATH_WITHOUT_LOGIN:
        token = request.token
        if token is None or len(request.token) == 0:
            return
        jwt_manager = JWTManager()
        check_res = jwt_manager.validate_token(token)
        if not check_res[0]:
            return
        redis_client = RedisConnectionPool().get_connection()
        user_token_key = user_service.get_user_key(check_res[1], check_res[2])
        user = redis_client.get(user_token_key)
        if user is None:
            return
        user = {
            'id': check_res[1],
            'email': check_res[2]
        }
        request.ctx.user = user
    else:
        token = request.token
        if token is None or len(request.token) == 0:
            return fail(ERROR_CODE["NOT_AUTHORIZED"])
        jwt_manager = JWTManager()
        check_res = jwt_manager.validate_token(token)
        if not check_res[0]:
            return fail(ERROR_CODE["NOT_AUTHORIZED"])
        redis_client = RedisConnectionPool().get_connection()
        user_token_key = user_service.get_user_key(check_res[1], check_res[2])
        user = redis_client.get(user_token_key)
        if user is None:
            return fail(ERROR_CODE["NOT_AUTHORIZED"])
        user = {
            'id': check_res[1],
            'email': check_res[2]
        }
        request.ctx.user = user


