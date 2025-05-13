export default {
    template: `
    <div class="container">
        <h1>Books On Rent</h1>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="role === 'user'">
            <div v-if="myBooks.length">
                <table class="book-table">
                    <thead>
                        <tr>
                            <th>Image</th>
                            <th>Title</th>
                            <th>Author</th>
                            <th><th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="book in myBooks" :key="book.id">
                            <td><img :src="book.image" alt="Book cover" class="book-img"></td>
                            <td>{{ book.title }}</td>
                            <td>{{ book.author }}</td>
                            <td>
                            <button @click="readBook(book.id)">Read</button>
                            <button @click="returnBook(book.id)">Return</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else>
                <p>You have no books.</p>
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
            myBooks: []
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
                if (this.role === 'user') {
                    this.fetchMyBooks();
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
        async fetchMyBooks() {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch('/uboard/mybooks', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();

                if (response.ok) {
                    this.myBooks = data.books;
                } else {
                    this.error = data.error || 'An error occurred';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
        async returnBook(bookId) {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch(`/uboard/return/${bookId}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    alert('Book returned successfully!');
                    this.fetchMyBooks();  // Refresh the list of books
                } else {
                    const data = await response.json();
                    this.error = data.error || 'An error occurred';
                }
            } catch (error) {
                this.error = 'Network error';
            }
        },
    }
};
