// data_bills.js

import express from 'express';
import fetch from 'node-fetch';

const app = express();
const PORT = 3000;
const API_KEY = '70d8db9c548f4ea0b9f7ea947fe662ab'; // 실제 API 키로 교체
const MEMBER_NAME = '곽상언'; // 국회의원 이름

// 국회의원이 발의한 법률안 데이터 가져오기
async function fetchBillsProposedByMember(memberName, apiKey) {
    const url = 'https://open.assembly.go.kr/portal/openapi/nzmimeepazxkubdpn';
    const params = new URLSearchParams({
        Key: apiKey,
        Type: 'json',
        pIndex: 1,
        pSize: 100,
        PROPOSER: memberName,
        AGE: '22'  // 국회 대수
    });

    try {
        const response = await fetch(`${url}?${params.toString()}`);
        const data = await response.json();
        
        // API 응답 데이터 전체 로그
        console.log("API Response:", JSON.stringify(data, null, 2));

        let bills = [];
        const resultCode = data?.nzmimeepazxkubdpn?.[0]?.head?.[1]?.RESULT?.CODE;
        
        if (resultCode === 'INFO-000') {
            bills = data.nzmimeepazxkubdpn[1].row.map(item => ({
                bill_id: item.BILL_ID,
                bill_name: item.BILL_NAME,
                propose_date: item.PROPOSE_DT,
                result: item.PROC_RESULT || "N/A", // 결과가 없을 경우 기본값 설정
                detail_link: item.DETAIL_LINK,
                proposer: item.RST_PROPOSER
            }));
        } else {
            console.error("API Response Error: Unexpected structure or missing data.");
        }
        
        return bills;
    } catch (error) {
        console.error('API fetch error:', error);
        return [];
    }
}

// API 엔드포인트 설정
app.get('/api/bills', async (req, res) => {
    const bills = await fetchBillsProposedByMember(MEMBER_NAME, API_KEY);
    res.json(bills); // JSON 형식으로 응답
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
