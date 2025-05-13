export default {
    data() {
        return {
            genre: {},
            books: [],
            showAddBookForm: false,
            showDetailsModal: false,
            selectedBook: null,
            newBook: {
                title: '',
                author: '',
                image: null,
                content: null,
            },
            error: '',
            success: ''
        };
    },
    async created() {
        const genreId = this.$route.params.genreId;
        await this.fetchBooks(genreId);
    },
    methods: {
        readBook(contentUrl) {
            window.open(contentUrl, '_blank');
        },
        editBook(book) {
            // Implement edit functionality
        },

        async fetchBooks(genreId) {
            try {
                const response = await fetch(`/liboard/genres/${genreId}/books`, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    this.genre = data.genre;
                    this.books = data.books;
                } else {
                    this.error = 'Failed to fetch books';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        toggleAddBookForm() {
            this.showAddBookForm = !this.showAddBookForm;
        },
        handleFileUpload(event, type) {
            if (type === 'image') {
                this.newBook.image = event.target.files[0];
            } else if (type === 'content') {
                this.newBook.content = event.target.files[0];
            }
        },
        async addBook() {
            const formData = new FormData();
            formData.append('title', this.newBook.title);
            formData.append('author', this.newBook.author);
            formData.append('image', this.newBook.image);
            formData.append('content', this.newBook.content);

            try {
                const response = await fetch(`/liboard/genres/${this.genre.id}/books`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    },
                    body: formData
                });

                if (response.ok) {
                    this.success = 'Book added successfully!';
                    this.error = '';
                    this.showAddBookForm = false;
                    this.newBook = {};  // Reset form
                    await this.fetchBooks(this.genre.id);
                } else {
                    const data = await response.json();
                    this.error = data.error || 'An error occurred';
                    this.success = '';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        openDetailsModal(book) {
            this.selectedBook = book;
            this.showDetailsModal = true;
        },
        async deleteBook(bookId) {
            try {
                const response = await fetch(`/liboard/books/${bookId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });

                if (response.ok) {
                    this.success = 'Book deleted successfully!';
                    this.error = '';
                    this.showDetailsModal = false;
                    await this.fetchBooks(this.genre.id);
                } else {
                    this.error = 'Failed to delete book';
                    this.success = '';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        }
    },
    template: `
    <div class='container'>
        <h2>{{ genre.name }} - Books</h2>
        <button @click="showAddBookForm = true">Add New Book</button>

        <div v-if="showAddBookForm" class="add-book-form">
            <h3>Add New Book</h3>
            <form @submit.prevent="addBook">
                <div>
                    <label for="title">Book Title:</label>
                    <input type="text" v-model="newBook.title" required>
                </div>
                <div>
                    <label for="author">Author:</label>
                    <input type="text" v-model="newBook.author" required>
                </div>
                <div>
                    <label for="image">Image:</label>
                    <input type="file" @change="handleFileUpload($event, 'image')">
                </div>
                <div>
                    <label for="content">Content:</label>
                    <input type="file" @change="handleFileUpload($event, 'content')">
                </div>
                <button type="submit">Add Book</button>
                <button @click="showAddBookForm = false">Cancel</button>
            </form>
        </div>

        <table class="book-table">
            <thead>
                <tr>
                    <th></th>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="book in books" :key="book.id">
                    <td><img :src="book.image" alt="Book Image" class="book-image"></td>
                    <td>{{ book.title }}</td>
                    <td>{{ book.author }}</td>
                    <td>
                        <button @click="openDetailsModal(book)">See Details</button>
                    </td>
                </tr>
            </tbody>
        </table>

        <div v-if="showDetailsModal" class="modal">
            <div class="modal-content">
                <h3>{{ selectedBook.title }}</h3>
                <img :src="selectedBook.image" alt="Book Image" class="book-image">
                <p><strong>Author:</strong> {{ selectedBook.author }}</p>
                <p><strong>Price:</strong>  {{ selectedBook.price }}</p>
                <p><strong>Rating:</strong> {{ selectedBook.rating }}</p>
                <div>
                    <h4>Feedbacks</h4>
                    <ul>
                        <li v-for="feedback in selectedBook.feedbacks" :key="feedback.id">{{ feedback.text }}</li>
                    </ul>
                </div>
                <button @click="readBook(selectedBook.content)">Read</button>
                <button @click="deleteBook(selectedBook.id)">Delete</button>
                <button @click="editBook(selectedBook)">Edit</button>
                <button @click="showDetailsModal = false">Close</button>
            </div>
        </div>
    </div>
    `
};
