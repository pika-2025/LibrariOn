import Home from "../pages/Home.js";
import Login from "../pages/Login.js";
import Register from "../pages/Register.js";
import LibrarianDashboard from "../pages/Liboard.js";
import Genres from "../pages/Genres.js";
import GenreBooks from "../pages/GenreBooks.js";
import UserDashboard from "../pages/Uboard.js";
import MyBooks from "../pages/MyBooks.js";
import MyRequests from "../pages/MyRequests.js";
import Uprofile from "../pages/Uprofile.js";
import UserList from "../pages/UserList.js";
import RentalHist from "../pages/RentalHist.js"
import BooksRented from "../pages/RentedBooks.js"


const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/liboard', component: LibrarianDashboard, meta: { requiresAuth: true, role: 'librarian' } },
    { path: '/liboard/genres', component: Genres, meta: { requiresAuth: true, role: 'librarian' } },
    { path: '/liboard/genres/:genreId/books', component: GenreBooks, meta: { requiresAuth: true, role: 'librarian' } },
    { path: '/uboard', component: UserDashboard, meta:{requiresAuth:true, role:'user'}},
    { path: '/uboard/mybooks', component: MyBooks, meta:{requiresAuth:true, role: 'user'}},
    { path: '/uboard/myrequests', component: MyRequests, meta:{requiresAuth:true, role: 'user'}},
    { path: '/uboard/profile', component: Uprofile, meta: {requiresAuth:true, role:'user'}},
    {path: '/liboard/users', component: UserList, meta: {requiresAuth:true, role:'librarian'}},
    {path: '/liboard/rental_hist', component: RentalHist, meta: {requiresAuth:true, role:'librarian'}},
    {path: '/liboard/on_rent', component: BooksRented, meta: {requiresAuth:true, role:'librarian'}}
];


const router = new VueRouter({
    routes,
});


router.beforeEach(async (to, from, next) => {
    const token = localStorage.getItem('access_token');
    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!token) {
            next('/login');
        } else {
            try {
                const response = await fetch('/user_info', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    if (to.meta.role && data.role !== to.meta.role) {
                        next('/');
                    } else {
                        next();
                    }
                } else {
                    next('/login');
                }
            } catch (error) {
                next('/login');
            }
        }
    } else {
        next();
    }
});

export default router;