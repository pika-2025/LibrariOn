export default {
    template: `
    <div class="container">
        <h1>Welcome to the Librarian Dashboard</h1>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="role === 'librarian'">
            <h2>Rental Requests</h2>
            <div v-if="rentalRequests.length">
                <table class="rental-requests-table">
                    <thead>
                        <tr>
                            <th>Image</th>
                            <th>Title</th>
                            <th>Username</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="request in rentalRequests" :key="request.id">
                            <td><img :src="request.image" alt="Book cover" class="request-img"></td>
                            <td>{{ request.book }}</td>
                            <td>{{ request.user }}</td>
                            <td>{{ request.status }}</td>
                            <td>
                                <button @click="acceptRequest(request.id)">Accept</button>
                                <button @click="rejectRequest(request.id)">Reject</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else>
                <p>No rental requests.</p>
            </div>
        </div>
        <div v-else>
            <p>You do not have permission to access this dashboard.</p>
        </div>
    </div>
    `,
    data() {
        return {
            username: '',
            role: '',
            error: '',
            rentalRequests: []
        };
    },
    async created() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            this.$router.push('/login');
            return;
        }

        try {
            const response = await fetch('/user_info', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();

            if (response.ok) {
                this.username = data.username;
                this.role = data.role;
                if (this.role === 'librarian') {
                    this.fetchRentalRequests();
                } else {
                    this.$router.push('/login');
                }
            } else {
                this.error = data.error || 'An error occurred';
                this.$router.push('/login');
            }
        } catch (error) {
            this.error = 'Network error';
            this.$router.push('/login');
        }
    },
    methods: {
        async fetchRentalRequests() {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch('/liboard', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();

                if (response.ok) {
                    this.rentalRequests = data.rental_requests.filter(request => request.status === 'pending')
                    .map(request => ({
                        ...request,
                    }));
                } else {
                    this.error = data.error || 'An error occurred';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        async acceptRequest(requestId) {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch(`/liboard/rental_requests/${requestId}/accept`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    alert('Request accepted!');
                    this.fetchRentalRequests();  // Refresh the requests list
                } else {
                    const data = await response.json();
                    this.error = data.error || 'An error occurred';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        async rejectRequest(requestId) {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch(`/liboard/rental_requests/${requestId}/reject`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    alert('Request rejected!');
                    this.fetchRentalRequests();  // Refresh the requests list
                } else {
                    const data = await response.json();
                    this.error = data.error || 'An error occurred';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        }
    }
};
