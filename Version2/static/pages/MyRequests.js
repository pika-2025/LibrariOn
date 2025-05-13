export default {
  template: `
    <div class='container'>
      <h1>My Requests</h1>
      <table class='book-table'>
        <thead>
          <tr>
            <th>Book Title</th>
            <th>Request Date</th>
            <th>Return Date</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in rentalRequests" :key="request.id">
            <td>{{ request.book }}</td>
            <td>{{ request.request_date }}</td>
            <td>{{ request.return_date }}</td>
            <td>{{ request.status }}</td>
            <td>
              <button v-if="request.status === 'pending'" @click="cancelRequest(request.id)">Cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
  data() {
    return {
      rentalRequests: []
    };
  },
  created() {
    this.loadRequests();
  },
  methods: {
    async loadRequests() {
      try {
        const response = await fetch('/uboard/myrequests', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        const data = await response.json();
        this.rentalRequests = data.rental_requests;
      } catch (error) {
        console.error('Error fetching requests:', error);
      }
    },
    async cancelRequest(requestId) {
      try {
        const response = await fetch(`/uboard/myrequests/${requestId}/cancel`, {
          method: 'POST',  // Changed to POST
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (response.ok) {
          this.rentalRequests = this.rentalRequests.map(request =>
            request.id === requestId ? { ...request, status: 'cancelled' } : request
          );
        } else {
          console.error('Failed to cancel request');
        }
      } catch (error) {
        console.error('Error canceling request:', error);
      }
    }
  }
};
