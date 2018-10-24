"""
骨架数据
"""
def get_send_data(
        p_name:str,
        msg_mark:str,
        msg:str,
        other_data:str = ''
):
    """
    获取发送消息数据
    :param p_name:
    :param msg_mark:
    :param msg:
    :param other_data:
    :return:
    """
    return {
            'tag': p_name,
            'msg_mark': msg_mark,
            'msg': msg,
            'other_data': other_data
        }