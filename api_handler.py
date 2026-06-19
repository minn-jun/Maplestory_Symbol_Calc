import requests


class NexonAPI:
    BASE_URL = "https://open.api.nexon.com/maplestory/v1"

    def __init__(self, api_key):
        self.headers = {"x-nxopen-api-key": api_key}
        self.ocid_cache = {}

    def _get(self, endpoint, params=None):
        response = requests.get(
            f"{self.BASE_URL}/{endpoint}",
            headers=self.headers,
            params=params or {},
            timeout=15,
        )
        if response.status_code != 200:
            raise RuntimeError(f"API 호출 실패: {response.status_code} - {response.text}")
        return response.json()

    def get_ocid(self, character_name):
        character_name = character_name.strip()
        if character_name in self.ocid_cache:
            return self.ocid_cache[character_name]

        data = self._get("id", {"character_name": character_name})
        ocid = data.get("ocid")
        if not ocid:
            raise RuntimeError("OCID를 조회할 수 없습니다.")

        self.ocid_cache[character_name] = ocid
        return ocid

    def get_character_info(self, character_name, date=None):
        params = {"ocid": self.get_ocid(character_name)}
        if date:
            params["date"] = date
        return self._get("character/basic", params)

    def get_symbol_info(self, character_name, date=None):
        params = {"ocid": self.get_ocid(character_name)}
        if date:
            params["date"] = date
        return self._get("character/symbol-equipment", params)
