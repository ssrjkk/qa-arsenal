import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const createTime = new Trend('create_time');
const updateTime = new Trend('update_time');
const deleteTime = new Trend('delete_time');

export const options = {
    stages: [
        { duration: '20s', target: 5 },
        { duration: '40s', target: 10 },
        { duration: '20s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<1000', 'p(99)<2000'],
        http_req_failed: ['rate<0.1'],
        errors: ['rate<0.2'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'https://jsonplaceholder.typicode.com';

const payload = JSON.stringify({
    title: 'k6 Load Test',
    body: 'Testing CRUD operations under load',
    userId: 1,
});

const params = {
    headers: {
        'Content-Type': 'application/json',
    },
};

export default function () {
    // Create resource
    const createRes = http.post(`${BASE_URL}/posts`, payload, params);
    createTime.add(createRes.timings.duration);
    errorRate.add(createRes.status !== 201);
    check(createRes, {
        'create status is 201': (r) => r.status === 201,
        'create returns id': (r) => r.json('id') > 0,
    });

    const postId = createRes.json('id');

    // Update resource
    const updateRes = http.put(`${BASE_URL}/posts/${postId}`, payload, params);
    updateTime.add(updateRes.timings.duration);
    errorRate.add(updateRes.status !== 200);
    check(updateRes, {
        'update status is 200': (r) => r.status === 200,
    });

    // Delete resource
    const deleteRes = http.del(`${BASE_URL}/posts/${postId}`);
    deleteTime.add(deleteRes.timings.duration);
    errorRate.add(deleteRes.status !== 200);
    check(deleteRes, {
        'delete status is 200': (r) => r.status === 200,
    });

    // Read scenario
    const readRes = http.get(`${BASE_URL}/posts/1`);
    errorRate.add(readRes.status !== 200);
    check(readRes, {
        'read status is 200': (r) => r.status === 200,
    });

    sleep(0.5);
}

export function handleSummary(data) {
    return {
        'stdout': `Total: ${data.metrics.http_reqs.values.count} requests\n` +
            `Failed: ${(data.metrics.http_req_failed.values.passes / data.metrics.http_reqs.values.count * 100).toFixed(2)}%\n` +
            `Avg: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms`,
    };
}