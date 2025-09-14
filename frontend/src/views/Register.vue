<template>
    <div class="container d-flex justify-content-center text-center">
        <div class="card" style="width: 60rem; margin-top: 10rem;">
            <div class="card-body">
                <figure class="text-center">
                    <blockquote class="blockquote">
                        <h2><span class="badge text-bg-warning">New User</span></h2>
                    </blockquote>
                </figure>
                <form @submit.prevent="register" class="row g-3 needs-validation">
                    <div class="col-md-6">
                        <label for="user_id" class="form-label">User ID : </label>
                        <input type="text" v-model="user_id" class="form-control" id="user_id" name="user_id" title="Please provide a User ID!" required>
                        <div class="invalid-feedback">
                            Please provide a User ID!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="password" class="form-label">Password : </label>
                        <input type="password" v-model="password" class="form-control" id="password" name="password" title="Password must be at least 8 characters long!" pattern="^.{8,}$" required>
                        <div class="invalid-feedback">
                            Password must be at least 8 characters long!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="user_fname" class="form-label">First Name : </label>
                        <input type="text" v-model="user_fname" class="form-control" id="user_fname" name="user_fname" title="Please provide user first name!" required>
                        <div class="invalid-feedback">
                            Please provide user first name!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="user_lname" class="form-label">Last Name : </label>
                        <input type="text" v-model="user_lname" class="form-control" id="user_lname" name="user_lname" title="Please provide user last name!" required>
                        <div class="invalid-feedback">
                            Please provide user last name!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="user_qualification" class="form-label">Qualification : </label>
                        <input type="text" v-model="user_qualification" class="form-control" id="user_qualification" name="user_qualification" title="Please provide highest qualification!" required>
                        <div class="invalid-feedback">
                            Please provide highest qualification!
                        </div>
                    </div>
                    <div class="col-md-6">
                        <label for="user_dob" class="form-label">DOB : YYYY-MM-DD</label>
                        <input type="text" v-model="user_dob" class="form-control" id="user_dob" name="user_dob" title="1985-02-01" pattern="\d{4}-\d{2}-\d{2}" required>
                        <div class="invalid-feedback">
                            Please provide date of birth!
                        </div>
                    </div>
                    <div style="padding: 1rem;">
                        <button type="submit" class="btn btn-secondary">Save</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>


<script>
export default {
    data() {
        return {
            // Define your component's data properties here
            user_id: '',
            password: '',
            user_fname: '',
            user_lname: '',
            user_qualification: '',
            user_dob: '',
            role_id: 'user'
        }
    },
    methods: {
        async register() {
            // Implement your login logic here
            try{
                const response = await fetch('http://127.0.0.1:5000/api/users/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: this.user_id,
                        password: this.password,
                        user_fname: this.user_fname,
                        user_lname: this.user_lname,
                        user_qualification: this.user_qualification,
                        user_dob: this.user_dob,
                        role_id: this.role_id
                    })
                });
                const data = await response.json();
                if(!response.ok){
                    alert(data.error);
                    return;
                }
                else{
                    alert(data.message);
                    this.$router.push("/login");
                }
            } catch (error) {
                console.error("Registration failed:", error);
            }
        }
    }
}

</script>