import { jwtDecode } from "jwt-decode";

export default {
    name: 'HeaderBar',
    data() {
        return {
            // Define your component's data properties here
            user: "Guest",
            role: null,
            loggedIn: false,
            isExpired: true
        }
    },
    methods: {
        async userStatus() {
            // Implement your user status logic here
            try {
                const access_token = localStorage.getItem("access_token");
                if (!access_token) {
                    this.user = "Guest";
                    this.role = null;
                    this.loggedIn = false;
                    this.isExpired = true;
                    return;
                }

                const response = await fetch('http://127.0.0.1:5000/api/users/login/ping', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${access_token}`
                    }
                });
                const data = await response.json();
                if (!response.ok) {
                    return
                }
            
                const decoded = jwtDecode(access_token);
                this.user = decoded.sub;
                this.role = decoded.role;
                this.isExpired = Date.now() / 1000 >= decoded.exp;
                if (!this.isExpired) {
                    this.loggedIn = true;
                }

            } catch (error) {
                console.error("Failed to fetch user status:", error);
            }
        }
    },
    async created() {
        await this.userStatus();
    }
}