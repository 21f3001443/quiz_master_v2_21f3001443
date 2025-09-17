<template>
    <nav class="navbar navbar-expand-lg fixed-top bg-dark text-light" style="height: 15mm;">
        <div class="container-fluid">
            
            <!-- Navigation Links -->
            <div class="navbar-nav">
                <ul v-if="loggedIn" class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <router-link to="/" class="nav-link text-light fw-bold">Home</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link to="/quiz" class="nav-link text-light fw-bold">Quiz</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link to="/userprofile" class="nav-link text-light fw-bold">User</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link to="/summary" class="nav-link text-light fw-bold">Summary</router-link>
                    </li>
                    <li class="nav-item">
                        <button @click="logout" class="btn btn-link text-light fw-bold text-decoration-none">Logout</button>
                    </li>
                </ul>
                <ul v-if="!loggedIn" class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <router-link to="/login" class="nav-link text-light fw-bold">Login</router-link>
                    </li>
                    <li class="nav-item">
                        <router-link to="/register" class="nav-link text-light fw-bold">Register</router-link>
                    </li>
                </ul>
            </div>
            <form class="d-flex mx-auto" action="#" method="GET">
                <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search" name="search" id="search">
            </form>

            <!-- Welcome Message -->
            <span class="navbar-text text-light fw-bold">
                Welcome {{ user }}
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
        },
        async logout() {
            try {
                const access_token = localStorage.getItem("access_token");
                const response = await fetch('http://127.0.0.1:5000/api/users/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${access_token}`
                    }
                });
                const data = await response.json();
                if (!response.ok) {
                    return
                }
                localStorage.removeItem("access_token");
                this.user = "Guest";
                this.role = null;
                this.loggedIn = false;
                this.isExpired = true;
            } catch (error) {
                console.error("Failed to logout:", error);
            }
        }
    },
    async created() {
        await this.userStatus();
    }
}
</script>