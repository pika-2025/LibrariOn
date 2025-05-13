const Register = {
    data() {
        return {
            username: '',
            email: '',
            password: '',
            fullName: '',
            error: '',
            success: '',
            librarianExists: false
        };
    },
    async created() {
        const response = await fetch('/check_librarian');
        const data = await response.json();
        this.librarianExists = data.librarian_exists;
    },
    methods: {
        async register() {
            const requestData = {
                username: this.username,
                email: this.email,
                password: this.password,
                full_name: this.fullName,
            };

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData),
                });

                const data = await response.json();

                if (response.ok) {
                    this.success = 'User registered successfully!';
                    this.error = '';
                    this.username = '';
                    this.email = '';
                    this.password = '';
                    this.fullName = '';
                } else {
                    this.error = data.error || 'An error occurred';
                    this.success = '';
                }
            } catch (error) {
                this.error = 'An error occurred during registration';
            }
        }
    },
    template: `
        <div class = 'container'>
            <h1>Register</h1>
            <div v-if="error" class="error">{{ error }}</div>
            <div v-if="success" class="success">{{ success }}</div>
            <form @submit.prevent="register">
                <div>
                    <label for="fullName">Full Name:</label>
                    <input type="text" id="fullName" v-model="fullName" required>
                </div>
                <div>
                    <label for="username">Username:</label>
                    <input type="text" id="username" v-model="username" required>
                </div>
                <div>
                    <label for="email">Email:</label>
                    <input type="email" id="email" v-model="email" required>
                </div>
                <div>
                    <label for="password">Password:</label>
                    <input type="password" id="password" v-model="password" required>
                </div>
                <button type="submit">Register</button
            </form>
        </div>
    `
};

export default Register;