import httpx

class AccountApi:
    def __init__(self, base_url: str = "http://185.185.143.231:8085") -> None:
        self._base_url = base_url
        self._client = httpx.Client(base_url=self._base_url) # wtf

    def register_user(self, login: str, email: str, password: str) -> httpx.Response:
        data = {
            "login": login,
            "email": email,
            "password": password
            }
        return self._client.post("/register/user/async-register", json=data)

    def activate_user(
            self,
            token: str
    ) -> httpx.Response:
        url = "/register/user/activate"
        response = self._client.put(
            url=url,
            params={'token': token}
        )
        assert response.status_code == 200
        assert response.json()["resource"] is not None
        return response
