<template>
    <HeaderBar />
    <div class="container d-flex justify-content-center text-center">
        <div class="card" style="width: 30rem; margin-top: 10rem;">
            <div class="card-body">
                <figure class="text-center">
                    <blockquote class="blockquote">
                        <img src="../assets/logo.svg" class="img-fluid logosvg" alt="..." width="32" height="32">
                        <h3>Quizmaster</h3>
                    </blockquote>
                    <figcaption class="blockquote-footer">
                        Quizmaster Pro: Engage, Challenge, Conquer!
                    </figcaption>
                </figure>
                <form @submit.prevent="login" class="align-items-center">
                    <div class="form-floating mb-3">
                        <input type="text" v-model="username" class="form-control" id="floatingusername" placeholder="name@example.com" name="login_id">
                        <label for="floatingusername">Username(E-mail)</label>
                    </div>
                    <div class="form-floating">
                        <input type="password" v-model="password" class="form-control" id="floatingPassword" placeholder="Password" name="login_password">
                        <label for="floatingPassword">Password</label>
                    </div>
                    <div style="padding: 1rem;">
                        <button type="submit" class="btn btn-secondary">Login</button>
                        <a href="/user/account/create" class="link-danger" style="padding: 1rem;">Create new user</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>


<script>
import HeaderBar from '../components/HeaderBar.vue';

export default {
    name: 'Login',
    components: {
        HeaderBar
    },
    data() {
        return {
            // Define your component's data properties here
            username: '',
            password: ''
        }
    },
    methods: {
        async login() {
            // Implement your login logic here
            try{
                const response = await fetch('http://127.0.0.1:5000/api/users/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: this.username,
                        password: this.password
                    })
                });
                const data = await response.json();
                if(!response.ok){
                    alert(data.error);
                    return;
                }
                else{
                    localStorage.setItem("access_token", data.access_token);
                    localStorage.setItem("refresh_token", data.refresh_token);
                    this.$router.push("/");
                }
            } catch (error) {
                console.error("Login failed:", error);
            }
        }
    }
}

</script>