const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 3000;

// 국회 API 키와 URL
const API_KEY = '70d8db9c548f4ea0b9f7ea947fe662ab';
const BILL_LIST_URL = 'https://open.assembly.go.kr/portal/openapi/nwbpacrgavhjryiph';
const VOTE_URL = 'https://open.assembly.go.kr/portal/openapi/nojepdqqaweusdfbi';

// 국회 회기 정보와 의원 코드 설정
const SESSION_NUMBER = 21; // 예: 21대 국회
const MEMBER_CODE = 'JNL7001A'; // 곽상언 의원의 MONA_CD

// 특정 회기의 법률안 목록을 가져오는 함수
async function fetchBillsForSession(sessionNumber) {
    try {
        const response = await axios.get(BILL_LIST_URL, {
            params: {
                Key: API_KEY,
                Type: 'json',
                AGE: sessionNumber
            }
        });
        const bills = response.data.ALLBILL[1].row;
        return bills.map(bill => bill.BILL_ID); // BILL_ID 목록 추출
    } catch (error) {
        console.error('Error fetching bill list:', error.message);
        return [];
    }
}

// 특정 법률안에 대한 특정 의원의 표결 정보를 가져오는 함수
async function fetchVoteDataForMember(billId, memberCode) {
    try {
        const response = await axios.get(VOTE_URL, {
            params: {
                Key: API_KEY,
                Type: 'json',
                AGE: SESSION_NUMBER,
                BILL_ID: billId,
                MONA_CD: memberCode
            }
        });
        return response.data.response.items || [];
    } catch (error) {
        console.error(`Error fetching vote data for BILL_ID ${billId}:`, error.message);
        return [];
    }
}

// 특정 회기의 모든 법률안에 대한 곽상언 의원의 표결 정보를 수집하는 엔드포인트
app.get('/api/v1/vote_data', async (req, res) => {
    try {
        const billIds = await fetchBillsForSession(SESSION_NUMBER);
        const allVotes = [];

        // 각 법률안에 대한 표결 정보 수집
        for (const billId of billIds) {
            const voteData = await fetchVoteDataForMember(billId, MEMBER_CODE);
            allVotes.push(...voteData);
        }

        res.json(allVotes);
    } catch (error) {
        console.error('Error fetching vote data:', error.message);
        res.status(500).json({ error: 'Failed to fetch vote data' });
    }
});

// 서버 실행
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
