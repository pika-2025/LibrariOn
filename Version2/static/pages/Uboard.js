export default {
  data() {
      return {
          books: [],
          error: '',
          showModal: false,
          selectedBook: null,
          searchQuery: ''
      };
  },
  async created() {
      const token = localStorage.getItem('access_token');
      if (!token) {
          this.$router.push('/login');
          return;
      }
      await this.fetchBooks();
  },
  methods: {
      async fetchBooks() {
          const token = localStorage.getItem('access_token');
          try {
              const response = await fetch('/uboard', {
                  headers: {
                      'Authorization': `Bearer ${token}`
                  }
              });
              const data = await response.json();

              if (response.ok) {
                  this.books = data.books.filter(book => book.is_available);
              } else {
                  this.error = data.error || 'An error occurred';
              }
          } catch (error) {
              console.error('Network error:', error);
              this.error = 'Network error';
          }
      },
      async openBookDetails(bookId) {
          const token = localStorage.getItem('access_token');
          try {
              const response = await fetch(`/uboard/book/${bookId}`, {
                  headers: {
                      'Authorization': `Bearer ${token}`
                  }
              });
              const data = await response.json();
              console.log(data);  // Debugging line
    
              if (response.ok) {
                  this.selectedBook = data.book;
                  this.showModal = true;
              } else {
                  this.error = data.error || 'An error occurred';
              }
          } catch (error) {
              console.error('Network error:', error);
              this.error = 'Network error';
          }
      },
      closeModal() {
          this.showModal = false;
          this.selectedBook = null;
      },
      async rentBook(bookId) {
          const token = localStorage.getItem('access_token');
          try {
              const response = await fetch(`/uboard/rent/${bookId}`, {
                  method: 'POST',
                  headers: {
                      'Authorization': `Bearer ${token}`
                  }
              });

              if (response.ok) {
                  alert('Rental request sent!');
                  await this.fetchBooks();  // Refresh the books list
                  this.closeModal();
              } else {
                  const data = await response.json();
                  this.error = data.error || 'An error occurred';
              }
          } catch (error) {
              console.error('Network error:', error);
              this.error = 'Network error';
          }
      }
  },
  computed: {
      filteredBooks() {
          const query = this.searchQuery.toLowerCase();
          return this.books.filter(book => {
              return book.title.toLowerCase().includes(query) || 
                     book.genre.toLowerCase().includes(query);
          });
      }
  },
  template: `
    <div class="container">
      <h1>Books</h1>

      <!-- Search Bar -->
      <div class="search-bar">
          <input type="text" v-model="searchQuery" placeholder="Search by title or genre..." />
      </div>
      <hr>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="filteredBooks.length" class="books-row">
        <div v-for="book in filteredBooks" :key="book.id" class="card">
          <img :src="book.image" alt="Book Image" v-if="book.image">
          <div class="card-body">
            <h3 class="card-title">{{ book.title }}</h3>
            <p class="card-text"><strong>Author:</strong> {{ book.author }}</p>
            <button @click="openBookDetails(book.id)" class="btn btn-primary">Details</button>
            <button @click="rentBook(book.id)" class="btn btn-success mt-2">Request Rental</button>
          </div>
        </div>
      </div>
      <div v-else>
        <p>No books available.</p>
      </div>

      <!-- Modal for Book Details -->
      <div v-if="showModal" class="modal" @click.self="closeModal">
        <div class="modal-content">
          <span class="close-button" @click="closeModal">&times;</span>
          <div v-if="selectedBook">
            <img :src="selectedBook.image" class="img-fluid" alt="Book Image" v-if="selectedBook.image">
            <h3>{{ selectedBook.title }}</h3>
            <p><strong>Author:</strong> {{ selectedBook.author }}</p>
            <p><strong>Genre:</strong> {{ selectedBook.genre }}</p>
            <p v-if="selectedBook.content">Content available</p>
            <p v-else>No content available</p>
            <button @click="rentBook(selectedBook.id)" class="btn btn-primary" :disabled="!selectedBook.is_available">Rent</button>
          </div>
        </div>
      </div>
    </div>
  `,
}
