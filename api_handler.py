import requests
from datetime import datetime, timedelta

class NexonAPI:
    BASE_URL = "https://open.api.nexon.com/maplestory/v1"

    def __init__(self, api_key):
        self.headers = {"x-nxopen-api-key": api_key}
        self.ocid_cache = {}

    def _get(self, endpoint, params=None):
        """API GET 요청을 처리하는 내부 메소드"""
        response = requests.get(f"{self.BASE_URL}/{endpoint}", headers=self.headers, params=params)
        if response.status_code != 200:
            raise Exception(f"API 호출 실패: {response.status_code} - {response.text}")
        return response.json()

    def _get_ocid(self, character_name):
        """캐릭터 OCID를 조회하고 캐시합니다."""
        if character_name in self.ocid_cache:
            return self.ocid_cache[character_name]
        
        data = self._get("id", {"character_name": character_name})
        ocid = data.get("ocid")
        if not ocid:
            raise Exception("OCID를 조회할 수 없습니다.")
        self.ocid_cache[character_name] = ocid
        return ocid

    def get_character_info(self, character_name):
        """캐릭터 기본 정보를 조회합니다."""
        ocid = self._get_ocid(character_name)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return self._get("character/basic", {"ocid": ocid, "date": yesterday})

    def get_symbol_info(self, character_name):
        """캐릭터 심볼 정보를 조회합니다."""
        ocid = self._get_ocid(character_name)
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return self._get("character/symbol-equipment", {"ocid": ocid, "date": yesterday})