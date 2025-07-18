export interface User {
	username: string;
	email: string | null;
	full_name: string | null;
}

let _user: User | null | undefined = $state();

export const user = {
	get value() {
		return _user;
	},
	set(newUser: User | null) {
		_user = newUser;
	},
	update(fn: (current: User | null | undefined) => User | null) {
		_user = fn(_user);
	}
};
