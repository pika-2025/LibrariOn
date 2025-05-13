export default {
    template: `
    <nav>
        <h1 class='logo'>LibrON</h1>
        <router-link to="/liboard">Dashboard</router-link>
        <router-link to="/liboard/genres">Books</router-link>
        <router-link to="/liboard/users">Users List</router-link>
        <router-link to="/liboard/rental_hist">Rental History</router-link>
        <router-link to="/liboard/on_rent">Rented Books</router-link>
        <router-link to="/liboard/stats">See Stats</router-link>
        <button @click="logout">Logout</button>

    </nav>
    `,
    methods: {
        logout() {
            localStorage.removeItem('access_token');
            this.$router.push('/login');
        }
    }
};

