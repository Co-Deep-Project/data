# 국회의원 본회의 표결정보 (의원별, 의안별 투표 추적)
# https://open.assembly.go.kr/portal/data/service/selectAPIServicePage.do/OPR1MQ000998LC12535
# 요청주소 : https://open.assembly.go.kr/portal/openapi/nojepdqqaweusdfbi

import sqlite3
import requests
from datetime import datetime

# API 요청에 필요한 정보
api_url = "https://open.assembly.go.kr/portal/openapi/nojepdqqaweusdfbi"
key = "..." 
type_format = "json"
age = "22"
pSize = 100

# 종로구 국회의원 목록
jongro_reps = ["FIE6569O"]

# SQLite 데이터베이스 연결
conn = sqlite3.connect("vote_data.db")
cursor = conn.cursor()

# 테이블 생성 
cursor.execute('''
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mona_cd TEXT,
    vote_date TEXT,
    bill_no TEXT,
    bill_name TEXT,
    result_vote_mod TEXT
)
''')
conn.commit()

# API 요청
def fetch_vote_data(api_url, key, type_format, age, mona_cd, pIndex, pSize):
    params = {
        "Key": key,
        "Type": type_format,
        "AGE": age,
        "MONA_CD": mona_cd,
        "pIndex": pIndex,
        "pSize": pSize
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# 데이터베이스에 데이터 저장
def update_vote_data():
    for mona_cd in jongro_reps:
        pIndex = 1
        while True:
            data = fetch_vote_data(api_url, key, type_format, age, mona_cd, pIndex, pSize)
            if data and "response" in data:
                items = data["response"]["item"]
                if not items:
                    break

                for item in items:
                    vote_date = item["VOTE_DATE"]
                    bill_no = item["BILL_NO"]
                    bill_name = item["BILL_NAME"]
                    result_vote_mod = item["RESULT_VOTE_MOD"]

                    cursor.execute('''
                    INSERT INTO votes (mona_cd, vote_date, bill_no, bill_name, result_vote_mod)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (mona_cd, vote_date, bill_no, bill_name, result_vote_mod))
                pIndex += 1
            else:
                break
        conn.commit()
    print("Data updated successfully")

# 데이터 업데이트 실행
update_vote_data()
conn.close()
