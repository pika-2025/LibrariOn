const Login = {
    template: `
    <div class='container'>
        <h1>Login</h1>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="success" class="success">{{ success }}</div>
        <form @submit.prevent = "submitInfo">
            <div>
                <label for="username">Username:</label>
                <input type="text" id="username" v-model="username" required>
            </div>
            <div>
                <label for="password">Password:</label>
                <input type="password" id="password" v-model="password" required>
            </div>
            <button type = "submit">Login</button>
        </form>
    </div>`,
    data() {
        return {
            username: '',
            password: '',
            error: "",
            success: ""
        };
    },
    methods: {
        async submitInfo() {
            const url = window.location.origin;
            const response = await fetch(url + '/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: this.username,
                    password: this.password,
                })
            });
            const data = await response.json();
        
            if (response.ok) {
                localStorage.setItem('access_token', data.access_token);
                this.success = 'Login successful!';
                this.error = '';
                this.username = '';
                this.password = '';
                    
                const userResponse = await fetch('/user_info', {
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`
                    }
                });
                const userData = await userResponse.json();
        
                if (userResponse.ok) {
                    console.log('User data:', userData);
                    if (userData.role === 'librarian') {
                        this.$router.push('/liboard');
                    } else {
                        this.$router.push('/uboard');
                    }
                } else {
                    this.error = userData.error || 'An error occurred';
                }
            } else {
                this.error = data.error || 'An error occurred';
            }
        }
    }
}
export default Login;    