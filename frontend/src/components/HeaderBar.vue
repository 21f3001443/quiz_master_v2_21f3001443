<template>
    <nav class="navbar navbar-expand-lg fixed-top bg-dark text-light" style="height: 15mm;">
        <div class="container-fluid">
            
            <!-- Navigation Links -->
            <div class="navbar-nav">
                <router-link to="/" class="nav-link text-light fw-bold">Home</router-link>
                <router-link to="/quiz" class="nav-link text-light fw-bold">Quiz</router-link>
                <router-link to="/userprofile" class="nav-link text-light fw-bold">User</router-link>
                <router-link to="/summary" class="nav-link text-light fw-bold">Summary</router-link>
                <router-link to="/logout" class="nav-link text-light fw-bold">Logout</router-link>
            </div>
            <form class="d-flex mx-auto" action="#" method="GET">
                <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" name="search" id="search">
            </form>

            <!-- Welcome Message -->
            <span class="navbar-text text-light fw-bold">
                Welcome Guest
            </span>
        </div>
    </nav>
</template>

<script>
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

            } catch (error) {
                console.error("Failed to fetch user status:", error);
            }
        }
    }
}
</script>