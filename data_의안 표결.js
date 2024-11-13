const express = require('express');
const axios = require('axios');

const app = express();
const port = 3000;
const API_KEY = '###';
const BILL_LIST_URL = 'https://open.assembly.go.kr/portal/openapi/nwbpacrgavhjryiph';
const VOTE_URL = 'https://open.assembly.go.kr/portal/openapi/nojepdqqaweusdfbi';

let billIdCache = [];

// 모든 BILL_ID 가져오기
async function fetchBillIds() {
    if (billIdCache.length > 0) {
        console.log("Using cached BILL_IDs:", billIdCache);
        return billIdCache;
    }

    let pIndex = 1;
    const billIds = [];

    console.log("Starting to fetch BILL_IDs...");

    try {
        const response = await axios.get(BILL_LIST_URL, {
            params: {
                Key: API_KEY,
                Type: 'json',
                AGE: 22,
                pSize: 10,
                pIndex: pIndex
            }
        });
        const data = response.data;
        console.log("API Response for Bill List:", data);

        if (data.nwbpacrgavhjryiph && data.nwbpacrgavhjryiph[1].row) {
            const rows = data.nwbpacrgavhjryiph[1].row;
            for (let row of rows) {
                if (row.BILL_ID) {
                    billIds.push(row.BILL_ID);
                }
            }
        } else {
            console.log("No rows found in the response for BILL_IDs.");
        }
    } catch (error) {
        console.error("Error fetching bill list:", error.message);
    }

    billIdCache = billIds;
    console.log("Retrieved BILL_IDs:", billIds);
    return billIds;
}

// 특정 국회의원의 표결 데이터를 BILL_ID로 가져오기
async function fetchVoteDataForMember(billId, memberName) {
    try {
        const response = await axios.get(VOTE_URL, {
            params: {
                Key: API_KEY,
                Type: 'json',
                BILL_ID: billId,
                AGE: 22,
                HG_NM: memberName
            }
        });
        const data = response.data;
        console.log(`API Response for Vote Data (BILL_ID: ${billId}):`, data);

        // API 응답 데이터 구조에 맞춰 조건문 수정
        if (
            data.nojepdqqaweusdfbi &&
            data.nojepdqqaweusdfbi[1] &&
            data.nojepdqqaweusdfbi[1].row
        ) {
            return data.nojepdqqaweusdfbi[1].row;
        } else {
            console.log(`No items found for BILL_ID: ${billId}`);
            return [];
        }
    } catch (error) {
        console.error(`Error fetching vote data for BILL_ID ${billId}:`, error.message);
        return [];
    }
}

// 모든 BILL_ID에 대해 병렬로 표결 데이터 가져오기
async function fetchAllVoteDataForMember(memberName) {
    const billIds = await fetchBillIds();
    const allVoteData = [];

    for (let billId of billIds) {
        const voteData = await fetchVoteDataForMember(billId, memberName);
        allVoteData.push(...voteData);
    }

    console.log("Total Vote Data for Member:", allVoteData);
    return allVoteData;
}

app.get('/api/vote_data', async (req, res) => {
    const memberName = req.query.name;
    if (!memberName) {
        return res.status(400).json({ error: "Member name is required" });
    }

    const voteData = await fetchAllVoteDataForMember(memberName);
    res.json(voteData);
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
