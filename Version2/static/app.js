import router from "./utilities/router.js";
import Navbar from "./components/Navbar.js";
import LibNavbar from "./components/LibNavbar.js";
import Unavbar from "./components/Unavbar.js";

new Vue({
    el: "#app",
    template:`
    <div>
        <Navbar v-if="!isLiboardPage && !isUboardPage"/>        
        <LibNavbar v-if="isLiboardPage"/>
        <Unavbar v-if="isUboardPage"/>
        <router-view/>
    </div>
    `,
    router,
    computed: {
        isLiboardPage(){
            return this.$route.path.startsWith('/liboard');
        },
        isUboardPage(){
            return this.$route.path.startsWith('/uboard')
        }
    },
    components: {
        Navbar,
        LibNavbar,
        Unavbar
    },
});