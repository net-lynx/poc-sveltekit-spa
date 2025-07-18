<script lang="ts">
	import { user } from '$lib/stores/user.svelte';
	import { api } from '$lib/api';

	let protectedData = $state('ยังไม่ได้ดึงข้อมูล');
	let isLoading = $state(false);

	async function fetchProtectedData() {
		isLoading = true;
		try {
			// Endpoint นี้ต้องใช้ token ในการเข้าถึง
			const response = await api('/api/users/me'); 
			if (response.ok) {
				const data = await response.json();
				protectedData = JSON.stringify(data, null, 2);
			} else {
				protectedData = 'ไม่สามารถดึงข้อมูลได้ อาจจะเพราะคุณยังไม่ได้ล็อกอิน';
			}
		} catch (e) {
			console.error(e);
			protectedData = 'เกิดข้อผิดพลาดในการดึงข้อมูล';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="mx-auto max-w-3xl py-5">
	<h1>SvelteKit + FastAPI Auth POC</h1>

	{#if user.value}
		<p>คุณกำลังล็อกอินในชื่อ <strong>{user.value.username}</strong>.</p>
		<button onclick={fetchProtectedData} disabled={isLoading}>
			{isLoading ? 'กำลังโหลด...' : 'ดึงข้อมูลส่วนตัว (Protected)'}
		</button>
		
		<h3>ข้อมูลที่ได้รับ:</h3>
		<pre>{protectedData}</pre>
	{:else}
		<p>คุณยังไม่ได้เข้าสู่ระบบ กรุณา <a href="/login">ไปที่หน้าล็อกอิน</a>.</p>
	{/if}
</div>

<style>
	pre {
		background-color: #eee;
		padding: 1rem;
		border-radius: 8px;
		white-space: pre-wrap;
		word-break: break-all;
		margin-top: 1rem;
	}
	button {
		padding: 0.5rem 1rem;
	}
	h1 {
		margin-bottom: 1rem;
	}
</style>