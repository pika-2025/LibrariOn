export default {
  template: `
    <div class="container">
      <h1>All Rental Requests</h1>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="role === 'librarian'">
        <!-- Export CSV Button -->
        <button @click="exportCSV" class="export-btn">Export as CSV</button>

        <div v-if="rentalRequests.length">
          <!-- Search input -->
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search by book, user, or status"
            class="search-input"
          />

          <table class="book-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Book</th>
                <th>User</th>
                <th>Date Requested</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <!-- Use computed property to filter requests -->
              <tr v-for="request in filteredRequests" :key="request.id">
                <td>{{ request.id }}</td>
                <td>{{ request.book }}</td>
                <td>{{ request.user }}</td>
                <td>{{ request.date_requested }}</td>
                <td>{{ request.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else>
          <p>No rental requests found.</p>
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
      rentalRequests: [],
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
            Authorization: `Bearer ${token}`,
          },
        });
        const data = await response.json();

        if (response.ok) {
          this.rentalRequests = data.rental_requests;
        } else {
          this.error = data.error || 'An error occurred';
        }
      } catch (error) {
        this.error = 'Network error';
      }
    },
    exportCSV() {
      const csvRows = [];
      const headers = ['Book Name', 'Content', 'Author', 'Date Issued', 'Return Date', 'User'];
      csvRows.push(headers.join(','));

      this.filteredRequests.forEach(request => {
        const bookName = request.book;
        const content = request.content || '';
        const author = request.author || '';
        const dateIssued = new Date(request.date_requested).toLocaleDateString();
        const returnDate = new Date(new Date(request.date_requested).setDate(new Date(request.date_requested).getDate() + 7)).toLocaleDateString();
        const user = request.user;

        csvRows.push([bookName, content, author, dateIssued, returnDate, user].join(','));
      });

      const csvString = csvRows.join('\n');
      const blob = new Blob([csvString], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'rental_requests.csv';
      a.click();
      URL.revokeObjectURL(url);
    },
  },
  computed: {
    filteredRequests() {
      const query = this.searchQuery.toLowerCase();
      return this.rentalRequests.filter((request) => {
        return (
          request.book.toLowerCase().includes(query) ||
          request.user.toLowerCase().includes(query) ||
          request.status.toLowerCase().includes(query)
        );
      });
    },
  },
};
