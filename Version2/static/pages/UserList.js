export default {
    template: `
    <div class="container">
        <h1>User Management</h1>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="users.length">
            <table class="book-table">
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Full Name</th>
                        <th>Status</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="user in users" :key="user.id" :class="{'active-user': user.is_active, 'disabled-user': !user.is_active}">
                        <td>{{ user.id }}</td>
                        <td>{{ user.full_name }}</td>
                        <td>{{ user.is_active}}</td>                        
                        <td>
                            <button @click="openUserDetails(user.id)">Details</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div v-else>
            <p>No users found.</p>
        </div>

        <!-- User Details Modal -->
        <b-modal v-model="showModal" title="User Details">
            <div v-if="selectedUser">
                <p><strong>ID:</strong> {{ selectedUser.id }}</p>
                <p><strong>Full Name:</strong> {{ selectedUser.full_name }}</p>
                <p><strong>Username:</strong> {{ selectedUser.username }}</p>
                <p><strong>Email:</strong> {{ selectedUser.email }}</p>
                <p><strong>Role:</strong> {{ selectedUser.role }}</p>
                <p><strong>Total Books Rented:</strong> {{ selectedUser.rental_count }}</p>
                <button v-if="selectedUser.is_active" @click="disableUser">Disable User</button>
            </div>
            <template v-slot:modal-footer>
                <b-button variant="secondary" @click="showModal = false">Close</b-button>
            </template>
        </b-modal>
    </div>
    `,
    data() {
        return {
            users: [],
            showModal: false,
            selectedUser: null,
            error: '',
        };
    },
    async created() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            this.$router.push('/login');
            return;
        }

        await this.fetchUsers(token);
    },
    methods: {
        async fetchUsers(token) {
            try {
                const response = await fetch('/liboard/users', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
    
                if (response.ok) {
                    this.users = data;
                    console.log(this.users); // Debugging: Check the fetched user data
                } else {
                    this.error = data.error || 'An error occurred while fetching users.';
                }
            } catch (error) {
                this.error = 'Network error occurred while fetching users.';
            }
        },
    
        async openUserDetails(userId) {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch(`/liboard/users/${userId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
    
                if (response.ok) {
                    this.selectedUser = data;
                    this.showModal = true;
                    console.log(this.selectedUser); // Debugging: Check the fetched user details
                } else {
                    this.error = data.error || 'An error occurred while fetching user details.';
                }
            } catch (error) {
                this.error = 'Network error occurred while fetching user details.';
            }
        },
    
        async disableUser() {
            const token = localStorage.getItem('access_token');
            const userId = this.selectedUser.id;
    
            try {
                const response = await fetch(`/liboard/users/${userId}/disable`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
    
                if (response.ok) {
                    // Update the status of the selected user
                    this.selectedUser.is_active = false;
    
                    // Optionally, update the user list
                    const userIndex = this.users.findIndex(user => user.id === userId);
                    if (userIndex !== -1) {
                        this.users[userIndex].is_active = false;
                    }
    
                    alert('User disabled successfully!');
                } else {
                    const data = await response.json();
                    this.error = data.error || 'An error occurred while disabling the user.';
                }
            } catch (error) {
                this.error = 'Network error occurred while disabling the user.';
            }
        }
    }
}
