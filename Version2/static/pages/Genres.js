export default {
    data() {
        return {
            genres: [],
            showAddGenreForm: false,
            newGenre: {
                name: '',
                description: '',
                image: null,
            },
            error: '',
            success: ''
        };
    },
    async created() {
        await this.fetchGenres();
    },
    methods: {
        async fetchGenres() {
            try {
                const response = await fetch('/liboard/genres', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                const data = await response.json();
                console.log(data);  // Check what data is being received
                if (response.ok) {
                    this.genres = data;
                } else {
                    this.error = 'Failed to fetch genres';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        
        toggleAddGenreForm() {
            this.showAddGenreForm = !this.showAddGenreForm;
        },
        handleFileUpload(event) {
            this.newGenre.image = event.target.files[0];
        },
        async addGenre() {
            const formData = new FormData();
            formData.append('name', this.newGenre.name);
            formData.append('description', this.newGenre.description);
            if (this.newGenre.image) {
                formData.append('image', this.newGenre.image);
            }

            try {
                const response = await fetch('/liboard/genres', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    },
                    body: formData
                });

                if (response.ok) {
                    this.success = 'Genre added successfully!';
                    this.error = '';
                    this.showAddGenreForm = false;
                    this.newGenre.name = '';
                    this.newGenre.description = '';
                    this.newGenre.image = null;
                    await this.fetchGenres();
                } else {
                    const data = await response.json();
                    this.error = data.error || 'An error occurred';
                    this.success = '';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        viewBooks(genreId) {
            this.$router.push(`/liboard/genres/${genreId}/books`);
        },
        async deleteGenre(genreId) {
            try {
                const response = await fetch(`/liboard/genres/${genreId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
        
                if (response.ok) {
                    this.success = 'Genre deleted successfully!';
                    this.error = '';
                    await this.fetchGenres();
                } else {
                    const data = await response.json();
                    this.error = data.error || 'Failed to delete genre';
                    this.success = '';
                }
            } catch (error) {
                console.error('Delete genre error:', error); // Log detailed error
                this.error = 'Network error';
            }
        }
    },
    template: `
    <div class='container'>
        <h2>Genres</h2>
        <button @click="showAddGenreForm = true">Add New Genre</button>

        <div v-if="showAddGenreForm" class="add-genre-form">
            <h3>Add New Genre</h3>
            <form @submit.prevent="addGenre">
                <div>
                    <label for="name">Genre Name:</label>
                    <input type="text" v-model="newGenre.name" required>
                </div>
                <div>
                    <label for="description">Description:</label>
                    <textarea v-model="newGenre.description"></textarea>
                </div>
                <div>
                    <label for="image">Image:</label>
                    <input type="file" @change="handleFileUpload">
                </div>
                <button type="submit">Add Genre</button>
                <button @click="showAddGenreForm = false">Cancel</button>
            </form>
        </div>

        <table class="genre-table">
            <thead>
                <tr>
                    <th></th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Date Created</th>
                    <th>Actions</th>

                </tr>
            </thead>
            <tbody>
                <tr v-for="genre in genres" :key="genre.id">
                    <td><img :src="genre.image" alt="Genre Image" class="genre-image"></td>
                    <td>{{ genre.name }}</td>
                    <td>{{ genre.description }}</td>
                    <td>{{genre.date_created}}</td>
                    <td>
                        <button @click="viewBooks(genre.id)">View Books</button>
                        <button @click="deleteGenre(genre.id)">Delete</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    `
};
