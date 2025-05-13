export default {
    data() {
        return {
            user: {
                full_name: '',
                email: '',
                username: ''
            },
            showEditProfileModal: false,
            editProfile: {
                full_name: '',
                email: ''
            },
            error: '',
            success: ''
        };
    },
    async created() {
        await this.loadProfile();
    },
    methods: {
        async loadProfile() {
            try {
                const response = await fetch('/user_info', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    this.user = data;
                    this.editProfile = { ...data };
                } else {
                    this.error = 'Failed to load profile';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        async updateProfile() {
            try {
                const response = await fetch('/uboard/update_profile', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.editProfile)
                });
                if (response.ok) {
                    this.success = 'Profile updated successfully!';
                    this.error = '';
                    this.user = { ...this.editProfile };
                    this.showEditProfileModal = false;
                } else {
                    const data = await response.json();
                    this.error = data.error || 'Failed to update profile';
                    this.success = '';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        openEditProfileModal() {
            this.showEditProfileModal = true;
        },
        closeEditProfileModal() {
            this.showEditProfileModal = false;
        }
    },
    template: `
    <div class='container'>
        <h1>User Profile</h1>
        <div>
            <p><strong>Full Name:</strong> {{ user.full_name }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Username:</strong> {{ user.username }}</p>
            <button @click="openEditProfileModal">Edit Profile</button>
        </div>

        <!-- Edit Profile Modal -->
        <div v-if="showEditProfileModal" class="modal">
            <div class="modal-content">
                <h2>Edit Profile</h2>
                <form @submit.prevent="updateProfile">
                    <div>
                        <label for="full_name">Full Name:</label>
                        <input type="text" v-model="editProfile.full_name" id="full_name" required />
                    </div>
                    <div>
                        <label for="email">Email:</label>
                        <input type="email" v-model="editProfile.email" id="email" required />
                    </div>
                    <button type="submit">Save Changes</button>
                    <button @click="closeEditProfileModal">Cancel</button>
                </form>
                <p v-if="error" class="error">{{ error }}</p>
                <p v-if="success" class="success">{{ success }}</p>
            </div>
        </div>
    </div>
    `
};
