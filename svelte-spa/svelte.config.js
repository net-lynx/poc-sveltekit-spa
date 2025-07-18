import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		// ใช้อะแดปเตอร์ static เพื่อสร้าง SPA
		adapter: adapter({
			// Directory สำหรับไฟล์ build
			pages: 'build',
			assets: 'build',
			// สำคัญ: สำหรับ SPA ให้ทุก request ที่ไม่เจอไฟล์ไปที่ index.html
			fallback: 'index.html',
			precompress: false,
			strict: true
		}),
        // ปิดการใช้งาน Server-Side Rendering
        prerender: {
            handleHttpError: 'ignore',
        },
	}
};

export default config;
