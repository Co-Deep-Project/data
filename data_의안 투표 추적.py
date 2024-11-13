from flask import Flask, jsonify, request
import requests
import time

app = Flask(__name__)

# API Key and URLs
API_KEY = "# 실제 API 키로 교체"
BILL_LIST_URL = "https://open.assembly.go.kr/portal/openapi/ALLBILL"
VOTE_URL = "https://open.assembly.go.kr/portal/openapi/nojepdqqaweusdfbi"

# Helper function to get bill IDs for the 22nd National Assembly
def get_all_bill_ids():
    bill_params = {
        "Key": API_KEY,
        "Type": "json",
        "pSize": 10  # 한 페이지당 결과 수
    }
    
    pIndex = 1
    bill_ids = []
    
    while True:
        bill_params["pIndex"] = pIndex
        response = requests.get(BILL_LIST_URL, params=bill_params, timeout=30)
        
        if response.status_code == 200:
            bill_data = response.json()
            allbill_data = bill_data.get("ALLBILL", [])
            
            if not allbill_data or len(allbill_data) < 2 or "row" not in allbill_data[1]:
                print("No rows found in ALLBILL data. Exiting loop.")
                break
            
            rows = allbill_data[1]["row"]
            for row in rows:
                bill_id = row.get("BILL_ID")
                if bill_id:
                    bill_ids.append(bill_id)
            
            pIndex += 1
            time.sleep(0.5)
        else:
            print("Failed to retrieve bill list:", response.status_code)
            break
    
    return bill_ids

# Helper function to get vote data for a specific member and BILL_ID
def get_vote_data_for_member(bill_id, member_name):
    vote_params = {
        "Key": API_KEY,
        "Type": "json",
        "BILL_ID": bill_id,
        "AGE": "22",
        "HG_NM": member_name  # 특정 의원 이름 필터 추가
    }
    
    response = requests.get(VOTE_URL, params=vote_params, timeout=10)
    
    if response.status_code == 200:
        vote_data = response.json()
        votes = vote_data.get("response", {}).get("items", [])
        return votes
    else:
        return []

# Endpoint to get vote data for a specific member
@app.route('/api/v1/vote_data', methods=['GET'])
def get_vote_data():
    name = request.args.get("name")  # 의원 이름을 쿼리 파라미터로 받음
    if not name:
        return jsonify({"error": "Please provide a member name"}), 400
    
    all_vote_data = []
    bill_ids = get_all_bill_ids()

    for bill_id in bill_ids:
        vote_data = get_vote_data_for_member(bill_id, name)
        all_vote_data.extend(vote_data)

    return jsonify(all_vote_data), 200

if __name__ == "__main__":
    app.run(debug=True)
