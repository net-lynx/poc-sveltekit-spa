<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { user } from '$lib/stores/user.svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';

	let { children } = $props();

	onMount(async () => {
		// โค้ดส่วนนี้จะทำงานแค่ฝั่ง client เท่านั้น
		// ลอง fetch ข้อมูล user ทุกครั้งที่โหลดหน้า เพื่อให้แน่ใจว่าข้อมูลล่าสุด
		try {
			const response = await api('/api/users/me');
			if (response.ok) {
				const userData = await response.json();
				user.set(userData); // ถ้าสำเร็จ ให้เก็บข้อมูล user ไว้ใน store
			} else {
				// ถ้าไม่สำเร็จ และไม่ได้อยู่ที่หน้า login อยู่แล้ว ให้ส่งไปหน้า login
				if (page.route.id !== '/login') {
					user.set(null); // ล้างข้อมูล user เก่า
					await goto('/login');
				}
			}
		} catch (error) {
			console.error('ไม่สามารถดึงข้อมูลผู้ใช้เมื่อโหลดหน้า', error);
			if (page.route.id !== '/login') {
				user.set(null); // ล้างข้อมูล user เก่า
				await goto('/login');
			}
		}
	});

	async function handleLogout() {
		await api('/api/logout', { method: 'POST' });
		user.set(null); // ล้างข้อมูลผู้ใช้ใน store
		await goto('/login');
	}
</script>

<header>
	<nav>
		<a href="/">หน้าหลัก</a>
		<div class="user-info">
			{#if user}
				<span>สวัสดี, {user.value?.username}</span>
				<button onclick={handleLogout}>ออกจากระบบ</button>
			{:else}
				<a href="/login">เข้าสู่ระบบ</a>
			{/if}
		</div>
	</nav>
</header>

<main>
	{@render children()}
</main>

<style>
	header {
		background-color: #f8f9fa;
		padding: 0.5rem 1rem;
		border-bottom: 1px solid #dee2e6;
	}
	nav {
		display: flex;
		justify-content: space-between;
		align-items: center;
		max-width: 960px;
		margin: 0 auto;
	}
	.user-info {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	main {
		padding: 1rem;
		max-width: 960px;
		margin: 1rem auto;
	}
</style>
