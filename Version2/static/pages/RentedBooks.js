export default {
    template: `
      <div class="container">
        <h1>Books on Rent</h1>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="role === 'librarian'">
          <div v-if="booksOnRent.length">
            <!-- Search input -->
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search by book name or username"
              class="search-input"
            />
  
            <table class="book-table">
              <thead>
                <tr>
                  <th>Book ID</th>
                  <th>Image</th>
                  <th>Book Name</th>
                  <th>User</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <!-- Use computed property to filter books -->
                <tr v-for="book in filteredBooksOnRent" :key="book.book_id">
                  <td>{{ book.book_id }}</td>
                  <td><img :src="book.image_url" alt="Book Image" class="book-image"/></td>
                  <td>{{ book.book_name }}</td>
                  <td>{{ book.username }}</td>
                  <td>
                    <button @click="revokeAccess(book.book_id)">
                      Revoke Access
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else>
            <p>No books are currently on rent.</p>
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
        booksOnRent: [],
        searchQuery: '', // New data property for search input
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
            Authorization: `Bearer ${token}`,
          },
        });
        const data = await response.json();
  
        if (response.ok) {
          this.username = data.username;
          this.role = data.role;
          if (this.role === 'librarian') {
            this.fetchBooksOnRent();
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
      async fetchBooksOnRent() {
        const token = localStorage.getItem('access_token');
        try {
          const response = await fetch('/liboard/on_rent', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          const data = await response.json();
  
          if (response.ok) {
            this.booksOnRent = data.books_on_rent;
          } else {
            this.error = data.error || 'An error occurred';
          }
        } catch (error) {
          this.error = 'Network error';
        }
      },
      async revokeAccess(bookId) {
        const token = localStorage.getItem('access_token');
        try {
          const response = await fetch(`/liboard/revoke_access/${bookId}`, {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          const data = await response.json();
  
          if (response.ok) {
            this.fetchBooksOnRent(); // Refresh the list after revoking access
          } else {
            this.error = data.error || 'An error occurred';
          }
        } catch (error) {
          this.error = 'Network error';
        }
      },
    },
    computed: {
      filteredBooksOnRent() {
        const query = this.searchQuery.toLowerCase();
        return this.booksOnRent.filter((book) => {
          return (
            book.book_name.toLowerCase().includes(query) ||
            book.username.toLowerCase().includes(query)
          );
        });
      },
    },
  };
  