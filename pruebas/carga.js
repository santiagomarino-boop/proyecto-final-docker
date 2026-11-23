import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8082';

export const options = {
  stages: [
    { duration: '20s', target: 10 },
    { duration: '40s', target: 30 },
    { duration: '20s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<2000'],
  },
};

export default function () {
  const url = Math.random() < 0.3 ? `${BASE_URL}/slow?ms=350` : `${BASE_URL}/`;
  const res = http.get(url, { timeout: '10s' });
  check(res, { 'HTTP 200': (r) => r.status === 200 });
  sleep(0.15);
}
