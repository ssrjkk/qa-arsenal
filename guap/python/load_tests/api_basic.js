import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

export const options = {
    stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'],
        http_req_failed: ['rate<0.05'],
        errors: ['rate<0.1'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'https://jsonplaceholder.typicode.com';

export default function () {
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };

    // Scenario 1: Get all users
    const usersRes = http.get(`${BASE_URL}/users`, { headers });
    responseTime.add(usersRes.timings.duration);
    errorRate.add(usersRes.status !== 200);
    check(usersRes, {
        'users status is 200': (r) => r.status === 200,
        'users returns array': (r) => Array.isArray(r.json()),
    });

    // Scenario 2: Get single user
    const userRes = http.get(`${BASE_URL}/users/1`, { headers });
    responseTime.add(userRes.timings.duration);
    errorRate.add(userRes.status !== 200);
    check(userRes, {
        'user status is 200': (r) => r.status === 200,
        'user has id': (r) => r.json('id') === 1,
    });

    // Scenario 3: Get posts for user
    const postsRes = http.get(`${BASE_URL}/posts?userId=1`, { headers });
    responseTime.add(postsRes.timings.duration);
    errorRate.add(postsRes.status !== 200);
    check(postsRes, {
        'posts status is 200': (r) => r.status === 200,
        'posts are for user 1': (r) => r.json().every(p => p.userId === 1),
    });

    // Scenario 4: Get todos
    const todosRes = http.get(`${BASE_URL}/todos?userId=1`, { headers });
    responseTime.add(todosRes.timings.duration);
    errorRate.add(todosRes.status !== 200);
    check(todosRes, {
        'todos status is 200': (r) => r.status === 200,
        'todos is array': (r) => Array.isArray(r.json()),
    });

    sleep(1);
}

export function handleSummary(data) {
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'summary.json': JSON.stringify(data),
    };
}

function textSummary(data, options) {
    const indent = options.indent || '';
    let output = `${indent}Test Summary:\n`;
    output += `${indent}===========\n`;
    output += `${indent}Total Requests: ${data.metrics.http_reqs.values.count}\n`;
    output += `${indent}Failed Requests: ${data.metrics.http_req_failed.values.passes}\n`;
    output += `${indent}Avg Response Time: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
    return output;
}