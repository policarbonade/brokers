from json import loads


def get_activation_token_by_login(
        response,
        login
):
    token = None
    for item in response.json()['items']:
        try:
            user_data = loads(item['Content']['Body'])
            user_login = user_data['Login']
            if user_login == login:
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
        except Exception:
            print("Битый формат ответа почтового сервиса")
    return token
