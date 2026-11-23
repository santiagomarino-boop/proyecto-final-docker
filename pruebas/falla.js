import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8082';

export const options = {
  vus: 15,
  duration: '90s',
  thresholds: { http_req_failed: ['rate<0.05'] },
};

export default function () {
  const res = http.get(`${BASE_URL}/`, { timeout: '10s' });
  check(res, { 'HTTP 200': (r) => r.status === 200 });
  sleep(0.3);
}
