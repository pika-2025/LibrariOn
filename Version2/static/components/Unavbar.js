// static/components/Unavbar.js
const Unavbar = {
    template: `
    <nav>
        <h1 class = 'logo'>LibrON</h1>
        <router-link to="/uboard">Dashboard</router-link>
        <router-link to="/uboard/mybooks">My Books</router-link>
        <router-link to="/uboard/myrequests">Requests</router-link>
        <router-link to="/uboard/profile">Profile</router-link>
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
export default Unavbar;
