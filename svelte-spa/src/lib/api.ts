import { user } from '$lib/stores/user.svelte';
import { goto } from '$app/navigation';
import { browser } from '$app/environment';

// URL ของ FastAPI Backend ของคุณ
const BASE_URL = 'http://localhost:8000';

// ตัวแปรเพื่อป้องกันไม่ให้ยิง refresh token ซ้ำซ้อนกัน
let isRefreshing = false;

/**
 * ฟังก์ชันกลางสำหรับส่ง request ไปยัง API
 */
async function send(path: string, options: RequestInit = {}): Promise<Response> {
	// สำคัญ: บอกให้ browser ส่ง cookie ไปกับ request ด้วย
	options.credentials = 'include';
	options.headers = {
		'Content-Type': 'application/json',
		...options.headers
	};

	return fetch(`${BASE_URL}${path}`, options);
}

/**
 * Custom fetcher ที่มี logic การ refresh token อัตโนมัติ
 */
export const api = async (path: string, options: RequestInit = {}): Promise<Response> => {
	const response = await send(path, options);

	// ถ้าเจอ 401 Unauthorized แสดงว่า access_token หมดอายุ
	if (response.status === 401) {
		if (isRefreshing) {
			// ถ้ากำลัง refresh อยู่ ให้รอสักครู่แล้วลองใหม่
			// (ใน POC แบบง่าย เราจะแค่ reject ไปก่อน)
			return Promise.reject(new Error('Token refresh in progress'));
		}

		isRefreshing = true;

		// พยายามขอ access_token ใหม่โดยใช้ refresh_token
		const refreshResponse = await send('/api/refresh', { method: 'POST' });

		isRefreshing = false;

		if (refreshResponse.ok) {
			// ถ้า refresh สำเร็จ, ให้ลองยิง request เดิมอีกครั้ง
			console.log('Token ได้รับการรีเฟรชแล้ว กำลังลองอีกครั้ง...');
			return send(path, options);
		} else {
			// ถ้า refresh ไม่สำเร็จ (อาจจะเพราะ refresh_token หมดอายุ)
			console.log('การรีเฟรช Token ล้มเหลว กำลังออกจากระบบ...');
			user.set(null); // เคลียร์ข้อมูล user ใน store
			if (browser) {
				await goto('/login'); // ส่งไปหน้า login
			}
			// คืนค่า response ที่ผิดพลาดเดิมกลับไป
			return refreshResponse;
		}
	}

	return response;
};
