from genaipf.utils.mysql_utils import CollectionPool


# 记录一条新消息
async def add_gpt_message(gpt_message):
    sql = "INSERT INTO `gpt_messages` (`content`, `type`, `userid`, `msggroup`, `device_no`) VALUES(%s, %s, %s, %s, %s)"
    res = await CollectionPool().insert(sql, gpt_message)
    return res

async def add_gpt_message_with_code(gpt_message):
    sql = "INSERT INTO `gpt_messages` (`content`, `type`, `userid`, `msggroup`, `code`, `device_no`) VALUES(%s, %s, %s, %s, %s, %s)"
    res = await CollectionPool().insert(sql, gpt_message)
    return res

# 获取用户消息列表
async def get_gpt_message(userid, msggroup):
    sql = 'SELECT id, content, type, msggroup, create_time, code FROM gpt_messages WHERE ' \
          'userid=%s AND msggroup=%s and deleted=0'
    result = await CollectionPool().query(sql, (userid, msggroup))
    return result

# 获取用户消息列表用作上下文
async def get_gpt_message_limit(userid, msggroup, limit):
    sql = 'SELECT id, content, type, msggroup, create_time, code FROM gpt_messages WHERE ' \
          'userid=%s AND msggroup=%s and deleted=0 ORDER BY id DESC LIMIT %s'
    result = await CollectionPool().query(sql, (userid, msggroup, limit))
    if len(result) > 0 :
        result.reverse()
        if result[0]['type'] != 'user' :
            result.pop(0)
    return result

# 获取用户对话列表
async def get_msggroup(userid):
    sql = "SELECT id, content, type, msggroup FROM gpt_messages WHERE " \
          "userid=%s and type = 'user' and deleted=0 GROUP BY msggroup"
    result = await CollectionPool().query(sql, (userid))
    return result

# 删除用户对话列表
async def del_msggroup(userid, msggroup):
    sql = 'update gpt_messages set deleted=1 WHERE ' \
          'userid=%s AND msggroup in %s and deleted=0'
    result = await CollectionPool().update(sql, (userid, msggroup))
    return result

async def get_predict(coin):
    sql = "SELECT date, open, high, low, close FROM kline_predictd where symbol='{}USDT' order by date desc limit 3".format(coin)
    result = await CollectionPool().query(sql)
    return result

async def set_gpt_gmessage_rate_by_id(rate, comment, code):
    sql = 'UPDATE gpt_messages set user_rate=%s, comment=%s WHERE code=%s and deleted=0'
    result = await CollectionPool().update(sql, (rate, comment, code))
    return result

async def del_gpt_message_by_code(userid,codes):
    sql = 'update gpt_messages set deleted = 1 WHERE userid=%s and code in %s and deleted=0'
    result = await CollectionPool().update(sql,(userid,codes))
    return result

async def add_share_message(code, messages, userid):
    sql = "INSERT INTO `share_messages` (`code`, `messages`, `userid`) VALUES(%s, %s, %s)"
    result = await CollectionPool().insert(sql, (code, messages, userid))
    return result


async def get_share_msg(code):
    sql = 'SELECT id, code, messages FROM share_messages WHERE ' \
          'code=%s'
    result = await CollectionPool().query(sql, (code))
    return result