<script lang="ts">
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { user } from '$lib/stores/user.svelte';

	// --- Svelte 5 Runes for State Management ---
	let username = $state('johndoe'); // ใส่ค่าเริ่มต้นเพื่อความสะดวกในการทดสอบ
	let password = $state('password'); // รหัสผ่านไม่ได้ใช้จริงใน backend แต่มีไว้ใน UI
	let error = $state('');
	let isLoading = $state(false);

	async function handleLogin() {
		error = '';
		isLoading = true;
		try {
			const response = await api('/api/login', {
				method: 'POST',
				body: JSON.stringify({ username, password })
			});

			if (response.ok) {
				// ถ้าล็อกอินสำเร็จ ให้ fetch ข้อมูล user และอัปเดต store
				try {
					const userResponse = await api('/api/users/me');
					if (userResponse.ok) {
						const userData = await userResponse.json();
						user.set(userData); // อัปเดตข้อมูล user ใน store
					}
				} catch (userError) {
					console.error('ไม่สามารถดึงข้อมูลผู้ใช้หลังจาก login:', userError);
				}
				
				// จากนั้นค่อย redirect ไปหน้าหลัก
				await goto('/');
			} else {
				const data = await response.json();
				error = data.detail || 'การล็อกอินล้มเหลว';
			}
		} catch (e) {
			console.error(e);
			error = 'เกิดข้อผิดพลาดที่ไม่คาดคิดในการเชื่อมต่อ';
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="container">
	<h1>เข้าสู่ระบบ (Svelte 5)</h1>
	<form
		onsubmit={(e) => {
			e.preventDefault();
			handleLogin();
		}}
	>
		<label>
			<span>ชื่อผู้ใช้</span>
			<input type="text" bind:value={username} required />
		</label>
		<label>
			<span>รหัสผ่าน</span>
			<input type="password" bind:value={password} required />
		</label>

		{#if error}
			<p class="error">{error}</p>
		{/if}

		<button type="submit" disabled={isLoading}>
			{#if isLoading}
				กำลังโหลด...
			{:else}
				เข้าสู่ระบบ
			{/if}
		</button>
	</form>
</div>

<style>
	.container {
		max-width: 400px;
		margin: 4rem auto;
		padding: 2rem;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
	}
	h1 {
		text-align: center;
		margin-bottom: 1.5rem;
	}
	.error {
		color: #d9534f;
		background-color: #f2dede;
		border: 1px solid #ebccd1;
		padding: 0.75rem;
		border-radius: 4px;
		margin: 0;
		text-align: center;
	}
	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	label span {
		display: block;
		margin-bottom: 0.25rem;
	}
	input {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}
	button {
		margin-top: 1rem;
		padding: 0.75rem;
		border: none;
		background-color: #007bff;
		color: white;
		border-radius: 4px;
		cursor: pointer;
		font-size: 1rem;
	}
	button:disabled {
		background-color: #a0a0a0;
		cursor: not-allowed;
	}
</style>
