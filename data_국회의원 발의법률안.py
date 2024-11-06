# 정책 일관성 평가
# 공약 이행 타임라인
# 국회의원 발의법률안
# 요청주소 : https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn

import requests
import json
import sqlite3
import time
from datetime import datetime

# 데이터베이스 연결
conn = sqlite3.connect("bills.db")
cursor = conn.cursor()

# 테이블 생성
def create_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        bill_id TEXT PRIMARY KEY,
        bill_name TEXT,
        propose_date TEXT,
        result TEXT,
        detail_link TEXT,
        proposer TEXT
    )
    """)
    conn.commit()

# 새로운 법률안을 DB에 추가
def insert_or_update_bill(bill):
    cursor.execute("""
    INSERT OR REPLACE INTO bills (bill_id, bill_name, propose_date, result, detail_link, proposer)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (bill['bill_id'], bill['bill_name'], bill['propose_date'], bill['result'], bill['detail_link'], bill['proposer']))
    conn.commit()

# API에서 법률안 가져오기
def fetch_bills_proposed_by_member(member_name, api_key):
    url = "https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn"
    params = {
        'Key': api_key,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100,
        'PROPOSER': member_name,
        'AGE': '21'  # 21대 국회
    }

    response = requests.get(url, params=params)
    data = response.json()

    bills = []
    
    if data['nzmimeepazxkubdpn'][0]['head'][0]['RESULT']['CODE'] == 'INFO-000':
        for item in data['nzmimeepazxkubdpn'][1]['row']:
            bill = {
                'bill_id': item['BILL_ID'],
                'bill_name': item['BILL_NAME'],
                'propose_date': item['PROPOSE_DT'],
                'result': item['PROC_RESULT'],
                'detail_link': item['DETAIL_LINK'],
                'proposer': item['RST_PROPOSER']
            }
            bills.append(bill)
    
    return bills

# 업데이트 기능: 새로운 데이터 추가
def update_bills(member_name, api_key):
    bills = fetch_bills_proposed_by_member(member_name, api_key)
    for bill in bills:
        insert_or_update_bill(bill)

# 타임라인 데이터 형식으로 데이터 가져오기
def get_timeline_data():
    cursor.execute("SELECT bill_name, propose_date, result, detail_link, proposer FROM bills ORDER BY propose_date")
    rows = cursor.fetchall()
    
    timeline_data = []
    for row in rows:
        timeline_entry = {
            'title': row[0],
            'date': row[1],
            'result': row[2],
            'link': row[3],
            'proposer': row[4]
        }
        timeline_data.append(timeline_entry)
    
    return timeline_data

# 주기적으로 데이터 업데이트
def periodic_update(member_name, api_key, interval=86400):
    while True:
        print("Updating bills data...")
        update_bills(member_name, api_key)
        print("Update complete. Next update in 24 hours.")
        time.sleep(interval)  # 24시간마다 업데이트

# 초기화 및 테스트
create_table()
api_key = "your_api_key_here"
member_name = "곽상언"  # 국회의원 이름

# 주기적 업데이트 실행 (백그라운드에서 실행할 수 있음)
# periodic_update(member_name, api_key)

# 타임라인 데이터 가져오기 및 JSON으로 변환
timeline_data = get_timeline_data()
timeline_json = json.dumps(timeline_data, ensure_ascii=False, indent=4)
print(timeline_json)

# 데이터베이스 닫기
conn.close()
